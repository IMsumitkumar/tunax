from django.http.response import JsonResponse
from .models import ScrimsAddOnTournament


def allowed_only_tournament_owner(view_func):
    def wrapper_func(request, *args, **kwargs):
        scrim_instance = ScrimsAddOnTournament.objects.get(id=kwargs.get('scrim_instance_id'))
        if request.user == scrim_instance.admin:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({"status": False, "response": "You are not allowed to view this content"})
    return wrapper_func