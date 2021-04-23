from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth import authenticate

def login(request):
	
	if request.method == "POST":
		uniqueVisitorId = request.POST['uniqueVisitorId']

		if cache.get(uniqueVisitorId) != None and cache.get(uniqueVisitorId) > 3:
			cache.set(uniqueVisitorId, cache.get(uniqueVisitorId), 600)
			context = {
				"message": 'Your account has been temporarily locked out because of too many failed login attempts.'
			}
			return render(request, 'accounts/login.html', context)

		username = request.POST['username'].replace(" ", "")
		password = request.POST['password']

		if not request.POST.get('rememberMe', None):
			request.session.set_expiry(0)

		user = authenticate(username=username, password=password)
		if user:
			auth_login(request, user)
			cache.delete(uniqueVisitorId)
			return redirect('book:mainpage')

		if cache.get(uniqueVisitorId) == None:
			cache.set(uniqueVisitorId, 1)
		else:
			cache.incr(uniqueVisitorId, 1)

		context = {
			"message": "Username or Password did not match!",
			"username": username
		}
		return render(request, 'accounts/login.html', context)
	return render(request, 'accounts/login.html')

def register(request):
	return render(request, 'accounts/registration.html')