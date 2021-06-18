from .decorators import allowed_only_tournament_owner
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import (EnrollmentInTournament, EnrollmentTeam, TeamMember,
                    Teams, Token, TopWinners, TournaRegistration, TournaWinnerResult,
                    HomeImages, TournamentOrganizer, EnrolledTournaments)
from .tasks import send_multi_email_task, send_single_email_task
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings
from uuid import uuid4
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags

# home page not much dynamic content
def home(request):
    context = {}
    return render(request, 'tournament/home.html', context=context)


# displaying list of all the tournaments in /tournaments
def tournament(request):
    today = timezone.now()

    # based on that user can filter tournaments 
    # this is only for showcase purpose
    # coding is in filter_tournament function
    tournament_status = ['UPCOMING', 'LIVE', 'ENDED']

    # fetching all the tournaments (most recent first) and paginate the
    # content 
    all_tournament = TournaRegistration.objects.all().order_by('-id')
    paginator = Paginator(all_tournament, 15)
    page_number = request.GET.get('page')
    tournaments = paginator.get_page(page_number)

    context = {
        'tournament_status': tournament_status,
        'today': today,
        'tournaments': tournaments
    }

    return render(request, 'tournament/tournaments.html',context=context)


# filtering the content based on upcoming, live, ended
def filter_tournament(request):
    # getting the list of all selected checkboxes
    # if nothinh selected that means no need to filter
    # show all content
    status = request.GET.getlist('status[]')  
    if len(status)==0:
        status = ['UPCOMING', 'LIVE', 'ENDED']
    
    all_tournament = TournaRegistration.objects.all().order_by('-id')

    try:
        # fetching all tournaments whose status is in user required status lst
        all_tournament = [obj for obj in all_tournament if obj.status_is in status]
    except Exception as e:
        print(e)

    # paginate the content
    paginator = Paginator(all_tournament, 15)
    page_number = request.GET.get('page')
    tournaments = paginator.get_page(page_number)

    context = {
        'tournaments': tournaments, 
    }

    # contains the html which is delivered after the filter using ajax
    template = render_to_string('components/filter-tournaments.html', context)
    return JsonResponse({"data": template})


# detaiils of a perticular tournaments
# pk is primary key of tournament 
def tournament_detail(request, pk):
    today = timezone.now()
    tournament = TournaRegistration.objects.get(id=pk)

    try:
        # fetching all the enrolled teams for the tournament
        enrolled_teams = EnrollmentTeam.objects.select_related('tournament') \
                    .filter(tournament=EnrollmentInTournament.objects.get(tournament=tournament))
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


    # will filter teams based on confirmed, pending, declined 
    # by the admin of the touenament
    pending_teams = []
    confirmed_teams = []
    decline_teams = []
    for i in enrolled_teams:
        x = EnrollmentTeam.objects.get(id=i.id)
        team = Teams.objects.get(id = x.enrolled_teams.id)

        if team.is_confirmed == 'CONFIRMED':
            confirmed_teams.append(team)
        elif team.is_confirmed == 'PENDING':
            pending_teams.append(team)
        else:
            decline_teams.append(team)

    try:
        # tournament prize sectiion contains top 3 players that will show in the prize section
        teams = TournaWinnerResult.objects.order_by('-total_points') \
                                .filter(target_tournament=tournament)
    except:
        teams = []


    context = {
        'tournament': tournament,
        'today': today,
        'enrolled_teams': enrolled_teams,
        'pending_teams': pending_teams,
        'confirmed_teams': confirmed_teams,
        'teams': teams,
        'winners': teams[0:3],
        'active_user_teams': active_user_teams,
    }
    return render(request, 'tournament/tournament-details.html', context=context)


