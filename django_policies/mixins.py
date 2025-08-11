from typing import Any
from django.contrib.auth.mixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from django.views.generic.edit import BaseCreateView


class PermissionRequiredMixin(BasePermissionRequiredMixin):
    def get_permission_object(self) -> Any:
        if hasattr(self, "object"):
            return getattr(self, "object")

        if not isinstance(self, BaseCreateView):
            if hasattr(self, "get_object"):
                return getattr(self, "get_object")()

        return None

    def has_permission(self) -> bool:
        obj = self.get_permission_object()
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms, obj)
