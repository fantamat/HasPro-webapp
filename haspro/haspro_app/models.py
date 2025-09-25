from django.db import models

from users.models import Project, User


class Company(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="companies")
	name = models.CharField(max_length=255)
	address = models.CharField(max_length=255)
	city = models.CharField(max_length=100)
	zipcode = models.CharField(max_length=20)
	ico = models.CharField("IČO", max_length=20)
	dic = models.CharField("DIČ", max_length=20)
	logo = models.FileField(upload_to='company_logos/', blank=True, null=True)

	def __str__(self):
		return self.name

class BuildingOwner(models.Model):
	name = models.CharField(max_length=255)
	address = models.CharField(max_length=255)
	city = models.CharField(max_length=100)
	zipcode = models.CharField(max_length=20)
	ico = models.CharField("IČO", max_length=20)
	dic = models.CharField("DIČ", max_length=20)
	managed_by = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.name

class BuildingManager(models.Model):
	name = models.CharField(max_length=255)
	address = models.CharField(max_length=255)
	phone = models.CharField(max_length=30)
	phone2 = models.CharField(max_length=30, blank=True, null=True)
	email = models.EmailField()

	def __str__(self):
		return self.name

class Building(models.Model):
	building_id = models.CharField(max_length=100)
	address = models.CharField(max_length=255)
	city = models.CharField(max_length=100)
	zipcode = models.CharField(max_length=20)
	note = models.TextField(blank=True, null=True)
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	owner = models.ForeignKey(BuildingOwner, on_delete=models.CASCADE)
	manager = models.ForeignKey(BuildingManager, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return f"{self.building_id} - {self.address}"

	def get_full_address(self):
		return f"{self.address}, {self.city}, {self.zipcode}"

class Fault(models.Model):
	short_name = models.CharField(max_length=100)
	description = models.TextField()
	default_fix_time_days = models.IntegerField()

	def __str__(self):
		return self.short_name
	
class PossibleFault(models.Model):
	fault = models.ForeignKey(Fault, on_delete=models.CASCADE)
	building = models.ForeignKey(Building, on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.fault.short_name} in {self.building.building_id}"

class Firedistinguisher(models.Model):
	kind = models.CharField(max_length=100)
	type = models.CharField(max_length=100)
	manufacturer = models.CharField(max_length=100)
	serial_number = models.CharField(max_length=100)
	eliminated = models.BooleanField(default=False)
	manufactured_year = models.IntegerField(null=True, blank=True)
	managed_by = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
	next_inspection = models.DateField(null=True, blank=True)

	def __str__(self):
		return f"{self.kind} {self.serial_number}"

	def get_current_placement(self):
		placement = FiredistinguisherPlacement.objects.filter(firedistinguisher=self).order_by('-created_at').first()
		return placement

class FiredistinguisherPlacement(models.Model):
	description = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	firedistinguisher = models.ForeignKey(Firedistinguisher, on_delete=models.CASCADE)
	building = models.ForeignKey(Building, on_delete=models.CASCADE)

	def __str__(self):
		return self.description
	

class FiredistinguisherServiceActionType(models.TextChoices):
	INSPECTION = 'Inspection', 'Inspekce'
	FULLFILMENT = 'Fullfilment', 'Náplň'
	PRESURE_TEST = 'Presure Test', 'Tlaková zkouška'
	MAINTENANCE = 'Maintenance', 'Údržba'
	HOSE_REPLACEMENT = 'Hose Replacement', 'Výměna hadice'
	VALVE_REPLACEMENT = 'Valve Replacement', 'Výměna ventilu'
	REFILL_AND_PRESSURIZE = 'Refill and Pressurize', 'Náplň a natlakování'
	SAFETY_PIN = 'Safety Pin', 'Pojistka'
	OTHER = 'Other', 'Jiné'

class FiredistinguisherServiceAction(models.Model):
	action_type = models.CharField(max_length=100, db_index=True)
	description = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	firedistinguisher = models.ForeignKey(Firedistinguisher, on_delete=models.CASCADE)

	def __str__(self):
		return self.description
	


class InspectionRecord(models.Model):
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_file = models.FileField(upload_to='inspection_uploads/', blank=True, null=True)

    def __str__(self):
        return f"Inspection on {self.date} by {self.inspector}"
	

class FaultInspection(models.Model):
    fault = models.ForeignKey(Fault, on_delete=models.CASCADE, null=True, blank=True)
    short_name = models.CharField(max_length=100)
    description = models.TextField()
    inspection = models.ForeignKey(InspectionRecord, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    responsible_person = models.CharField(max_length=255, blank=True, null=True)
    fix_due_date = models.DateField(blank=True, null=True)
    resolved = models.BooleanField(default=False)
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"Fault {self.fault.short_name} in inspection {self.inspection.id}"

class FaultPhoto(models.Model):
    fault_inspection = models.ForeignKey(FaultInspection, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='fault_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id} uploaded at {self.uploaded_at}"

