from django.shortcuts import render
from .models import Book
import requests

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
		print("ex")
		return render(request, "mainpage.html", {"bookresults":requested_books, "no_result":"Sorry, we could't find any results matching {}".format(booksearch)})
	return render(request, "mainpage.html",{})

def bookinstance(request):
	return render(request, "bookpage.html", {})