from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
	uid = models.CharField(max_length=64)
	title =  models.CharField(max_length=1024)
	authors = models.CharField(max_length=1024)
	publisher = models.CharField(max_length=1024)
	published_date = models.CharField(max_length=32)
	description = models.CharField(max_length=8192)
	isbn_13 = models.CharField(max_length=32)
	isbn_10 = models.CharField(max_length=32)
	genre = models.CharField(max_length=1024)
	average_rating = models.FloatField()
	ratings_count = models.IntegerField()
	thumbnail = models.CharField(max_length=1024)
	favourites = models.ManyToManyField(User, related_name='favourites')
	readingnow = models.ManyToManyField(User, related_name='readingnow')
	toread = models.ManyToManyField(User, related_name='toread')
	haveread = models.ManyToManyField(User, related_name='haveread')