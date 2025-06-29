from django.test import TestCase

from django_policies.decorators import register
from django_policies.policies import Policy
from django_policies.registry import PolicyRegistry, default_registry
from testapp.models import Article


class RegisterDecoratorTest(TestCase):
    def test_register(self):
        r = PolicyRegistry()

        @register(Article, r)
        class TestPolicy(Policy):
            pass

        self.assertIn("testapp.add_article", r._registry)

    def test_register_non_policy(self):
        r = PolicyRegistry()

        with self.assertRaises(ValueError):

            @register(Article, r)
            class FakePolicy:
                pass

        self.assertNotIn("testapp.add_article", r._registry)

    def test_default(self):
        @register(Article)
        class TestPolicy(Policy):
            pass

        self.assertIn("testapp.add_article", default_registry._registry)
        default_registry.unregister(Article)
