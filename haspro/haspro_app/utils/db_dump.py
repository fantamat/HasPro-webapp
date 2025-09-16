import sqlite3
from haspro_app.models import Company, BuildingOwner, BuildingManager, Building, Fault, Firedistinguisher, FiredistinguisherPlacement

def export_project_to_sqlite(project_id, buffer):
    # Query all related records
    companies = Company.objects.filter(project_id=project_id)
    owners = BuildingOwner.objects.filter(managed_by__in=companies)
    managers = BuildingManager.objects.all()
    buildings = Building.objects.filter(company__in=companies)
    faults = Fault.objects.all()
    firedistinguisher = Firedistinguisher.objects.filter(managed_by__in=companies)
    placements = FiredistinguisherPlacement.objects.filter(firedistinguisher__in=firedistinguisher)

    # Create SQLite DB
    conn = sqlite3.connect(buffer)
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE company (
        id INTEGER PRIMARY KEY,
        name TEXT,
        address TEXT,
        city TEXT,
        zipcode TEXT,
        ico TEXT,
        dic TEXT,
        logo TEXT
    )''')
    c.execute('''CREATE TABLE buildingowner (
        id INTEGER PRIMARY KEY,
        name TEXT,
        address TEXT,
        city TEXT,
        zipcode TEXT,
        ico TEXT,
        dic TEXT,
        managed_by INTEGER
    )''')
    c.execute('''CREATE TABLE buildingmanager (
        id INTEGER PRIMARY KEY,
        name TEXT,
        address TEXT,
        phone TEXT,
        phone2 TEXT,
        email TEXT
    )''')
    c.execute('''CREATE TABLE building (
        id INTEGER PRIMARY KEY,
        building_id TEXT,
        address TEXT,
        city TEXT,
        zipcode TEXT,
        note TEXT,
        company INTEGER,
        owner INTEGER,
        manager INTEGER
    )''')
    c.execute('''CREATE TABLE fault (
        id INTEGER PRIMARY KEY,
        short_name TEXT,
        description TEXT
    )''')
    c.execute('''CREATE TABLE firedistinguisher (
        id INTEGER PRIMARY KEY,
        kind TEXT,
        type TEXT,
        manufacturer TEXT,
        serial_number TEXT,
        eliminated INTEGER,
        last_inspection TEXT,
        manufactured_year TEXT,
        last_fullfilment TEXT,
        managed_by INTEGER
    )''')
    c.execute('''CREATE TABLE firedistinguisherplacement (
        id INTEGER PRIMARY KEY,
        description TEXT,
        created_at TEXT,
        firedistinguisher INTEGER,
        building INTEGER
    )''')

    # Insert data
    for obj in companies:
        c.execute('INSERT INTO company VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [obj.id, obj.name, obj.address, obj.city, obj.zipcode, obj.ico, obj.dic, str(obj.logo)])
    for obj in owners:
        c.execute('INSERT INTO buildingowner VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [obj.id, obj.name, obj.address, obj.city, obj.zipcode, obj.ico, obj.dic, obj.managed_by_id])
    for obj in managers:
        c.execute('INSERT INTO buildingmanager VALUES (?, ?, ?, ?, ?, ?)', [obj.id, obj.name, obj.address, obj.phone, obj.phone2, obj.email])
    for obj in buildings:
        c.execute('INSERT INTO building VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [obj.id, obj.building_id, obj.address, obj.city, obj.zipcode, obj.note, obj.company_id, obj.owner_id, obj.manager_id])
    for obj in faults:
        c.execute('INSERT INTO fault VALUES (?, ?, ?)', [obj.id, obj.short_name, obj.description])
    for obj in firedistinguisher:
        c.execute('INSERT INTO firedistinguisher VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [obj.id, obj.kind, obj.type, obj.manufacturer, obj.serial_number, int(obj.eliminated), str(obj.last_inspection), str(obj.manufactured_year), str(obj.last_fullfilment), obj.managed_by_id])
    for obj in placements:
        c.execute('INSERT INTO firedistinguisherplacement VALUES (?, ?, ?, ?, ?)', [obj.id, obj.description, str(obj.created_at), obj.firedistinguisher_id, obj.building_id])

    conn.commit()
    conn.close()

# Example usage:
# export_project_to_sqlite(project_id=1, output_path='/tmp/project_dump.sqlite')

import io


def create_snapshot_file_for_user(user):
    buffer = io.BytesIO()
    export_project_to_sqlite(project_id=user.current_project.id, buffer=buffer)
    buffer.seek(0)
    return buffer