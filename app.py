from dash import html, Dash,dcc
import dash_leaflet as dl
import dash
import os
from dotenv import dotenv_values
import json
from dash_extensions.javascript import assign
from psycopg import connect
config =  dotenv_values(".env")

app = Dash(__name__, use_pages=True, url_base_pathname='/')

#LOAD ASSETS FILES JS

scripts = html.Div([
    html.Script(src=app.get_asset_url('bundle.js'), type='text/javascript'),
])

##LOAD FILES && PARSING && CONVERTING TO GEOJSON

files = os.listdir('./assets')

geojsons = {"type":"FeatureCollection", "features":[]}
for file in files:
    if file.endswith(".geojson"):
        with open('./assets/'+file,'r') as raw:
            tmp = {"type":"Feature", "properties":{}, "geometry":{}}
            tmp["geometry"] = json.loads(raw.read())
            tmp['properties']['id']=file
            geojsons["features"].append(tmp)
# geoComponent = dl.GeoJSON(data=geojsons, id="geojson")
print(config)

conn = connect(config["DB_CONNECTION"])



if conn is None:
    print("Error")
else:
    print("Connected")



cur = conn.cursor()


cur.execute(open('./sql/test.sql','r').read())
rows = cur.fetchall()
geoComponent = dl.GeoJSON(data=json.loads(rows[0][0]))
# open('./assets/test.geojson','w').write(rows[0][0])
# print(rows[0][0])



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
            dl.EditControl(id="edit_control", draw={
                'polyline':{
                    'shapeOptions':{
                        'color':'#ff7777',
                        'weight':10
                    }
                },
                'polygon':False,
                'rectangle':False,
                'circle':False,
                'marker':False,
                'circlemarker':False

            })]),geoComponent],style={'width':'1200px','height':'900px'},center=center,zoom=9, id="map");
layout = html.Div([scripts,map,html.Div(id="test")])

def map():
    return layout

dash.register_page("Home",path="/",layout=layout)
dash.register_page("Map",path="/map",layout=map)

app.layout =  html.Div([
    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),
    dash.page_container,
])


app.title = "Demarches"



app.run(dev_tools_hot_reload=True,debug=True)