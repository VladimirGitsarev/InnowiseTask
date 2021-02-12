from django.db import models
from app.models import Profile

class Swipe(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    liked = models.BooleanField(null=False)

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='swipes',
    )

    swiped = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='swiped',
    )

    def __str__(self):
        return '{} {} swiped {} {}, liked: {}'.format(
            self.profile.fname, self.profile.lname,
            self.swiped.fname, self.swiped.lname,
            self.liked
            )

    