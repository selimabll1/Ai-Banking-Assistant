from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # You can extend the base user or use your own
    pass

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)  # 👈 match your DB column

    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.text[:20]}"

class ChatSuggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    clicked_at = models.DateTimeField(auto_now_add=True)




