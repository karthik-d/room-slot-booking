from django.db import models
from django.contrib.auth import get_user_model
import datetime

class Message(models.Model):
    sender = models.ForeignKey(get_user_model(), related_name='message_receiver', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(get_user_model(), related_name='message_sender', on_delete=models.CASCADE, null=True)
    body = models.CharField(max_length=200, null=True,)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False, null=False)

    def __str__(self):
        return str(self.timestamp)

    class Meta:
        ordering = ['-timestamp']
