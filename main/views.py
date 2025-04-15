from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def book(request):
    return render(request, 'book.html')

def manage(request):
    return render(request, 'manage.html')

def register(request):
    return render(request, 'register.html')

def home(request):
    return render(request, 'index.html')

