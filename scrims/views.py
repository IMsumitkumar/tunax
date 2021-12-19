from django.conf import settings
from django.utils.html import strip_tags
from tournament.tasks import send_multi_email_task, send_single_email_task
from tournament.views import tournament
from scrims.decorators import allowed_only_tournament_owner
from django.db.models.fields import EmailField
from django.urls.resolvers import LocaleRegexDescriptor
import scrims
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.template.loader import get_template, render_to_string
from .models import (EnrollmentInScrim, EnrollmentTeamInScrim,
                     ScrimsAddOnTournament, ScrimWinnerResult, TopWinnersInScrim)
from tournament.models import TeamMember, Teams, TournaRegistration
from django.shortcuts import redirect, render
from django.utils import timezone


def scrim_detail(request, tournament_slug, scrim_slug):
    today = timezone.now()
    tournament = TournaRegistration.objects.get(slug=tournament_slug)
    scrimst3_tourna = ScrimsAddOnTournament.objects.filter(tournament = tournament)
    scrim_instance = ScrimsAddOnTournament.objects.get(slug = scrim_slug)
    
    try:
        enrolled_teams = EnrollmentTeamInScrim.objects.select_related('scrim_instance') \
                    .filter(scrim_instance=EnrollmentInScrim.objects.get(scrim_instance=scrim_instance))
    except:
        enrolled_teams = []

    try:
        # teams of the current logged in user so that user can use the existing team to register
        # distinct -> no duplication of teams 
        # distict -> only works with postgresql database
        active_user_teams = Teams.objects.filter(team_owner=request.user) \
                        .distinct('team_name')
    except:
        active_user_teams = []

    pending_teams = []
    confirmed_teams = []
    decline_teams = []
    for i in enrolled_teams:
        x = EnrollmentTeamInScrim.objects.get(id=i.id)
        team = Teams.objects.get(id = x.enrolled_teams.id)

        if team.is_confirmed == 'CONFIRMED':
            confirmed_teams.append(team)
        elif team.is_confirmed == 'PENDING':
            pending_teams.append(team)
        else:
            decline_teams.append(team)


    try:
        # tournament prize sectiion contains top 3 players that will show in the prize section
        teams = ScrimWinnerResult.objects.order_by('-total_points') \
                                .filter(target_scrim=scrim_instance)
    except:
        teams = []

    context = {
        'tournament': tournament,
        'scrim_instance': scrim_instance,

        'today': today,
        'enrolled_teams': enrolled_teams,
        'pending_teams': pending_teams,
        'confirmed_teams': confirmed_teams,
        'teams': teams,
        'winners': teams[0:3],
        'active_user_teams': active_user_teams,
        'scrimst3_tourna': scrimst3_tourna  
    }

    print("tournament", tournament.id)
    print("scrim_instance", scrim_instance.id)
    print("enrolled_teams", enrolled_teams)
    print("active_user_teams", active_user_teams)



    return render(request, 'scrims/tournament-details.html', context=context)

@login_required(login_url='login')
def register_in_scrim_form(request, tournament_slug, scrim_slug, confirmed_slots, total_slots):
    if request.method == 'POST':
        if int(confirmed_slots) >= int(total_slots):
            return JsonResponse({"status": False, "response": "You can not register in this tournament because slots are full."})
        else:
            scrim_instance = ScrimsAddOnTournament.objects.get(slug=scrim_slug)
            team_name = request.POST.get('team_name')
            whatsapp_number = request.POST.get('whatsapp_number') if isinstance(request.POST.get('whatsapp_number'), int) \
                                                                     else None
            team_email = request.POST.get('team_email')

            playername = request.POST.getlist('playername')
            discordtag = request.POST.getlist('discordtag')
            teamrole = request.POST.getlist('teamrole')

            if 'teamavatar' in request.FILES:
                team_avatar = request.FILES['teamavatar']
                
                team_obj = Teams.objects.create(team_owner=request.user, team_pic=team_avatar, team_name=team_name, team_email=team_email,
                                        team_whstapp_no = whatsapp_number)
            else:
                team_obj = Teams.objects.create(team_owner=request.user, team_name=team_name, team_email=team_email,
                                        team_whstapp_no = whatsapp_number)

            lst = [playername, discordtag, teamrole]

            for i in range(len(playername)):
                team = [x[i] for x in lst]
                TeamMember.objects.create(team=team_obj, team_member=team[0], 
                    discord_tag=team[1], team_role=team[2])

            if EnrollmentInScrim.objects.filter(scrim_instance=scrim_instance).exists():
                EnrollmentTeamInScrim.objects.create(scrim_instance=EnrollmentInScrim.objects.filter(scrim_instance=scrim_instance)[0],
                                            enrolled_teams=team_obj)
            else:
                EnrollmentTeamInScrim.objects.create(scrim_instance=EnrollmentInScrim.objects.create(scrim_instance=scrim_instance),
                                            enrolled_teams=team_obj)            

            messages.success(request, f"{team_obj.team_name} registered in {scrim_instance.tournament_name} day scrim")
            return redirect(f"/tournament/scrims/instance/{tournament_slug}/{scrim_slug}/")
    return redirect(f"/tournament/scrims/instance/{tournament_slug}/{scrim_slug}/")

