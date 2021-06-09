from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tournaments', views.tournament, name='view-tournaments'),
    path('filter-tournament', views.filter_tournament, name="filter-tournament"),
    path('tournament/<str:pk>/', views.tournament_detail, name="tournament-detail"),
    path('create-tournament', views.create_tournament, name="create-tournament"),
    path("register-existing-team/<str:pk>/", views.register_by_existing_team , name="register-existing-team"),

    path('teamregistration/<str:pk>/<str:confirmed_slots>/<str:total_slots>/', views.register_in_tourna_form, name='team-registration'),

    path('manage-crud-tournament-result/<str:pk>/', views.manage_tourna_result, name="manage-tournament-result"),
    path('save-tourna-result/<str:pk>/', views.save_tourna_result, name='saveTournamentrResult'),
    path('update-tourna-result', views.update_tourna_result, name='updateTournamentrResult'),
    path('delete-tourna-result', views.delete_tourna_result, name='deleteTournamentrResult'),
    path('send_tourna_result/<str:pk>/', views.send_tourna_result, name='sendTournamentResult'),

    path('team-confirm/<str:pk>/<str:pk2>/', views.change_team_confirmation_status, name='team-confirm'),
    path('team-decline/<str:pk>/<str:pk2>/', views.change_team_decline_status, name='team-declined'),
    path('send-id-pass/<str:pk>/', views.send_id_password_to_registered_team, name="send-id-pass"),

    path('invite-tournament-organizer/<str:pk>/', views.invite_organizer, name="inviteorganizer"),
    path('accept-invite-tournament-organizer/<str:token_id>/<str:token>/<str:pk>/', views.accept_invite_organizer, name="accept-invite-organizer",),
]