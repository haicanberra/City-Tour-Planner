from django import forms
from .models import Search

DOCUMENTATIONS = (
    ('yes', 'Yes'),
    ('no', 'No'),
)

# https://wiki.openstreetmap.org/wiki/Map_features#Tourism
TOURISM_FILTERS = (
    ('*','*'),
    ('no', 'No'),
    ('alpine_hut','Alpine hut'),
    ('apartment','Apartment'),
    ('aquarium','Aquarium'),
    ('artwork','Artwork'),
    ('attraction','Attraction'),
    ('camp_pitch','Camp pitch'),
    ('camp_site','Camp site'),
    ('caravan_site','Caravan site'),
    ('chalet','Chalet'),
    ('gallery','Gallery'),
    ('guest_house','Guest house'),
    ('hostel','Hostel'),
    ('hotel','Hotel'),
    ('information','Information'),
    ('motel','Motel'),
    ('museum','Museum'),
    ('picnic_site','Picnic site'),
    ('theme_park','Theme park'),
    ('viewpoint','Viewpoint'),
    ('wilderness_hut','Wilderness hut'),
    ('zoo','Zoo'),
)

# https://wiki.openstreetmap.org/wiki/Map_features#Amenity
AMENITY_FILTERS = (
    ('no', 'No'),
    ('bar', 'Bar'),
    ('biergarten','Biergarten'),
    ('cafe','Cafe'),
    ('fast_food','Fast food'),
    ('food_court','Food court'),
    ('ice_cream','Ice cream'),
    ('pub','Pub'),
    ('restaurant','Restaurant'),
    ('library','Library'),
    ('bicycle_rental','Bicycle rental'),
    ('boat_rental','Boat rental'),
    ('bus_station','Bus station'),
    ('car_rental','Car rental'),
    ('charging_station','Charging station'),
    ('ferry_terminal','Ferry terminal'),
    ('fuel','Fuel'),
    ('parking','Parking'),
    ('taxi','Taxi'),
    ('atm','ATM'),
    ('bank','Bank'),
    ('hospital','Hospital'),
    ('arts_centre','Arts centre'),
    ('casino','Casino'),
    ('cinema','Cinema'),
    ('fountain','Fountain'),
    ('nightclub','Nightclub'),
    ('theatre','Theatre'),
    ('townhall','Townhall'),
    ('toilets','Toilets'),
    ('marketplace','Marketplace'),
)

class SearchForm(forms.ModelForm):
    address = forms.CharField(
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
        required = False,
        label = "Tourism",
        choices = TOURISM_FILTERS,
    )
    amenity_filters = forms.ChoiceField(
        required = False,
        label = "Amenity",
        choices = AMENITY_FILTERS,
    )

    class Meta:
        model = Search
        fields = ['address', 'documented', 'tourism_filters', 'amenity_filters']