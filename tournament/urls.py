from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tournaments', views.tournament, name='view-tournaments'),
    path('filter-tournament', views.filter_tournament, name="filter-tournament"),
    path('tournament/<slug:tournament_slug>/', views.tournament_detail, name="tournament-detail"),
    path('create-tournament', views.create_tournament, name="create-tournament"),
    path("register-existing-team/<slug:tournament_slug>/", views.register_by_existing_team , name="register-existing-team"),

    path('teamregistration/<slug:tournament_slug>/<str:confirmed_slots>/<str:total_slots>/', views.register_in_tourna_form, name='team-registration'),

    path('manage-crud-tournament-result/<slug:tournament_slug>/', views.manage_tourna_result, name="manage-tournament-result"),
    path('save-tourna-result/<slug:tournament_slug>/', views.save_tourna_result, name='saveTournamentrResult'),
    path('update-tourna-result', views.update_tourna_result, name='updateTournamentrResult'),
    path('delete-tourna-result', views.delete_tourna_result, name='deleteTournamentrResult'),
    path('send_tourna_result/<slug:tournament_slug>/', views.send_tourna_result, name='sendTournamentResult'),

    path('team-confirm/<slug:tournament_slug>/<str:pk2>/', views.change_team_confirmation_status, name='team-confirm'),
    path('team-decline/<slug:tournament_slug>/<str:pk2>/', views.change_team_decline_status, name='team-declined'),
    path('send-id-pass/<slug:tournament_slug>/', views.send_id_password_to_registered_team, name="send-id-pass"),

    path('invite-tournament-organizer/<slug:tournament_slug>/', views.invite_organizer, name="inviteorganizer"),
    path('accept-invite-tournament-organizer/<str:token_id>/<str:token>/<slug:tournament_slug>/', views.accept_invite_organizer, name="accept-invite-organizer",),
]