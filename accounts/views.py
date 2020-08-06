from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from book.models import Book, Review
from django.core.cache import cache

def login(request):
	if request.method == "POST":

		if cache.get('loginAttempts') != None and cache.get('loginAttempts') > 3:
			cache.set('loginAttempts', cache.get('loginAttempts'), 600)
			context = {"message": 'Your account has been temporarily locked out because of too many failed login attempts.'}
			return render(request,"login.html", context)

		username = request.POST['username'].replace(" ", "")
		password = request.POST['password']

		if not request.POST.get('remember_me', None):
			request.session.set_expiry(0)

		user = authenticate(username=username, password=password)
		if user:
			auth_login(request, user)
			return redirect('book:mainpage')
		else:
			if cache.get('loginAttempts') == None:
				cache.set('loginAttempts', 1)
			else:
				cache.incr('loginAttempts', 1)

			context = {"message": "Username or Password did not match!", "username": username}
			return render(request,"login.html", context)
	return render(request,"login.html", {})

def register(request):
	if request.method == "POST":
		email = request.POST['email']
		password = request.POST['password']
		password_2 = request.POST['confirm_password'];
		firstname = request.POST['first_name']
		lastname = request.POST['last_name']		

		if User.objects.filter(username=email).exists():
			context = {
				"message": "An account already exists for this email address!",
				"email": email,
				"firstname": firstname,
				"lastname": lastname
			}
			return render(request,"registration.html", context)
		else:
			context = {}
			if(password!=password_2):
				context = {
					"message": "Your passwords do not match!",
					"email": email,
					"firstname": firstname,
					"lastname": lastname
				}
				return render(request,"registration.html", context)

			if(len(password)<8 or any(letter.isalpha() for letter in password)==False or any(capital.isupper() for capital in password)==False or any(number.isdigit() for number in password)==False):
				context = {
					"message": "Your password is not strong enough.",
					"email": email,
					"firstname": firstname,
					"lastname": lastname
				}
				return render(request,"registration.html", context)

			user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)
			user.is_active = False
			user.save()

			current_site = get_current_site(request)
			email_subject = "Activate your BookWire Account"
			message = render_to_string('activate.html',
				{"user":user,
				"domain":current_site.domain,
				"uid": urlsafe_base64_encode(force_bytes(user.pk)),
				"token": generate_token.make_token(user)
				})

			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
			email_message.send()

			context = {"activate": "We've sent you an activation link. Please check your email."}
			return render(request,"registration.html", context)
	return render(request,"registration.html", {})

def logout(request):
	auth_logout(request)
	return redirect('accounts:login')

@login_required
def profile(request):
	if request.method == "POST":
		firstname = request.POST['first_name'].strip()
		lastname = request.POST['last_name'].strip()

		password = request.POST['password']
		password_2 = request.POST['password2'];

		user = User.objects.get(pk=(request.user.id))
		user.first_name = firstname
		user.last_name = lastname

		if(password and password_2):
			if(password!=password_2):
				context = {"message": "Your passwords do not match!"}
				return render(request,"profile.html", context)

			if(len(password)<8 or any(letter.isalpha() for letter in password)==False or any(capital.isupper() for capital in password)==False or any(number.isdigit() for number in password)==False):
				context = {"message": "Your password is not strong enough."}
				return render(request,"profile.html", context)
			
			user.set_password(password)
		user.save()

		if(password and password_2):
			user = authenticate(username=user.username, password=password)
			if user:
				auth_login(request, user)
			else:
				return redirect("accounts:login")

		context = {
			"success": "Your details are updated.",
			"first_name": firstname,
			"last_name": lastname,
		}
		return render(request,"profile.html", context)

	context = {
		"first_name": request.user.first_name,
		"last_name": request.user.last_name,
		"email": request.user.email,
		"likes": Review.objects.filter(likes__id=request.user.pk).count(),
		"dislikes": Review.objects.filter(dislikes__id=request.user.pk).count(),
		"comments": Review.objects.filter(user=request.user.pk).count(),
		"books_read": Book.objects.filter(haveread__id=request.user.pk).count()
	}
	return render(request,"profile.html", context)


def activateaccount(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except Exception as e:
		user = None

	if user is not None and generate_token.check_token(user, token):
		user.is_active = True
		user.save()
		messages.add_message(request,messages.SUCCESS,"Account activated successfully")
		return redirect('accounts:login')
	return render(request, "activate_failed.html",status=401)

def password_request(request):
	if request.method == "POST":
		email = request.POST["email"]

		try:
			user = User.objects.get(username=email)
		except User.DoesNotExist:
			user = None

		if user is not None:
			username = user.first_name

			current_site = get_current_site(request)
			domain = current_site.domain

			uid = urlsafe_base64_encode(force_bytes(user.pk))
			token = generate_token.make_token(user)

			email_subject = "Request to change BookWire Password"
			message = """Hi {},\n\n
			You have recently request to change your account password.
			Please click this link below to change your account password. \n\n
			http://{}/accounts/password_change/{}/{}""".format(username, domain, uid, token)

			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
			email_message.send()

		return render(request, "password_request.html",{"message": "Check your email for a password change link."})
	return render(request, "password_request.html",{})

def password_change(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except Exception as e:
		user = None

	if request.method == "POST" and user is not None and generate_token.check_token(user, token):
		password_1 = request.POST["password_1"]
		password_2 = request.POST["password_2"]

		if password_1 and password_2:
			if(password_1!=password_2):
				context = {"message": "Your passwords do not match!"}
				return render(request,"password_reset_form.html", context)

			if(len(password_1)<8 or any(letter.isalpha() for letter in password_1)==False or any(capital.isupper() for capital in password_1)==False or any(number.isdigit() for number in password_1)==False):
				context = {"message": "Your password is not strong enough."}
				return render(request,"password_reset_form.html", context)

			user.set_password(password_1)
			user.save()
			return redirect("accounts:login")

	if user is not None and generate_token.check_token(user, token):
		return render(request, "password_reset_form.html",{})
	else:
		return render(request, "activate_failed.html",status=401)
