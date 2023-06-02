from django.shortcuts import render, redirect
import folium
from .forms import SearchForm
from .models import Search
from django.http import HttpResponse

from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
from OSMPythonTools.nominatim import Nominatim
from django.contrib import messages

# Create your views here.
def planner(request):
    nominatim = Nominatim()
    overpass = Overpass()
    location = nominatim.query('Edmonton')
    selector = ['"tourism"="attraction"']
    documented = True
    map = folium.Map(location=[53.631611, -113.323975], zoom_control=False)

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = SearchForm()

    last_search_obj = Search.objects.all().last()
    address = last_search_obj.address
    temp = nominatim.query(address)
    lat, lon = location.toJSON()[0]['lat'], location.toJSON()[0]['lon']
    documented = last_search_obj.documented
    amenity_filters = last_search_obj.amenity_filters
    tourism_filters = last_search_obj.tourism_filters
    if amenity_filters == "no":
        if tourism_filters == '*':
            selector = ['"tourism"']
        else:
            selector = ['"tourism"='+'"'+tourism_filters+'"']
    else:
        if tourism_filters == '*':
            selector = ['"tourism"','"amenity"']
        else:
            selector = [
            '"tourism"='+'"'+tourism_filters+'"', 
            '"amenity"='+'"'+amenity_filters+'"'
            ]
    query = overpassQueryBuilder(area=temp,elementType=['node', 'way'],selector=selector,out='body')
    result = overpass.query(query)

    places_nodes = {}
    places_ways = {}
    tag_filters = ['wikidata', 'wikipedia', 'website', 'addr:city']
    for i in result.elements():
        if i.type() == "node":
            if i.lat() != None and i.lon() != None:
                if documented:
                    for f in tag_filters:
                        if i.tag(f)!=None and i.tag('name')!=None:
                            places_nodes[i.tag('name')] = (i.lat(), i.lon())
                            break
                else:
                    if i.tag('name')!=None:
                            places_nodes[i.tag('name')] = (i.lat(), i.lon())
        elif i.type() == "way":
            n = i.nodes()[0]
            if documented:
                for f in tag_filters:
                    if i.tag(f)!=None and i.tag('name')!=None:
                        places_ways[i.tag('name')] = (n.lat(), n.lon())
            else:
                if i.tag('name')!=None:
                        places_ways[i.tag('name')] = (n.lat(), n.lon())
    
    map = folium.Map(location=[lat, lon], zoom_control=False)
    for key in places_nodes:
        folium.Marker(places_nodes[key], tooltip=key, popup=key).add_to(map)
    for key in places_ways:
        folium.Marker(places_ways[key], tooltip=key, popup=key).add_to(map)
    if len(places_nodes) == 0 and len(places_ways) == 0:
        messages.warning(request, "No places were found.")
        return redirect('/')

    map = map._repr_html_()
    context = {
        'map': map,
        'form': form,
    } 
    return render(request, 'planner/planner.html', context)