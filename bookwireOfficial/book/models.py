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

	def updateIsFavourite(self, request):
		if request.user not in self.isFavourite.all():
			self.isFavourite.add(request.user)
			return True
		else:
			self.isFavourite.remove(request.user)
			return False

	def updateReadingNow(self, request):
		if request.user not in self.readingNow.all():
			self.readingNow.add(request.user)
			return True
		else:
			self.readingNow.remove(request.user)
			return False

	def updateToRead(self, request):
		if request.user not in self.toRead.all():
			self.toRead.add(request.user)
			return True
		else:
			self.toRead.remove(request.user)
			return False

	def updateHaveRead(self, request):
		if request.user not in self.haveRead.all():
			self.haveRead.add(request.user)
			return True
		else:
			self.haveRead.remove(request.user)
			return False

	# def __str__ (self):
	# 	return self.isbn13

class Category(models.Model):
	name = models.CharField(max_length=1000)

	def __str__ (self):
		return self.name