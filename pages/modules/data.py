from pages.modules.config import PageConfig

from pages.modules.global_components.loading_box import LoadingBox
from pages.modules.global_components.info_box import InfoBox

from pages.modules.managers.data_manager import DataCache

import psycopg as pg
import os
def conn():
    conn = pg.connect(os.getenv("DB_CONNECTION"))
    if conn is None:
        print("Error")
    else:
        print("Connected")
    return conn

## GLOBAL DATA

GLOBAL_CONFIG = PageConfig("global")
CONN = conn()
APP_INFO_BOX = InfoBox(GLOBAL_CONFIG)
LOADING_BOX = LoadingBox(GLOBAL_CONFIG)
CACHE = DataCache()


class BuiltInCallbackFnc():

    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def flight_fetch(self, data):
        '''Need a IncomingData object as an Input of the callback, Return the geojson and an output message'''

        from pages.modules.managers.data_manager import Flight
        flight = self.data_manager.get_flight_by_uuid(data['uuid'])
        if flight == None:
            return [None, APP_INFO_BOX.build_message("Flight not found", 'error')]
        flight = flight.get_last_flight()
        return [Flight.build_complete_geojson(flight), APP_INFO_BOX.build_message("Flight found")]
       
