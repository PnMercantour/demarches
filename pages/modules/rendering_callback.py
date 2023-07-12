from dash import callback, html, ClientsideFunction,clientside_callback,ctx
import dash_leaflet as dl
import dash
import dash_bootstrap_components as dbc
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


## Admin Panel Callbacks
def set_trigger_dialog_box(adminPanel):
    from pages.modules.components import SavingMode
    @callback(
        [Output(adminPanel.get_dialog(), 'open'), Output(adminPanel.get_dialog(), 'children')],
        [Input(adminPanel.get_trigger_dialog_button(),'n_clicks'), Input(adminPanel.get_cancel_button(),'n_clicks'), Input(adminPanel.get_accepter_button(),'n_clicks'), Input(adminPanel.get_refuser_button(),'n_clicks')],
        State('url_data','data'),
        prevent_initial_call=True,
    )
    def __set__(*args):
        data = args[-1]
        mode = SavingMode.ST_AVIS if data['st_token'] is not None else SavingMode.REQUEST_ST

        if args[0] is not None and ctx.triggered_id == adminPanel.get_trigger_dialog_button().id:
            if mode == SavingMode.REQUEST_ST:
                return [True, adminPanel.init_dialog(title="Remarque ?")]
            else:
                return [True, adminPanel.init_dialog(title="Prescription ?")]
        elif args[2] is not None and ctx.triggered_id == adminPanel.get_accepter_button().id:
            return [True, adminPanel.init_dialog(title="Motif ?")]

        elif args[3] is not None and ctx.triggered_id == adminPanel.get_refuser_button().id:
            return [True, adminPanel.init_dialog(title="Motif ?")]
        elif args[1] is not None and ctx.triggered_id == adminPanel.get_cancel_button().id:
            return [False, adminPanel.init_dialog(title="Motif ?")]    
        else:
            return [False, dash.no_update]
def set_init_admin_panel_callback(adminPanel):
    from pages.modules.components import SavingMode
    @callback(
        Output(adminPanel.get_form(), 'children'),
        Input('url_data','data'),
    )
    def __set__(data):
        st_token = data['st_token']
        mode = SavingMode.REQUEST_ST if st_token is None else SavingMode.ST_AVIS
        return adminPanel.init_output(mode)
    @callback(
        [Output(adminPanel.get_trigger_dialog_button(), 'children'), Output(adminPanel.get_submit(), 'children'), Output(adminPanel.get_email_input(), 'disabled'), Output(adminPanel.get_password_input(), 'disabled'), Output(adminPanel.get_accepter_button(), 'disabled'), Output(adminPanel.get_refuser_button(), 'disabled')],
        Input('url_data','data'),
    )
    def __set__(data):
        st_token = data['st_token']
        mode = SavingMode.REQUEST_ST if st_token is None else SavingMode.ST_AVIS
        return [SavingMode.to_str(mode), SavingMode.to_str(mode), mode == SavingMode.ST_AVIS, mode == SavingMode.ST_AVIS, mode == SavingMode.ST_AVIS, mode == SavingMode.ST_AVIS]

    
        


        

