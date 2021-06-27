from django.utils import timezone
from scrims.models import EnrollmentInScrim, EnrollmentTeamInScrim, ScrimsAddOnTournament
from django.db.models.query_utils import Q
from django.http import request
from tournament.models import EnrollmentInTournament, EnrollmentTeam, Teams, TopWinners, TournaRegistration, TournamentOrganizer
from django import template
from datetime import timedelta


register = template.Library()

@register.filter('have_tournament_owner_permission')
def have_tournament_owner_permission(user, pk):
    tournament = TournaRegistration.objects.get(id=pk)

    try:
        status = (user == tournament.admin or TournamentOrganizer.objects.filter(tournament=tournament).filter(helper=user).exists())
        return status
    except:
        return False


@register.filter('is_slots_left')
def is_slots_left(total_slots, confirmed_slots):
    if len(confirmed_slots) >= int(total_slots):
        return False
    else:
        return True


@register.filter('user_already_registered')
def user_already_registered(user, pk):
    tournament = TournaRegistration.objects.get(id=pk)

    try:
        enrolled_teams = EnrollmentTeam.objects.select_related('tournament') \
                    .filter(tournament=EnrollmentInTournament.objects.get(tournament=tournament))
    except:
        enrolled_teams = []
        
    
    for i in enrolled_teams:
        x = EnrollmentTeam.objects.get(id=i.id)
        team = Teams.objects.get(id = x.enrolled_teams.id)
        if team.team_owner == user:
            return True
        else:
            return False


@register.filter('is_winner')
def is_winner(user_id, pk):
    tournament = TournaRegistration.objects.get(id=pk)

    result = TopWinners.objects.filter(tournament=tournament, team_owner_id=user_id).order_by('-id')[0:3]
    if result:
        return True
    else:
        return False

@register.filter('have_discord')
def have_discord(server_id):
    if len(str(server_id)) > 15:
        return True
    else:
        return False

@register.filter('have_youtube')
def have_youtube(youtube_url):
    if len(str(youtube_url)) > 10:
        return True
    else:
        return False

@register.filter('next_number')
def next_number(num):
    return num + 1


@register.filter('user_already_registered_in_scrim')
def user_already_registered_in_scrim(user, scrim_instance_id):
    scrim_instance = ScrimsAddOnTournament.objects.get(id=scrim_instance_id)
    try:
        enrolled_teams = EnrollmentTeamInScrim.objects.select_related('scrim_instance') \
                    .filter(scrim_instance=EnrollmentInScrim.objects.get(scrim_instance=scrim_instance))
    except:
        enrolled_teams = []

    for i in enrolled_teams:
        x = EnrollmentTeamInScrim.objects.get(id=i.id)
        team = Teams.objects.get(id = x.enrolled_teams.id)
        if team.team_owner == user:
            return True
        else:
            return False

@register.filter("active_before_24_hour")
def active_before_24_hour(start_time):
    today = timezone.now()
    before_one_day = start_time - timedelta(days=1)
    if today >= before_one_day:
        return True
    else:
        return False

@register.filter("is_game_type_scrims")
def is_game_type_scrims(game_type: str):
    if game_type == 'T3 Scrims':
        return True
    else:
        return False