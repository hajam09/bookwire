from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Category(models.Model):
	name = models.CharField(max_length=512)

	class Meta:
		verbose_name_plural = "Categories"

	def __str__(self):
		return self.name

class Community(models.Model):
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	communityTitle = models.TextField()
	communityDescription = models.TextField()
	createdTime = models.DateTimeField(default=datetime.now)
	communityLikes = models.ManyToManyField(User, related_name='communityLikes')
	communityDislikes = models.ManyToManyField(User, related_name='communityDislikes')
	communityBanner = models.ImageField(upload_to='communitybanner/', blank=True, null=True)
	communityLogo = models.ImageField(upload_to='communitylogo/', blank=True, null=True, default='communitylogo/defaultimg/default-community-logo.jpg')
	communityMembers = models.ManyToManyField(User, related_name='communityMembers')

	class Meta:
		verbose_name_plural = "Communities"

class Forum(models.Model):
	community = models.ForeignKey(Community, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	forumTitle = models.TextField()
	forumDescription = models.TextField(blank=True, null=True)
	createdTime = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField(default=False)
	forumLikes = models.ManyToManyField(User, related_name='forumLikes')
	forumDislikes = models.ManyToManyField(User, related_name='forumDislikes')
	forumImage = models.ImageField(upload_to='forumimage/', blank=True, null=True)
	forumWatchers = models.ManyToManyField(User, blank=True, related_name='forumWatchers')

	def increaseForumVote(self, request):
		if(request.user not in self.forumLikes.all()):
			self.forumLikes.add(request.user)
		else:
			self.forumLikes.remove(request.user)

		if(request.user in self.forumDislikes.all()):
			self.forumDislikes.remove(request.user)

	def decreaseForumVote(self, request):
		if(request.user not in self.forumDislikes.all()):
			self.forumDislikes.add(request.user)
		else:
			self.forumDislikes.remove(request.user)

		if(request.user in self.forumLikes.all()):
			self.forumLikes.remove(request.user)

	class Meta:
		verbose_name_plural = "Forums"

class ForumComment(models.Model):
	forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='forums')
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	commentDescription = models.TextField()
	createdTime = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField(default=False)
	edited = models.BooleanField(default=False)
	reply = models.ForeignKey('ForumComment', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
	forumCommentLikes = models.ManyToManyField(User, related_name='forumCommentLikes')
	forumCommentDislikes = models.ManyToManyField(User, related_name='forumCommentDislikes')

	def increaseForumCommentLikes(self, request):
		if(request.user not in self.forumCommentLikes.all()):
			self.forumCommentLikes.add(request.user)
		else:
			self.forumCommentLikes.remove(request.user)

		if(request.user in self.forumCommentDislikes.all()):
			self.forumCommentDislikes.remove(request.user)

	def increaseForumCommentDislikes(self, request):
		if(request.user not in self.forumCommentDislikes.all()):
			self.forumCommentDislikes.add(request.user)
		else:
			self.forumCommentDislikes.remove(request.user)

		if(request.user in self.forumCommentLikes.all()):
			self.forumCommentLikes.remove(request.user)

	class Meta:
		verbose_name_plural = "ForumComment"