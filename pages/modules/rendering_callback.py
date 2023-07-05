from dash import callback
import dash_leaflet as dl
from dash.dependencies import Input, Output

from pages.modules.config import EDIT_STATE, INFO_BOX_ID, INFO
from pages.modules.data import FLIGHT, FILE


def set_info_listener_callback():
    @callback(
        Output(INFO_BOX_ID, 'children'),
        Input(INFO, 'data')
    )
    def __set__(data):
        return data['message']

def set_flight_callback(geojson_comp_id ='flight'):
    @callback(
        Output(geojson_comp_id, 'data'),
        Input('url_data','data')
    )
    def edit_flight_callback(data):
        print(data)
        (flight,json) = FLIGHT(data['uuid'], force_update=True)
        if 'error' in flight:
            print(flight['error'])
            return None
        return json

def set_file_info_callback(output):
    @callback(
        output,
        Input('url_data','data')
    )
    def edit_file_info_callback(data):
        (info,_) = FLIGHT(data['uuid'])
        if 'error' in info:
            return [None,None,None,None]
        data = FILE(info['dossier_id'])
        return [data['state'],data['number'],data['creation_date'], f"Can edit : {EDIT_STATE[data['state']]}"]


