
from django.db import models
from django.conf import settings

from app.services import image_file_path

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    info = models.CharField(max_length=300)
    vip = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)

class Images(models.Model):
    image = models.ImageField(upload_to=image_file_path)
    date = models.DateTimeField(auto_now_add=True)

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='images',
    )

class Location(models.Model):
    location = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)

    latitude = models.FloatField(default=None, null=True)
    longitude = models.FloatField(default=None, null=True)

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='location',
    )

    def __str__(self):
        return '{}, {}'.format(self.profile, self.location)

