<div align="center">


<img src="./assets/thumbnail.png" width="300">


# Django City Explorer

</div> 

---

## Contents
* [About](#about)
* [Specifications](#specifications)
* [Usages](#usages)
* [Notes](#notes)
* [References](#references)

---

<a name="about"></a>
## About
Django City Explorer - Interactive Tourism Map with Routing Functionality  
- Developed a Django web application enabling city exploration of over 10 types of tourist attractions and 30 categories of amenities in nearly 500 cities.
- Optimized routes between user-selected point of interest waypoints by utilizing OpenRouteService API, reducing travel time by an average of 25%.
- Integrated Nominatim and Overpass API for geocoding and mapping, allowing real-time filtering and visualization on an interactive Folium map.

---

<a name="specifications"></a>
## Specifications
### <ins>Front-end</ins>
- Bootstrap 4.
- Django Crispy Forms .
- Folium.
- HTML.
### <ins>APIs</ins>
- Nominatim.
- OpenRouteService.
- OpenStreetMap.
- Overpass.
### <ins>Back-end</ins>
- SQLite3.
### <ins>Marker</ins>
- #### Description:   
Stores a collection of markers for a specific city for placing on the map.  
- #### Fields:  
```city```: The name of the city (CharField with maximum length of 100 characters, nullable).  
```places```: A JSONField that stores information about places associated with the marker. Default value is an empty dictionary.  
### <ins>Search</ins>
- #### Description:   
Represents a search query for a city, including specific categorical point of interest filters.  
- #### Fields:  
```city```: The name of the city (CharField with maximum length of 100 characters, nullable).  
```documented```: A field representing if the location has a website documentation (Boolean).  
```tourism_filters```: A field to store specific categorical point of interest filters for the search (CharField with maximum length of 100 characters, nullable).  
```marker```: A foreign key relationship to the Marker model, representing the associated marker for the search. It uses the CASCADE deletion behavior, nullable.
### <ins>Address</ins>
- #### Description:  
Represents an address where user stays.
- #### Fields:  
```address```: The street address (CharField with maximum length of 500 characters, nullable).
### <ins>Path</ins>
- #### Description:  
Represents a path to draw and optimize, defined by the user.
- #### Fields:  
```paths```: The path value (CharField with maximum length of 500 characters, nullable).  
```query```: A JSONField to store query information associated with the path. Default value is an empty list.

---

<a name="usages"></a>
## Usages
- Build and run Dockerfile in ```/src```:
    ```
    docker build -t cityexplorer ./src
    docker run -p 8000:8000 cityexplorer
    ```
- Access http://127.0.0.1:8000/ in browser.
- ```zNone``` modifier: clear all markers.
- Start path with ```0```: disable path optimization.
- Start path with ```-1```: start from a marker.
- Enter marker's index for path optimization.

---

<a name="notes"></a>
## Notes
- Default data is in fixtures.
- <ins>Add</ins>: Street view maybe.

---

<a name="references"></a>
## References
- OpenRouteService [VROOM API](https://github.com/VROOM-Project/vroom/blob/master/docs/API.md).
