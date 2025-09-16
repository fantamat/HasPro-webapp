import re
import numpy as np
import pandas as pd

from ..models import BuildingManager, Building, Firedistinguisher, FiredistinguisherPlacement

def parse_address(address):
    address, zip_code_city = address.split(',')

    parts = re.split(r'[^\s\d]+', zip_code_city)
    zipcode = parts[0].strip()
    city = zip_code_city.replace(zipcode, '').strip()

    return address.strip(), city, zipcode


def process_building_manager_row(row, owner, company):
    if row is None or "Dům" not in row or pd.isna(row["Dům"]):
        return 0

    building_id = row["Dům"]
    if type(building_id) is float or type(building_id) is np.float64:
        building_id = str(int(building_id))
    else:
        building_id = str(building_id).strip()

    out = 0

    # Process the row and create a BuildingManager instance
    building_manager = BuildingManager.objects.filter(name=row["Funkcionář"]).first()
    if building_manager is None:
        building_manager = BuildingManager(
            name=row["Funkcionář"],
            address=row["Adresa"],
            phone=row["Telefon"],
            email=row["Email"]
        )
        building_manager.save()
        out += 1
    else:
        building_manager.address = row["Adresa"]
        building_manager.phone = row["Telefon"]
        building_manager.email = row["Email"]
        if "Telefon2" in row and not pd.isna(row["Telefon2"]):
            building_manager.phone2 = row["Telefon2"]
        building_manager.save()
    

    address, city, zipcode = parse_address(row["Adresa"])

    # Process the row and create a Building instance

    building = Building.objects.filter(building_id=building_id, company=company).first()
    if building is not None:
        # Update existing building
        building.address = address
        building.city = city
        building.zipcode = zipcode
        building.note = "Imported from file"
        building.company = company
        building.owner = owner
        building.manager = building_manager
        building.save()
    else:
        building = Building(
            building_id=building_id,
            address=address,
            city=city,
            zipcode=zipcode,
            note="Imported from file",
            company=company,
            owner=owner,
            manager=building_manager
        )
        building.save()
        out += 1

    return out


def import_building_manager_data(file, owner, company):
    # Logic to import building manager data from the uploaded file
    # return number of imported records and error message
    if file.name.endswith('.csv'):
        # Process CSV file
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        # Process Excel file
        df = pd.read_excel(file)
    else:
        return 0, "Unsupported file format. Please upload a CSV or Excel file."


    required_columns = {'Dům', 'Adresa', 'Funkcionář', 'Adresa funkcionáře', "Telefon", 'Telefon2', 'Email'}
    if not required_columns.issubset(df.columns):
        return 0, "Invalid file format. Required columns are missing. Required columns: " + ", ".join(required_columns)

    out = 0
    for idx in df.index:
        out += process_building_manager_row(df.loc[idx], owner, company)

    return out, None  # Example return, replace with actual logic




def process_firedistinguisher_row(row, company):
    if row is None or "Výrobní číslo" not in row or pd.isna(row["Výrobní číslo"]):
        return 0

    serial_number = str(row["Výrobní číslo"]).strip()

    if '/' in serial_number and len(serial_number) > 3:
        manufactured_year = int(serial_number[serial_number.find('/')+1:serial_number.find('/')+3])
        if manufactured_year < 50:
            manufactured_year += 2000
        else:
            manufactured_year += 1900
    else:
        manufactured_year = None

    out = 0

    # Process the row and create a Firedistinguisher instance
    firedistinguisher = Firedistinguisher.objects.filter(serial_number=serial_number, managed_by=company).first()
    if firedistinguisher is None:
        firedistinguisher = Firedistinguisher(
            kind=row["Druh"],
            type=row["Typ"],
            manufacturer=row["Výrobce"],
            serial_number=serial_number,
            eliminated=(str(row["Vyyřazen"]) != '') or (str(row["Provozuschopný"]).lower() == 'ne'),
            last_inspection=None,
            manufactured_year=manufactured_year,
            last_fullfilment=None,
            managed_by=company
        )
        firedistinguisher.save()
        out += 1
    else:
        firedistinguisher.kind = row["Druh"]
        firedistinguisher.type = row["Typ"]
        firedistinguisher.manufacturer = row["Výrobce"]
        firedistinguisher.eliminated = (str(row["Vyyřazen"]) != '') or (str(row["Provozuschopný"]).lower() == 'ne')
        firedistinguisher.manufactured_year = manufactured_year
        firedistinguisher.save()    

    building_id = row["Samospráva"]
    if type(building_id) is float or type(building_id) is np.int64:
        building_id = str(int(building_id))
    
    building = Building.objects.filter(building_id=building_id, company=company).first()

    if building is not None:
        placement = FiredistinguisherPlacement(
            description=row["Umístění"],
            firedistinguisher=firedistinguisher,
            building=building
        )
        placement.save()
        out += 1
    
    return out

    
def import_firedistinguisher_data(file, company):
    # Logic to import fire distinguisher data from the uploaded file
    # return number of imported records and error message
    if file.name.endswith('.csv'):
        # Process CSV file
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        # Process Excel file
        df = pd.read_excel(file)
    else:
        return 0, "Unsupported file format. Please upload a CSV or Excel file."

    required_columns = {'Samospráva', 'Umístění', 'Druh', 'Typ', 'Výrobce', 'Výrobní číslo', 'Tlaková zkouška', 'Oprava', 'Vyyřazen', 'Provozuschopný', 'Příští per. zkouška'}

    if not required_columns.issubset(df.columns):
        return 0, "Invalid file format. Required columns are missing. Required columns: " + ", ".join(required_columns)

    out = 0
    for idx in df.index:
        out += process_firedistinguisher_row(df.loc[idx], company)

    return out, None  # Example return, replace with actual logic
