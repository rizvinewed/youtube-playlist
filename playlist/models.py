from django.db import models
from django.utils import timezone


class Playlist(models.Model):
    url = models.CharField(max_length=500, null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.CharField(max_length=200, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    from_video = models.IntegerField(null=True, blank=True)
    to_video = models.IntegerField(null=True, blank=True)
    channel_name = models.CharField(max_length=200, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "playlist"
        ordering = ["-created_date"]

    def __str__(self) -> str:
        if self.ip_address:
            return f"{self.name} || {self.channel_name} - {self.ip_address}"
        return f"{self.name}"


class Feedback(models.Model):
    feedback = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "feedback"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.feedback[:50]}"
