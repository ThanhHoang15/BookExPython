from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Book


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'web', 'price', 'picture']


class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Username", help_text="")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, help_text="")
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, help_text="")

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]