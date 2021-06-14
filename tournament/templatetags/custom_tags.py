from django.db.models.query_utils import Q
from django.http import request
from tournament.models import EnrollmentInTournament, EnrollmentTeam, Teams, TopWinners, TournaRegistration, TournamentOrganizer
from django import template

register = template.Library()

@register.filter('have_tournament_owner_permission')
def have_tournament_owner_permission(user, pk):
    tournament = TournaRegistration.objects.get(id=pk)

    try:
        status = (user == tournament.admin or TournamentOrganizer.objects.exclude(pk=pk).filter(helper=user).exists())
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


