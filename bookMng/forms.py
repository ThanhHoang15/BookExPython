from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Book, BookComment, BookRating


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'web', 'price', 'picture']


class CommentForm(ModelForm):
    class Meta:
        model = BookComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your comment here...'
            })
        }


class RatingForm(ModelForm):
    value = forms.ChoiceField(
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
        widget=forms.Select()
    )

    class Meta:
        model = BookRating
        fields = ['value']


class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Username", help_text="")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, help_text="")
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, help_text="")

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]