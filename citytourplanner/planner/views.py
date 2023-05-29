from django.shortcuts import render, redirect
import folium, geocoder
from .forms import SearchForm
from .models import Search
from django.http import HttpResponse

# Create your views here.
def planner(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = SearchForm()
    address = Search.objects.all().last()
    location = geocoder.osm(address)
    lat, lng = location.lat, location.lng
    country = location.country

    if lat==None or lng==None:
        address.delete()
        return HttpResponse('Invalid address?')
    
    map = folium.Map(location=[lat, lng], zoom_control=False)
    folium.Marker([lat, lng], tooltip='Click', popup=country).add_to(map)

    map = map._repr_html_()
    context = {
        'map': map,
        'form': form,
    }
    return render(request, 'planner/planner.html', context)