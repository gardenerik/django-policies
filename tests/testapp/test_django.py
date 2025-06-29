from django.apps import apps
from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import TestCase

from django_policies.registry import default_registry
from testapp.models import Article


class DjangoIntegrationTest(TestCase):
    def setUp(self):
        with self.settings(POLICIES_AUTODISCOVER=True):
            aconfig = apps.get_app_config("django_policies")
            aconfig.ready()

    def test_autodiscover(self):
        self.assertTrue(len(default_registry._registry) > 0)

    def test_permission_check(self):
        u = User.objects.create_user("admin", "admin@localhost", "admin")

        self.assertTrue(u.has_perm("testapp.add_article"))
        self.assertTrue(u.has_perm("testapp.change_article", Article()))
        self.assertFalse(u.has_perm("testapp.delete_article"))

    def test_template_tag(self):
        user = User.objects.create_user("admin", "admin@localhost", "admin")

        tests = [
            ('user "testapp.add_article"', "True"),
            ('user "testapp.change_article" article', "True"),
            ('user "testapp.change_article"', "False"),
            ('user "testapp.delete_article"', "False"),
            ('user "random"', "False"),
        ]

        for test in tests:
            template = Template(
                "{% load policies %}{% has_perm " + test[0] + " as p %}{{ p }}"
            )
            ctx = Context({"user": user, "article": Article()})
            result = template.render(ctx)
            self.assertEqual(result, test[1])
