from django import forms
from .models import Search

class SearchForm(forms.ModelForm):
    address = forms.CharField(
        label = "Hotel's Address",
        max_length = 100,
        required = True,
    )

    class Meta:
        model = Search
        fields = ['address']