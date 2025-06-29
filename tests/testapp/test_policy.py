from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase

from django_policies.policies import Policy


class PolicyTest(TestCase):
    def test_get_permission_methods(self):
        tests = [
            ("testapp.add_article", {"can_add", "can_add_article"}),
            ("testapp.publish_article", {"can_publish", "can_publish_article"}),
            (
                "testapp.do_something_article",
                {"can_do_something", "can_do_something_article"},
            ),
            ("testapp.nounderscores", {"can_nounderscores"}),
            ("noapp", {"can_noapp"}),
            ("noapp_article", {"can_noapp", "can_noapp_article"}),
        ]

        p = Policy()
        for inp, out in tests:
            self.assertEqual(p.get_permission_methods(inp), out)

    def test_check_permission_object(self):
        class TestPolicy(Policy):
            def can_add(self, *args):
                self.add_called = args
                return True

            def can_add_some(self, *args):
                self.add_some_called = args
                return True

            def can_publish_article(self, *args):
                self.publish_called = args
                return True

            can_change = True

        user = User()
        obj = 34

        p = TestPolicy()
        res = p.check_permission(user, "testapp.add_article", obj)
        self.assertTrue(res)
        self.assertTrue(hasattr(p, "add_called"))
        self.assertFalse(hasattr(p, "add_some_called"))
        self.assertFalse(hasattr(p, "publish_called"))
        self.assertEqual(p.add_called, (user, obj))

        p = TestPolicy()
        res = p.check_permission(user, "testapp.publish_article", obj)
        self.assertTrue(res)
        self.assertTrue(hasattr(p, "publish_called"))
        self.assertFalse(hasattr(p, "add_some_called"))
        self.assertFalse(hasattr(p, "add_called"))
        self.assertEqual(p.publish_called, (user, obj))

        res = p.check_permission(user, "some_random_permission", obj)
        self.assertFalse(res)

        res = p.check_permission(user, "testapp.change_article", obj)
        self.assertTrue(res)

    def test_check_permission_no_object(self):
        class TestPolicy(Policy):
            def can_add(self, *args):
                self.add_called = args
                return True

            def can_add_some(self, *args):
                self.add_some_called = args
                return True

            can_change_some = True

        user = User()

        p = TestPolicy()
        res = p.check_permission(user, "testapp.add_article")
        self.assertTrue(res)
        self.assertFalse(hasattr(p, "add_called"))
        self.assertEqual(p.add_some_called, (user,))

        res = p.check_permission(user, "testapp.change_article")
        self.assertTrue(res)

    def test_check_permission_invalid(self):
        class TestPolicy(Policy):
            def can_add_some(self, *args):
                return 12

            can_change_some = 34

        user = User()

        p = TestPolicy()
        with self.assertRaises(ValueError):
            p.check_permission(user, "testapp.add_article")

        with self.assertRaises(ValueError):
            p.check_permission(user, "testapp.change_article")

    def test_anonymous(self):
        class TestPolicy(Policy):
            can_change = True

        tests = [
            (True, False),
            (False, True),
        ]

        auser = AnonymousUser()

        for anonymous, expected in tests:
            TestPolicy.deny_anonymous = anonymous
            self.assertEqual(
                TestPolicy().check_permission(auser, "testapp.change_article", 12),
                expected,
            )
