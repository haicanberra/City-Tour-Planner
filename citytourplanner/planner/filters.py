DOCUMENTATIONS = (
    ('yes', 'Yes'),
    ('no', 'No'),
)

# https://wiki.openstreetmap.org/wiki/Map_features#Tourism
TOURISM_FILTERS = (
    ('*','*'),
    ('apartment','Apartment'),
    ('aquarium','Aquarium'),
    ('artwork','Artwork'),
    ('attraction','Attraction'),
    ('gallery','Gallery'),
    ('hotel','Hotel'),
    ('information','Information'),
    ('motel','Motel'),
    ('museum','Museum'),
    ('picnic_site','Picnic site'),
    ('theme_park','Theme park'),
    ('viewpoint','Viewpoint'),
    ('zoo','Zoo'),
)

# https://wiki.openstreetmap.org/wiki/Map_features#Amenity
AMENITY_FILTERS = (
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

_list = list(TOURISM_FILTERS + AMENITY_FILTERS)
_list.sort(key = lambda a: a[0])
COMBINED = tuple(_list)