from django.contrib import admin
from .models import (Clan, HomeImages, Member, Teams, TeamMember, Token, TopWinners,
         TournaRegistration,EnrollmentInTournament, TournaWinnerResult, 
         EnrollmentTeam, TournamentOrganizer, EnrolledTournaments)


class MemberInline(admin.TabularInline):
    model = Member

class ClanAdmin(admin.ModelAdmin):
    inlines = [MemberInline,]
    class Meta:
        model = Clan

class TeamMemberInline(admin.TabularInline):
    model = TeamMember

class TeamsAdmin(admin.ModelAdmin):
    inlines = [TeamMemberInline,]
    class Meta:
        model = Teams



class EnrollmentTeamInline(admin.TabularInline):
    model = EnrollmentTeam

class EnrollmentInTournamentAdmin(admin.ModelAdmin):
    inlines = [EnrollmentTeamInline,]
    class Meta:
        model = EnrollmentInTournament

admin.site.register(HomeImages)
admin.site.register(TournaRegistration)
admin.site.register(Clan, ClanAdmin)
admin.site.register(Teams, TeamsAdmin)
admin.site.register(TournaWinnerResult)
admin.site.register(EnrollmentInTournament, EnrollmentInTournamentAdmin)
admin.site.register(Token)
admin.site.register(TeamMember)
admin.site.register(TopWinners)
admin.site.register(EnrolledTournaments)
admin.site.register(TournamentOrganizer)
