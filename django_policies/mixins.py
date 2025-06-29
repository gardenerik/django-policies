from django.contrib.auth.mixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)


class PermissionRequiredMixin(BasePermissionRequiredMixin):
    def get_permission_object(self):
        return None

    def has_permission(self) -> bool:
        obj = self.get_permission_object()
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms, obj)
