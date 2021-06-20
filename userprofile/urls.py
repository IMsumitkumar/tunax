from django.urls import path
from . import views

urlpatterns = [
    path('organized-tournaments/', views.user_profile, name="user-profile"),
    path('my-tournaments/', views.my_tournaments, name="my-tournaments"),
    path('certificate/<int:tournament_id>/', views.create_certificate, name="create-certificate"),
]