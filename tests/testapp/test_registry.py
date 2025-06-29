from django.test import TestCase

from django_policies.policies import Policy
from django_policies.registry import (
    PolicyRegistry,
    autodiscover_policies,
    default_registry,
)
from testapp.models import Article


class RegistryTests(TestCase):
    def test_get_permissions_for_model(self):
        r = PolicyRegistry()
        permissions = r.get_permissions_for_model(Article)

        expected = [
            "testapp.add_article",
            "testapp.change_article",
            "testapp.delete_article",
            "testapp.view_article",
            "testapp.publish_article",
        ]

        self.assertEqual(len(permissions), len(expected))
        for e in expected:
            self.assertIn(e, permissions)

    def test_register(self):
        r = PolicyRegistry()

        class TestPolicy(Policy):
            pass

        r.register(Article, TestPolicy)
        self.assertIn("testapp.add_article", r._registry)
        self.assertEqual(r._registry["testapp.add_article"], TestPolicy)

    def test_register_twice(self):
        r = PolicyRegistry()

        class TestPolicy(Policy):
            pass

        class TestPolicy2(Policy):
            pass

        r.register(Article, TestPolicy)
        with self.assertRaises(ValueError):
            r.register(Article, TestPolicy2)
        self.assertEqual(r._registry["testapp.add_article"], TestPolicy)

    def test_unregister(self):
        r = PolicyRegistry()

        class TestPolicy(Policy):
            pass

        r.register(Article, TestPolicy)
        r.unregister(Article)
        self.assertEqual(r._registry, {})

    def test_unregister_unknown(self):
        r = PolicyRegistry()
        r.unregister(Article)
        self.assertEqual(r._registry, {})

    def test_autodiscover(self):
        autodiscover_policies()

        self.assertIn("testapp.add_article", default_registry._registry)

        from testapp.policies import ArticlePolicy

        self.assertEqual(
            default_registry._registry["testapp.add_article"], ArticlePolicy
        )
        default_registry.unregister(Article)
