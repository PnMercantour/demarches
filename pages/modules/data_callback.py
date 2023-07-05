
from dash import callback
from dash.dependencies import Input, Output, State

from pages.modules.data import SECURITY_CHECK, FILE, FLIGHT, SAVE_FLIGHT
from pages.modules.config import EDIT_STATE, INFO, SAVE_BUTTON_ID,SavingMode, EDIT_CONTROL_ID

def set_output_if_edit_callback(output, data_to_set, default):
    @callback(
        output,
        Input('url_data','data')
    )
    def __set__(data):
        (flight,_) = FLIGHT(data['uuid'])
        if 'error' in flight:
            return default
        file = FILE(flight['dossier_id'], force_update=True)
        return data_to_set if EDIT_STATE[file['state']] and SECURITY_CHECK(file['number'], data['security_token']) else default

def set_on_save_callback(savingMode:SavingMode):
    @callback(
        Output(INFO, 'data'),
        Input(SAVE_BUTTON_ID, 'n_clicks'),
        State(EDIT_CONTROL_ID, 'geojson'),
        State('url_data','data'),
        prevent_initial_call=True
    )
    def __set__(n_clicks, geojson, data):
        if n_clicks is not None:
            st = data['security_token']
            (current_flight,_) = FLIGHT(data['uuid'])
            if 'error' in current_flight:
                return {'message':current_flight['error']}
    
            file = FILE(current_flight['dossier_id'])
            flight = (_,geojson)
            (out,_) = SAVE_FLIGHT(file, flight, savingMode, st)
            if 'error' in out:
                return {'message':out['error']}
            else:
                return {'message': f'Flight saved with uuid {out["uuid"]}'}
        else:
            return {'message':"Nothing"}
        