from django import template
from django.conf import settings

_ = None  # Dummy variable to ensure the import is not optimized away

register = template.Library()


@register.simple_tag
def get_analytics_id():
    """Get Google Analytics ID from settings."""
    return settings.GOOGLE_ANALYTICS_ID
