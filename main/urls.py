from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book, name='book'),
    path('manage/', views.manage, name='manage'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('reschedule/<int:appointment_id>/', views.reschedule, name='reschedule'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('checkin/<int:appointment_id>/', views.check_in, name='check_in'),
    
]

