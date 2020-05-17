from django.urls import path, include
from book import views
app_name = "book"
urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('bookinstance/', views.bookinstance, name='bookinstance'),
]