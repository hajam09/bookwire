from django.shortcuts import render
from book.utils import googleBooksAPIRequests
from book.models import Book
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def mainpage(request):
	if request.method == "POST":

		bookSearchQuery = request.POST["booksearch"]
		requestedBooks = googleBooksAPIRequests(bookSearchQuery)

		if len(requestedBooks) > 0:
			context = {
				"bookResults": requestedBooks,
				"bookSearchQuery": bookSearchQuery
			}
			return render(request, "book/mainpage.html", context)
		else:
			context = {
				"noResult": "Sorry, we could't find any results matching ' {} '".format(bookSearchQuery)
			}
		return render(request, "book/mainpage.html", context)

	context = {
		"recentlyAddedBooks": recentlyAddedBooks(),
		"booksBasedOnRatings": booksBasedOnRatings(),
		"favouriteBooksFromSimilarUsers": favouriteBooksFromSimilarUsers(request),
	}
	
	return render(request, "book/mainpage.html", context)

def recentlyAddedBooks():
	allBooks = Book.objects.all()
	top20Books = allBooks[len(allBooks)-20:] if allBooks.count()>20 else allBooks[:]
	
	recentlyAddedBooks = [
		{
			"isbn13": i.isbn13,
			"title": i.unCleanData['title'],
			"thumbnail": i.unCleanData['thumbnail']
		}	
		for i in top20Books
	]
	return recentlyAddedBooks

def booksBasedOnRatings():
	if Book.objects.count() == 0:
		return []

	allBooks = Book.objects.all().prefetch_related('isFavourite')
	dictBooks = {}
	for i in allBooks:

		dictBooks[i.unCleanData["isbn13"]] = {
			"isbn13": i.unCleanData["isbn13"],
			"title": i.unCleanData['title'],
			"thumbnail": i.unCleanData['thumbnail']
		}

		i.cleanData.pop("description")
		i.cleanData.pop("isbn10")
		i.cleanData.pop("thumbnail")
		i.cleanData.pop("uid")
		i.cleanData["favouritesCount"] = i.isFavourite.count()

	allBooksCleaned = [i.cleanData for i in allBooks]

	# Implementing weighted average for each book's average rating // Non - personalized

	df = pd.DataFrame(allBooksCleaned)

	v = df['ratingsCount']
	R = df['averageRating']
	C = df['averageRating'].mean()
	m = df['ratingsCount'].quantile(0.70)

	df['weightedAverage'] = ((R*v) + (C*m))/(v+m)

	# This is for recommending books to the users based on scaled weighting (50%) and favouritesCount (50%).
	scaling = MinMaxScaler()
	bookScaled = scaling.fit_transform(df[['weightedAverage', 'favouritesCount']])
	bookNormalized = pd.DataFrame(bookScaled, columns=['weightedAverage', 'favouritesCount'])

	df[['normalizedWeightAverage','normalizedPopularity']] = bookNormalized
	df['score'] = df['normalizedWeightAverage'] * 0.5 + df['normalizedPopularity'] * 0.5
	booksScoredFromDf = df.sort_values(['score'], ascending=False)
	finalResult = list(booksScoredFromDf[['isbn13']].head(15)['isbn13'])

	return [ dictBooks[isbn] for isbn in finalResult ]

def favouriteBooksFromSimilarUsers(request):
	if not request.user.is_authenticated or not request.user.is_superuser:
		return []
	return []