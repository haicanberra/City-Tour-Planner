from django import forms
from .models import Search
from .filters import *


class SearchForm(forms.ModelForm):
    city = forms.CharField(
        required = True,
        label = "City",
        max_length = 100,
    )
    documented = forms.ChoiceField(
        required = False,
        label = "Documentations",
        choices = DOCUMENTATIONS,
    )
    tourism_filters = forms.ChoiceField(
        required = True,
        label = "Tourism",
        choices = COMBINED,
    )

    class Meta:
        model = Search
        fields = ['city', 'documented', 'tourism_filters']