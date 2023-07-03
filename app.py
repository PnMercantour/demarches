from dash import html, Dash,dcc, clientside_callback,ClientsideFunction
import dash_leaflet as dl
import dash
import os
from dotenv import dotenv_values
import json
from dash_extensions.javascript import assign
from psycopg import connect
from dash.dependencies import Input, Output, State

config =  dotenv_values(".env")

app = Dash(__name__)


draw_flag = assign("""function(feature, latlng){
const flag = L.icon({iconUrl: `https://img.icons8.com/ios/50/circled-h.png`, iconSize: [50, 50]});
return L.marker(latlng, {icon: flag});
}""")

#LOAD ASSETS FILES JS



##LOAD FILES && PARSING && CONVERTING TO GEOJSON

files = os.listdir('./assets')



conn = connect(config["DB_CONNECTION"])



if conn is None:
    print("Error")
else:
    print("Connected")



cur = conn.cursor()


cur.execute(open('./sql/test.sql','r').read())
rows = cur.fetchall()

# geobuf = geojson_to_geobuf(json.loads(rows[0][0]))
geojson = json.loads(rows[0][0])



geoComponent = dl.GeoJSON(data=geojson,id="geojson",options=dict(pointToLayer=draw_flag),cluster=True, superClusterOptions=dict(radius=200))
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

            })]), geoComponent],style={'width':'1200px','height':'900px'},center=center,zoom=9, id="map");
layout = html.Div([map,html.Button("Continuer sur démarches simplifiées",id="continue"), html.Div(id="output")])

clientside_callback(ClientsideFunction(namespace='clientside', function_name='save_and_redirect'),
Output("output","children"),
Input("continue","n_clicks"), prevent_initial_call=True)

def map():
    return layout


app.layout =  map()

app.title = "Demarches"


app.run(dev_tools_hot_reload=True,debug=False)