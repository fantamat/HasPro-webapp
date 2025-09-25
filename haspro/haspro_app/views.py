
from django.shortcuts import render, redirect
from urllib3 import request
from .models import Building, BuildingOwner, BuildingManager, Firedistinguisher, FiredistinguisherPlacement, Company, Fault, PossibleFault
from .forms.building_form import BuildingForm
from .forms.owner_form import BuildingOwnerForm
from .forms.buildingmanager_form import BuildingManagerForm
from .forms.fireestinguisher_form import FiredistinguisherForm
from .forms.feplacement_form import FiredistinguisherPlacementForm
from .utils.db_dump import create_snapshot_file
from .utils.imports import import_building_manager_data, import_firedistinguisher_data
from .utils.add_inspection import add_inspection
from django.http import FileResponse
from django.contrib import messages
from django.utils.translation import gettext as _
import logging
import traceback
from django.db.models import Max
from users.utils import project_permission_decorator


logger = logging.getLogger(__name__)

def company_decorator(view_func):
    def _wrapped_view(request, *args, **kwargs):
        company = Company.objects.filter(project=request.project).first()
        if company:
            request.company = company
        return view_func(request, *args, **kwargs)
        
    return _wrapped_view



@project_permission_decorator()
@company_decorator
def home(request):
    if not request.user or not request.user.is_authenticated:
        return redirect('account_login')
    else:
        return render(request, 'home.html', {'user': request.user, 'company': request.company, 'permissions': request.project_permission})


# _______________________________ Building _______________________________

@project_permission_decorator(require_view=True)
@company_decorator
def building_list(request):
    buildings = Building.objects.filter(company=request.company).order_by("building_id").all()

    if request.COOKIES.get('firedist'):
        building_with_firedist_placed = (
            FiredistinguisherPlacement.objects
            .filter(firedistinguisher__managed_by=request.company)
            .values('firedistinguisher')
            .annotate(latest_id=Max('id'))
            .values_list('building', flat=True)
        )
        buildings = buildings.filter(id__in=building_with_firedist_placed)

    faults = Fault.objects.all()

    return render(request, 'building/building_list.html', {'buildings': buildings, 'faults': faults})

