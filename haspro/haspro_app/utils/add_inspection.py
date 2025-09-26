import sqlite3
import tempfile
import os
import io
import datetime

from django.db import transaction
from django.core.files import File

from ..models import (
    InspectionRecord, 
    FaultInspection, 
    Building, 
    FaultPhoto,
    Firedistinguisher,
    FiredistinguisherPlacement,
    FiredistinguisherServiceAction,
    FiredistinguisherServiceActionType,
    FiredistinguisherKind,
)



class InspectionImportError(Exception):
    pass



def connect_and_verify_db(file_path):
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        # Example: get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        required_tables = {
            "inspection_record", 
            "fault_inspection", 
            "fault_photo", 
            "firedistinguisher", 
            "firedistinguisher_placement", 
            "firedistinguisher_service_action", 
            "database_version"
        }
        table_names = {table[0] for table in tables}
        missing_tables = required_tables - table_names
        if missing_tables:
            raise InspectionImportError(f"Missing tables: {', '.join(missing_tables)}")
        conn.close()
        return tables
    except sqlite3.DatabaseError as e:
        raise InspectionImportError(f"Database error: {e}")


def _add_inspection_record(obj_map, conn, user, company, db_file_buffer):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inspection_record")
    records = cursor.fetchall()

    if len(records) != 1:
        raise InspectionImportError("The database must contain exactly one inspection record.")

    obj_map["InspectionRecord"] = {}

    record = records[0]
    id, _, date, notes, building_id, created_at, _ = record

    building = Building.objects.filter(id=building_id, company=company).first()

    if not building:
        raise InspectionImportError(f"Building with ID {building_id} not found in the current company.")

    # Check if the record already exists
    existing = InspectionRecord.objects.filter(date=date, building_id=building_id).first()
    if existing:
        # TODO: maybe store for later processing
        raise InspectionImportError(f"InspectionRecord for date {date} and building {building_id} already exists.")

    # Create new InspectionRecord
    inspection = InspectionRecord(
        inspector=user,
        date=date,
        notes=notes,
        building_id=building_id,
        created_at=created_at,
        uploaded_file=File(db_file_buffer)
    )

    inspection.save()
    
    # Track the uploaded file for potential cleanup
    if "uploaded_files" in obj_map and inspection.uploaded_file:
        obj_map["uploaded_files"].append(inspection.uploaded_file.path)

    obj_map["InspectionRecord"][id] = inspection
    
    return 1



