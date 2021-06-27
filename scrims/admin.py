from scrims.models import EnrollmentInScrim, EnrollmentTeamInScrim, ScrimsAddOnTournament, TopWinnersInScrim, ScrimWinnerResult
from django.contrib import admin

# Register your models here.

class EnrollmentTeamInScrimInline(admin.TabularInline):
    model = EnrollmentTeamInScrim

class EnrollmentInScrimAdmin(admin.ModelAdmin):
    inlines = [EnrollmentTeamInScrimInline,]
    class Meta:
        model = EnrollmentInScrim

admin.site.register(ScrimsAddOnTournament)
admin.site.register(EnrollmentInScrim, EnrollmentInScrimAdmin)
admin.site.register(ScrimWinnerResult)
admin.site.register(TopWinnersInScrim)
