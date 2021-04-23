from django.contrib import admin
from book.models import Book
from book.models import Category

admin.site.register(Book)
admin.site.register(Category)