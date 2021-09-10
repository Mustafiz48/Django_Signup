from django.contrib.auth.models import User
from Signup_App import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from Signup_App.serializers import UserListSerializer, UserDetailSerializer
from Signup_App.forms import Signup_form,Password_reset_form,Email_form
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# for email verification
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .email_token_genaration import account_activation_token
from django.core.mail import send_mail, EmailMessage

# rest-frameworks
from rest_framework import mixins
from rest_framework import generics
from rest_framework.decorators import api_view


@login_required
@api_view(['GET'])
def home(request):
    if request.method == 'GET':
        user = request.user
        print(user)
        return render(request, 'Signup_App/home.html', {'user': request.user})


@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect('signin')


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):

    """
    get:
        provides user details
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer


@api_view(['GET', 'POST'])
def signup(request):

    # registred = False

    if request.method == "POST":
        user_data = Signup_form(data=request.POST)

        if user_data.is_valid():
            user = user_data.save()
            user.set_password(user.password)
            user.is_active = False
            user.save()

            # activation email sending part
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('Signup_App/email_template.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = user.email
            email = EmailMessage(mail_subject, message,
                                 to=[to_email])
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')

            # return render(request,'first_app/signup.html')

        else:
            print(user_data.errors)

    else:
        user_data = Signup_form()

    return render(request, 'Signup_App/signup.html',
                  {'user_data': user_data}
                  )

# Email activation

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')





def reset_password(request):

    # reset email sending part
    if request.method == "POST":
        email = Email_form(data=request.POST)
        User = get_user_model()


        if email.is_valid():
            mail = email.cleaned_data['email']


            user = User.objects.get(email=mail)
            current_site = get_current_site(request)
            mail_subject = 'Password Reset'
            message = render_to_string('Signup_App/password_reset_email_template.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = user.email
            email = EmailMessage(mail_subject, message,
                                    to=[to_email])
            email.send()
            return HttpResponse('Please check your email address to change Password')
        
        else:
            print(email.errors)
    else:
        user_data = Email_form()

    return render(request, 'Signup_App/email_form.html',
                  {'user_data': user_data}
                  )

    # return render(request,'first_app/signup.html')


#Password_reset_form
#Password Reset
def reset(request, uidb64, token):
    if request.method=='POST':

        User = get_user_model()
        
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):

            new_pass = Password_reset_form(data=request.POST)
            print("Haaa")
            print(new_pass)
            if new_pass.is_valid():
                passwrd = new_pass.cleaned_data['password']
                user.set_password(passwrd)
                user.save()

            return HttpResponse('Your Password Has been Changed!.')
        else:
            return HttpResponse('Activation link is invalid!')

    else:
        new_password = Password_reset_form()

    return render(request, 'Signup_App/password_reset.html',
                  {'new_password': new_password}
                  )


@api_view(['GET', 'POST'])
def signin(request):
    if(request.method == 'POST'):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        # print('in sign in' + user)
        if user:
            if user.is_active:
                login(request, user)
                print("Login successful")
                messages.success(request, "Logged in Successfully!")
                return HttpResponseRedirect('home')

            else:
                return HttpResponse("Acount not Active")
        else:
            print("Unauthorised Entry")
            return HttpResponse("Invalid login request! \n Please provide valid username and password or check if your email is activated")
    else:
        return render(request, 'Signup_App/signin.html')
