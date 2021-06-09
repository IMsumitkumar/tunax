from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_profile, name="user-profile"),
    path('certificate/<int:tournament_id>/', views.create_certificate, name="create-certificate"),
]