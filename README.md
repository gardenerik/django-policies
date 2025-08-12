<div align="center">
  <h1>Django Policies</h1>
  <p>Policy-based Django permissions backend</p>
</div>

Django Policies is a flexible, code-based permissions backend for Django,
inspired by [Laravel's policies](https://laravel.com/docs/12.x/authorization#writing-policies).
Instead of managing object-level permissions via the database, Django Policies
lets you define rules using simple Python methods, making your authorization
logic easier to test, maintain, and reason about.

```python
@register(Article)
class ArticlePolicy(Policy):
  def can_change(self, user, article):
    if user.is_staff:
      return True
 
    return user == article.author
```

## Installation

```shell
pip install django-policies
```

Add `django_policies` to `INSTALLED_APPS` and add backend to `AUTHENTICATION_BACKENDS`:

```python
# settings.py snippet
INSTALLED_APPS = [
    ...
    "django_policies",
]

AUTHENTICATION_BACKENDS = [
    "django_policies.backends.PolicyBackend",
    "django.contrib.auth.backends.ModelBackend",
]
```

Register your first policy in `policies.py` in your application. Django Policies
will automatically discover policies.

```python
from django_policies.decorators import register
from django_policies.policies import Policy
...

@register(Article)
class ArticlePolicy(Policy):
    def can_change(self, user, obj):
        return user == obj.author
```

## Usage

### Permission mapping

When a policy is registered, all permission checks for that model will be
handled by the registered policy. By default, 4 permissions are registered for
the model (`add_<model>`, `change_<model>`, `delete_<model>`, `view_<model>`)
and more can be added using [permissions](https://docs.djangoproject.com/en/dev/ref/models/options/#permissions)
in the model's meta.

For every permission, two methods on the policy class are considered (in this order,
first that is found will be called):

- full permission name: `can_change_article`
- last part of the permission name dropped: `can_change`

Permissions that are not defined in the policy will not be handled by Policies,
but can still be handled by other authentication backends.

### Permission checks without object

Sometimes, you may need to check if a user has permission without an object
instance. For example when you don't have an instance available (creating a
new one), or when you want to know if a user has a permission in general.

When a permission check is initiated without an object instance, Django Policies
will consult `can_<perm>_some(user)` method instead of `can_<perm>(user, object)`:

```python
class ArticlePolicy(Policy):
    def can_change(self, user, object):
        # Called when an object instance is provided.
        ...

    def can_change_some(self, user):
        # Called when an object instance is not provided.
        ...
```

The `_some` prefix can be configured using `no_object_suffix` property on the
policy class.

### Constant policies

Sometimes, you want to set policy to a constant value:

```python
class ArticlePolicy(Policy):
    def can_change(self, user, obj):
        return False
```

You can also set `can_change` to a constant boolean value:

```python
class ArticlePolicy(Policy):
    can_change = False
```

### Handling anonymous users

By default, your policies will get called for AnonymousUser, so you will need to
handle their permissions as well.

```python
def can_change(self, user, obj):
    if not user.is_authenticated:
        return False

    ...
```

Handling anonymous users in every method can lead to repetitive code. To
simplify this, you can globally deny access for anonymous users in a policy by
setting `deny_anonymous`:

```python
class ArticlePolicy(Policy):
    deny_anonymous = True
```

The above is equivalent to inserting `if not user.is_authenticated: return False` to all policy methods.

For some applications, you will find that denying anoymous access should be the
default. Django Policies allows you to change the project default in Django settings:

```python
POLICIES_DENY_ANONYMOUS_DEFAULT = True
```

### Checking permissions

Inside views, you can use the default Django's `has_perm` on the user object:

```python
user.has_perm("app.change_article", article) # -> calls can_change

user.has_perm("app.change_article") # -> calls can_change_some
```

In template code, Django does not provide a way to access object permissions, so
a custom template tag is provided:

```jinja2
{% load policies %}

{% has_perm user "app.change_article" article as can_change %}
{% if can_change %}...{% endif %}

{% has_perm user "app.change_article" as can_change %}
{% if can_change %}...{% endif %}
which is the same as {% if perms.app.change_article %}...{% endif %}
```

For generic views, a modified `PermissionRequiredMixin` is provided:

```python
from django_policies.mixins import PermissionRequiredMixin

class MyView(PermissionRequiredMixin, ...):
    permission_required = "app.change_article"

    def get_permission_object(self):
        return self.article
```

### Automatic discovery

Django Policies automatically discovers `policies.py` files in all installed apps.
This behavior can be disabled by changing the `POLICIES_AUTODISCOVER` setting
to `False`. Alternatively, a different file can be discovered by changing
`POLICIES_AUTODISCOVER_MODULE` to another module name.

## Other packages

- [django-rules](https://github.com/dfunckt/django-rules), a different take on
  object permissions based on combining logic predicates
- [django-guardian](https://github.com/django-guardian/django-guardian), also a
  different take storing object permissions in a database
