from django.shortcuts import render, redirect
from .models import Book, Review
import requests, json
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict, HttpResponse
from django.contrib.auth.models import User

def mainpage(request):
	if request.method == "POST":
		booksearch = request.POST["booksearch"]
		response = requests.get("https://www.googleapis.com/books/v1/volumes?q="+booksearch)
		requested_books = []

		try:
			json_response = response.json()["items"]

			for book in json_response:
				if(len(book['volumeInfo']['industryIdentifiers'])==2):
					uid = book['id']
					title = book['volumeInfo']['title']

					if('authors' in  book['volumeInfo']):
						authors = book['volumeInfo']['authors']
						authors.sort()
						authors = ",".join(authors)
					else:
						authors = "None"

					if('publisher' in book['volumeInfo']):
						publisher = book['volumeInfo']['publisher']
					else:
						publisher = "None"

					if('publishedDate' in book['volumeInfo']):
						published_date = book['volumeInfo']['publishedDate']
					else:
						published_date = "None"

					if('description' in book['volumeInfo']):
						description = book['volumeInfo']['description']
					else:
						description = "None"

					isbn_13 = None
					isbn_10 = None

					if(book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_10"):
						isbn_10 = book['volumeInfo']['industryIdentifiers'][0]['identifier']
					elif(book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_13"):
						isbn_13 = book['volumeInfo']['industryIdentifiers'][0]['identifier']

					if(book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_10"):
						isbn_10 = book['volumeInfo']['industryIdentifiers'][1]['identifier']
					elif(book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_13"):
						isbn_13 = book['volumeInfo']['industryIdentifiers'][1]['identifier']

					if('categories' in book['volumeInfo']):
						categories = book['volumeInfo']['categories']
						genre = [i.title().replace(",", " &").replace("  ", "") for i in categories]
						genre.sort()
						genre = ",".join(genre)
					else:
						genre = "None"

					if('averageRating' in book['volumeInfo']):
						average_rating = book['volumeInfo']['averageRating']
					else:
						average_rating = 0.0
					average_rating = round(average_rating,1)

					if('ratingsCount' in book['volumeInfo']):
						ratings_count = book['volumeInfo']['ratingsCount']
					else:
						ratings_count = 0

					if('thumbnail' in book['volumeInfo']['imageLinks']):
						thumbnail = book['volumeInfo']['imageLinks']['thumbnail']
					else:
						thumbnail = "None"

					if Book.objects.filter(isbn_13=isbn_13).exists():
						requested_books.append(Book.objects.get(isbn_13=isbn_13))
					else:
						print("new book")
						new_book = Book.objects.create(uid=uid,title=title,authors=authors,
							publisher=publisher,published_date=published_date,description=description,
							isbn_13=isbn_13,isbn_10=isbn_10,genre=genre,average_rating=average_rating,
							ratings_count=ratings_count,thumbnail=thumbnail)
						requested_books.append(new_book)
		except:
			pass
		return render(request, "mainpage.html", {"bookresults":requested_books, "no_result":"Sorry, we could't find any results matching {}".format(booksearch)})
	return render(request, "mainpage.html",{})

@csrf_exempt
def bookinstance(request,isbn_13):
	try:
		book = Book.objects.get(isbn_13=isbn_13)
		reviews = Review.objects.filter(book=book)
	except Book.DoesNotExist:
		return redirect("book:mainpage")

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

def usershelf(request):
	context = {}
	return render(request, "usershelf.html", context)