
from django.shortcuts import render, redirect
from .models import Building, BuildingOwner, Firedistinguisher, FiredistinguisherPlacement, Company
from .forms.building_form import BuildingForm
from .forms.owner_form import BuildingOwnerForm
from .forms.fireestinguisher_form import FiredistinguisherForm
from .forms.feplacement_form import FiredistinguisherPlacementForm
from .utils.db_dump import create_snapshot_file
from .utils.imports import import_building_manager_data, import_firedistinguisher_data
from .utils.add_inspection import add_inspection
from django.http import FileResponse
from django.contrib import messages
import logging
import traceback

logger = logging.getLogger(__name__)

# _______________________________ Building _______________________________


def building_list(request):
    buildings = Building.objects.all()
    return render(request, 'building/building_list.html', {'buildings': buildings})


def building_create(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:building-list')
    else:
        form = BuildingForm()
    return render(request, 'building/building_form.html', {'form': form, 'create': True})


def building_edit(request, pk):
    building = Building.objects.get(pk=pk)
    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:building-list')
    else:
        form = BuildingForm(instance=building)
    return render(request, 'building/building_form.html', {'form': form, 'create': False})

def building_delete(request, pk):
    building = Building.objects.get(pk=pk)
    if request.method == 'POST':
        building.delete()
        messages.success(request, f"Building deleted {building.id}.")
    return redirect('haspro_app:building-list')


# _______________________________ Building Owner _______________________________

def buildingowner_list(request):
    owners = BuildingOwner.objects.all()
    return render(request, 'buildingowner/buildingowner_list.html', {'owners': owners})

def buildingowner_create(request):
    if request.method == 'POST':
        form = BuildingOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:buildingowner-list')
    else:
        form = BuildingOwnerForm()
    return render(request, 'buildingowner/buildingowner_form.html', {'form': form, 'create': True})

def buildingowner_edit(request, pk):
    owner = BuildingOwner.objects.get(pk=pk)
    if request.method == 'POST':
        form = BuildingOwnerForm(request.POST, instance=owner)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:buildingowner-list')
    else:
        form = BuildingOwnerForm(instance=owner)
    return render(request, 'buildingowner/buildingowner_form.html', {'form': form, 'create': False})

def buildingowner_delete(request, pk):
    owner = BuildingOwner.objects.get(pk=pk)
    if request.method == 'POST':
        owner.delete()
        messages.success(request, f"Building owner deleted {owner.name}.")
    return redirect('haspro_app:buildingowner-list')


# _______________________________ Fire Distinguisher _______________________________

def firedistinguisher_list(request):
    firedistinguisher_list = Firedistinguisher.objects.all()
    return render(request, 'firedistinguisher/firedistinguisher_list.html', {'firedistinguisher_list': firedistinguisher_list})


def firedistinguisher_create(request):
    if request.method == 'POST':
        form = FiredistinguisherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('haspro_app:firedistinguisher-list')
    else:
        form = FiredistinguisherForm()
    return render(request, 'firedistinguisher/firedistinguisher_form.html', {'form': form, 'create': True})


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

    return render(request, 'firedistinguisher/firedistinguisher_form.html', {'form': form, 'create': False, 'placements': placements})


def firedistinguisher_delete(request, pk):
    firedistinguisher = Firedistinguisher.objects.get(pk=pk)
    if request.method == 'POST':
        firedistinguisher.delete()
        messages.success(request, f"Fire extinguisher deleted {firedistinguisher.serial_number}.")
    return redirect('haspro_app:firedistinguisher-list')

# _______________________________ Data Imports _______________________________

def tools_view(request):
    company = Company.objects.filter(project=request.user.current_project).first()
    return render(request, 'tools/tools.html', {'owners': BuildingOwner.objects.filter(managed_by=company).all()})



def import_building_manager_list(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            company = Company.objects.filter(project=request.user.current_project).first()
            if 'owner' in request.POST:
                try:
                    owner = BuildingOwner.objects.get(id=int(request.POST['owner']), managed_by=company)
                except BuildingOwner.DoesNotExist:
                    messages.error(request, f"Error importing building manager data: Selected owner does not exist.")
                    return redirect('haspro_app:tools-view')
            else:
                messages.error(request, f"Error importing building manager data: No owner selected.")
                return redirect('haspro_app:tools-view')
                
            num_imported, error_message = import_building_manager_data(file, owner, company)
            if error_message:
                messages.error(request, f"Error importing building manager data: {error_message}")
            else:
                messages.success(request, f"Successfully imported {num_imported} buildings and their managers.")

        else:
            messages.error(request, f"Error importing building manager data no file provided")

    return redirect('haspro_app:tools-view')


def import_firedistinguisher_list(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            company = Company.objects.filter(project=request.user.current_project).first()
            if 'owner' in request.POST:
                try:
                    owner = BuildingOwner.objects.get(id=int(request.POST['owner']), managed_by=company)
                except BuildingOwner.DoesNotExist:
                    messages.error(request, f"Error importing fire distinguisher data: Selected owner does not exist.")
                    return redirect('haspro_app:tools-view')
            else:
                messages.error(request, f"Error importing fire distinguisher data: No owner selected.")
                return redirect('haspro_app:tools-view')

            num_imported, error_message = import_firedistinguisher_data(file, company)
            if error_message:
                messages.error(request, f"Error importing fire distinguisher data: {error_message}")
            else:
                messages.success(request, f"Successfully imported {num_imported} fire distinguisher records.")

        else:
            messages.error(request, f"Error importing fire distinguisher data no file provided")
    return redirect('haspro_app:tools-view')



# _______________________________ Data Exports _______________________________


def set_export_template(request):
    # Placeholder for setting export template logic
    pass


def export_reports_for_owner(request, owner_id):
    # Placeholder for exporting data by owner logic
    pass



# _______________________________ Mobile app interface _______________________________

def get_db_snapshot(request):
    # Create a current project snapshot for the user
    if not request.user.is_authenticated:
        render(request, '403.html', status=403)

    # Logic to create a snapshot
    try:
        company = Company.objects.filter(project=request.user.current_project).first()
        if not company:
            return render(request, '404.html', status=404)
        buffer = create_snapshot_file(company)
    except Exception as e:
        logger.error(f"Error creating snapshot for user {request.user.id}: {e} Traceback: {traceback.format_exc()}", exc_info=True)
        return render(request, '500.html', status=500)

    return FileResponse(buffer, as_attachment=True, filename='db_snapshot.bin')


def upload_inspection_records(request):
    # Handle uploaded inspection data from mobile app
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            company = Company.objects.filter(project=request.user.current_project).first()
            if not company:
                messages.error(request, "Error updating inspection records: No company found.")
                return redirect('haspro_app:tools-view')

            num_updated, error_message = add_inspection(user, company, file)
            if error_message:
                messages.error(request, f"Error updating inspection records: {error_message}")
            else:
                messages.success(request, f"Successfully updated {num_updated} inspection records.")

        else:
            messages.error(request, "Error updating inspection records: No file provided.")

    return redirect('haspro_app:tools-view')

