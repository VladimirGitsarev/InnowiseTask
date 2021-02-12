from django.db import models
from app.models import Profile

class Chat(models.Model):
    user1 = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE,
        related_name='user1'
    )

    user2 = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='user2'
    )

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Chat {}: {} {} - {} {}'.format(
            self.id, 
            self.user1.fname, self.user1.lname,
            self.user2.fname, self.user2.lname
        )

class Message(models.Model):
    message = models.CharField(max_length=300)
    sender = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE
    )

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE
    )

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Message from {} {} to chat {}'.format(
            self.sender.fname, self.sender.lname, self.chat
        )