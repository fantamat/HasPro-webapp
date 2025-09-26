from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import Project, User

import math


class Company(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="companies", verbose_name=_("Project"))
	name = models.CharField(_("Name"), max_length=255)
	address = models.CharField(_("Address"), max_length=255)
	city = models.CharField(_("City"), max_length=100)
	zipcode = models.CharField(_("ZIP Code"), max_length=20)
	ico = models.CharField(_("IČO"), max_length=20)
	dic = models.CharField(_("DIČ"), max_length=20)
	logo = models.FileField(_("Logo"), upload_to='company_logos/', blank=True, null=True)

	class Meta:
		verbose_name = _("Company")
		verbose_name_plural = _("Companies")

	def __str__(self):
		return self.name

class BuildingOwner(models.Model):
	name = models.CharField(_("Name"), max_length=255)
	address = models.CharField(_("Address"), max_length=255)
	city = models.CharField(_("City"), max_length=100)
	zipcode = models.CharField(_("ZIP Code"), max_length=20)
	ico = models.CharField(_("IČO"), max_length=20)
	dic = models.CharField(_("DIČ"), max_length=20)
	managed_by = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Managed by"))

	class Meta:
		verbose_name = _("Building Owner")
		verbose_name_plural = _("Building Owners")

	def __str__(self):
		return self.name

class BuildingManager(models.Model):
	name = models.CharField(_("Name"), max_length=255)
	address = models.CharField(_("Address"), max_length=255)
	phone = models.CharField(_("Phone"), max_length=30)
	phone2 = models.CharField(_("Phone 2"), max_length=30, blank=True, null=True)
	email = models.EmailField(_("Email"))

	class Meta:
		verbose_name = _("Building Manager")
		verbose_name_plural = _("Building Managers")

	def __str__(self):
		return self.name

class Building(models.Model):
	building_id = models.CharField(_("Building ID"), max_length=100)
	address = models.CharField(_("Address"), max_length=255)
	city = models.CharField(_("City"), max_length=100)
	zipcode = models.CharField(_("ZIP Code"), max_length=20)
	note = models.TextField(_("Note"), blank=True, null=True)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_("Company"))
	owner = models.ForeignKey(BuildingOwner, on_delete=models.CASCADE, verbose_name=_("Owner"))
	manager = models.ForeignKey(BuildingManager, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Manager"))
	last_inspection_date = models.DateField(_("Last Inspection Date"), null=True, blank=True)
	inspection_interval_days = models.IntegerField(_("Inspection Interval (Days)"), default=180)

	class Meta:
		verbose_name = _("Building")
		verbose_name_plural = _("Buildings")

	def __str__(self):
		return f"{self.building_id} - {self.address}"

	def get_full_address(self):
		return f"{self.address}, {self.city}, {self.zipcode}"

class Fault(models.Model):
	short_name = models.CharField(_("Short Name"), max_length=100)
	description = models.TextField(_("Description"))
	default_fix_time_days = models.IntegerField(_("Default Fix Time (Days)"))

	class Meta:
		verbose_name = _("Fault")
		verbose_name_plural = _("Faults")

	def __str__(self):
		return self.short_name
	
class PossibleFault(models.Model):
	fault = models.ForeignKey(Fault, on_delete=models.CASCADE, verbose_name=_("Fault"))
	building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name=_("Building"))

	class Meta:
		verbose_name = _("Possible Fault")
		verbose_name_plural = _("Possible Faults")

	def __str__(self):
		return f"{self.fault.short_name} in {self.building.building_id}"


class FiredistinguisherKind(models.TextChoices):
	SNOW = 'Snow', _('Snow')
	POWDER = 'Powder', _('Powder')
	WATER = 'Water', _('Water')
	FOAM = 'Foam', _('Foam')
	OTHER = 'Other', _('Other')


