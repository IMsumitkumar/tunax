from django.db.models.signals import pre_save
from battleground.utils import unique_slug_generate
from django.utils import timezone
from tournament.models import Teams, TournaRegistration
from django.conf import settings
from django.db import models


class ScrimsAddOnTournament(models.Model):
    tournament = models.ForeignKey(TournaRegistration, on_delete=models.CASCADE)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament_name = models.CharField(max_length=100, blank=False, null=False)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    slots = models.IntegerField()

    @property
    def status_is(self):
        if self.start_at > timezone.now():
            return "UPCOMING"
        elif self.end_at < timezone.now():
            return "ENDED"
        elif self.start_at < timezone.now() < self.end_at:
            return "LIVE"

    def __str__(self):
        return self.tournament_name

def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generate(instance)

pre_save.connect(slug_generator, sender=ScrimsAddOnTournament)

class EnrollmentInScrim(models.Model):
    scrim_instance = models.ForeignKey(ScrimsAddOnTournament, on_delete=models.CASCADE)

    def __str__(self):
        return self.scrim_instance.tournament_name

class EnrollmentTeamInScrim(models.Model):
    scrim_instance = models.ForeignKey(EnrollmentInScrim, on_delete=models.CASCADE)
    enrolled_teams = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='enrolledteaminscrim')

class ScrimWinnerResult(models.Model):
    target_scrim = models.ForeignKey(ScrimsAddOnTournament, on_delete=models.CASCADE)
    teamid = models.IntegerField(blank=True, null=True)
    teamname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    killspts = models.PositiveIntegerField(blank=True, null=True)
    placepts = models.PositiveIntegerField(blank=True, null=True)
    total_points = models.PositiveIntegerField(blank=True, null=True)
    get_prize = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        try:
            team = Teams.objects.get(pk=int(self.teamid))
            team_email = team.team_email
            team_name = team.team_name
            self.email = team_email
            self.teamname = team_name
        except:
            self.email = ''
            self.teamname = ''
        self.total_points = int(self.killspts) + int(self.placepts)
        super(ScrimWinnerResult, self).save(*args, **kwargs)
    
    def __str__(self):
        total_pts = int(self.killspts) + int(self.placepts)
        return f"{self.teamname} | {total_pts}"

class TopWinnersInScrim(models.Model):
    team_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    scrim = models.ForeignKey(ScrimsAddOnTournament, on_delete=models.CASCADE,null=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.scrim.tournament_name