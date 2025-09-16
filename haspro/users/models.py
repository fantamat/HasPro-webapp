import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    phone = models.CharField(max_length=16, unique=True, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    # Indicates if the user currently has an active paid subscription

    signature = models.FileField(upload_to='signatures/', blank=True, null=True)

    technicianID = models.CharField(max_length=100, blank=True, null=True)
    
    current_project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name="current_users")

    def __str__(self):
        return self.username


class Project(models.Model):
    """Model representing a project owned by a user."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class ProjectPermissions(models.Model):
    """Model representing user permissions for a project."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="permissions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_permissions")
    can_edit = models.BooleanField(default=False)
    can_view = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.project.name} Permissions"