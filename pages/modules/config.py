import dash_leaflet as dl
from dotenv import dotenv_values
from dash_extensions.javascript import Namespace

## GLOBAL CONFIGURATION
CONFIG =  dotenv_values(".env")
NS_RENDER = Namespace("carto","rendering")

EDIT_STATE = {
    'none' : True,
    'en_construction' : True,
    'en_instruction' : False,
    "accepte" : False,
    "refuse" : False,
    "sans_suite" : False,
}

class SavingMode:
    CREATE = 0
    UPDATE = 1
    ADMIN = 2

    def to_str(mode):
        if mode == SavingMode.CREATE:
            return "Continuer sur démarches simplifiées"
        elif mode == SavingMode.UPDATE:
            return "Mettre à jour et soummetre à validation"
        elif mode == SavingMode.ADMIN:
            return "Valider et envoyer au pétiionnaire"



#TODO: Make a better config file

## DB CONFIGURATION
def CONN():
    from psycopg import connect
    conn = connect(CONFIG["DB_CONNECTION"])
    if conn is None:
        print("Error")
    else:
        print("Connected")
    return conn


## ID CONFIGURATION
EDIT_CONTROL_ID = "comp_edit"
SAVE_BUTTON_ID = "comp_save"
INFO_BOX_ID = "info-box"
INFO = "info"

## MAP CONFIGURATION
EDIT_CONTROL_EDIT_DRAW = {
                'polyline':{'shapeOptions':{
                        'color':'#ff7777',
                        'weight':6,
                        'opacity':1
                    },
                },
                'polygon':False,
                'rectangle':False,
                'circle':False,
                'marker':False,
                'circlemarker':False
            }
EDIT_CONTROL_NO_EDIT_DRAW = {
                'polyline':False,
                'polygon':False,
                'rectangle':False,
                'circle':False,
                'marker':False,
                'circlemarker':False
}

EDIT_CONTROL = dl.FeatureGroup([ dl.EditControl(draw=EDIT_CONTROL_EDIT_DRAW, id=EDIT_CONTROL_ID)])



tile_url = ("https://wxs.ign.fr/CLEF/geoportail/wmts?" +
                "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                "&STYLE=normal" +
                "&TILEMATRIXSET=PM" +
                "&FORMAT=image/png"+
                "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2"+
                "&TILEMATRIX={z}" +
                "&TILEROW={y}" +
                "&TILECOL={x}")
tile_url = tile_url.replace("CLEF",CONFIG["IGN_KEY"])
tile_size = 256
attribution = "© IGN-F/Geoportail"

TILE = dl.TileLayer(url=tile_url,tileSize=tile_size,attribution=attribution)
MAP_STYLE = {'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}
CENTER = [44.13211482938621, 7.093281566795227]
ZOOM = 9




