# City-Explorer

## About
A Python-based full stack web application written in Django for exploring Point of Interest in any city around the world.  
  
## Packages  
### <ins>Front-end</ins>
- Bootstrap 4
- Django Crispy Forms 
- Folium
- HTML
### <ins>APIs</ins>
- Nominatim
- OpenRouteService
- OpenStreetMap
- Overpass
### <ins>Back-end</ins>
- SQLite3  
## References
- OpenRouteService [VROOM API](https://github.com/VROOM-Project/vroom/blob/master/docs/API.md)  
## Specifications
### Marker
- #### Description:   
Stores a collection of markers for a specific city for placing on the map.  
- #### Fields:  
```city```: The name of the city (CharField with maximum length of 100 characters, nullable).  
```places```: A JSONField that stores information about places associated with the marker. Default value is an empty dictionary.  
### Search
- #### Description:   
Represents a search query for a city, including specific categorical point of interest filters.  
- #### Fields:  
```city```: The name of the city (CharField with maximum length of 100 characters, nullable).  
```documented```: A field representing if the location has a website documentation (Boolean).  
```tourism_filters```: A field to store specific categorical point of interest filters for the search (CharField with maximum length of 100 characters, nullable).  
```marker```: A foreign key relationship to the Marker model, representing the associated marker for the search. It uses the CASCADE deletion behavior, nullable.
### Address
- #### Description:  
Represents an address where user stays.
- #### Fields:  
```address```: The street address (CharField with maximum length of 500 characters, nullable).
### Path
- #### Description:  
Represents a path to draw and optimize, defined by the user.
- #### Fields:  
```paths```: The path value (CharField with maximum length of 500 characters, nullable).  
```query```: A JSONField to store query information associated with the path. Default value is an empty list.

## Installation
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```
## Usages
- In ```cityexplorer/``` execute ```python manage.py runserver```.  
- In browser, go to ```localhost:8000```.
- ```zNone```: clear all markers.
- ```0``` at start: disable path optimization.
- ```-1``` at start: start from a marker.
- Enter marker's index for path optimization.

## Notes
- Default data is in fixtures.
- <ins>Add</ins>: Street view maybe.