# creation of a tournament 
@login_required(login_url='login')
def create_tournament(request):
    if request.method == 'POST':
        organizer = request.user
        tournament_name = request.POST.get('tournament_name')
        tournament_date = request.POST.get('tournament_date')
        tournament_time = request.POST.get('tournament_time')
        tournament_game = request.POST.get('tournament_game')
        tournament_type = request.POST.get('tournament_type')
        tournament_slots = request.POST.get('tournament_slots')
        tournament_rules = request.POST.get('tournament_rules')
        discord_server_id = request.POST.get('discord_server_id') if request.POST.get('discord_server_id') else 0
        youtube_url = request.POST.get('youtube_url')


        # if request ccontains tournament banner
        # than system will use and save that banner 
        # otherwise will use the default one
        if 'myfile' in request.FILES:
            tournament_banner = request.FILES['myfile']
            TournaRegistration.objects.create(
                admin=organizer, tournament_name=tournament_name,
                date=tournament_date, time=tournament_time, 
                banner=tournament_banner, game_type=tournament_game,
                team_type= tournament_type, slots=tournament_slots,
                rules=tournament_rules, discord_server_id=discord_server_id,
                youtube_url=youtube_url
            )
        else:
            tournament_banner = None
            TournaRegistration.objects.create(
                admin=organizer, tournament_name=tournament_name,
                date=tournament_date, time=tournament_time, 
                game_type=tournament_game,
                team_type= tournament_type, slots=tournament_slots,
                rules=tournament_rules, discord_server_id=discord_server_id,
                youtube_url=youtube_url
            ) 
            
        messages.success(request, f"Tournament {tournament_name} created successfully")
        print(f"Tournament {tournament_name} created!")

        return redirect('view-tournaments')
    return render(request, 'tournament/create-tournament.html')


# will register a team in tournament which is already registered by the the user
# on the platform, no need to recreate the same team again and again
@login_required(login_url='login')
def register_by_existing_team(request, pk):
    tournament = TournaRegistration.objects.get(id=pk)
    if request.method=='POST':
        # get the teamid from frontend and clone the team in a new model object
        # get the team members objects and clone the members in the new created team object
        team_id = request.POST.get("user_team_id")
        team = Teams.objects.get(id=team_id)
        new_team = Teams.objects.create(team_owner=request.user, team_pic=team.team_pic, team_name=team.team_name, 
            team_email=team.team_email, team_whstapp_no=team.team_whstapp_no)
        for member in team.get_team_member_list():
            TeamMember.objects.create(team_id=new_team.id, team_member=member.team_member,
                discord_tag=member.discord_tag, team_role=member.team_role)

        # reg_tournament = EnrollmentInTournament.objects.create(tournament_id=pk)
        # print(reg_tournament)
        if EnrollmentInTournament.objects.filter(tournament=tournament).exists():
            # if already exist than use that otherwise create mew and join
            EnrollmentTeam.objects.create(tournament=EnrollmentInTournament.objects.filter(tournament=tournament)[0],
                                        enrolled_teams=new_team)
        else:
            EnrollmentTeam.objects.create(tournament=EnrollmentInTournament.objects.create(tournament=tournament),
                                        enrolled_teams=new_team)

        # this is for, to create a record of all touenaments in which a specific user registered
        # in futture, i want to fetch all the tournament in which current logged in use registered
        # in that case it will help
        # any alternative, most welcomed by sumit
        EnrolledTournaments.objects.create(user=request.user, tournament=tournament)
        
        # EnrollmentTeam(tournament_id=reg_tournament.id, enrolled_teams_id=new_team.id)
        messages.success(request, f"Registered successfully")
        return redirect(f'/tournament/{pk}/')
    return redirect(f'/tournament/{pk}/')