class Firedistinguisher(models.Model):
	kind = models.CharField(_("Kind"), max_length=100, choices=FiredistinguisherKind.choices)
	size = models.FloatField(_("Size"), null=True, blank=True)
	power = models.CharField(_("Power"), max_length=100)
	manufacturer = models.CharField(_("Manufacturer"), max_length=100)
	serial_number = models.CharField(_("Serial Number"), max_length=100)
	eliminated = models.BooleanField(_("Eliminated"), default=False)
	manufactured_year = models.IntegerField(_("Manufactured Year"), null=True, blank=True)
	managed_by = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Managed by"))
	next_inspection = models.DateField(_("Next Inspection"), null=True, blank=True)
	next_periodic_test = models.DateField(_("Next Periodic Test"), null=True, blank=True)

	class Meta:
		verbose_name = _("Fire Extinguisher")
		verbose_name_plural = _("Fire Extinguishers")

	def __str__(self):
		return f"{self.kind} {self.serial_number}"

	def get_current_placement(self):
		placement = FiredistinguisherPlacement.objects.filter(firedistinguisher=self).order_by('-created_at').first()
		return placement
	
	def size_short(self):
		if math.floor(self.size*10) % 10 == 0:
			return str(int(self.size))
		else:
			return str(round(self.size, 1))

class FiredistinguisherPlacement(models.Model):
	description = models.CharField(_("Description"), max_length=255)
	created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
	firedistinguisher = models.ForeignKey(Firedistinguisher, on_delete=models.CASCADE, verbose_name=_("Fire Extinguisher"))
	building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name=_("Building"))

	class Meta:
		verbose_name = _("Fire Extinguisher Placement")
		verbose_name_plural = _("Fire Extinguisher Placements")

	def __str__(self):
		return self.description
	

class FiredistinguisherServiceActionType(models.TextChoices):
	INSPECTION = 'inspection', _('Inspection')
	ELIMINATION = 'elimination', _('Elimination')
	REFILL = 'refill', _('Refill')
	PERIODIC_TEST = 'periodic_test', _('Periodic Test')
	MAINTENANCE = 'maintenance', _('Maintenance')
	HOSE_REPLACEMENT = 'hose_replacement', _('Hose Replacement')
	VALVE_REPLACEMENT = 'valve_replacement', _('Valve Replacement')
	REFILL_AND_PRESSURIZE = 'refill_and_pressurize', _('Refill and Pressurize')
	SAFETY_PIN = 'safety_pin', _('Safety Pin')
	OTHER = 'other', _('Other')


class FiredistinguisherServiceAction(models.Model):
	firedistinguisher = models.ForeignKey(Firedistinguisher, on_delete=models.CASCADE, verbose_name=_("Fire Extinguisher"))
	action_type = models.CharField(_("Action Type"), max_length=100, db_index=True)
	description = models.CharField(_("Description"), max_length=255)
	created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
	inspection = models.ForeignKey('InspectionRecord', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Inspection"), related_name='firedistinguisher_actions')
	
	class Meta:
		verbose_name = _("Fire Extinguisher Service Action")
		verbose_name_plural = _("Fire Extinguisher Service Actions")

	def __str__(self):
		return self.description
	


class InspectionRecord(models.Model):
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Inspector"))
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    notes = models.TextField(_("Notes"), blank=True, null=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name=_("Building"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    uploaded_file = models.FileField(_("Uploaded File"), upload_to='inspection_uploads/', blank=True, null=True)

    class Meta:
        verbose_name = _("Inspection Record")
        verbose_name_plural = _("Inspection Records")

    def __str__(self):
        return f"Inspection on {self.date} by {self.inspector}"
	

class FaultInspection(models.Model):
    fault = models.ForeignKey(Fault, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Fault"))
    short_name = models.CharField(_("Short Name"), max_length=100)
    description = models.TextField(_("Description"))
    inspection = models.ForeignKey(InspectionRecord, on_delete=models.CASCADE, verbose_name=_("Inspection"))
    notes = models.TextField(_("Notes"), blank=True, null=True)
    responsible_person = models.CharField(_("Responsible Person"), max_length=255, blank=True, null=True)
    fix_due_date = models.DateField(_("Fix Due Date"), blank=True, null=True)
    resolved = models.BooleanField(_("Resolved"), default=False)
    present = models.BooleanField(_("Present"), default=False)

    class Meta:
        verbose_name = _("Fault Inspection")
        verbose_name_plural = _("Fault Inspections")

    def __str__(self):
        return f"Fault {self.fault.short_name} in inspection {self.inspection.id}"

class FaultPhoto(models.Model):
    fault_inspection = models.ForeignKey(FaultInspection, on_delete=models.CASCADE, verbose_name=_("Fault Inspection"))
    photo = models.ImageField(_("Photo"), upload_to='fault_photos/')
    uploaded_at = models.DateTimeField(_("Uploaded at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Fault Photo")
        verbose_name_plural = _("Fault Photos")

    def __str__(self):
        return f"Photo {self.id} uploaded at {self.uploaded_at}"

