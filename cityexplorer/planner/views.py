from django.shortcuts import render, redirect
import folium, subprocess
from .forms import *
from .models import *
from .filters import *
from .variables import *
import openrouteservice as ors
from django.urls import reverse
from django.middleware.csrf import get_token
from django.apps import apps

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
        pathform = PathForm(request.POST)
        if searchform.is_valid() and addressform.is_valid():
            search_obj = searchform.save(commit=False)
            marker_obj, created = Marker.objects.get_or_create(city=search_obj.city)
            search_obj.marker = marker_obj
            exist = Search.objects.filter(
                city=search_obj.city,
                marker=search_obj.marker,
                tourism_filters=search_obj.tourism_filters,
            ).count()
            if exist:
                Search.objects.filter(
                    city=search_obj.city,
                    marker=search_obj.marker,
                    tourism_filters=search_obj.tourism_filters,
                ).delete()
                Marker.objects.filter(city=search_obj.city).first().places = {
                    key: value
                    for key, value in search_obj.marker.places.items()
                    if search_obj.tourism_filters not in value
                }
            if len(search_obj.marker.places) == 0:
                exist = False
            if not exist:
                # Query if doesnt exist
                places = {}
                documented = search_obj.documented
                area = nominatim.query(search_obj.city)
                tourism_filters = search_obj.tourism_filters
                if tourism_filters == "znone":
                    models = [
                        "planner.Search",
                        "planner.Marker",
                        "planner.Path",
                        "planner.Address",
                    ]  # Replace with your app and model names
                    for model in models:
                        app_label, model_name = model.split(".")
                        Model = apps.get_model(app_label, model_name)
                        Model.objects.all().delete()
                    subprocess.call(["python", "manage.py", "loaddata", "fixture"])
                    return redirect("/")
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
                length = len(Marker.objects.filter(city=search_obj.city).first().places)
                if length > 0:
                    counter = (
                        max(
                            Marker.objects.filter(city=search_obj.city)
                            .first()
                            .places.values(),
                            key=lambda x: x[3],
                        )[3]
                        + 1
                    )
                else:
                    counter = 1
                for i in result.elements():
                    if i.tag("name") != None:
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
                                counter,
                            ]
                        else:
                            places[i.tag("name")] = [
                                (i.lat(), i.lon()),
                                links,
                                tourism_filters,
                                counter,
                            ]
                        counter += 1
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

            Address.objects.all().delete()
            addressform.save()

        if pathform.is_valid():
            Path.objects.all().delete()
            if exist:
                pathform.save()
            else:
                path_obj = pathform.save(commit=False)
                path_obj.paths = "0"
                path_obj.save()
        return redirect("/")
    else:
        searchform = SearchForm(instance=Search.objects.all().last())
        addressform = AddressForm(instance=Address.objects.all().last())
        pathform = PathForm(instance=Path.objects.all().last())

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
    if len(places):
        unique_tfilters = set(
            x[2].capitalize().replace("_", " ") for x in places.values()
        )
        featuregroups = {}
        for x in unique_tfilters:
            legends.append(x.capitalize().replace("_", " "))
            featuregroups[x] = folium.FeatureGroup(name=x)
        color_dict = COLOR_DICT

        # Plot markers
        for key in places:
            coord = places[key][0]
            links = places[key][1]
            tourism_filters = places[key][2].capitalize().replace("_", " ")
            index = places[key][3]
            documented = (
                Search.objects.filter(city=city, tourism_filters=places[key][2])
                .first()
                .documented
            )
            if documented == "yes":
                if len(links) > 0:
                    popup = (
                        '<span style="font-size: 14px;">'
                        + "("
                        + str(index)
                        + ")"
                        + "<br>"
                        + key
                        + "<br>"
                    )
                    for f in links:
                        match f:
                            case "website":
                                popup += f'<br><a href="{links[f]}" target="_blank">{f.capitalize()}</a>'
                            case "wikipedia":
                                popup += f'<br><a href="https://wikipedia.org/wiki/{(links[f]).replace(" ", "%20")}?uselang=en" target="_blank">{f.capitalize()}</a>'
                            case "wikidata":
                                popup += f'<br><a href="https://www.wikidata.org/wiki/{links[f]}?uselang=en" target="_blank">{f.capitalize()}</a>'
                    popup += "</span>"
                    marker = folium.Marker(
                        coord,
                        tooltip=key,
                        popup=folium.Popup(popup, max_width=MAX_POPUP_WIDTH),
                        icon=folium.Icon(color=color_dict[places[key][2]]),
                    )
                    featuregroups[tourism_filters].add_child(marker)
            else:
                popup = (
                    '<span style="font-size: 14px;">'
                    + "("
                    + str(index)
                    + ")"
                    + "<br>"
                    + key
                    + "<br>"
                    + "</span>"
                )
                marker = folium.Marker(
                    coord,
                    tooltip=key,
                    popup=folium.Popup(popup, max_width=MAX_POPUP_WIDTH),
                    icon=folium.Icon(color=color_dict[places[key][2]]),
                )
                featuregroups[tourism_filters].add_child(marker)

        # Add feature groups
        for x in featuregroups.values():
            map.add_child(x)

    # Process PATHING
    vehicle_start = list(reversed([float(alat), float(alon)]))
    path_obj = Path.objects.all().last()
    paths = [int(x) for x in path_obj.paths.split(",")]
    if paths[0] != 0:
        if len(path_obj.query) == 0:
            if paths[0] == -1 and len(paths) > 2:
                coords = []
            else:
                coords = [vehicle_start]
            places = Marker.objects.filter(city=city).first().places
            for i in paths:
                for key in places:
                    if places[key][3] == i:
                        coord = places[key][0]
                        coords.append(list(reversed(coord)))
            vehicles = [
                ors.optimization.Vehicle(
                    id=0,
                    profile=["foot-walking", "cycling-regular"],
                    start=coords[0],
                    end=coords[-1],
                    capacity=[len(paths) + 1],
                )
            ]
            jobs = []
            for index, coord in enumerate(coords):
                jobs.append(ors.optimization.Job(id=index, location=coord, amount=[1]))
            client = ors.Client(
                key="5b3ce3597851110001cf6248ab50f9fe9e7b4f909c6d2815fd39f3b0"
            )
            optimized = client.optimization(jobs=jobs, vehicles=vehicles, geometry=True)
            line_colors = ["green", "orange", "blue", "yellow"]
            linegroup = folium.FeatureGroup(name="Route")
            for route in optimized["routes"]:
                folium.PolyLine(
                    locations=[
                        list(reversed(coords))
                        for coords in ors.convert.decode_polyline(route["geometry"])[
                            "coordinates"
                        ]
                    ],
                    color=line_colors[route["vehicle"]],
                ).add_to(linegroup)
                path_obj.query.append(route)
        else:
            line_colors = ["green", "orange", "blue", "yellow"]
            linegroup = folium.FeatureGroup(name="Route")
            for route in path_obj.query:
                folium.PolyLine(
                    locations=[
                        list(reversed(coords))
                        for coords in ors.convert.decode_polyline(route["geometry"])[
                            "coordinates"
                        ]
                    ],
                    color=line_colors[route["vehicle"]],
                ).add_to(linegroup)
        map.add_child(linegroup)

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
    context = {
        "map": map,
        "searchform": searchform,
        "addressform": addressform,
        "pathform": pathform,
    }
    return render(request, "planner/planner.html", context)
