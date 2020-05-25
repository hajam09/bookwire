from django.shortcuts import render
from .models import Forum, Comment

def forum_mainpage(request):
	all_forums = Forum.objects.all()
	all_comments = Comment.objects.all()
	for i in all_forums:
		print(Comment.objects.filter(forum=i))
	context = {"all_forums": all_forums, "all_comments": all_comments}
	return render(request, "forum_mainpage.html", context)