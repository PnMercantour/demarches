
from dash import callback
from dash.dependencies import Input, Output, State

from pages.modules.data import SECURITY_CHECK, FILE, FLIGHT, SAVE_FLIGHT
from pages.modules.config import EDIT_STATE, INFO, SAVE_BUTTON_ID,SavingMode



def set_output_if_edit_callback(output, data_to_set, default):
    @callback(
        output,
        Input('url_data','data')
    )
    def __set__(data):
        (flight,_) = FLIGHT(data['uuid'])
        if 'error' in flight:
            return default
        file = FILE(flight['dossier_id'])
        return data_to_set if EDIT_STATE[file['state']] and SECURITY_CHECK(file['number'], {"security-token":data['security_token']}) else default

def set_on_save_callback(savingMode:SavingMode, edit_control):
    @callback(
        Output(INFO, 'data',allow_duplicate=True),
        Input(SAVE_BUTTON_ID, 'n_clicks'),
        State(edit_control, 'geojson'),
        State('url_data','data'),
        prevent_initial_call=True,
    )
    def __set__(n_clicks, geojson, data):
        if n_clicks is not None:
            #check if features is not empty
            if len(geojson['features']) == 0:
                return {'message':'No flight to save'}

            st = data['security_token']
            (current_flight,_) = FLIGHT(data['uuid'])
            if 'error' in current_flight:
                return {'message':current_flight['error']}
    
            file = FILE(current_flight['dossier_id'])
            flight = (_,geojson)
            (out,_) = SAVE_FLIGHT(file, flight, savingMode, {"security-token":st})
            if 'error' in out:
                return {'message':out['error']}
            else:
                return {'message': f'Flight saved with uuid {out["uuid"]}'}
        else:
            return {'message':"Nothing"}

def set_admin_panel_callback(adminPanel, edit_control):
    @callback(
        Output(INFO, 'data',allow_duplicate=True),
        Input(adminPanel.get_request_for_edit_button(),'n_clicks'),
        [State(adminPanel.get_email_input(), 'value'), State(adminPanel.get_password_input(), 'value'), State(edit_control, 'geojson'), State('url_data','data')],
        prevent_initial_call=True,
    )
    def __set__(n_clicks, email, password, geojson, data):
        if n_clicks is not None:
            if email is None or password is None:
                return {"message":"Please fill the email and password fields"}
            if len(geojson['features']) == 0:
                return {"message":"No flight to save"}
            uuid=data['uuid']
            (current_flight,_) = FLIGHT(uuid)
            if 'error' in current_flight:
                return  {'message':"Invalid uuid : " + uuid}
            file = FILE(current_flight['dossier_id'])
            flight = (_,geojson)
            print(f"Saving flight {uuid} with email {email} and password {password}")
            (out,_) = SAVE_FLIGHT(file, flight, SavingMode.REQUEST_EDIT, {"email":email,"password":password})
            if 'error' in out:
                return {'message':out['error']}
            else:
                return {'message': f'Flight saved with uuid {out["uuid"]}'}
        else:
            return {'message':"Nothing"}
