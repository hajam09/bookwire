from django.shortcuts import render, redirect
from .models import Book, Review
import requests, json
from datetime import datetime as dt
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict, HttpResponse
from django.contrib.auth.models import User
from django.core import serializers
from django.contrib.auth.decorators import login_required
from .bookHelper import googleBooksAPIRequests

def mainpage(request):
	if request.method == "POST":
		bookSearchQuery = request.POST["booksearch"]
		requestedBooks = googleBooksAPIRequests(bookSearchQuery)

		return render(request, "mainpage.html", {"bookresults":requestedBooks, "no_result":"Sorry, we could't find any results matching {}".format(bookSearchQuery)})
	return render(request, "mainpage.html",{})

@csrf_exempt
def bookinstance(request,isbn_13):
	# Review.objects.all().delete()
	try:
		book = Book.objects.get(isbn_13=isbn_13)
		reviews = Review.objects.filter(book=book).order_by('-created_at')

		if request.user.is_authenticated:
			if 'history' not in request.session:
				request.session['history'] = []
			history = request.session['history']
			if isbn_13 not in history:
				history.append(isbn_13)
			request.session['history'] = history

	except Book.DoesNotExist:
		return redirect("book:mainpage")

	if request.method == "POST" and request.user.is_authenticated and not request.user.is_superuser:
		functionality = request.POST["functionality"]
		if functionality == "create-review":
			description = request.POST["description"]
			value = request.POST["value"]
			# In the future delete user's previous comment if exist so it does not cause problem with dataframe.
			new_review = serializers.serialize("json", [Review.objects.create(book=book, user=request.user, description=description, rating_value=value, created_at=dt.now()),])

			# calculating the new average rating and rating count for adding a new review
			currentTotalRating = book.ratings_count * book.average_rating
			newTotalRating = currentTotalRating + int(value)
			newRatingCount = book.ratings_count + 1
			newAverageRating = round(newTotalRating/newRatingCount, 1)
			book.ratings_count = newRatingCount
			book.average_rating = newAverageRating
			book.save()

			return HttpResponse(json.dumps({"status_code": 200, "new_review": new_review}), content_type="application/json")
			# need else statement if cannot create review.

	if request.method == "DELETE" and request.user.is_authenticated and not request.user.is_superuser:
		DELETE = QueryDict(request.body)
		functionality = DELETE.get("functionality")

		if functionality == "delete-review":
			if(Review.objects.filter(book__isbn_13=isbn_13, user=request.user.pk).exists()):
				this_review = Review.objects.get(book__isbn_13=isbn_13, user=request.user.pk)

				# calculating the new average rating and rating count for deleting an existing review
				currentTotalRating = book.ratings_count * book.average_rating
				newTotalRating = currentTotalRating - this_review.rating_value
				newRatingCount = book.ratings_count - 1
				newAverageRating = round(newTotalRating/newRatingCount, 1)
				book.ratings_count = newRatingCount
				book.average_rating = newAverageRating
				book.save()

				this_review.delete()
				return HttpResponse(json.dumps({"status_code": 200, "removed": True}), content_type="application/json")
			return HttpResponse(json.dumps({"status_code": 404, "removed": False}), content_type="application/json")		

	if request.method == "PUT" and request.user.is_authenticated and not request.user.is_superuser:
		PUT = QueryDict(request.body)
		functionality = PUT.get("functionality")
		user = User.objects.get(id=int(request.user.pk))

		if functionality == "favourites":
			favourite_Book = Book.objects.filter(favourites__id=user.pk)
			if not book in favourite_Book:
				user.favourites.add(book)
				return HttpResponse(json.dumps({"status_code": 204}), content_type="application/json")
			else:
				user.favourites.remove(book)
				return HttpResponse(json.dumps({"status_code": 204}), content_type="application/json")

		elif functionality == "have-read":
			have_read_Book = Book.objects.filter(haveread__id=user.pk)
			if not book in have_read_Book:
				user.haveread.add(book)
				return HttpResponse(json.dumps({"status_code": 204}), content_type="application/json")
			else:
				user.haveread.remove(book)
				return HttpResponse(json.dumps({"status_code": 204}), content_type="application/json")

		elif functionality == "to-read":
			toread_Book = Book.objects.filter(toread__id=user.pk)
			if not book in toread_Book:
				user.toread.add(book)
				return HttpResponse(json.dumps({"status_code": 204}), content_type="application/json")
			else:
				user.toread.remove(book)
				return HttpResponse(json.dumps({"status_code": 204}), content_type="application/json")

		elif functionality == "reading-now":
			reading_Book = Book.objects.filter(readingnow__id=user.pk)
			if not book in reading_Book:
				user.readingnow.add(book)
				return HttpResponse(json.dumps({"status_code": 204}), content_type="application/json")
			else:
				user.readingnow.remove(book)
				return HttpResponse(json.dumps({"status_code": 204}), content_type="application/json")

		elif functionality == "like-comment":
			this_review = Review.objects.get(id=int(PUT.get("review_id")))
			list_of_liked = Review.objects.filter(likes__id=user.pk)
			list_of_disliked = Review.objects.filter(dislikes__id=user.pk)
			if(this_review not in list_of_liked):
				user.likes.add(this_review)
			else:
				user.likes.remove(this_review)
			if(this_review in list_of_disliked):
				user.dislikes.remove(this_review)
			this_review = serializers.serialize("json", [this_review,])
			return HttpResponse(json.dumps({"status_code": 200, "this_review": this_review}), content_type="application/json")

		elif functionality == "dislike-comment":
			this_review = Review.objects.get(id=int(PUT.get("review_id")))
			list_of_liked = Review.objects.filter(likes__id=user.pk)
			list_of_disliked = Review.objects.filter(dislikes__id=user.pk)
			if(this_review not in list_of_disliked):
				user.dislikes.add(this_review)
			else:
				user.dislikes.remove(this_review)
			if(this_review in list_of_liked):
				user.likes.remove(this_review)
			this_review = serializers.serialize("json", [this_review,])
			return HttpResponse(json.dumps({"status_code": 200, "this_review": this_review}), content_type="application/json")
			

	elif request.method == "PUT" and not request.user.is_authenticated:
		response_data = {"status_code": 403, "message": "Please login to access this feature."}
		return HttpResponse(json.dumps(response_data), content_type="application/json")

	elif request.method == "PUT" and request.user.is_superuser:
		response_data = {"status_code": 403, "message": "You do not have the permission to access this feature."}

	context = {"book": book, "reviews": reviews}
	if request.user.is_authenticated and not request.user.is_superuser:
		context["in_favourite_Book"] = True if book in Book.objects.filter(favourites__id=request.user.pk) else False
		context["in_reading_Book"] = True if book in Book.objects.filter(readingnow__id=request.user.pk) else False
		context["in_to_read_Book"] = True if book in Book.objects.filter(toread__id=request.user.pk) else False
		context["in_have_read_Book"] = True if book in Book.objects.filter(haveread__id=request.user.pk) else False

	return render(request, "bookpage.html", context)

