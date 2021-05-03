from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth import authenticate
from accounts.forms import RegistrationForm
from accounts.forms import LoginForm
from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import redirect

def login(request):

	if request.method == "POST":
		uniqueVisitorId = request.POST['uniqueVisitorId']

		if cache.get(uniqueVisitorId) != None and cache.get(uniqueVisitorId) > 3:
			print("FAIL")
			cache.set(uniqueVisitorId, cache.get(uniqueVisitorId), 600)
			messages.add_message(
				request,
				messages.INFO,
				"Your account has been temporarily locked out because of too many failed login attempts."
			)
			return redirect('accounts:login')

		form = LoginForm(request, request.POST)

		if form.is_valid():
			cache.delete(uniqueVisitorId)
			return redirect('book:mainpage')

		if cache.get(uniqueVisitorId) == None:
			cache.set(uniqueVisitorId, 1)
		else:
			cache.incr(uniqueVisitorId, 1)

	else:
		form = LoginForm()
	
	context = {
		"form": form
	}
	return render(request, 'accounts/login.html', context)

def register(request):
	if request.method == "POST":
		form = RegistrationForm(request.POST)
	else:
		form = RegistrationForm()
	context = {
		"form": form
	}
	return render(request, 'accounts/registration.html', context)