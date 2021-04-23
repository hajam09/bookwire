from django.db import models
from django.contrib.auth.models import User
import jsonfield

class Book(models.Model):
	isbn13 = models.CharField(max_length=32)
	cleanData = jsonfield.JSONField()
	unCleanData = jsonfield.JSONField()
	isFavourite = models.ManyToManyField(User, related_name='isFavourite')
	readingNow = models.ManyToManyField(User, related_name='readingNow')
	toRead = models.ManyToManyField(User, related_name='toRead')
	haveRead = models.ManyToManyField(User, related_name='haveRead')

	# def __str__ (self):
	# 	return self.isbn13

class Category(models.Model):
	name = models.CharField(max_length=1000)

	def __str__ (self):
		return self.name