# registration in tournament form
@login_required(login_url='login')
def register_in_tourna_form(request, pk, confirmed_slots, total_slots):
    if request.method == 'POST':
        # if some one is trying to register using the link not the dashboard even when slots
        # are full than response will be like that.
        if int(confirmed_slots) >= int(total_slots):
            return JsonResponse({"status": False, "response": "You are too smart kid! but not here"})
        else:
            # get the values from backend 
            # whatsapp number will only accept integers, not special characters
            tournament = TournaRegistration.objects.get(id=pk)
            team_name = request.POST.get('team_name')
            whatsapp_number = request.POST.get('whatsapp_number') if isinstance(request.POST.get('whatsapp_number'), int) \
                                                                     else None
            team_email = request.POST.get('team_email')

            playername = request.POST.getlist('playername')
            discordtag = request.POST.getlist('discordtag')
            teamrole = request.POST.getlist('teamrole')


            # if team avatar exist in request.POST than use the avatar to create team 
            # else use default team pic and use that
            if 'teamavatar' in request.FILES:
                team_avatar = request.FILES['teamavatar']
                
                team_obj = Teams.objects.create(team_owner=request.user, team_pic=team_avatar, team_name=team_name, team_email=team_email,
                                        team_whstapp_no = whatsapp_number)
            else:
                team_obj = Teams.objects.create(team_owner=request.user, team_name=team_name, team_email=team_email,
                                        team_whstapp_no = whatsapp_number)

            # playername, discordtag, teamrole is in a list
            # we have to insert data 3 by 3 [platername i, discordtag i, teamrole i]
            # making sets of 3 by 3 content and lopping them to create multiple model objects
            lst = [playername, discordtag, teamrole]

            for i in range(len(playername)):
                team = [x[i] for x in lst]
                TeamMember.objects.create(team=team_obj, team_member=team[0], 
                    discord_tag=team[1], team_role=team[2])

            
            # IF there is already tournament thn use that else create new one
            if EnrollmentInTournament.objects.filter(tournament=tournament).exists():
                EnrollmentTeam.objects.create(tournament=EnrollmentInTournament.objects.filter(tournament=tournament)[0],
                                            enrolled_teams=team_obj)
            else:
                EnrollmentTeam.objects.create(tournament=EnrollmentInTournament.objects.create(tournament=tournament),
                                            enrolled_teams=team_obj)

            # this is for, to create a record of all touenaments in which a specific user registered
            # in futture, i want to fetch all the tournament in which current logged in use registered
            # in that case it will help
            # any alternative, most welcomed by sumit
            EnrolledTournaments.objects.create(user=request.user, tournament=tournament)

            messages.success(request, f"{team_obj.team_name} registered in {tournament.tournament_name} tournament")
            return redirect(f'/tournament/{pk}/')
    return redirect(f'/tournament/{pk}/')



@login_required(login_url='login')
@allowed_only_tournament_owner
def change_team_confirmation_status(request, pk, pk2):
    # a confirmation button will be pressed from the frontend
    # when this url hits, a (pk) specific team will be confirmed in the tournament
    team = Teams.objects.get(id = pk2)
    team.is_confirmed = 'CONFIRMED'
    team.save()
    # send email
    tournament = TournaRegistration.objects.get(id=pk)

    # data dictionary used in email context
    email_data_dict = {
        'team_name': team.team_name,
        'team_email': team.team_email,
    }

    content_data_dict = {
        'team_name': team.team_name,
        "tournament_name": tournament.tournament_name,
        "tournament_banner": tournament.banner.url,
        "start_time": tournament.start_at,
        "end_time": tournament.end_at,
        "team_type": tournament.team_type,
    }

    # after confirmation, a confitmation email will be sent to related team
    email_body = f"Your Slot in {tournament.tournament_name} has been Confirmed"
    email_content = get_template("emails/team_confirmation_email.html").render(content_data_dict)
    send_single_email_task.delay(email_data_dict, email_body, email_content)

    return redirect(f'/tournament/{pk}/')



@login_required(login_url='login')
@allowed_only_tournament_owner
def change_team_decline_status(request, pk, pk2):
    # a declination button will be pressed from the frontend
    # when this url hits, a (pk) specific team will be declined in the tournament
    team = Teams.objects.get(id = pk2)
    team.is_confirmed = 'DECLINED'
    team.save()
    # send email
    tournament = TournaRegistration.objects.get(id=pk)

    # helps in email content
    email_data_dict = {
        'team_name': team.team_name,
        'team_email': team.team_email,
    }

    content_data_dict = {
        'team_name': team.team_name,
        "tournament_name": tournament.tournament_name,
    }

    # decliaton email will be sent to the related user
    email_body = f"Your Slot in {tournament.tournament_name} has been Declined"
    email_content = get_template("emails/team_decline_email.html").render(content_data_dict)

    send_single_email_task.delay(email_data_dict, email_body, email_content)

    return redirect(f'/tournament/{pk}/')


