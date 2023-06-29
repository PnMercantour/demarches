from dash import html, Dash
import dash_leaflet as dl
import os
from dotenv import dotenv_values
import json

config =  dotenv_values(".env")
app = Dash()

##LOAD FILES && PARSING && CONVERTING TO GEOJSON

files = os.listdir('./geojson')

geojsons = {"type":"FeatureCollection", "features":[]}
for file in files:
    with open('./geojson/'+file,'r') as raw:
        tmp = {"type":"Feature", "properties":{}, "geometry":{}}
        tmp["geometry"] = json.loads(raw.read())
        tmp['properties']['id']=file
        geojsons["features"].append(tmp)
geoComponent = dl.GeoJSON(data=geojsons)



tile_url = ("https://wxs.ign.fr/CLEF/geoportail/wmts?" +
                        "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                        "&STYLE=normal" +
                        "&TILEMATRIXSET=PM" +
                        "&FORMAT=image/png"+
                        "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2"+
                        "&TILEMATRIX={z}" +
                        "&TILEROW={y}" +
                        "&TILECOL={x}")
tile_url = tile_url.replace("CLEF",config["IGN_KEY"])
tile_size = 256
attribution = "© IGN-F/Geoportail"

tile = dl.TileLayer(url=tile_url,tileSize=tile_size,attribution=attribution)

center = [44.13211482938621, 7.093281566795227]
map = dl.Map(children=[tile,  dl.FeatureGroup([
            dl.EditControl(id="edit_control", drawToolbar={'mode':'polyline'})]),geoComponent],style={'width':'1200px','height':'900px'},center=center,zoom=9);
layout = html.Div(map)


app.layout = layout
app.title = "Demarches"

app.run(dev_tools_hot_reload=True,debug=True)