# HASPRO - webapp





## PROMPTS

### Models


This application is designed to store records of periodic safety inspections carried out in buildings each year. During these inspections, safety workers check for common issues (such as clear escape routes, correct placement of fire extinguishers, etc.) and also perform routine maintenance and servicing of the extinguishers installed in the building.

The system consists of two parts:
1. A web application that manages and stores all the necessary inspection records and reference data. (this application)
2. A mobile Android application that safety workers use on-site to conduct inspections. After completing a check, the mobile app generates a special file (an SQLite database) containing details of the inspection and any actions taken, which is then sent back to the web application for storage and tracking.



DB:

Company (currently logged in company, contains regular records for the comapny identificaiton)
- name
- adress
- city
- zipcode
- IČO
- DIČ (vat ID)


BuildingOwner
- name
- adress
- city
- zipcode
- IČO
- DIČ (vat ID)


Building
- BuildingID (assigned by the owner)
- Adress
- city
- zipcode
- note
- links: Company, BuildingOwner, BuildingManager


BuildingManager
- name
- Adress (one line)
- phone
- phone2
- email


Faults
- shortName
- description



Firedistinguisher
- kind
- type
- manufacturer
- serialNumber
- eliminated
- lastInspection
- manufacuredAt
- lastFullfilment



FireDistinguisherPlacement
- description
- createdAt
- links: Firedistinguisher, Building


Fill out the models.py for this app



## Debuging


```
sudo ENV=dev sh build.sh
sudo ENV=dev docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up
```