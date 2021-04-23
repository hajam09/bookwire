from django.urls import path, include
from forum import views
app_name = "forum"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('c/<slug:community_id>/', views.communitypage, name='communitypage'),
	path('c/<slug:community_id>/f/<slug:forum_id>/', views.forumpage, name='forumpage'),
]