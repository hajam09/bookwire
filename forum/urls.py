from django.urls import path, include
from forum import views
app_name = "forum"
urlpatterns = [
	path('', views.forum_mainpage, name='forum_mainpage'),
]