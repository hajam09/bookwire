from django.urls import path
from django.urls import re_path
from django.urls import include
from book import views
app_name = "book"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('bookinstance/<slug:isbn_13>', views.bookinstance, name='bookinstance'),
	re_path(r'^updateShelf/(?P<isbn_13>.*)/(?P<shelf_type>.*)$',views.updateShelf, name='updateShelf'),
]