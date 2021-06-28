from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.conf import settings
from django.db.models.expressions import F
from django.utils import timezone
from .helping_functions import combine_datetime 
from djrichtextfield.models import RichTextField


class HomeImages(models.Model):
    home_name      = models.CharField(max_length=250)

    home_banner = ProcessedImageField(upload_to='homeImages/',
                        processors=[ResizeToFill(1080, 448)],
                        format='WebP',
                        options={'quality': 60},
                        null=True, blank=True)
    carousel_one = ProcessedImageField(upload_to='homeImages/',
                        processors=[ResizeToFill(1080, 448)],
                        format='WebP',
                        options={'quality': 60},
                        null=True, blank=True)
    carousel_two = ProcessedImageField(upload_to='homeImages/',
                        processors=[ResizeToFill(1080, 448)],
                        format='WebP',
                        options={'quality': 60},
                        null=True, blank=True)
    carousel_three = ProcessedImageField(upload_to='homeImages/',
                        processors=[ResizeToFill(1080, 448)],
                        format='WebP',
                        options={'quality': 60},
                        null=True, blank=True)
    carousel_four = ProcessedImageField(upload_to='homeImages/',
                        processors=[ResizeToFill(1080, 448)],
                        format='WebP',
                        options={'quality': 60},
                        null=True, blank=True)

    tourna_banner  = models.ImageField(upload_to='homeImages/', null=True, blank=True)

    def __str__(self):
        return self.home_name


class TournaRegistration(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament_name = models.CharField(max_length=100, blank=False, null=False)
    date = models.CharField(max_length=100, blank=False, null=False)
    time = models.CharField(max_length=100, blank=False, null=False)
    banner = ProcessedImageField(upload_to='tourna_banner/',
                        default='default/teampic.jpg',
                        processors=[ResizeToFill(300, 200)],
                        format='WebP',
                        options={'quality': 60},
                        null=True, blank=True)
    game = models.CharField(max_length=50, blank=False, null=False)
    game_type = models.CharField(max_length=50, blank=False, null=False)
    game_days_count = models.IntegerField()
    team_type = models.CharField(max_length=50, blank=False, null=False)
    slots = models.IntegerField()
    rules = RichTextField()
    discord_server_id = models.PositiveBigIntegerField()
    youtube_url = models.URLField()
    is_over = models.BooleanField(default=False)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.start_at = combine_datetime(self.date, self.time)
        self.end_at = self.start_at + timedelta(minutes=30)

        super(TournaRegistration, self).save(*args, **kwargs)

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

class Clan(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    clan_name = models.CharField(max_length=100)

    def __str__(self):
        return self.clan_name

    class Meta:
        ordering = ['id']

class Member(models.Model):
    CLAN_ROLE = [
        ('Leader', 'Leader'),
        ('Co-Leader', 'Co-Leader'),
        ('Elite', 'Elite'),
        ('Member', 'Member')
    ]

    clan = models.ForeignKey(Clan, on_delete=models.CASCADE)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    clan_role = models.CharField(choices=CLAN_ROLE, max_length=20)
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.member} is {self.clan_role} of clan {self.clan}"

class Teams(models.Model):
    status = [
        ('CONFIRMED', 'CONFIRMED'),
        ('PENDING', 'PENDING'),
        ('DECLINED', 'DECLINED')
    ]
    team_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team_pic = ProcessedImageField(upload_to='teampic/',
                        default='default/teampic.jpg',
                        processors=[ResizeToFill(90, 90)],
                        format='WebP',
                        options={'quality': 60},
                        null=True, blank=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    team_email = models.EmailField(max_length=100, blank=True, null=True)
    team_whstapp_no = models.IntegerField(blank=True, null=True)
    is_confirmed = models.CharField(choices=status, default='PENDING', max_length=50)

    def get_team_member_list(self):
        return self.team_desc.all()

    def __str__(self):
        if self.is_confirmed == 'CONFIRMED':
            return f"{self.enrolled_teams.team_name} is confirmed"
        elif self.is_confirmed == 'PENDING':
            return f"{self.enrolled_teams.team_name} is pending"
        else:
            return f"{self.enrolled_teams.team_name} is declined"

    def __str__(self):
        return self.team_name

class TeamMember(models.Model):
    GAME_ROLE = [
        ('RUSHER', 'RUSHER'),
        ('IGL', 'IGL'),
        ('FRAGGER', 'FRAGGER'),
        ('CAMPER', 'CAMPER')
    ]

    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_desc')
    team_member = models.CharField(max_length=100, blank=True, null=True)
    discord_tag = models.CharField(max_length=100, blank=True, null=True)
    team_role = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.team_member} is from {self.team.team_name}"


class EnrollmentInTournament(models.Model):
    tournament = models.ForeignKey(TournaRegistration, on_delete=models.CASCADE)

    def __str__(self):
        return self.tournament.tournament_name

class EnrollmentTeam(models.Model):
    
    tournament = models.ForeignKey(EnrollmentInTournament, related_name='to_be_enrolled_in', on_delete=models.CASCADE)
    enrolled_teams = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='enrolledteam')


class TournaWinnerResult(models.Model):
    target_tournament = models.ForeignKey(TournaRegistration, on_delete=models.CASCADE)
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
        super(TournaWinnerResult, self).save(*args, **kwargs)

    def __str__(self):
        total_pts = int(self.killspts) + int(self.placepts)
        return f"{self.teamname} | {total_pts}"


class Token(models.Model):
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        if timezone.now() > (self.created_at + timedelta(minutes=10)):
            return True
        return False

class TopWinners(models.Model):
    team_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    tournament = models.ForeignKey(TournaRegistration, on_delete=models.CASCADE,null=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.tournament.tournament_name

class TournamentOrganizer(models.Model):
    tournament = models.ForeignKey(TournaRegistration, on_delete=models.CASCADE)
    helper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.helper} is helper in {self.tournament.tournament_name}"


class EnrolledTournaments(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    tournament = models.ForeignKey(TournaRegistration, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.user.username