@login_required
@csrf_exempt
def usershelf(request):
	if 'history' not in request.session:
		request.session['history'] = []

	if request.method == "PUT":
		PUT = QueryDict(request.body)
		functionality = PUT.get("functionality")
		isbn_13 = PUT.get("isbn_13")
		user = User.objects.get(id=int(request.user.pk))
		book = Book.objects.get(isbn_13=isbn_13)

		if functionality == "remove-from-favourites":
			if book in Book.objects.filter(favourites__id=request.user.pk):
				user.favourites.remove(book)
				return HttpResponse(json.dumps({"status_code": 200, "removed": True}), content_type="application/json")
			return HttpResponse(json.dumps({"status_code": 200, "removed": False}), content_type="application/json")

		elif functionality == "remove-from-reading-now":
			if book in Book.objects.filter(readingnow__id=request.user.pk):
				user.readingnow.remove(book)
				return HttpResponse(json.dumps({"status_code": 200, "removed": True}), content_type="application/json")
			return HttpResponse(json.dumps({"status_code": 200, "removed": False}), content_type="application/json")

		elif functionality == "remove-from-to-read":
			if book in Book.objects.filter(toread__id=request.user.pk):
				user.toread.remove(book)
				return HttpResponse(json.dumps({"status_code": 200, "removed": True}), content_type="application/json")
			return HttpResponse(json.dumps({"status_code": 200, "removed": False}), content_type="application/json")

		elif functionality == "remove-from-have-read":
			if book in Book.objects.filter(haveread__id=request.user.pk):
				user.haveread.remove(book)
				return HttpResponse(json.dumps({"status_code": 200, "removed": True}), content_type="application/json")
			return HttpResponse(json.dumps({"status_code": 200, "removed": False}), content_type="application/json")

	context = {
		"favourite_book": Book.objects.filter(favourites__id=request.user.pk),
		"have_read_book": Book.objects.filter(haveread__id=request.user.pk),
		"to_read_book": Book.objects.filter(toread__id=request.user.pk),
		"reading_now_book": Book.objects.filter(readingnow__id=request.user.pk),
		"reviewed_book": Review.objects.filter(user=request.user.pk),
		"visited_book": [Book.objects.get(isbn_13=items) for items in request.session['history']]
	}
	return render(request, "usershelf.html", context)