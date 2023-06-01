from django.shortcuts import render, redirect
import folium
from .forms import SearchForm
from .models import Search
from django.http import HttpResponse

from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
from OSMPythonTools.nominatim import Nominatim

# Create your views here.
def planner(request):
    nominatim = Nominatim()
    overpass = Overpass()

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = SearchForm()

    address = Search.objects.all().last()
    location = nominatim.query(address)
    lat, lon = location.toJSON()[0]['lat'], location.toJSON()[0]['lon']
    selector = ['"tourism"="attraction"']
    query = overpassQueryBuilder(area=location,elementType=['node', 'way'],selector=selector,out='body')
    result = overpass.query(query)

    places_nodes = {}
    places_ways = {}
    tag_filters = ['wikidata', 'wikipedia', 'website', 'addr:city']
    for i in result.elements():
        if i.type() == "node":
            if i.lat() != None and i.lon() != None:
                for f in tag_filters:
                    if i.tag(f)!=None and i.tag('name')!=None:
                        places_nodes[i.tag('name')] = (i.lat(), i.lon())
                        break
        elif i.type() == "way":
            n = i.nodes()[0]
            for f in tag_filters:
                if i.tag(f)!=None and i.tag('name')!=None:
                    places_ways[i.tag('name')] = (n.lat(), n.lon())
    
    # if lat==None or lng==None:
    #     address.delete()
    #     return HttpResponse('Invalid address?')
    
    map = folium.Map(location=[lat, lon], zoom_control=False)
    for key in places_nodes:
        folium.Marker(places_nodes[key], tooltip=key, popup=key).add_to(map)
    for key in places_ways:
        folium.Marker(places_ways[key], tooltip=key, popup=key).add_to(map)

    map = map._repr_html_()
    context = {
        'map': map,
        'form': form,
    }
    return render(request, 'planner/planner.html', context)