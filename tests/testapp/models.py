from django.db import models
from django.conf import settings


class Article(models.Model):
    name = models.CharField(max_length=128)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        permissions = [("publish_article", "Can publish article")]