# will send id password of the tournament to all the registered
# cconfirmed teams, when admin wants to send the credentials     
@login_required(login_url='login')
@allowed_only_tournament_owner
def send_id_password_to_registered_team(request, pk):
    tournament = TournaRegistration.objects.get(id=pk)

    # filter out alll the confirmed team of the tournament
    try:
        enrolled_teams = EnrollmentTeam.objects.select_related('tournament') \
                    .filter(tournament=EnrollmentInTournament.objects.get(tournament=tournament))
    except:
        enrolled_teams = []
        
    if request.method == "POST":
        tourna_id = request.POST.get('tournament_id')
        tourna_pass = request.POST.get('tournament_password')


        # collecting emails of all the confirmed teams 
        # sending id and password getting from request to collected emails
        emails = []
        for i in enrolled_teams:
            x = EnrollmentTeam.objects.get(id=i.id)
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
            'tournament_name': tournament.tournament_name,
            'date': tournament.date,
            'time': tournament.time,
            'start_time': tournament.start_at, 
            'banner': tournament.banner.url,
            'team_type': tournament.team_type,
        }

        # decliaton email will be sent to the related user
        email_body = f'ID PASS for {tournament.tournament_name}'
        email_content = get_template("emails/tournament_idpass_email.html").render(content_data_dict)
        
        # sending emails using celery
        send_multi_email_task.delay(email_data_dict, email_body, email_content)
        return redirect(f'/tournament/{pk}/')
    else:
        return redirect(f'/tournament/{pk}/')


@login_required(login_url='login')
@allowed_only_tournament_owner
def manage_tourna_result(request, pk):


    tournament = TournaRegistration.objects.get(id=pk)
    try:
        enrolled_teams = EnrollmentTeam.objects.select_related('tournament') \
                    .filter(tournament=EnrollmentInTournament.objects.get(tournament=tournament))
    except:
        enrolled_teams = []


    pending_teams = []
    confirmed_teams = []
    decline_teams = []

   
    for i in enrolled_teams:
        x = EnrollmentTeam.objects.get(id=i.id)
        team = Teams.objects.get(id = x.enrolled_teams.id)

        if team.is_confirmed == 'CONFIRMED':
            confirmed_teams.append(team)
        elif team.is_confirmed == 'PENDING':
            pending_teams.append(team)
        else:
            decline_teams.append(team)

    try:
        teams = TournaWinnerResult.objects.order_by('-total_points').filter(target_tournament=tournament)
    except:
        teams = []

    context = {
        'tournament': tournament,
        'enrolled_teams': enrolled_teams,
        'pending_teams': pending_teams,
        'confirmed_teams': confirmed_teams,
        'declined_teams': decline_teams,
        'teams': teams,
    }
    return render(request, 'tournament/crud-tournament-result.html', context=context)


# saving tournament result
@login_required(login_url='login')
@allowed_only_tournament_owner
def save_tourna_result(request, pk):
    tournament = TournaRegistration.objects.get(id=pk)
    if request.method == 'POST':
        try:
            general_team_id = request.POST.get('general_teamid')
            team_id = request.POST.get('teamid')
            teamkill = request.POST.get('teamkill')
            teamplace = request.POST.get('teamplace')

            # if id is present, that means update
            # if id is not present, create new
            if team_id == '':
                team_result = TournaWinnerResult(
                    target_tournament=tournament,
                    teamid = general_team_id,
                    killspts=teamkill,
                    placepts=teamplace
                )
            else:
                team_result = TournaWinnerResult(
                    id=team_id,
                    target_tournament=tournament,
                    teamid=general_team_id,
                    killspts=teamkill,
                    placepts=teamplace
                )
            team_result.save()

            try:
                # gettning all the created teams and packing them in list 
                teams = list(TournaWinnerResult.objects.filter(target_tournament=tournament).values_list())
            except:
                teams = []

            return JsonResponse({'status': 'Save', 'response_data': teams})
        except Exception as e:
            messages.error(request, "no")
            return JsonResponse({'status': 0})
    else:
        return JsonResponse({'status': 0})

# @allowed_only_tournament_owner
@login_required(login_url='login')
def delete_tourna_result(request):
    if request.method == 'POST':
        team_id = request.POST.get('sid')

        TournaWinnerResult.objects.get(pk=team_id).delete()

        return JsonResponse({'status': 1})
    else:
        return JsonResponse({'status': 0})