@login_required(login_url='login')
def register_by_existing_team_in_scrim(request, tournament_slug, scrim_slug):
    scrim_instance = ScrimsAddOnTournament.objects.get(slug=scrim_slug)
    if request.method == 'POST':
        team_id = request.POST.get("user_team_id")
        team = Teams.objects.get(id=team_id)
        new_team = Teams.objects.create(team_owner=request.user, team_pic=team.team_pic, team_name=team.team_name,
            team_email=team.team_email, team_whstapp_no=team.team_whstapp_no)
    
        for member in team.get_team_member_list():
            TeamMember.objects.create(team_id=new_team.id, team_member=member.team_member,
                discord_tag=member.discord_tag, team_role=member.team_role)
        
        if EnrollmentInScrim.objects.filter(scrim_instance=scrim_instance).exists():
                EnrollmentTeamInScrim.objects.create(scrim_instance=EnrollmentInScrim.objects.filter(scrim_instance=scrim_instance)[0],
                                            enrolled_teams=new_team)
        else:
            EnrollmentTeamInScrim.objects.create(scrim_instance=EnrollmentInScrim.objects.create(scrim_instance=scrim_instance),
                                        enrolled_teams=new_team)
        
        messages.success(request, f"Your Team {team.team_name} Registered successfully")
        return redirect(f"/tournament/scrims/instance/{tournament_slug}/{scrim_slug}/")
    return redirect(f"/tournament/scrims/instance/{tournament_slug}/{scrim_slug}/")


@login_required(login_url='login')
@allowed_only_tournament_owner
def change_team_confirmation_status_in_t3scrim(request, team_id, tournament_slug, scrim_slug):
    team = Teams.objects.get(id=team_id)
    team.is_confirmed = 'CONFIRMED'
    team.save()

    tournament_instance = TournaRegistration.objects.get(slug=tournament_slug)
    scrim_instance = ScrimsAddOnTournament.objects.get(slug=scrim_slug)

    email_data_dict = {
        'team_name': team.team_name,
        'team_email': team.team_email,
    }   

    content_data_dict = {
        'team_name': team.team_name,
        "tournament_name": scrim_instance.tournament_name,
        "tournament_banner": tournament_instance.banner.url,
        "start_time": scrim_instance.start_at,
        "end_time": scrim_instance.end_at,
        "team_type": tournament_instance.team_type,
    }

    # after confirmation, a confitmation email will be sent to related team
    email_body = f"Your Slot in {scrim_instance.tournament_name} has been Confirmed"
    email_content = get_template("emails/team_confirmation_email.html").render(content_data_dict)
    send_single_email_task.delay(email_data_dict, email_body, email_content)


    return redirect(f"/tournament/scrims/instance/{tournament_slug}/{scrim_slug}/")


@login_required(login_url='login')
@allowed_only_tournament_owner
def change_team_decline_status_in_scrim(request, team_id, tournament_slug, scrim_slug):
    team = Teams.objects.get(id=team_id)
    team.is_confirmed = 'DECLINED'
    team.save()

    # tournament = TournaRegistration.objects.get(slug=tournament_slug)
    scrim_instance = ScrimsAddOnTournament.objects.get(slug=scrim_slug)

    email_data_dict = {
        'team_name': team.team_name,
        'team_email': team.team_email,
    }

    content_data_dict = {
        'team_name': team.team_name,
        "tournament_name": scrim_instance.tournament_name,
    }

    email_body = f"Your Slot in {scrim_instance.tournament_name} has been Declined"
    email_content = get_template("emails/team_decline_email.html").render(content_data_dict)

    send_single_email_task.delay(email_data_dict, email_body, email_content)

    return redirect(f"/tournament/scrims/instance/{tournament_slug}/{scrim_slug}/")


