from django.db import models


class Trend(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, null=True)
    cover_picture_url = models.URLField(blank=True, null=True)
    url = models.URLField()
    source = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

