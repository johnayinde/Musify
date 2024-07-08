from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login_user, name='login'),
    path('logout', views.login_user, name='logout'),
    path('music/<str:pk>', views.music, name='music'),
    path('artist/<str:pk>', views.artist_profile, name='profile'),
    path('search', views.search, name='search'),
    
    
]
