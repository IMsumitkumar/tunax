from django import forms
from django.db.models import fields
from django.forms import widgets
from .models import TournaWinnerResult

class TournamentResultForm(forms.ModelForm):
    class Meta:
        model = TournaWinnerResult
        fields = ['rank', 'team']
        # widgets = {
        #     'rank': forms.TextInput(attrs={'class':'form-control'}),
        #     'team': forms.TextInput(attrs={'class':'form-control'})
        # }
