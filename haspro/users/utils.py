from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.core.cache import cache

from .models import ProjectPermissions, User


def get_cached_user_current_project(user_id):
    """
    Get user's current project from cache or database with memory caching
    """
    cache_key = f"user_current_project_{user_id}"
    
    # Try to get from cache first
    project = cache.get(cache_key)
    
    if project is None:
        # Not in cache, query database
        try:
            user = User.objects.select_related('current_project').get(id=user_id)
            project = user.current_project
        except User.DoesNotExist:
            project = None
        
        # Cache the result for 30 minutes (1800 seconds) - projects change less frequently
        cache.set(cache_key, project, 1800)
    
    return project


def get_cached_project_permission(user_id, project_id):
    """
    Get project permission from cache or database with memory caching
    """
    cache_key = f"project_permission_{user_id}_{project_id}"
    
    # Try to get from cache first
    project_permission = cache.get(cache_key)
    
    if project_permission is None:
        # Not in cache, query database
        try:
            project_permission = ProjectPermissions.objects.filter(
                project_id=project_id, 
                user_id=user_id
            ).first()
        except ProjectPermissions.DoesNotExist:
            project_permission = None
        
        # Cache the result for 15 minutes (900 seconds)
        # Use None if no permission found to avoid repeated DB queries
        cache.set(cache_key, project_permission, 900)
    
    return project_permission


def invalidate_user_current_project_cache(user_id):
    """
    Helper function to invalidate user's current project cache
    """
    cache_key = f"user_current_project_{user_id}"
    cache.delete(cache_key)


def invalidate_project_permission_cache(user_id, project_id):
    """
    Helper function to invalidate cache when permissions change
    """
    cache_key = f"project_permission_{user_id}_{project_id}"
    cache.delete(cache_key)


def project_permission_decorator(require_admin=False, require_edit=False, require_view=False):
    def project_decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Use cached current project to avoid database hit
                project = get_cached_user_current_project(request.user.id)
                if not project:
                    return render(request, '403.html', {
                        'error_message': "No project associated with the user."
                    }, status=403)
                request.project = project

                # Use cached project permission
                project_permission = get_cached_project_permission(request.user.id, project.id)
                request.project_permission = project_permission

                if require_admin and (not project_permission or not project_permission.is_admin):
                    return render(request, '403.html', {
                        'error_message': "You do not have admin permissions for this project."
                    }, status=403)
                if require_edit and (not project_permission or not project_permission.can_edit):
                    return render(request, '403.html', {
                        'error_message': "You do not have edit permissions for this project."
                    }, status=403)
                if require_view and (not project_permission or not project_permission.can_view):
                    return render(request, '403.html', {
                        'error_message': "You do not have view permissions for this project."
                    }, status=403)

                return view_func(request, *args, **kwargs)
            else:
                return redirect('account_login')

        return _wrapped_view
    return project_decorator

