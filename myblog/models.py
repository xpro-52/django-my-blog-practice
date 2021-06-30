from django.db import models
from django.conf import settings
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=200)
    text = models.TextField()

    class Meta:
        ordering = ['-published_date']

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def private(self):
        self.published_date = None
        self.save()

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    public_name = models.CharField(max_length=200)
    born = models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=200, blank=True, null=True)
    github = models.URLField(max_length=200)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.public_name

