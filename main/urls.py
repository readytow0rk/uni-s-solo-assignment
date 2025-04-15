from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book, name='book'),
    path('manage/', views.manage, name='manage'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    
    
    
]

