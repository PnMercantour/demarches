from dash import html,dcc, callback
import dash_leaflet as dl
import dash
import requests
import os
from dotenv import dotenv_values
from dash_extensions.javascript import Namespace
import json
from psycopg import connect
import psycopg
from dash.dependencies import Input, Output, State
from uuid import uuid4, UUID


config =  dotenv_values(".env")


dash.register_page(__name__, path='/',path_template='/view/<uuid>')

print('Refreshed '+str(__name__))

ns = Namespace("carto",'rendering')

draw_flag = ns("draw_drop_zone")

#LOAD ASSETS FILES JS

#TODO:Save uuid in browser storage to retrieve it later

##LOAD FILES && PARSING && CONVERTING TO GEOJSON

def polylines_to_multilinestring(features):
    src = {"type":"MultiLineString","coordinates":[]}
    src['coordinates'] = list(map(lambda x: x['geometry']['coordinates'],features))
    return src


files = os.listdir('./assets')



conn = connect(config["DB_CONNECTION"])



if conn is None:
    print("Error")
else:
    print("Connected")


def reinit_transaction():
    cur = conn.cursor()
    cur.execute(open('./sql/abort.sql','r').read())
    conn.commit()
    cur.close()

cur = conn.cursor()



cur.execute(open('./sql/test.sql','r').read())
rows = cur.fetchall()

# geobuf = geojson_to_geobuf(json.loads(rows[0][0]))
geojson = json.loads(rows[0][0])



geoComponent = dl.GeoJSON(data=geojson,id="geojson",options=dict(pointToLayer=draw_flag),cluster=True, superClusterOptions=dict(radius=200))


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


def generate_carto_info(_geojson):
    uuid = str(uuid4())
    geom = polylines_to_multilinestring(_geojson['features'])
    cur = conn.cursor()
    try:
        #clean transaction
        cur.execute(open('./sql/generate_carto.sql','r').read(),(uuid,json.dumps(geom)))
        conn.commit()
    except psycopg.Error as e:
        print(e)

    cur.close()

    return uuid


def generate_file_ds(carto_id):
    security_token = uuid4()

    data = {
        #url edit mode for petitionnaire
        "champ_Q2hhbXAtMzQzNjE0Nw==" : f"http://51.210.52.71:8050/edit/{carto_id}/{str(security_token)}",
        #url for instructor
        "champ_Q2hhbXAtMzQzMTI3MA==" : f"http://51.210.52.71:8050/admin/{carto_id}",
        #security token for verification
        "champ_Q2hhbXAtMzQzNTcxMg==" : str(security_token),
    }

    header = {
        "Content-Type":"application/json",
    }
    req = requests.post("https://www.demarches-simplifiees.fr/api/public/v1/demarches/77818/dossiers",headers=header,json=data)
    print(req.json(),flush=True)
    return (req.json()["dossier_url"], req.json()["dossier_id"], req.json()['dossier_number'])
    

def update_carto_info(file_id, file_number, carto_id):
    reinit_transaction()
    cur = conn.cursor()
    try:
        cur.execute(open('./sql/create_file_update_carto.sql','r').read(),(file_id,file_number,carto_id,carto_id))
        conn.commit()
    except psycopg.Error as e:

        print(e)
        return f'{{"error":"{e}"}}'
    cur.close()
    return True

def retrieve_carto(uuid):
    print("retrieve carto for "+uuid)
    reinit_transaction()
    cur = conn.cursor()
    try:
        cur.execute(open('./sql/fetch_carto.sql','r').read(),(uuid,))
        conn.commit()
    except psycopg.Error as e:
        print(e)
        return f'{{"error":"{e}"}}'
    
    carto = cur.fetchone()
    cur.close()
    return carto[0]




def layout(uuid=None):
    map = dl.Map(children=[tile,  dl.FeatureGroup([
            dl.EditControl(id="edit_control", draw={
                'polyline':{
                    'shapeOptions':{
                        'color':'#ff7777',
                        'weight':10,
                        'opacity':1
                    }
                },
                'polygon':False,
                'rectangle':False,
                'circle':False,
                'marker':False,
                'circlemarker':False

            })]), geoComponent, html.Div(id='current-path')],style={'width':'1200px','height':'900px'},center=center,zoom=9, id="map");
    pre_layout = html.Div([map,html.Button("Continuer sur démarches simplifiées",id="continue"), html.Div(id="output")])
    return html.Div([pre_layout, dcc.Store(id='memory', storage_type='session'), dcc.Store(id='url-key',data={'uuid':uuid, 'is_current_path': False if uuid == '' or uuid == None else True})])

output = {
    "memory" : Output("memory","data"),
    "url-key" : Output("url-key","data"),
    "info-box" : Output("info-box","children"),
}
input = {
    "memory" : Input("memory","data"),
    'edit_control' : Input('edit_control', 'geojson'),
    'url-key' : Input("url-key","data"),
}
state= {
    "url-key" : State("url-key","data"),
    'memory' : State('memory','data')
}
@callback([Output('memory', 'data')],[input['url-key'],input['edit_control']],state['memory'])
def update_memory(url_key,geojson,data):
    #fetch 
    if data is None:
        data = {
            'uuid' : None,
            'already_saved' : False,
            'current_path' : None,
            'editing_path' : None,
            'error': None
        }
    data['error'] = None

    if not(data['already_saved']) and url_key['is_current_path']:
        print("already saved")
        carto = retrieve_carto(url_key['uuid'])
        tmp = json.loads(carto)
        if not('error' in tmp):
            data['already_saved'] = True
            data['current_path'] = tmp
        else:
            data['error'] = "Impossible de récupérer le tracé"

    if not(url_key['is_current_path']) and data['current_path'] is not None:
        print("Reseting path")
        data['already_saved'] = False
        data['current_path'] = None

    if geojson is not None:
        data['editing_path'] = geojson
    return [data]
@callback(Output("output","children"),[Input("continue","n_clicks")], State('memory','data'),prevent_initial_call=True)
def save_and_redirect(n_clicks,geojson):
    if n_clicks is not None:
      carto_id = generate_carto_info(geojson['editing_path'])
      (url, id, number) = generate_file_ds(carto_id)
      if update_carto_info(id, number, carto_id):
        return dcc.Location(href=url, id="finalized",refresh=True)
      else:
        return "There were an error"

@callback(Output('continue','hidden'),Input('memory','data'),prevent_initial_call=True)
def hide_continue(data):
    if data['already_saved']:
        return True
    return False

@callback(Output('current-path', 'children'), Input('memory','data'), prevent_initial_call=True)
def update_data(data):
    if data['already_saved']:
        return dl.GeoJSON(data=data['current_path'])
    return None

# @callback(output['info-box'],input['memory'],prevent_initial_call=True)
# def update_info_box(data):
#     if data['error'] is not None:
#         return html.Div(data['error'])
#     return html.Div("")



# layout = layout_var



