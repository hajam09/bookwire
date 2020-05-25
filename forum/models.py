from django.db import models
from django.contrib.auth.models import User

class Forum(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=1024)
	description = models.CharField(max_length=2048)
	created_at = models.DateField()

class Comment(models.Model):
	forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
	owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	description = models.TextField(max_length=1024)
	created_at = models.DateTimeField()