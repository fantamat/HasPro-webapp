import sqlite3
import io
import tempfile

from haspro_app.models import Company, BuildingOwner, BuildingManager, Building, Fault, Firedistinguisher, FiredistinguisherPlacement

def export_project_to_sqlite(company, file_name):
    # Query all related records
    owners = BuildingOwner.objects.filter(managed_by=company)
    managers = BuildingManager.objects.all()
    buildings = Building.objects.filter(company=company)
    faults = Fault.objects.all()
    firedistinguisher = Firedistinguisher.objects.filter(managed_by=company)
    placements = FiredistinguisherPlacement.objects.filter(firedistinguisher__in=firedistinguisher)

    # Create SQLite DB
    conn = sqlite3.connect(file_name)
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
    c.execute('''CREATE TABLE files (
              id INTEGER PRIMARY KEY,
              name TEXT,
              path TEXT,
              content BLOB,
              created_at TEXT,
              updated_at TEXT
    )''')

    # Insert data
    c.execute('INSERT INTO company VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [company.id, company.name, company.address, company.city, company.zipcode, company.ico, company.dic, str(company.logo)])
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

    # Insert company logo file into files table if logo exists
    if company.logo:
        c.execute(
            'INSERT INTO files (id, name, path, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
            [company.logo.file.id if hasattr(company.logo, 'file') and hasattr(company.logo.file, 'id') else company.id,
             getattr(company.logo, 'name', 'logo'),
             str(company.logo),
             company.logo.read() if hasattr(company.logo, 'read') else None,
             getattr(company.logo, 'created_at', None),
             getattr(company.logo, 'updated_at', None)]
        )

    conn.commit()
    
    c.execute('VACUUM')
    conn.close()


def create_snapshot_file(company):
    buffer = io.BytesIO()

    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        export_project_to_sqlite(company, temp_file.name)

        with open(temp_file.name, 'rb') as f:
            buffer.write(f.read())

    buffer.seek(0)
    return buffer