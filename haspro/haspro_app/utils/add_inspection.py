import sqlite3
import tempfile
import os
import io

from django.db import transaction
from django.core.files import File

from ..models import (
    InspectionRecord, 
    FaultInspection, 
    FiredistinguisherInspection, 
    Building, 
    FaultPhoto,
    Firedistinguisher,
    FiredistinguisherPlacement,
    FiredistinguisherServiceAction,
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
        required_tables = {"InspectionRecord", "FaultInspection"} # TODO fill all required tables
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
    cursor.execute("SELECT * FROM InspectionRecord")
    records = cursor.fetchall()

    if len(records) != 1:
        raise InspectionImportError("The database must contain exactly one inspection record.")

    obj_map["InspectionRecord"] = {}

    record = records[0]
    id, inspector_id, date, notes, building_id, created_at, uploaded_file = record

    building = Building.objects.filter(id=building_id, company=company).first()

    if not building:
        raise InspectionImportError(f"Building with ID {building_id} not found in the current company.")

    if inspector_id != user.id:
        raise InspectionImportError("Inspector ID does not match the current user.")

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

    obj_map["InspectionRecord"][id] = inspection
    
    return 1



def _add_fault_records(obj_map, conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM FaultInspection")
        records = cursor.fetchall()
    
    num_updated = 0

    obj_map["FaultInspection"] = {}
    for record in records:
        id, fault_id, inspection_id, notes, responsible_person, fix_due_date, resolved, present = record

        if inspection_id not in obj_map["InspectionRecord"]:
            raise InspectionImportError(f"Referenced InspectionRecord ID {inspection_id} not found in the imported data.")

        # Create new FaultInspection
        fault_inspection = FaultInspection(
            fault_id=fault_id,
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

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM FaultPhoto")
        records = cursor.fetchall()

    obj_map["FaultPhoto"] = {}

    for record in records:
        id, fault_id, photo, uploaded_at = record

        if fault_id not in obj_map["FaultInspection"]:
            raise InspectionImportError(f"Referenced FaultInspection ID {fault_id} not found in the imported data.")

        fault_photo = FaultPhoto(
            fault_inspection=obj_map["FaultInspection"].get(fault_id),
            photo=File(io.BytesIO(photo)),
            uploaded_at=uploaded_at
        )
        fault_photo.save()
        obj_map["FaultPhoto"][id] = fault_photo

    return num_updated

def _add_new_firedistinguisher(obj_map, conn, company):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Firedistinguisher")
        records = cursor.fetchall()
    
    num_updated = 0

    obj_map["Firedistinguisher"] = {}
    for record in records:
        id, kind, type, manufacturer, serial_number, eliminated, last_inspection, manufactured_year, last_fullfilment, managed_by_id = record


        if Firedistinguisher.objects.filter(serial_number=serial_number).exists():
            continue  # Skip existing

        # Create new Firedistinguisher
        fd = Firedistinguisher(
            kind=kind,
            type=type,
            manufacturer=manufacturer,
            serial_number=serial_number,
            eliminated=eliminated,
            last_inspection=last_inspection,
            manufactured_year=manufactured_year,
            last_fullfilment=last_fullfilment,
            managed_by=company
        )
        fd.save()

        obj_map["Firedistinguisher"][id] = fd
        num_updated += 1

    return num_updated

def _add_firedistinguisher_placements(obj_map, conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM FiredistinguisherPlacement")
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
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM FiredistinguisherInspection")
        records = cursor.fetchall()
    
    num_updated = 0

    obj_map["FiredistinguisherInspection"] = {}
    for record in records:
        id, firedistinguisher_id, inspection_id, notes, condition, fullfilment_date = record

        if inspection_id not in obj_map["InspectionRecord"]:
            raise InspectionImportError(f"Referenced InspectionRecord ID {inspection_id} not found in the imported data.")

        if firedistinguisher_id in obj_map["Firedistinguisher"]:
            firedistinguisher_id = obj_map["Firedistinguisher"].get(firedistinguisher_id).pk

        # Create new FiredistinguisherInspection
        fi = FiredistinguisherInspection(
            firedistinguisher_id=firedistinguisher_id,
            inspection=obj_map["InspectionRecord"].get(inspection_id),
            notes=notes,
            condition=condition,
            fullfilment_date=fullfilment_date
        )
        fi.save()

        obj_map["FiredistinguisherInspection"][id] = fi
        num_updated += 1

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM FiredistinguisherServiceAction")
        records = cursor.fetchall()

    obj_map["FiredistinguisherServiceAction"] = {}
    for record in records:
        id, firedistinguisher_id, action_type, description, created_at = record

        if firedistinguisher_id not in obj_map["Firedistinguisher"]:
            raise InspectionImportError(f"Referenced Firedistinguisher ID {firedistinguisher_id} not found in the imported data.")

        service_action = FiredistinguisherServiceAction(
            firedistinguisher=obj_map["Firedistinguisher"].get(firedistinguisher_id),
            action_type=action_type,
            description=description,
            created_at=created_at
        )
        service_action.save()
        obj_map["FiredistinguisherServiceAction"][id] = service_action

    return num_updated


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


    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        temp_file.write(file.read())
        temp_file.flush()
        temp_file.close()
        
        connect_and_verify_db(temp_file.name)
 
        with sqlite3.connect(temp_file.name) as conn:
            with transaction.atomic():
                obj_map = {}
                _add_inspection_record(obj_map, conn, user, company, file)
                _add_fault_records(obj_map, conn)
                _add_new_firedistinguisher(obj_map, conn, company)
                _add_firedistinguisher_placements(obj_map, conn)
                _add_firedistinguisher_inspections(obj_map, conn)

