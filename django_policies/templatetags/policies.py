from django import template


register = template.Library()


@register.simple_tag
def has_perm(user, perm, obj=None):
    return user.has_perm(perm, obj)
