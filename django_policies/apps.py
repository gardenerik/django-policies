from django.apps import AppConfig
from django.conf import settings

from django_policies.registry import autodiscover_policies


class DjangoPoliciesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_policies"

    def ready(self):
        if not getattr(settings, "POLICIES_AUTODISCOVER", True):
            return

        autodiscover_policies(
            getattr(settings, "POLICIES_AUTODISCOVER_MODULE", "policies")
        )
