from django.shortcuts import render

from django.http import HttpResponse
from .models import MainMenu

# Create your views here.


# def index(request):
#     return HttpResponse("Hello World")

# def index(request):
#   return render(request, 'base.html')

def index(request):
    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })