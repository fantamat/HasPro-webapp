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

	def __str__(self):
		return self.short_name

class Firedistinguisher(models.Model):
	kind = models.CharField(max_length=100)
	type = models.CharField(max_length=100)
	manufacturer = models.CharField(max_length=100)
	serial_number = models.CharField(max_length=100)
	eliminated = models.BooleanField(default=False)
	last_inspection = models.DateField(null=True, blank=True)
	manufactured_year = models.IntegerField(null=True, blank=True)
	last_fullfilment = models.DateField(null=True, blank=True)
	managed_by = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

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
	

class FiredistinguisherAction(models.Model):
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

    record = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return f"Inspection on {self.date} by {self.inspector}"
	

class InspectionRecordActions(models.Model):
    inspection_record = models.ForeignKey(InspectionRecord, on_delete=models.CASCADE, related_name="actions")
    action_description = models.TextField()
    performed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Action for {self.inspection_record} at {self.performed_at}"
	
