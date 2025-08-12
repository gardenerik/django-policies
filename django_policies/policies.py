from typing import TYPE_CHECKING, Any

from django.conf import settings

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth.models import AbstractUser, AnonymousUser

    AnyUser = AbstractUser | AnonymousUser


class Policy:
    no_object_suffix: str = "_some"
    deny_anonymous: bool | None = None

    def get_permission_methods(self, permission: str) -> list[str]:
        methods = []
        permission = permission.split(".", 1)[-1]

        # can_change_model
        methods.append(f"can_{permission}")

        # can_change
        perm_name = permission.rsplit("_", 1)[0]
        methods.append(f"can_{perm_name}")

        return methods

    def check_permission(
        self, user: "AnyUser", permission: str, obj: Any = None
    ) -> bool:
        if self.deny_anonymous is None:
            self.deny_anonymous = getattr(
                settings, "POLICIES_DENY_ANONYMOUS_DEFAULT", False
            )

        for method in self.get_permission_methods(permission):
            if obj is None:
                method += self.no_object_suffix

            if not hasattr(self, method):
                continue

            if self.deny_anonymous and not user.is_authenticated:
                return False

            attr = getattr(self, method)
            if callable(attr):
                args = [user]
                if obj is not None:
                    args.append(obj)

                val = attr(*args)
                if not isinstance(val, bool):
                    raise ValueError(f"{method} returned {type(val)}, expected bool.")
                return val
            if isinstance(attr, bool):
                return attr

            raise ValueError(
                f"Invalid value of {method} in {self.__class__.__name__}: expected boolean or a callable."
            )

        return False