def _add_fault_records(obj_map, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fault_inspection")
    records = cursor.fetchall()
    
    num_updated = 0

    obj_map["FaultInspection"] = {}
    for record in records:
        id, fault_id, short_name, description, inspection_id, notes, responsible_person, fix_due_date, resolved, present = record

        if fix_due_date and len(fix_due_date) > 10:
            fix_due_date = fix_due_date[:10]

        if inspection_id not in obj_map["InspectionRecord"]:
            raise InspectionImportError(f"Referenced InspectionRecord ID {inspection_id} not found in the imported data.")

        # Create new FaultInspection
        fault_inspection = FaultInspection(
            fault_id=fault_id,
            short_name=short_name,
            description=description,
            inspection=obj_map["InspectionRecord"].get(inspection_id),
            notes=notes,
            responsible_person=responsible_person,
            fix_due_date=fix_due_date,
            resolved=resolved,
            present=present
        )
        fault_inspection.save()

        obj_map["FaultInspection"][id] = fault_inspection
        num_updated += 1

    cursor.execute("SELECT * FROM fault_photo")
    records = cursor.fetchall()

    obj_map["FaultPhoto"] = {}

    for record in records:
        id, fault_id, photo, uploaded_at = record

        if fault_id not in obj_map["FaultInspection"]:
            raise InspectionImportError(f"Referenced FaultInspection ID {fault_id} not found in the imported data.")

        # Create new File
        photo_file = File(io.BytesIO(photo))
        photo_file.name = f"fault_{fault_id:04d}_photo_{id:04d}.jpg"

        fault_photo = FaultPhoto(
            fault_inspection=obj_map["FaultInspection"].get(fault_id),
            photo=photo_file,
            uploaded_at=uploaded_at
        )
        fault_photo.save()
        
        # Track the uploaded file for potential cleanup
        if "uploaded_files" in obj_map and fault_photo.photo:
            obj_map["uploaded_files"].append(fault_photo.photo.path)
        
        obj_map["FaultPhoto"][id] = fault_photo

    return num_updated

def _add_new_firedistinguisher(obj_map, conn, company):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM firedistinguisher")
    records = cursor.fetchall()

    num_updated = 0

    obj_map["Firedistinguisher"] = {}
    for record in records:
        id, kind, size, power, manufacturer, serial_number, eliminated, manufactured_year, managed_by_id, next_inspection = record

        fd = Firedistinguisher.objects.filter(serial_number=serial_number).first()
        if fd:
            obj_map["Firedistinguisher"][id] = fd
            continue  # Skip existing

        # Create new Firedistinguisher
        fd = Firedistinguisher(
            kind=kind,
            size=size,
            power=power,
            manufacturer=manufacturer,
            serial_number=serial_number,
            eliminated=eliminated,
            manufactured_year=manufactured_year,
            managed_by=company,
            next_inspection=next_inspection
        )
        fd.save()

        obj_map["Firedistinguisher"][id] = fd
        num_updated += 1

    return num_updated

def _add_firedistinguisher_placements(obj_map, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM firedistinguisher_placement")
    records = cursor.fetchall()

    num_updated = 0

    obj_map["FiredistinguisherPlacement"] = {}
    for record in records:
        id, description, created_at, firedistinguisher_id, building_id = record

        if firedistinguisher_id in obj_map["Firedistinguisher"]:
            firedistinguisher_id = obj_map["Firedistinguisher"].get(firedistinguisher_id).pk

        # Create new FiredistinguisherPlacement
        fdp = FiredistinguisherPlacement(
            description=description,
            created_at=created_at,
            firedistinguisher_id=firedistinguisher_id,
            building_id=building_id
        )
        fdp.save()

        obj_map["FiredistinguisherPlacement"][id] = fdp
        num_updated += 1

    return num_updated


def _add_firedistinguisher_inspections(obj_map, conn):
    
    num_updated = 0

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM firedistinguisher_service_action")
    records = cursor.fetchall()

    obj_map["FiredistinguisherServiceAction"] = {}
    for record in records:
        id, firedistinguisher_id, action_type, description, created_at = record

        if firedistinguisher_id not in obj_map["Firedistinguisher"]:
            raise InspectionImportError(f"Referenced Firedistinguisher ID {firedistinguisher_id} not found in the imported data.")

        fd = obj_map["Firedistinguisher"].get(firedistinguisher_id)

        service_action = FiredistinguisherServiceAction(
            firedistinguisher=fd,
            action_type=action_type,
            description=description,
            created_at=created_at
        )
        service_action.save()
        obj_map["FiredistinguisherServiceAction"][id] = service_action

    return num_updated



def _update_firedistinguisher_next_inspection(obj_map):
    for fda in obj_map.get("FiredistinguisherServiceAction", {}).values():
        if fda.action_type == FiredistinguisherServiceActionType.INSPECTION:
            fd = Firedistinguisher.objects.filter(id=fda.firedistinguisher.id).first()
            fd.next_inspection = fda.created_at + datetime.timedelta(days=365)  # Set next inspection one year later
            fd.save()

        elif fda.action_type == FiredistinguisherServiceActionType.ELIMINATION:
            fd = Firedistinguisher.objects.filter(id=fda.firedistinguisher.id).first()
            fd.eliminated = True
            fd.next_inspection = None
            fd.next_periodic_test = None
            fd.save()

        elif fda.action_type == FiredistinguisherServiceActionType.PERIODIC_TEST:
            fd = Firedistinguisher.objects.filter(id=fda.firedistinguisher.id).first()
            fd.next_inspection = fda.created_at + datetime.timedelta(days=365)  # Set next inspection one year later
            if fd.kind == FiredistinguisherKind.WATER or fd.kind == FiredistinguisherKind.FOAM:
                fd.next_periodic_test = fda.created_at + datetime.timedelta(days=365 * 3)  # Set next periodic test three years later
            else:
                fd.next_periodic_test = fda.created_at + datetime.timedelta(days=365 * 5)  # Set next periodic test five years later
            fd.save()
    


def add_inspection(user, company, file):
    """
    Add inspection data from an uploaded SQLite database file.
    - accepts only one inspection record
    - all referenced buildings must exist in the current company
    - if the inspection record already exists (same date and building), it is skipped
    - if the inspector does not match the current user, an error is raised
    :param user: The user performing the import.
    :param company: The company associated with the import.
    :param file: The uploaded file object (should be a SQLite database).
    :return: A tuple (num_updated, error_message). If error_message is None,
    """

    # Create a temporary file that won't be auto-deleted
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.read())
        temp_file.flush()  # Ensure data is written to disk
        temp_filename = temp_file.name

    # Track uploaded files for cleanup on failure
    uploaded_files = []
    
    try:
        connect_and_verify_db(temp_filename)

        with sqlite3.connect(temp_filename) as conn:
            with transaction.atomic():
                obj_map = {"uploaded_files": uploaded_files}  # Pass the list to track files
                _add_inspection_record(obj_map, conn, user, company, file)
                _add_fault_records(obj_map, conn)
                _add_new_firedistinguisher(obj_map, conn, company)
                _add_firedistinguisher_placements(obj_map, conn)
                _add_firedistinguisher_inspections(obj_map, conn)
                
        _update_firedistinguisher_next_inspection(obj_map)

        # If we get here, transaction was successful
        return len(obj_map.get("InspectionRecord", {})), None
        
    except InspectionImportError as e:
        # Clean up uploaded files if transaction fails
        for file_path in uploaded_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError:
                pass  # Ignore cleanup errors
        return 0, str(e)
    except Exception as e:
        # Clean up uploaded files if transaction fails  
        for file_path in uploaded_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError:
                pass  # Ignore cleanup errors
        raise e
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)



