from django.http.response import JsonResponse
from django.shortcuts import redirect
from .models import TournaRegistration, TournamentOrganizer


def allowed_only_tournament_owner(view_func):
    def wrapper_func(request, *args, **kwargs):
        tournament = TournaRegistration.objects.get(id=kwargs.get('pk'))
        if request.user == tournament.admin or TournamentOrganizer.objects.exclude(pk=kwargs.get('pk')) \
                                                                    .filter(helper=request.user).exists():
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({"status": False, "response": "You are not allowed to view this content"})
    return wrapper_func


