from django.urls import path
from . import views

urlpatterns = [
    path('instance/<str:tournament_instance_id>/<str:scrim_instance_id>/', views.scrim_detail, name='t3scrim-detail'),

    path('teamregistration/<str:tournament_instance_id>/<str:scrim_instance_id>/<str:confirmed_slots>/<str:total_slots>/', views.register_in_scrim_form, name='team-registration-in-t3scrim'),
    path("register-existing-team/<str:tournament_instance_id>/<str:scrim_instance_id>/", views.register_by_existing_team_in_scrim , name="register-existing-team-in-t3scrim"),

    path('team-confirm/<str:team_id>/<str:tournament_instance_id>/<str:scrim_instance_id>/', views.change_team_confirmation_status_in_t3scrim, name='team-confirm-in-t3scrim'),
    path('team-decline/<str:team_id>/<str:tournament_instance_id>/<str:scrim_instance_id>/', views.change_team_decline_status_in_scrim, name='team-declined-in-t3scrim'),
    path('send-id-pass/<str:tournament_instance_id>/<str:scrim_instance_id>/', views.send_id_pass_to_confirmed_teams_in_scrim, name="send-id-pass-in-t3scrim"),

    path('manage-crud-scrim-result/<str:tournament_instance_id>/<str:scrim_instance_id>/', views.manage_scrim_result, name="manage-t3scrim-result"),
    path('create-scrim-result/<str:scrim_instance_id>/', views.create_scrim_result, name='createt3ScrimResult'),
    path('update-scrim-result/<str:scrim_instance_id>/', views.update_scrim_result, name='updatet3ScrimResult'),
    path('delete-scrim-result/<str:scrim_instance_id>/', views.delete_scrim_result, name='deletet3ScrimResult'),

    path('send_scrim_result/<str:tournament_instance_id>/<str:scrim_instance_id>/', views.send_scrim_result, name="sendt3ScrimResult"),
]


