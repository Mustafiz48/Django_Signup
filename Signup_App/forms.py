from django import forms
from django.contrib.auth.models import User


class Signup_form(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=264)
    last_name = forms.CharField(max_length=264)

    class Meta():
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class Password_reset_form(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())


class Email_form(forms.Form):
    email = forms.CharField(widget=forms.EmailInput())
