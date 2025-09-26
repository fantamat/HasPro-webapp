import datetime
import re
import numpy as np
import pandas as pd
import logging

from ..models import BuildingManager, Building, Firedistinguisher, FiredistinguisherPlacement, FiredistinguisherKind

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_address(address):
    adress_split = address.split(',')
    if len(adress_split) < 2:
        return address.strip(), '', ''
    else:
        address = ','.join(adress_split[:-1])
        zip_code_city = adress_split[-1]

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
    person_name = str(row["Funkcionář"])\
        .replace("Správce-náhr.orgán", "")\
        .replace("Předseda samosprávy", "")\
        .replace("Předseda SVJ", "")\
        .strip()

    building_manager = BuildingManager.objects.filter(name=person_name).first()
    if building_manager is None:
        building_manager = BuildingManager(
            name=person_name,
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



def _eliminated(row):
    if "Vyřazen" in row and row["Vyřazen"] is not np.nan and str(row["Vyřazen"]) != '':
        return True
    if "Provozuschopný" in row and row["Provozuschopný"] is not np.nan and str(row["Provozuschopný"]).lower() == 'ne':
        return True
    return False


def _next_inspection(row):
    if "Příští per. zkouška" in row and row["Příští per. zkouška"] is not np.nan and str(row["Příští per. zkouška"]) != '':
        if type(row["Příští per. zkouška"]) is datetime.datetime:
            return row["Příští per. zkouška"].date()
        else:
            try:
                return pd.to_datetime(str(row["Příští per. zkouška"]), format='%Y/%m').date()
            except Exception as e:
                logger.error(f"Error parsing next inspection date: {e}")
                return None
    return None



def _get_kind_and_size(text: str):
    text = text.strip().lower()
    kind = FiredistinguisherKind.OTHER
    size = None

    kind_char = text[0]
    if kind_char == 's':
        kind = FiredistinguisherKind.SNOW
    elif kind_char == 'p':
        kind = FiredistinguisherKind.POWDER
    elif kind_char == 'v' or kind_char == 'w':
        kind = FiredistinguisherKind.WATER
    elif kind_char == 'f' or kind_char == 'p':
        kind = FiredistinguisherKind.FOAM
    else:
        kind = FiredistinguisherKind.OTHER
        
    if len(text) > 1:
        size_text = text[1:].strip()
        try:
            size = float(size_text.replace(',', '.'))
        except ValueError:
            size = None

    return kind, size



def process_firedistinguisher_row(row, owner, company):
    if row is None or "Výrobní číslo" not in row or pd.isna(row["Výrobní číslo"]):
        return 0

    serial_number = str(row["Výrobní číslo"]).strip()

    if '/' in serial_number and len(serial_number) > 3:

        manufactured_year = serial_number[serial_number.find('/')+1:serial_number.find('/')+3]
        try:
            manufactured_year = int(manufactured_year)
            if manufactured_year < 50:
                manufactured_year += 2000
            else:
                manufactured_year += 1900
        except ValueError:
            manufactured_year = None
    else:
        manufactured_year = None

    out = 0

    # Process the row and create a Firedistinguisher instance
    firedistinguisher = Firedistinguisher.objects.filter(serial_number=serial_number, managed_by=company).first()
    kind, size = _get_kind_and_size(str(row["Druh"]))



    if firedistinguisher is None:
        firedistinguisher = Firedistinguisher(
            kind=kind,
            size=size,
            power=row["Typ"],
            manufacturer=row["Výrobce"],
            serial_number=serial_number,
            eliminated=_eliminated(row),
            manufactured_year=manufactured_year,
            managed_by=company,
            next_inspection=_next_inspection(row)
        )
        firedistinguisher.save()
        out += 1
    else:
        firedistinguisher.kind = kind
        firedistinguisher.size = size
        firedistinguisher.power = row["Typ"]
        firedistinguisher.manufacturer = row["Výrobce"]
        firedistinguisher.eliminated = _eliminated(row)
        firedistinguisher.manufactured_year = manufactured_year
        firedistinguisher.next_inspection = _next_inspection(row)
        firedistinguisher.save()

    building_id = row["Samospráva"]
    if type(building_id) in [float, np.float64, np.int64, int]:
        try:
            building_id = str(int(building_id))
        except ValueError:
            logger.error(f"Invalid building ID: {building_id}")
            building_id = None

    building = Building.objects.filter(building_id=building_id, company=company, owner=owner).first()

    if building is not None:
        if firedistinguisher.get_current_placement() is not None and firedistinguisher.get_current_placement().building == building:
            return out  # No change in placement
        
        # Create new placement
        placement = FiredistinguisherPlacement(
            description=row["Umístění"],
            firedistinguisher=firedistinguisher,
            building=building
        )
        placement.save()
        out += 1
    
    return out

    
def import_firedistinguisher_data(file, owner, company):
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

    required_columns = {'Samospráva', 'Umístění', 'Druh', 'Typ', 'Výrobce', 'Výrobní číslo', 'Tlaková zkouška', 'Oprava', 'Vyřazen', 'Provozuschopný', 'Příští per. zkouška'}

    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        logger.error(f"Missing required columns: {missing}")
        return 0, "Invalid file format. Required columns are missing. Missing columns: " + ", ".join(missing)

    out = 0
    for idx in df.index:
        out += process_firedistinguisher_row(df.loc[idx], owner, company)

    return out, None  # Example return, replace with actual logic
