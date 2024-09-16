from django.db import models

# Articles model
class Article(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    source_name = models.CharField(max_length=255)
    pictureUrl = models.URLField(unique=True, null=True)
    topic = models.CharField(max_length=255)

    def __str__(self):
        return self.title