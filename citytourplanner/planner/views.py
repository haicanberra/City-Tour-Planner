from django.shortcuts import render, redirect
import folium
from .forms import SearchForm, AddressForm
from .models import Search, Address, Marker
from .filters import *
from .variables import *

from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
from OSMPythonTools.nominatim import Nominatim
from django.contrib import messages


# Create your views here.
def planner(request):
    legends = [HOME]
    exist = False

    # Initialize query and folium variables
    nominatim = Nominatim()
    overpass = Overpass()
    area = nominatim.query("Edmonton")
    selector = ['"tourism"="attraction"']
    documented = "yes"
    map = folium.Map(
        location=[53.631611, -113.323975],
        zoom_control=False,
    )

    # Submit button pressed basically
    if request.method == "POST":
        searchform = SearchForm(request.POST)
        addressform = AddressForm(request.POST)
        if searchform.is_valid() and addressform.is_valid():
            search_obj = searchform.save(commit=False)
            marker_obj, created = Marker.objects.get_or_create(city=search_obj.city)
            search_obj.marker = marker_obj
            exist = Search.objects.filter(
                city=search_obj.city,
                documented=search_obj.documented,
                marker=search_obj.marker,
                tourism_filters=search_obj.tourism_filters,
            ).count()
            if exist:
                Search.objects.filter(
                    city=search_obj.city,
                    documented=search_obj.documented,
                    marker=search_obj.marker,
                    tourism_filters=search_obj.tourism_filters,
                ).delete()
            else:
                # Query if doesnt exist
                places = {}
                documented = search_obj.documented
                tourism_filters = search_obj.tourism_filters

                # Process string for query if no same search done before
                if tourism_filters == "*":
                    selector = ['"tourism"']
                elif tourism_filters in [x[0] for x in TOURISM_FILTERS]:
                    selector = ['"tourism"=' + '"' + tourism_filters + '"']
                elif tourism_filters in [x[0] for x in AMENITY_FILTERS]:
                    selector = ['"amenity"=' + '"' + tourism_filters + '"']
                query = overpassQueryBuilder(
                    area=area,
                    elementType=["node", "way"],
                    selector=selector,
                    out="body",
                )
                result = overpass.query(query)

                # Filter, places must have a name, sites are optional, put in a dict
                tag_filters = ["website", "wikipedia", "wikidata"]
                for i in result.elements():
                    if i.tag("name") != None:
                        if documented == "yes":
                            links = {}
                            for f in tag_filters:
                                if i.tag(f) != None:
                                    links[f] = i.tag(f)
                        if i.type() == "way":
                            j = i.nodes()[0]
                            places[i.tag("name")] = [
                                (j.lat(), j.lon()),
                                links,
                                tourism_filters,
                            ]
                        else:
                            places[i.tag("name")] = [
                                (i.lat(), i.lon()),
                                links,
                                tourism_filters,
                            ]
                # Error for no result returned from query
                if len(places) == 0:
                    Search.objects.filter(
                        city=search_obj.city, tourism_filters=tourism_filters
                    ).delete()
                    messages.warning(request, "No places were found.")
                    return redirect("/")
                marker_obj = Marker.objects.filter(city=search_obj.city).first()
                marker_obj.places.update(places)
                marker_obj.save()
            search_obj.save()

            address_obj = addressform.save(commit=False)
            exist2 = Address.objects.filter(address=address_obj.address).count()
            if exist2:
                Address.objects.filter(address=address_obj.address).delete()
            address_obj.save()
    else:
        searchform = SearchForm(instance=Search.objects.all().last())
        addressform = AddressForm(instance=Address.objects.all().last())

    # Get address attribute from last Address
    last_address_obj = Address.objects.all().last()
    address = last_address_obj.address
    addressquery = nominatim.query(address)
    alat, alon = addressquery.toJSON()[0]["lat"], addressquery.toJSON()[0]["lon"]

    # Get search attributes from last Search
    last_search_obj = Search.objects.all().last()
    city = last_search_obj.city
    area = nominatim.query(city)
    lat, lon = area.toJSON()[0]["lat"], area.toJSON()[0]["lon"]

    # Change map to last search's location, plot Home marker
    map = folium.Map(location=[lat, lon], zoom_control=False)
    marker = folium.Marker(
        (alat, alon), tooltip=HOME, popup=HOME, icon=folium.Icon(color=COLORS[0])
    )
    tempgroup = folium.FeatureGroup(name=HOME)
    tempgroup.add_child(marker)
    map.add_child(tempgroup)

    # Plot all markers in the same city from all searches
    places = Marker.objects.filter(city=city).first().places
    unique_tfilters = set(x[2].capitalize().replace("_", " ") for x in places.values())
    featuregroups = {}
    for x in unique_tfilters:
        legends.append(x.capitalize().replace("_", " "))
        featuregroups[x] = folium.FeatureGroup(name=x)
    unique_colors = len(unique_tfilters)
    color_dict = dict(zip(unique_tfilters, COLORS[1 : unique_colors + 1]))

    # Plot markers
    for key in places:
        coord = places[key][0]
        links = places[key][1]
        tourism_filters = places[key][2].capitalize().replace("_", " ")
        if documented == "yes":
            if len(links) > 0:
                popup = key
                for f in links:
                    match f:
                        case "website":
                            popup += f'<br><a href="{links[f]}" target="_blank">{f.capitalize()}</a>'
                        case "wikipedia":
                            popup += f'<br><a href="https://wikipedia.org/wiki/{(links[f]).replace(" ", "%20")}?uselang=en" target="_blank">{f.capitalize()}</a>'
                        case "wikidata":
                            popup += f'<br><a href="https://www.wikidata.org/wiki/{links[f]}?uselang=en" target="_blank">{f.capitalize()}</a>'
                marker = folium.Marker(
                    coord,
                    tooltip=key,
                    popup=folium.Popup(popup, max_width=MAX_POPUP_WIDTH),
                    icon=folium.Icon(color=color_dict[tourism_filters]),
                )
                featuregroups[tourism_filters].add_child(marker)
        else:
            marker = folium.Marker(
                coord,
                tooltip=key,
                popup=folium.Popup(key, max_width=MAX_POPUP_WIDTH),
                icon=folium.Icon(color=color_dict[tourism_filters]),
            )
            featuregroups[tourism_filters].add_child(marker)

    # Add feature groups
    for x in featuregroups.values():
        map.add_child(x)

    # Add Map styles
    folium.TileLayer("cartodbpositron").add_to(map)
    folium.TileLayer("cartodbdark_matter").add_to(map)

    # Compile
    folium.LayerControl(position="topleft", collapsed=False).add_to(map)

    # Create a custom legend HTML
    legend_html = LEGEND_HTML
    for color, legend in zip(COLORS, legends):
        legend_html += f'<li><span style="color: {color};">&#9679;</span> {legend}</li>'
    legend_html += "</ul></div>"

    # Add the custom legend to the map
    map.get_root().html.add_child(folium.Element(legend_html))

    # Send to view
    map = map._repr_html_()
    context = {"map": map, "searchform": searchform, "addressform": addressform}
    return render(request, "planner/planner.html", context)
