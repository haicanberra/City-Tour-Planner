from django.shortcuts import render, redirect
import folium, random
from folium import plugins
from .forms import SearchForm
from .models import Search
from .filters import *
from django.http import HttpResponse

from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
from OSMPythonTools.nominatim import Nominatim
from django.contrib import messages

# Create your views here.
def planner(request):
    MAX_POPUP_WIDTH = 500
    colors = ['red','blue','gray','darkred','lightred','orange','beige','green','darkgreen','lightgreen','darkblue','lightblue','purple','darkpurple','pink','cadetblue','lightgray','black']
    legends = []

    nominatim = Nominatim()
    overpass = Overpass()
    location = nominatim.query('Edmonton')
    selector = ['"tourism"="attraction"']
    documented = "yes"
    map = folium.Map(location=[53.631611, -113.323975], zoom_control=False)

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = SearchForm(instance=Search.objects.all().last())

    last_search_obj = Search.objects.all().last()
    city = last_search_obj.city
    tourism_lso = last_search_obj.tourism_filters
    area = nominatim.query(city)
    lat, lon = area.toJSON()[0]['lat'], area.toJSON()[0]['lon']
    map = folium.Map(location=[lat, lon], zoom_control=False)

    same_city_objs = Search.objects.filter(city=city)
    index = 0
    for search_obj in same_city_objs:
        color = colors[index]
        index += 1

        documented = search_obj.documented
        tourism_filters = search_obj.tourism_filters
        legends.append(tourism_filters.capitalize())

        if tourism_filters == '*':
            selector = ['"tourism"']
        elif tourism_filters in [x[0] for x in TOURISM_FILTERS]:
            selector = ['"tourism"='+'"'+tourism_filters+'"']
        elif tourism_filters in [x[0] for x in AMENITY_FILTERS]:
            selector = ['"amenity"='+'"'+tourism_filters+'"']
        query = overpassQueryBuilder(area=area,elementType=['node', 'way'],selector=selector,out='body')
        result = overpass.query(query)

        places = {}
        tag_filters = ['website', 'wikipedia', 'wikidata']
        for i in result.elements():
            if i.tag('name') != None:
                if documented == "yes":
                    links = {}
                    for f in tag_filters:
                        if i.tag(f) != None:
                            links[f] = i.tag(f)
                if i.type() == "way":
                    j = i.nodes()[0]
                    places[i.tag('name')] = [(j.lat(), j.lon()), links, tourism_filters]
                else:
                    places[i.tag('name')] = [(i.lat(), i.lon()), links, tourism_filters]

        for key in places:
            if documented == "yes":
                if len(places[key][1]) > 0:
                    popup = key
                    for f in places[key][1]:
                        match f:
                            case 'website':
                                popup += f'<br><a href="{places[key][1][f]}" target="_blank">{f.capitalize()}</a>'
                            case 'wikipedia':
                                temp2 = (places[key][1][f]).replace(" ", "%20")
                                popup += f'<br><a href="https://wikipedia.org/wiki/{temp2}?uselang=en" target="_blank">{f.capitalize()}</a>'
                            case 'wikidata':
                                popup += f'<br><a href="https://www.wikidata.org/wiki/{places[key][1][f]}?uselang=en" target="_blank">{f.capitalize()}</a>'
                    folium.Marker(places[key][0], tooltip=key, popup=folium.Popup(popup, max_width=MAX_POPUP_WIDTH), icon=folium.Icon(color=color)).add_to(map)
            else:
                folium.Marker(places[key][0], tooltip=key, popup=folium.Popup(key, max_width=MAX_POPUP_WIDTH), icon=folium.Icon(color=color)).add_to(map)

    if len(places) == 0:
        Search.objects.filter(
            city=city, tourism_filters=tourism_lso
        ).delete()
        messages.warning(request, "No places were found.")
        return redirect('/')

    plugins.Fullscreen(
        position="topright",                                   
        title="Full Screen",                       
        title_cancel="Exit Full Screen",                      
        force_separate_button=True,
    ).add_to(map) 
    plugins.MousePosition(
        position='bottomleft', 
        separator=' : ', 
        empty_string='Unavailable', 
        lng_first=False, 
        num_digits=5, 
        prefix='', 
        lat_formatter=None, 
        lng_formatter=None
    ).add_to(map) 

    # Create a custom legend HTML
    legend_html = '''<div style="position: fixed; top: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border-radius: 5px; border: 1px solid gray;"><h4>Legend</h4><ul style="list-style-type: none; padding: 0; margin: 0;">'''
    for color, legend in zip(colors, legends):
        legend_html += f'<li><span style="color: {color};">&#9679;</span> {legend}</li>'
    legend_html += '</ul></div>'
    # Add the custom legend to the map
    map.get_root().html.add_child(folium.Element(legend_html))

    map = map._repr_html_()
    context = {
        'map': map,
        'form': form,
    } 
    return render(request, 'planner/planner.html', context)