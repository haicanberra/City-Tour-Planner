from django import forms
from .models import Search, Address
from .filters import *


class SearchForm(forms.ModelForm):
    city = forms.CharField(
        required=True,
        label="City",
        max_length=100,
    )
    documented = forms.ChoiceField(
        label="Documentations",
        choices=DOCUMENTATIONS,
    )
    tourism_filters = forms.ChoiceField(
        label="Tourism",
        choices=COMBINED,
    )

    class Meta:
        model = Search
        fields = ["city", "documented", "tourism_filters"]


class AddressForm(forms.ModelForm):
    address = forms.CharField(
        required=True,
        label="Initial Address",
        max_length=500,
    )

    class Meta:
        model = Address
        fields = ["address"]