# @allowed_only_tournament_owner
@login_required(login_url='login')
def update_tourna_result(request):
    if request.method == 'POST':
        team_id = request.POST.get('sid')

        team = TournaWinnerResult.objects.get(pk=team_id)
        team_data = {"id": team.id, "teamname": team.teamname,
                     "killspts": team.killspts, "placepts":team.placepts}

        return JsonResponse(team_data)
    else:
        return JsonResponse({'status': 0})


# sending tournament result based on above CRUD
@allowed_only_tournament_owner
@login_required(login_url='login')
def send_tourna_result(request, pk):
    tournament = TournaRegistration.objects.get(id=pk)
    try:
        teams = TournaWinnerResult.objects.order_by('-total_points').filter(target_tournament_id=pk)
        team_emails = []
        for i in teams:
            team_emails.append(i.email)
    except:
        team_emails = []


    # if there are more than 3 teams listed by admin oof tournament, then top 3 will be winners
    # and rest of them need only result emails
    # top 3 will get congratulations email
    if len(teams) >=3:
        for i in teams[0:3]:
            team = Teams.objects.get(pk=int(21))
            TopWinners.objects.create(team_owner_id= team.team_owner.id,
                                        tournament=tournament, team=team)

        winner_data_dict = {'emails': team_emails[0:3]}
        rest_data_dict = {'emails': team_emails[3:]}

        content_data_dict ={
            'tournament_name': tournament.tournament_name,
            'tournament_url': f'http://127.0.0.1:8000/tournament/{pk}/'
        }

        winner_email_body = f"Congratulations! You win the {tournament.tournament_name} tournament"
        rest_email_body = f"Result of {tournament.tournament_name} is Here"


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
            'tournament_name': tournament.tournament_name,
            'tournament_url': f'http://127.0.0.1:8000/tournament/{pk}/'
        }
        email_body = f"Congratulations! You win the {tournament.tournament_name} tournament"
        email_content = render_to_string("emails/top_three_tournament_winner_result.html", content_data_dict)
        email_content = strip_tags(email_content)

        send_multi_email_task.delay(data_dict, email_body, email_content)

    return redirect(f'/manage-crud-tournament-result/{pk}/')


# invite someone who can help to the admin of tournament 
# more than 1 user can have access to the tournament result 
# page using this functionality 
@login_required(login_url='login')
def invite_organizer(request, pk):
    if request.method == 'POST':
        # creating a unique token in hex format
        # saving it to the database
        token = uuid4().hex
        token_obj = Token.objects.create(token=token)
        token_id = token_obj.id

        # creating a unique url which can only active for 10 minutes
        url = settings.BASE_URL + f"accept-invite-tournament-organizer/{token_id}/{token}/{pk}/"

        # sendig the url too the email provided by the admin of tournament
        data_dict = {'team_email':request.POST.get("email")}
        content_data_dict = {
            "invite_url": url
        }
        email_body = f"{request.user} invited you on platform!"

        email_content = get_template("emails/tournament_org_invitation.html").render(content_data_dict)

        send_single_email_task.delay(data_dict, email_body, email_content)

        return JsonResponse({'status': 1})
    else:
        return JsonResponse({'status': 0})
        # return redirect(f'/manage-crud-tournament-result/{pk}/')


# @login_required(login_url='login')
def accept_invite_organizer(request, token_id, token, pk):

    tournament = TournaRegistration.objects.get(id=pk)
    token_obj = Token.objects.get(id=token_id)
    if request.user.is_authenticated:
        # cheking if toke is espired or not
        # if expired then link also dead, user can not add itself to the tournament 
        # otganizer list otherwise newuser can manage, the tournament
        if token_obj.is_expired:
            return JsonResponse({"status": False, "response": "Session Failed."})
        else:
            if token_obj.token == token:
                TournamentOrganizer.objects.create(tournament=tournament, helper=request.user)

                return redirect(f'/tournament/{pk}/')
    else:
        messages.warning(request, "Please, Login :)")
        return redirect('register')