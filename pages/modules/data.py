from pages.modules.config import PageConfig

from pages.modules.global_components.info_box import InfoBox
from pages.modules.global_components.loading_box import LoadingBox
from pages.modules.global_components.flight_selector import FlightSelector

from pages.modules.managers.data_manager import DataCache, DataManager

import psycopg as pg
import os


## GLOBAL DATA
DATA_MANAGER = DataManager()
GLOBAL_CONFIG = PageConfig("global", data_manager=DATA_MANAGER)
APP_INFO_BOX = InfoBox(GLOBAL_CONFIG)
LOADING_BOX = LoadingBox(GLOBAL_CONFIG)
CACHE = DataCache()
SELECTOR = FlightSelector(GLOBAL_CONFIG)

print("GLOBAL DATA LOADED")

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
       
    def flight_and_similar_fetch(self, data):
        from pages.modules.managers.data_manager import Flight
        flight = self.data_manager.get_flight_by_uuid(data['uuid'])
        if flight == None:
            return [None, APP_INFO_BOX.build_message("Flight not found", 'error')]
        flight = flight.get_last_flight()
        print(flight)
        flight_geojson = Flight.get_geojson(flight)

        similar_flights = self.data_manager.get_similar_flights(flight)
        geojson = Flight.build_geojson_from_flights(similar_flights)
        # Append the current flight to the list
        geojson['features'].insert(0, flight_geojson)
        return [geojson, APP_INFO_BOX.build_message("Flight found"), flight.get_id()]

