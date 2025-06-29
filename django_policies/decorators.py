from django_policies.policies import Policy
from django_policies.registry import default_registry


def register(model, registry=None):
    if registry is None:
        registry = default_registry

    def _policy_wrapper(policy):
        if not issubclass(policy, Policy):
            raise ValueError("Wrapped class must be a subclass of Policy.")

        registry.register(model, policy)
        return policy

    return _policy_wrapper
