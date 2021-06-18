from django.core.paginator import Paginator
from django.http.response import HttpResponse, JsonResponse
from django.utils import timezone
from tournament.models import EnrollmentInTournament, EnrollmentTeam, Teams, TopWinners, TournaRegistration, EnrolledTournaments
from django.shortcuts import redirect, render
from django.contrib import messages
import mimetypes
from .textonimage.draw import make_certificate

# Create your views here.
def user_profile(request):
    today = timezone.now()
    tournament_status = ['UPCOMING', 'LIVE', 'ENDED']

    # logged in user tournaments
    user_tournament = TournaRegistration.objects.filter(admin=request.user)

    enrolled_tourna = EnrolledTournaments.objects.filter(user=request.user)

    # all tournaments in which logged user has registered
    # paginator = Paginator(all_tournament, 15)
    # page_number = request.GET.get('page')
    # tournaments = paginator.get_page(page_number)

    context = {
        'tournament_status': tournament_status,
        'today': today,
        'user_tournaments': user_tournament,
        'enrolled_tourna': enrolled_tourna,
    }
    return render(request, 'userprofile/profile.html', context=context)

def create_certificate(request, tournament_id):
    tournament = TournaRegistration.objects.get(id=tournament_id)

    winner_result = TopWinners.objects.filter(tournament=tournament, team_owner_id=request.user.id) \
                                        .order_by('-id')[0:3]
    names = []
    for i in winner_result:
        names.append(i.team_owner.username)

    if request.user.username in names:

        if request.user.username == names[0]:
            top_winner_obj = winner_result[0]

            # update a existing model field
            # print(TopWinners.objects.filter(pk=top_winner_obj.id).update(team_owner_id=1))

            team = Teams.objects.get(pk=top_winner_obj.team.id)
            data_dict = {
                "position": 1,
                "tournament_name": tournament.tournament_name,
                "tournament_owner":  tournament.admin,
                "team_owner": team.team_owner.username,
                "team_name": team.team_name
            }

            image_name = 'certificate.png'
            # create certificate for specific team
            image = make_certificate(image_name, data_dict)

            path = open(image, 'rb')
            mime_type, _ = mimetypes.guess_type(image)
            response = HttpResponse(path, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=%s" % image_name
            return response

        elif request.user.username == names[1]:
            top_winner_obj = winner_result[1]

            team = Teams.objects.get(pk=top_winner_obj.team.id)
            data_dict = {
                "position": 2,
                "tournament_name": tournament.tournament_name, 
                "team_owner": team.team_owner.username,
                "team_name": team.team_name
            }

            image_name = 'certificate.jpg'
            # create certificate for specific team
            image = make_certificate(image_name, data_dict)

            path = open(image, 'rb')
            mime_type, _ = mimetypes.guess_type(image)
            response = HttpResponse(path, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=%s" % image_name
            return response
            
        elif request.user.username == names[2]:
            top_winner_obj = winner_result[2]
            team = Teams.objects.get(pk=top_winner_obj.team.id)
            data_dict = {
                "position": 3,
                "tournament_name": tournament.tournament_name, 
                "team_owner": team.team_owner.username,
                "team_name": team.team_name
            }

            image_name = 'certificate.jpg'
            # create certificate for specific team
            image = make_certificate(image_name, data_dict)

            path = open(image, 'rb')
            mime_type, _ = mimetypes.guess_type(image)
            response = HttpResponse(path, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=%s" % image_name
            return response
        else:
            return JsonResponse({"status": 0})
    else:
        return JsonResponse({"status":0, "msg": "You are not eligible for certification"})




