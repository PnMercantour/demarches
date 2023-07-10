from dash import callback, ClientsideFunction,clientside_callback
import dash_leaflet as dl
from dash.dependencies import Input, Output, State

from pages.modules.config import EDIT_STATE, INFO_BOX_ID, INFO
from pages.modules.data import FLIGHT, FILE


def set_info_listener_callback():
    @callback(
        Output(INFO_BOX_ID, 'children'),
        Input(INFO, 'data'),
        State('url_data','data'))
    def __set__(data, url_data):
        (flight,_) = FLIGHT(url_data['uuid'])
        if 'error' in flight:
            return "Invalid uuid : " + url_data['uuid']
            
        if data is None:
            return "Nothing"
        if 'message' in data:
            return data['message']
        else:
            return "Nothing"

def set_flight_callback(geojson_comp_id ='flight'):
    @callback(
        Output(geojson_comp_id, 'data'),
        Input('url_data','data')
    )
    def edit_flight_callback(data):
        (flight,json) = FLIGHT(data['uuid'], force_update=True)
        if 'error' in flight:
            print(flight['error'])
            return None
        return json

def set_file_info_callback(output):
    @callback(
        output,
        Input('url_data','data'),
    )
    def edit_file_info_callback(data):
        (info,_) = FLIGHT(data['uuid'])
        if 'error' in info:
            return ["None","None","None","Invalid uuid"]
        data = FILE(info['dossier_id'])
        return [data['state'],data['number'],data['creation_date'], f"Can edit : {EDIT_STATE[data['state']]}"]




## MAP RENDER CALLBACKS
def set_file_state_comp(comp, fnc : callable):
    @callback(
        Output(comp, 'children'),
        Input('url_data','data')
    )
    def __set__(data):
        (info,_) = FLIGHT(data['uuid'])
        if 'error' in info:
            return None
        file = FILE(info['dossier_id'], force_update=True)
        return fnc(file)
        

