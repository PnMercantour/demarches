from dash import callback, html, ClientsideFunction,clientside_callback,ctx
import dash_leaflet as dl
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from pages.modules.config import EDIT_STATE, INFO_BOX_ID, INFO
from pages.modules.data import FLIGHT, FILE, IS_ST_ALREADY_REQUESTED, INFO_BOX_COMP, IS_FILE_CLOSED


def set_info_listener_callback():


    @callback(
        Output(INFO_BOX_ID, 'children'),
        Input(INFO, 'data'))
    def __set__(data):
        if data is None:
            return 'Nothing'
        if 'message' in data:
            return data['message']
        else:
            return 'Nothing'

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
        [Output(adminPanel.get_dialog(), 'open'), Output(adminPanel.get_dialog(), 'children'),Output(adminPanel.get_submit(), 'children')],
        [Input(adminPanel.get_trigger_dialog_button(),'n_clicks'), Input(adminPanel.get_cancel_button(),'n_clicks'), Input(adminPanel.get_accepter_button(),'n_clicks'), Input(adminPanel.get_refuser_button(),'n_clicks'), Input(adminPanel.get_submit(),'n_clicks')],
        State('url_data','data'),
        prevent_initial_call=True,
    )
    def __set__(*args):
        data = args[-1]
        mode = SavingMode.ST_AVIS if data['st_token'] is not None else SavingMode.REQUEST_ST

        if args[0] is not None and ctx.triggered_id == adminPanel.get_trigger_dialog_button().id:
            if mode == SavingMode.REQUEST_ST:
                adminPanel.set_mode(SavingMode.REQUEST_ST)
                return [True, adminPanel.init_dialog(title="Remarque ?"), "Remarque au ST"]
            else:
                adminPanel.set_mode(SavingMode.ST_AVIS)
                return [True, adminPanel.init_dialog(title="Prescription ?"), "Prescription ?"]
        elif args[2] is not None and ctx.triggered_id == adminPanel.get_accepter_button().id:
            adminPanel.set_mode(SavingMode.BLOCK_ACCEPTED)
            return [True, adminPanel.init_dialog(title="Motif ?"), "Prescription acceptée"]

        elif args[3] is not None and ctx.triggered_id == adminPanel.get_refuser_button().id:
            adminPanel.set_mode(SavingMode.BLOCK_REFUSED)
            return [True, adminPanel.init_dialog(title="Motif ?"), "Prescription refusée"]
        elif args[1] is not None and ctx.triggered_id == adminPanel.get_cancel_button().id:
            return [False, adminPanel.init_dialog(title="Motif ?"), dash.no_update] 
        elif args[4] is not None and ctx.triggered_id == adminPanel.get_submit().id:
            return [False, dash.no_update, dash.no_update]   
        else:
            return [False, dash.no_update, dash.no_update]
def set_init_admin_panel_callback(adminPanel):
    from pages.modules.components import SavingMode
    @callback(
        Output(adminPanel.get_form(), 'children'),
        Input('url_data','data'),
    )
    def __set__(data):
        st_token = data['st_token']
        mode = SavingMode.ST_AVIS if data['st_token'] is not None else SavingMode.REQUEST_ST
        return adminPanel.init_output(mode)
    @callback(
        [Output(adminPanel.get_trigger_dialog_button(), 'children'), Output(adminPanel.get_email_input(), 'disabled'), Output(adminPanel.get_password_input(), 'disabled'), Output(adminPanel.get_accepter_button(), 'hidden'), Output(adminPanel.get_refuser_button(), 'hidden'), Output(adminPanel.get_trigger_dialog_button(), 'hidden'), Output(adminPanel.get_login_field(), 'hidden')],
        Input('url_data','data'),
    )
    def __set__(data):
        st_token = data['st_token']
        mode = SavingMode.REQUEST_ST if st_token is None else SavingMode.ST_AVIS
        disabled_login = (mode == SavingMode.ST_AVIS) or IS_FILE_CLOSED(data['uuid'])
        disabled_submit = (IS_ST_ALREADY_REQUESTED(data['uuid']) and mode == SavingMode.REQUEST_ST) or  IS_FILE_CLOSED(data['uuid'])
        disabled_block = IS_FILE_CLOSED(data['uuid']) or mode == SavingMode.ST_AVIS
        return [SavingMode.to_str(mode), disabled_login, disabled_login, disabled_block, disabled_block, disabled_submit, disabled_login]

    
        


        