@login_required(login_url='login')
@allowed_only_tournament_owner
def send_id_pass_to_confirmed_teams_in_scrim(request, tournament_slug, scrim_slug):
    scrim_instance = ScrimsAddOnTournament.objects.get(slug=scrim_slug)
    tournament_instance = TournaRegistration.objects.get(slug=tournament_slug)

    try:
        enrolled_teams = EnrollmentTeamInScrim.objects.select_related('scrim_instance') \
                    .filter(scrim_instance=EnrollmentInScrim.objects.get(scrim_instance=scrim_instance))
    except:
        enrolled_teams = []

    if request.method == 'POST':
        tourna_id = request.POST.get("tournament_id")
        tourna_pass = request.POST.get("tournament_password")

        emails = []
        for i in enrolled_teams:
            x = EnrollmentTeamInScrim.objects.get(id=i.id)
            team = Teams.objects.get(id = x.enrolled_teams.id)
            if team.is_confirmed == 'CONFIRMED':
                emails.append(team.team_email)
            else:
                continue

        email_data_dict = {
            'emails': emails,
        }

        content_data_dict = {
            'tournament_id': tourna_id,
            'tournament_pass': tourna_pass,
            'tournament_name': scrim_instance.tournament_name,
            'date': scrim_instance.start_at,
            'time': scrim_instance.start_at,
            'start_time': scrim_instance.start_at, 
            'banner': tournament_instance.banner.url,
            'team_type': tournament_instance.team_type,
        }

        # decliaton email will be sent to the related user
        email_body = f'ID PASS for {scrim_instance.tournament_name}'
        email_content = get_template("emails/tournament_idpass_email.html").render(content_data_dict)
        
        # sending emails using celery
        send_multi_email_task.delay(email_data_dict, email_body, email_content)

        return redirect(f"/tournament/scrims/instance/{tournament_slug}/{scrim_slug}/")
    else:
        return redirect(f"/tournament/scrims/instance/{tournament_slug}/{scrim_slug}/")


@login_required(login_url='login')
@allowed_only_tournament_owner
def manage_scrim_result(request, tournament_slug, scrim_slug):
    tournament = TournaRegistration.objects.get(slug=tournament_slug)
    scrim_instance = ScrimsAddOnTournament.objects.get(slug=scrim_slug)
    try:
        enrolled_teams = EnrollmentTeamInScrim.objects.select_related('scrim_instance') \
                    .filter(scrim_instance=EnrollmentInScrim.objects.get(scrim_instance=scrim_instance))
    except:
        enrolled_teams = []

    pending_teams = []
    confirmed_teams = []
    decline_teams = []

    for i in enrolled_teams:
        x = EnrollmentTeamInScrim.objects.get(id=i.id)
        team = Teams.objects.get(id = x.enrolled_teams.id)

        if team.is_confirmed == 'CONFIRMED':
            confirmed_teams.append(team)
        elif team.is_confirmed == 'PENDING':
            pending_teams.append(team)
        else:
            decline_teams.append(team)
        
    try:
        teams = ScrimWinnerResult.objects.order_by('-total_points').filter(target_scrim=scrim_instance)
    except:
        teams = []

    context = {
        'tournament': tournament,
        'scrim_instance': scrim_instance,
        'enrolled_teams': enrolled_teams,
        'pending_teams': pending_teams,
        'confirmed_teams': confirmed_teams,
        'declined_teams': decline_teams,
        'teams': teams,
    }

    return render(request, 'scrims/crud-tournament-result.html', context = context)


