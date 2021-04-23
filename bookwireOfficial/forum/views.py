from datetime import datetime
from deprecated import deprecated
from django.contrib.auth.models import User
from django.core import serializers
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from forum.models import Category
from forum.models import Community
from forum.models import Forum
from forum.models import ForumComment
from http import HTTPStatus
from sklearn.preprocessing import MinMaxScaler
import json
import pandas as pd

def mainpage(request):

	if request.method == "POST" and "create_community" in request.POST:
		if not request.user.is_authenticated:
			return redirect('accounts:login')
		studyLevel = request.POST['studyLevel']
		category = Category.objects.get(name=studyLevel)
		title = request.POST['title']
		description = request.POST['description']

		new_community = Community.objects.create(
			creator = request.user,
			communityTitle = title,
			communityDescription = description,
		)

		return redirect('forum:communitypage', community_id=new_community.pk)

	popular_forums = GetPopularPosts()
	forums_split = [popular_forums[i:i + 15] for i in range(0, len(popular_forums), 15)]

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "fetch_forums":
			next_index = request.GET.get('next_index', None)
			forum_json = []

			try:
				next_forum = forums_split[int(next_index)]
			except IndexError:
				response = {
					"error": "IndexError"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			for e in next_forum:
				forum_json.append({
					'forumId': e.id,
					'forumCommunityId': e.community.id,
					'forumVotes': e.forum_likes.count() - e.forum_dislikes.count(),
					'forumCreatorFullName': e.creator.get_full_name(),
					'forumCreatedDate': vanilla_JS_date_conversion(e.created_at),
					'forumTitle': e.forum_title,
					'forumImage': str(e.forum_image),
					'forumDescription': e.forum_description,
					'forumCommentCount': e.forums.count(),
					'forumEdit': True if e.creator.id == request.user.pk else False,
					'forumWatching': True if request.user in e.watchers.all() else False,
					'forumWatchCount': e.watchers.count(),
				})

			response = {
				"status_code": HTTPStatus.OK,
				"forum_json": forum_json
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

	context = {
		"category": Category.objects.all(),
		"forums": forums_split[0] if len(forums_split)>0 else [],
	}
	return render(request, "forum/mainpage.html", context)

def communitypage(request, community_id):
	try:
		community = Community.objects.get(pk=community_id)
	except Community.DoesNotExist:
		raise Http404


	if request.method == "POST" and "create_forum" in request.POST:

		if not request.user.is_authenticated:
			return redirect('accounts:login')
			
		forum_title = request.POST['forum_title']
		description = request.POST['description']

		if not description and not "forum_image" in request.FILES:
			return redirect('forum:communitypage', community_id=community_id)

		try:
			forum_image = request.FILES["forum_image"]
		except KeyError as e:
			forum_image = None

		newForum = Forum.objects.create(
			community = community,
			creator = request.user,
			forumTitle = forum_title,
			forumDescription = description,
			forumImage = forum_image,
		)
		return redirect('forum:communitypage', community_id=community_id)

	all_forums = Forum.objects.filter(community=community).order_by('-id')
	forums_split = [all_forums[i:i + 15] for i in range(0, len(all_forums), 15)]

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "join_community":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to join this community."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			community.community_members.add(request.user)

			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "leave_community":
			community.community_members.remove(request.user)
			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "upvote_forum":
			# TODO: Get the forum object from the list. Manual test the implementation.
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to up vote this forum."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			forum_id = request.GET.get('forum_id', None)

			try:
				this_forum = Forum.objects.get(id=int(forum_id))
				# next((x for x in test_list if x.value == value), None)
				# This gets the first item from the list that matches the condition, and returns None if no item matches.
				# Get the Forum object from all_forums list.
			except Forum.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this forum has been deleted!"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			this_forum.increase_forum_vote(request)

			response = {
				"status_code": HTTPStatus.OK,
				"this_forum": serializers.serialize("json", [this_forum,]),
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "downvote_forum":
			# TODO: Get the forum object from the list. Manual test the implementation.
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to down vote this forum."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			forum_id = request.GET.get('forum_id', None)

			try:
				this_forum = Forum.objects.get(id=int(forum_id))
				# next((x for x in test_list if x.value == value), None)
				# This gets the first item from the list that matches the condition, and returns None if no item matches.
				# Get the Forum object from all_forums list.
			except Forum.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this forum has been deleted!"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			this_forum.decrease_forum_vote(request)

			response = {
				"status_code": HTTPStatus.OK,
				"this_forum": serializers.serialize("json", [this_forum,]),
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "fetch_forums":
			next_index = request.GET.get('next_index', None)
			forum_json = []
			try:
				next_forum = forums_split[int(next_index)]
			except IndexError:
				response = {
					"error": "IndexError"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")
				
			for e in next_forum:
				forum_json.append({
						'forumId': e.id,
						'forumVotes': e.forum_likes.count() - e.forum_dislikes.count(),
						'forumCreatorFullName': e.creator.get_full_name(),
						'forumCreatedDate': vanilla_JS_date_conversion(e.created_at),
						'forumTitle': e.forum_title,
						'forumImage': str(e.forum_image),
						'forumDescription': e.forum_description,
						'forumCommentCount': ForumComment.objects.filter(forum=e).count(),
						'forumEdit': True if e.creator.id == request.user.pk else False,
					})
			response = {
				"status_code": HTTPStatus.OK,
				"forum_json": forum_json
			}
			return HttpResponse(json.dumps(response), content_type="application/json")


		raise Exception("Unknown functionality communitypage")

	context = {
		"community": community,
		"forums": forums_split[0] if len(forums_split)>0 else [],
		"in_community": True if request.user in community.community_members.all() else False
	}
	return render(request, "forum/communitypage.html", context)

def forumpage(request, community_id, forum_id):
	try:
		forum = Forum.objects.select_related('creator', 'community').prefetch_related('forums', 'watchers', 'forum_dislikes', 'forum_likes', 'forums__forum_comment_dislikes', 'forums__forum_comment_likes', 'forums__creator', 'forums__reply').get(pk=forum_id)
	except Forum.DoesNotExist:
		raise Http404

	community = forum.community
		
	if community.id is not int(community_id):
		# Forum's community is not the same as the expected community from url.
		return HttpResponse("<h1>Bad Request. Looks like you are messing with the url.</h1>")

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "join_community":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to join this community."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			community.community_members.add(request.user)
			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "leave_community":
			community.community_members.remove(request.user)
			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "upvote_forum":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to up vote this forum."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			forum.increase_forum_vote(request)

			response = {
				"status_code": HTTPStatus.OK,
				"this_forum": serializers.serialize("json", [forum,]),
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "downvote_forum":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to down vote this forum."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			forum.decrease_forum_vote(request)

			response = {
				"status_code": HTTPStatus.OK,
				"this_forum": serializers.serialize("json", [forum,]),
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "post_comment":
			comment = request.GET.get('comment', None)
			master_comment = request.GET.get('master_comment', None)

			if master_comment is not None:
				master_comment = ForumComment.objects.get(id=int(master_comment))

			forum_comment = ForumComment.objects.create(
				forum = forum,
				creator = request.user,
				commentDescription = comment,
				reply = master_comment,
			)
			response = {
				"forum_comment": serializers.serialize("json", [forum_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "like_comment":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to like the question and answer. "
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			commentId = request.GET.get('commentId', None)

			try:
				this_comment = ForumComment.objects.get(id=int(commentId))
			except ForumComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this comment has been deleted!"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			this_comment.increase_forum_comment_likes(request)

			response = {
				"this_comment": serializers.serialize("json", [this_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "dislike_comment":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to like the question and answer. "
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			commentId = request.GET.get('commentId', None)
			
			try:
				this_comment = ForumComment.objects.get(id=int(commentId))
			except ForumComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this comment has been deleted!"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			this_comment.increase_forum_comment_dislikes(request)

			response = {
				"this_comment": serializers.serialize("json", [this_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "delete_forum_comment":
			comment_id = request.GET.get('comment_id', None)

			try:
				ForumComment.objects.get(pk=int(comment_id)).delete()
				response = {
					"status_code": HTTPStatus.OK
				}
				return HttpResponse(json.dumps(response), content_type="application/json")
			except ForumComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			response = {
				"status_code": HTTPStatus.BAD_REQUEST,
				"message": "Bad Request"
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "watch_unwatch_forum":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to watch this forum. "
				}
				return HttpResponse(json.dumps(response), content_type="application/json")
				
			if(request.user not in forum.watchers.all()):
				forum.watchers.add(request.user)
				is_watching = True
			else:
				forum.watchers.remove(request.user)
				is_watching = False

			response = {
				"is_watching": is_watching,
				"watch_count": forum.watchers.count(),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

	context = {
		"forum": forum,
		"in_community": True if request.user in community.community_members.all() else False,
		"is_watching": True if request.user in forum.watchers.all() else False,
	}
	return render(request, "forum/forumpage.html", context)

def vanilla_JS_date_conversion(python_date):
	date = python_date.strftime("%b. %d, %Y,")
	time = datetime.strptime( python_date.strftime("%H:%M"), "%H:%M")
	time = time.strftime("%I:%M %p").lower().replace("pm", "p.m.").replace("am", "a.m.")
	date_time = str(date + " " + time)
	return date_time

def GetPopularPosts():
	"""
		Return the most popular posts created on any community.
		Attributes to determine the popularity:
			forum vote, comment count, watch count and creation date is today (future).
	"""
	if Forum.objects.count() == 0:
		return []
		
	all_forums_obj = Forum.objects.all().prefetch_related('forum_likes', 'forum_dislikes', 'watchers', 'forums').select_related('creator', 'community')

	forum_list = [{
		'id': e.pk,
		'forum_vote': e.forum_likes.count() - e.forum_dislikes.count(),
		'comment_count': e.forums.all().count(),
		'watch_count': e.watchers.all().count()
		} for e in all_forums_obj]

	df = pd.DataFrame(forum_list)
	scaling = MinMaxScaler()
	divedent = 100/3

	forum_scaled = scaling.fit_transform(df[['forum_vote', 'comment_count', 'watch_count']])
	forum_normalized = pd.DataFrame(forum_scaled, columns=['forum_vote', 'comment_count', 'watch_count'])

	df[['normalized_forum_vote','normalized_comment_count','normalized_watch_count']]= forum_normalized
	df['score'] = df['normalized_forum_vote'] * divedent+ df['normalized_comment_count'] * divedent + df['normalized_watch_count'] * divedent

	forum_scored_df = df.sort_values(['score'], ascending=False)
	forum_id = list(forum_scored_df['id'])
	# all_forums = [all_forums_obj[i-1] for i in forum_id] use when pk is in order.
	return [j for i in forum_id for j in all_forums_obj if i == j.pk]