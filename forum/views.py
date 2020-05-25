from django.shortcuts import render
from .models import Forum, Comment

def forum_mainpage(request):
	all_forums = Forum.objects.all()
	context = {"all_forums": all_forums}
	return render(request, "forum_mainpage.html", context)