@project_permission_decorator(require_admin=True)
def building_create(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:building-list')
    else:
        form = BuildingForm()
    return render(request, 'building/building_form.html', {'form': form, 'create': True})


@project_permission_decorator(require_edit=True)
def building_edit(request, pk):
    building = Building.objects.get(pk=pk)
    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:building-list')
    else:
        form = BuildingForm(instance=building)

    # Get the latest placement for each firedistinguisher in the building
    latest_placements = (
        FiredistinguisherPlacement.objects
        .filter(building=building)
        .values('firedistinguisher')
        .annotate(latest_id=Max('id'))
    )

    # Get the actual placement objects
    latest_placement_objects = FiredistinguisherPlacement.objects.filter(
        id__in=[placement['latest_id'] for placement in latest_placements]
    )

    # Get the fire extinguishers from these placements
    firedistinguishers = Firedistinguisher.objects.filter(
        id__in=latest_placement_objects.values_list('firedistinguisher', flat=True)
    )

    faults = Fault.objects.all()
    possible_faults = list(map(lambda x: x.fault, PossibleFault.objects.filter(building=building).all()))
    additional_faults = list(filter(lambda x: x not in possible_faults, faults))

    return render(request, 'building/building_form.html', {'form': form, 'create': False, 'firedistinguishers': firedistinguishers, 'possible_faults': possible_faults, 'additional_faults': additional_faults})


@project_permission_decorator(require_edit=True)
def add_possible_fault(request, pk):
    building = Building.objects.get(pk=pk)
    if request.method == 'POST':
        fault_ids = request.POST.getlist('fault')
        if fault_ids:
            added_count = 0
            for fault_id in fault_ids:
                try:
                    fault = Fault.objects.get(pk=fault_id)
                    possible_fault, created = PossibleFault.objects.get_or_create(
                        building=building,
                        fault=fault
                    )
                    if created:
                        added_count += 1
                except Fault.DoesNotExist:
                    messages.error(request, _("Fault with ID %(fault_id)s does not exist.") % {'fault_id': fault_id})
            
            if added_count > 0:
                messages.success(request, _("Added %(count)d fault(s) to building.") % {'count': added_count})
            else:
                messages.info(request, _("No new faults were added (they may already exist for this building)."))
        else:
            messages.warning(request, _("No faults selected."))
    return redirect('haspro_app:building-edit', pk=pk)


@project_permission_decorator(require_admin=True)
def building_delete(request, pk):
    building = Building.objects.get(pk=pk)
    if request.method == 'POST':
        building.delete()
        messages.success(request, _("Building %(building_id)s deleted.") % {'building_id': building.id})
    return redirect('haspro_app:building-list')


# _______________________________ Building Owner _______________________________

@project_permission_decorator(require_view=True)
def buildingowner_list(request):
    owners = BuildingOwner.objects.all()
    return render(request, 'buildingowner/buildingowner_list.html', {'owners': owners})

@project_permission_decorator(require_admin=True)
def buildingowner_create(request):
    if request.method == 'POST':
        form = BuildingOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:buildingowner-list')
    else:
        form = BuildingOwnerForm()
    return render(request, 'buildingowner/buildingowner_form.html', {'form': form, 'create': True})


@project_permission_decorator(require_view=True)
def buildingowner_edit(request, pk):
    owner = BuildingOwner.objects.get(pk=pk)
    if request.method == 'POST':
        buildingowner_edit_post(request, owner)
    else:
        form = BuildingOwnerForm(instance=owner)

    managed_buildings = Building.objects.filter(owner=owner).all()
    return render(request, 'buildingowner/buildingowner_form.html', {'form': form, 'create': False, 'buildings': managed_buildings})

@project_permission_decorator(require_admin=True)
def buildingowner_edit_post(request, owner):
    form = BuildingOwnerForm(request.POST, instance=owner)
    if form.is_valid():
        form.save()
        return redirect('haspro_app:buildingowner-list')
    
    managed_buildings = Building.objects.filter(owner=owner).all()
    return render(request, 'buildingowner/buildingowner_form.html', {'form': form, 'create': False, 'buildings': managed_buildings})


@project_permission_decorator(require_admin=True)
def buildingowner_delete(request, pk):
    owner = BuildingOwner.objects.get(pk=pk)
    if request.method == 'POST':
        owner.delete()
        messages.success(request, _("Building owner %(name)s deleted.") % {'name': owner.name})
    return redirect('haspro_app:buildingowner-list')


# _______________________________ Building Manager _______________________________

@project_permission_decorator(require_view=True)
def buildingmanager_list(request):
    managers = BuildingManager.objects.all()
    return render(request, 'buildingmanager/buildingmanager_list.html', {'managers': managers})

@project_permission_decorator(require_admin=True)
def buildingmanager_create(request):
    if request.method == 'POST':
        form = BuildingManagerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:buildingmanager-list')
    else:
        form = BuildingManagerForm()
    return render(request, 'buildingmanager/buildingmanager_form.html', {'form': form, 'create': True})

@project_permission_decorator(require_admin=True)
def buildingmanager_edit(request, pk):
    manager = BuildingManager.objects.get(pk=pk)
    if request.method == 'POST':
        form = BuildingManagerForm(request.POST, instance=manager)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:buildingmanager-list')
    else:
        form = BuildingManagerForm(instance=manager)

    managed_buildings = Building.objects.filter(manager=manager).all()
    return render(request, 'buildingmanager/buildingmanager_form.html', {'form': form, 'create': False, 'buildings': managed_buildings})

@project_permission_decorator(require_admin=True)
def buildingmanager_delete(request, pk):
    manager = BuildingManager.objects.get(pk=pk)
    if request.method == 'POST':
        manager.delete()
        messages.success(request, _("Building manager %(name)s deleted.") % {'name': manager.name})
    return redirect('haspro_app:buildingmanager-list')


# _______________________________ Fire Distinguisher _______________________________

@project_permission_decorator(require_view=True)
def firedistinguisher_list(request):
    firedistinguisher_list = Firedistinguisher.objects.all()
    return render(request, 'firedistinguisher/firedistinguisher_list.html', {'firedistinguisher_list': firedistinguisher_list})

@project_permission_decorator(require_edit=True)
def firedistinguisher_create(request):
    if request.method == 'POST':
        form = FiredistinguisherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:firedistinguisher-list')
    else:
        form = FiredistinguisherForm()
    return render(request, 'firedistinguisher/firedistinguisher_form.html', {'form': form, 'create': True})

@project_permission_decorator(require_edit=True)
def firedistinguisher_edit(request, pk):
    firedistinguisher = Firedistinguisher.objects.get(pk=pk)
    if request.method == 'POST':
        form = FiredistinguisherForm(request.POST, instance=firedistinguisher)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:firedistinguisher-list')
    else:
        form = FiredistinguisherForm(instance=firedistinguisher)
    
    placements = FiredistinguisherPlacement.objects.filter(firedistinguisher=firedistinguisher).order_by('-created_at')

    actions = firedistinguisher.firedistinguisherserviceaction_set.all().order_by('-created_at')

    return render(request, 'firedistinguisher/firedistinguisher_form.html', {'form': form, 'create': False, 'placements': placements, 'actions': actions})


@project_permission_decorator(require_admin=True)
def firedistinguisher_delete(request, pk):
    firedistinguisher = Firedistinguisher.objects.get(pk=pk)
    if request.method == 'POST':
        firedistinguisher.delete()
        messages.success(request, _("Fire extinguisher %(serial_number)s deleted.") % {'serial_number': firedistinguisher.serial_number})
    return redirect('haspro_app:firedistinguisher-list')

# _______________________________ Data Imports _______________________________

@project_permission_decorator(require_admin=True)
@company_decorator
def tools_view(request):
    return render(request, 'tools/tools.html', {'owners': BuildingOwner.objects.filter(managed_by=request.company).all()})


@project_permission_decorator(require_admin=True)
@company_decorator
def import_building_manager_list(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            if 'owner' in request.POST:
                try:
                    owner = BuildingOwner.objects.get(id=int(request.POST['owner']), managed_by=request.company)
                except BuildingOwner.DoesNotExist:
                    messages.error(request, _("Error importing building manager data: Selected owner does not exist."))
                    return redirect('haspro_app:tools-view')
            else:
                messages.error(request, _("Error importing building manager data: No owner selected."))
                return redirect('haspro_app:tools-view')

            num_imported, error_message = import_building_manager_data(file, owner, request.company)
            if error_message:
                messages.error(request, _("Error importing building manager data: %(error)s") % {'error': error_message})
            else:
                messages.success(request, _("Successfully imported %(count)d buildings and their managers.") % {'count': num_imported})

        else:
            messages.error(request, _("Error importing building manager data: No file provided."))

    return redirect('haspro_app:tools-view')

@project_permission_decorator(require_admin=True)        
@company_decorator
def import_firedistinguisher_list(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            if 'owner' in request.POST:
                try:
                    owner = BuildingOwner.objects.get(id=int(request.POST['owner']), managed_by=request.company)
                except BuildingOwner.DoesNotExist:
                    messages.error(request, _("Error importing fire extinguisher data: Selected owner does not exist."))
                    return redirect('haspro_app:tools-view')
            else:
                messages.error(request, _("Error importing fire extinguisher data: No owner selected."))
                return redirect('haspro_app:tools-view')

            num_imported, error_message = import_firedistinguisher_data(file, owner, request.company)
            if error_message:
                messages.error(request, _("Error importing fire extinguisher data: %(error)s") % {'error': error_message})
            else:
                messages.success(request, _("Successfully imported %(count)d fire extinguisher records.") % {'count': num_imported})

        else:
            messages.error(request, _("Error importing fire extinguisher data: No file provided."))
    return redirect('haspro_app:tools-view')



# _______________________________ Data Exports _______________________________

@project_permission_decorator(require_admin=True)
@company_decorator
def set_export_template(request):
    # Placeholder for setting export template logic
    pass

@project_permission_decorator(require_admin=True)
@company_decorator
def export_reports_for_owner(request, owner_id):
    # Placeholder for exporting data by owner logic
    pass



# _______________________________ Mobile app interface _______________________________

@project_permission_decorator(require_view=True)
@company_decorator
def get_db_snapshot(request):    

    # Logic to create a snapshot
    try:
        if not request.company:
            return render(request, '404.html', {
                'error_message': _("No company found for the current project.")
            }, status=404)
        buffer = create_snapshot_file(request.company)
    except Exception as e:
        logger.error(f"Error creating snapshot for user {request.user.id}: {e} Traceback: {traceback.format_exc()}", exc_info=True)
        return render(request, '500.html', {
            'error_message': _("Error creating database snapshot.")
        }, status=500)

    return FileResponse(buffer, as_attachment=True, filename='db_snapshot.bin')


@project_permission_decorator(require_edit=True)
@company_decorator
def upload_inspection_records(request):
    # Handle uploaded inspection data from mobile app
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            if not request.company:
                messages.error(request, _("Error updating inspection records: No company found."))
                return redirect('haspro_app:tools-view')

            num_updated, error_message = add_inspection(request.user, request.company, file)
            if error_message:
                messages.error(request, _("Error updating inspection records: %(error)s") % {'error': error_message})
            else:
                messages.success(request, _("Successfully updated %(count)d inspection records.") % {'count': num_updated})

        else:
            messages.error(request, _("Error updating inspection records: No file provided."))

    return redirect('haspro_app:tools-view')

