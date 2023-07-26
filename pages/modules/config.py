from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:    
    from pages.modules.managers import DataManager
    from pages.modules.managers.security_manager import ISecurityManager

from demarches_simpy import DossierState

import dash_leaflet as dl
from dotenv import dotenv_values
from dash_extensions.javascript import Namespace

import dotenv

from enum import Enum

class SecurityLevel(Enum):
    AUTH=0 # Action requires authentication
    NO_AUTH=1 # Action does not require authentication


dotenv.load_dotenv()

class PageConfig():
    def __init__(self, page_name, data_manager : DataManager = None, security_manager : ISecurityManager = None):
        self.page_name = page_name
        self.data_manager = data_manager
        self.security_manager = security_manager
    @property
    def page_name(self):
        return self.__page_name
    @page_name.setter
    def page_name(self, value):
        self.__page_name = value

    @property
    def data_manager(self) -> DataManager:
        return self.__data_manager
    @data_manager.setter
    def data_manager(self, value):
        self.__data_manager = value

    @property
    def security_manager(self) -> ISecurityManager:
        return self.__security_manager
    @security_manager.setter
    def security_manager(self, value):
        self.__security_manager = value




def config_env(key):
    value = dotenv_values(".env").get(key) if key in dotenv_values(".env") else ""
    if value == "True":
        return True
    elif value == "False":
        return False
    else:
        return value

import json
config_file = json.loads(open('./config.json','r',encoding='utf-8').read())

def CONFIG(path,default : str ="")->str:
    '''exemple_key/exemple_key2/exemple_key3'''
    
    key = path.split("/")

    value = config_file

    while len(key) > 0:
        if key[0] in value:
            value = value[key.pop(0)]
        else:
            return default

    return value



NS_RENDER = Namespace("carto","rendering")


STATE_PROPS = {
    DossierState.CONSTRUCTION.value : {
        'color' : '#555555',
        'icon' : 'fa fa-circle',
        'text' : 'En construction'
    },
    DossierState.INSTRUCTION.value : {
        'color' : '#ffdd00',
        'icon' : 'fa fa-circle',
        'text' : 'En instruction'
    },
    DossierState.ACCEPTE.value : {
        'color' : '#00ff00',
        'icon' : 'fa fa-circle',
        'text' : 'Accepté'
    },
    DossierState.REFUSE.value : {
        'color' : '#ff0000',
        'icon' : 'fa fa-circle',
        'text' : 'Refusé'
    },
    DossierState.SANS_SUITE.value : {
        'color' : '#ff00ff',
        'icon' : 'fa fa-circle',
        'text' : 'Sans suite'
    },
}



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
tile_url = tile_url.replace("CLEF",config_env("IGN_KEY"))
tile_size = 256
attribution = "© IGN-F/Geoportail"

TILE = dl.TileLayer(url=tile_url,tileSize=tile_size,attribution=attribution)
MAP_STYLE = {'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}
CENTER = [44.13211482938621, 7.093281566795227]
ZOOM = 9




