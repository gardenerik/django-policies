from django_policies.decorators import register
from django_policies.policies import Policy
from testapp.models import Article


@register(Article)
class ArticlePolicy(Policy):
    can_add_some = True

    def can_change(self, user, obj):
        return True