@login_required(login_url='login')
@allowed_only_tournament_owner
def create_scrim_result(request, scrim_slug):
    scrim_instance = ScrimsAddOnTournament.objects.get(slug=scrim_slug)
    if request.method == 'POST':
        try:
            general_team_id = request.POST.get('general_teamid')
            team_id = request.POST.get('teamid')
            teamkill = request.POST.get('teamkill')
            teamplace = request.POST.get('teamplace')

            if team_id == '':
                team_result = ScrimWinnerResult(
                    target_scrim=scrim_instance,
                    teamid = general_team_id,
                    killspts=teamkill,
                    placepts=teamplace
                )
            else:
                team_result = ScrimWinnerResult(
                    id = team_id,
                    target_scrim=scrim_instance,
                    teamid = general_team_id,
                    killspts=teamkill,
                    placepts=teamplace
                )
            team_result.save()

            try:
                teams = list(ScrimWinnerResult.objects.filter(target_scrim=scrim_instance).values_list())
            except:
                teams = []

            return JsonResponse({"status": "Save", "response_data": teams})
        except:
            messages.error(request, "Data can not be updated!")
            return JsonResponse({"status": 0})
    else:
        return JsonResponse({"status": 0})
        

@login_required(login_url='login')
@allowed_only_tournament_owner
def update_scrim_result(request, scrim_slug):
    if request.method == 'POST':
        team_id = request.POST.get('sid')

        team = ScrimWinnerResult.objects.get(pk=team_id)
        team_data = {"id": team.id, "teamname": team.teamname,
                     "killspts": team.killspts, "placepts":team.placepts}

        return JsonResponse(team_data)
    else:
        return JsonResponse({'status': 0})

@login_required(login_url='login')
@allowed_only_tournament_owner
def delete_scrim_result(request, scrim_slug):
    if request.method == 'POST':
        team_id = request.POST.get('sid')

        ScrimWinnerResult.objects.get(pk=team_id).delete()

        return JsonResponse({'status': 1})
    else:
        return JsonResponse({'status': 0})


@login_required(login_url='login')
@allowed_only_tournament_owner
def send_scrim_result(request, tournament_slug, scrim_slug):
    scrim_instance = ScrimsAddOnTournament.objects.get(slug=scrim_slug)
    tournament_instance = TournaRegistration.objects.get(slug=tournament_slug)

    try:
        teams = ScrimWinnerResult.objects.order_by('-total_points').filter(target_scrim=scrim_instance)
        team_emails = []
        for i in teams:
            team_emails.append(i.email)
    except:
        team_emails = []

    if len(teams) >=3:
        for i in teams[0:3]:
            team = Teams.objects.get(pk=int(21))
            TopWinnersInScrim.objects.create(team_owner_id= team.team_owner.id,
                                        scrim=scrim_instance, team=team)

        winner_data_dict = {'emails': team_emails[0:3]}
        rest_data_dict = {'emails': team_emails[3:]}

        content_data_dict ={
            'tournament_name': scrim_instance.tournament_name,
            'tournament_url': f'{settings.BASE_URL}tournament/scrims/instance/{tournament_slug}/{scrim_slug}/'
        }

        winner_email_body = f"Congratulations! You win the {scrim_instance.tournament_name} tournament"
        rest_email_body = f"Result of {scrim_instance.tournament_name} is Here"


        winner_email_content = get_template("emails/top_three_tournament_winner_result.html").render(content_data_dict)
        rest_email_content = get_template("emails/tournament_result_to_rest.html").render(content_data_dict)

        send_multi_email_task.delay(winner_data_dict, winner_email_body, winner_email_content)
        send_multi_email_task.delay(rest_data_dict, rest_email_body, rest_email_content)
    else:
        # if there are total 3 or less than 3 teams
        # that means no need to divide winners, they are winers 
        # send congrats email to them
        data_dict = {
            'emails': team_emails,
        }
        content_data_dict ={
            'tournament_name': scrim_instance.tournament_name,
            'tournament_url': f'{settings.BASE_URL}tournament/scrims/instance/{tournament_slug}/{scrim_slug}/'
        }
        email_body = f"Congratulations! You win the {scrim_instance.tournament_name} tournament"
        email_content = get_template("emails/top_three_tournament_winner_result.html").render(content_data_dict)
        # email_content = render_to_string("emails/top_three_tournament_winner_result.html", content_data_dict)
        # email_content = strip_tags(email_content)

        send_multi_email_task.delay(data_dict, email_body, email_content)
    
    return HttpResponse({"status": 1})
