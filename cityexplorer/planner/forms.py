from django import forms
from .models import *
from .filters import *


class SearchForm(forms.ModelForm):
    city = forms.CharField(
        required=True,
        label="City",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "City name"}),
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
        label="Address",
        max_length=500,
        widget=forms.TextInput(attrs={"placeholder": "Initial address"}),
    )

    class Meta:
        model = Address
        fields = ["address"]


class PathForm(forms.ModelForm):
    paths = forms.CharField(
        label="Path",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Comma seperated integers"}),
    )

    class Meta:
        model = Path
        fields = ["paths"]
