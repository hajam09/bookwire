from django.urls import path, include
from book import views
app_name = "book"
urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('bookinstance/<slug:isbn_13>', views.bookinstance, name='bookinstance'),
	path('usershelf/', views.usershelf, name='usershelf'),
]