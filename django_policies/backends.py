from asgiref.sync import sync_to_async
from django.contrib.auth.backends import BaseBackend
from django_policies.registry import default_registry


class PolicyBackend(BaseBackend):
    async def ahas_perm(self, user_obj, perm, obj=None):
        return await sync_to_async(self.has_perm)(user_obj, perm, obj)

    def has_perm(self, user_obj, perm, obj=None) -> bool:
        return default_registry.check_permission(user_obj, perm, obj)  # pyright: ignore
