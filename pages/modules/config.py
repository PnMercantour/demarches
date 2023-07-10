import dash_leaflet as dl
from dotenv import dotenv_values
from dash_extensions.javascript import Namespace

## GLOBAL CONFIGURATION
def CONFIG(key):
    value = dotenv_values(".env").get(key) if key in dotenv_values(".env") else ""
    if value == "True":
        return True
    elif value == "False":
        return False
    else:
        return value
NS_RENDER = Namespace("carto","rendering")

EDIT_STATE = {
    'none' : True,
    'en_construction' : True,
    'en_instruction' : False,
    "accepte" : False,
    "refuse" : False,
    "sans_suite" : False,
}

STATE_PROPS = {
    'none' : {
        'color' : '#555555',
        'icon' : 'fa fa-circle',
        'text' : 'En construction'
    },
    'en_construction' : {
        'color' : '#555555',
        'icon' : 'fa fa-circle',
        'text' : 'En construction'
    },
    'en_instruction' : {
        'color' : '#ffdd00',
        'icon' : 'fa fa-circle',
        'text' : 'En instruction'
    },
    "accepte" : {
        'color' : '#00ff00',
        'icon' : 'fa fa-circle',
        'text' : 'Accepté'
    },
    "refuse" : {
        'color' : '#ff0000',
        'icon' : 'fa fa-circle',
        'text' : 'Refusé'
    },
    "sans_suite" : {
        'color' : '#ff00ff',
        'icon' : 'fa fa-circle',
        'text' : 'Sans suite'
    },
}

class SavingMode:
    CREATE = 0
    UPDATE = 1
    REQUEST_EDIT = 2
    BLOCK_ACCEPTED = 3
    BLOCK_REFUSED = 4

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
    conn = connect(CONFIG("DB_CONNECTION"))
    if conn is None:
        print("Error")
    else:
        print("Connected")
    return conn


## ID CONFIGURATION
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

EDIT_CONTROL = lambda : dl.EditControl(draw=EDIT_CONTROL_EDIT_DRAW)



tile_url = ("https://wxs.ign.fr/CLEF/geoportail/wmts?" +
                "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                "&STYLE=normal" +
                "&TILEMATRIXSET=PM" +
                "&FORMAT=image/png"+
                "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2"+
                "&TILEMATRIX={z}" +
                "&TILEROW={y}" +
                "&TILECOL={x}")
tile_url = tile_url.replace("CLEF",CONFIG("IGN_KEY"))
tile_size = 256
attribution = "© IGN-F/Geoportail"

TILE = dl.TileLayer(url=tile_url,tileSize=tile_size,attribution=attribution)
MAP_STYLE = {'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}
CENTER = [44.13211482938621, 7.093281566795227]
ZOOM = 9




