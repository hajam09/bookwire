# Generated by Django 3.1.7 on 2021-04-17 10:14

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('communityTitle', models.TextField()),
                ('communityDescription', models.TextField()),
                ('createdTime', models.DateTimeField(default=datetime.datetime.now)),
                ('communityBanner', models.ImageField(blank=True, null=True, upload_to='communitybanner/')),
                ('communityLogo', models.ImageField(blank=True, default='communitylogo/defaultimg/default-community-logo.jpg', null=True, upload_to='communitylogo/')),
                ('communityDislikes', models.ManyToManyField(related_name='communityDislikes', to=settings.AUTH_USER_MODEL)),
                ('communityLikes', models.ManyToManyField(related_name='communityLikes', to=settings.AUTH_USER_MODEL)),
                ('communityMembers', models.ManyToManyField(related_name='communityMembers', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Communities',
            },
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forumTitle', models.TextField()),
                ('forumDescription', models.TextField(blank=True, null=True)),
                ('createdTime', models.DateTimeField(default=datetime.datetime.now)),
                ('anonymous', models.BooleanField(default=False)),
                ('forumImage', models.ImageField(blank=True, null=True, upload_to='forumimage/')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.community')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('forumDislikes', models.ManyToManyField(related_name='forumDislikes', to=settings.AUTH_USER_MODEL)),
                ('forumLikes', models.ManyToManyField(related_name='forumLikes', to=settings.AUTH_USER_MODEL)),
                ('forumWatchers', models.ManyToManyField(blank=True, related_name='forumWatchers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Forums',
            },
        ),
        migrations.CreateModel(
            name='ForumComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commentDescription', models.TextField()),
                ('createdTime', models.DateTimeField(default=datetime.datetime.now)),
                ('anonymous', models.BooleanField(default=False)),
                ('edited', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('forum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forums', to='forum.forum')),
                ('forumCommentDislikes', models.ManyToManyField(related_name='forumCommentDislikes', to=settings.AUTH_USER_MODEL)),
                ('forumCommentLikes', models.ManyToManyField(related_name='forumCommentLikes', to=settings.AUTH_USER_MODEL)),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='forum.forumcomment')),
            ],
            options={
                'verbose_name_plural': 'ForumComment',
            },
        ),
    ]