from .models import Book
import requests, json

def googleBooksAPIRequests(booksearch):
	response = requests.get("https://www.googleapis.com/books/v1/volumes?q="+booksearch)
	requestedBooks = []

	try:
		jsonResponse = response.json()["items"]

		for book in jsonResponse:
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
					publishedDate = book['volumeInfo']['publishedDate']
				else:
					publishedDate = "None"

				if('description' in book['volumeInfo']):
					description = book['volumeInfo']['description']
				else:
					description = "None"

				isbn13 = None
				isbn10 = None

				if(book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_10"):
					isbn10 = book['volumeInfo']['industryIdentifiers'][0]['identifier']
				elif(book['volumeInfo']['industryIdentifiers'][0]['type'] == "ISBN_13"):
					isbn13 = book['volumeInfo']['industryIdentifiers'][0]['identifier']

				if(book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_10"):
					isbn10 = book['volumeInfo']['industryIdentifiers'][1]['identifier']
				elif(book['volumeInfo']['industryIdentifiers'][1]['type'] == "ISBN_13"):
					isbn13 = book['volumeInfo']['industryIdentifiers'][1]['identifier']

				if('categories' in book['volumeInfo']):
					categories = book['volumeInfo']['categories']
					genre = [i.title().replace(",", " &").replace("  ", "") for i in categories]
					genre.sort()
					genre = ",".join(genre)
				else:
					genre = "None"

				if('averageRating' in book['volumeInfo']):
					averageRating = book['volumeInfo']['averageRating']
				else:
					averageRating = 0.0
				averageRating = round(averageRating,1)

				if('ratingsCount' in book['volumeInfo']):
					ratingsCount = book['volumeInfo']['ratingsCount']
				else:
					ratingsCount = 0

				if('thumbnail' in book['volumeInfo']['imageLinks']):
					thumbnail = book['volumeInfo']['imageLinks']['thumbnail']
				else:
					thumbnail = "None"

				if Book.objects.filter(isbn_13=isbn13).exists():
					requestedBooks.append(Book.objects.get(isbn_13=isbn13))
				else:
					print("new book")
					newBookObject = Book.objects.create(uid=uid,title=title,authors=authors,
						publisher=publisher,published_date=publishedDate,description=description,
						isbn_13=isbn13,isbn_10=isbn10,genre=genre,average_rating=averageRating,
						ratings_count=ratingsCount,thumbnail=thumbnail)
					requestedBooks.append(newBookObject)
	except:
		pass
		
	return requestedBooks