from django.contrib import admin
from forum.models import Category, Community, Forum, ForumComment

admin.site.register(Category)
admin.site.register(Community)
admin.site.register(Forum)
admin.site.register(ForumComment)