from typing import TYPE_CHECKING, Any
from django.apps import apps
from itertools import chain
from importlib import import_module
from django.db.models import Model

from django_policies.policies import Policy

if TYPE_CHECKING:  # pragma: no cover
    from django_policies.policies import AnyUser


class PolicyRegistry:
    _registry: dict[str, type[Policy]]

    def __init__(self) -> None:
        self._registry = {}

    def get_permissions_for_model(self, model: type[Model]) -> list[str]:
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        if model_name is None:
            raise ValueError(f"model_name of {model.__class__.__name__} is None.")

        permissions = [f"{app_label}.{perm[0]}" for perm in model._meta.permissions]
        default_permissions = [
            f"{app_label}.{perm}_{model_name}"
            for perm in model._meta.default_permissions
        ]

        return list(chain(permissions, default_permissions))

    def register(self, model: type[Model], policy: type[Policy]):
        for perm in self.get_permissions_for_model(model):
            if perm in self._registry:
                raise ValueError(f"Permission {perm} is already registered.")
            self._registry[perm] = policy

    def unregister(self, model: type[Model]):
        for perm in self.get_permissions_for_model(model):
            if perm not in self._registry:
                continue
            del self._registry[perm]

    def check_permission(
        self, user: "AnyUser", permission: str, obj: Any = None
    ) -> bool:
        if permission not in self._registry:
            return False

        return self._registry[permission]().check_permission(user, permission, obj)


default_registry = PolicyRegistry()


def autodiscover_policies(module_name="policies"):
    for app in apps.get_app_configs():
        try:
            import_module(f"{app.name}.{module_name}")
        except ImportError:
            continue
