
from dash import callback, DiskcacheManager
from dash.dependencies import Input, Output, State
import dash
from pages.modules.data import SECURITY_CHECK, FILE, FLIGHT, SAVE_FLIGHT
from pages.modules.config import EDIT_STATE, INFO, SAVE_BUTTON_ID,SavingMode
from threading import Thread

 # Diskcache for non-production apps when developing locally
import diskcache
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

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
        secu = EDIT_STATE[file['state']] and SECURITY_CHECK(file['number'], {"security-token":data['security_token']})
        print("Is secu : ",secu)
        return data_to_set if secu else default

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
    from pages.modules.data import Background_Task
    import time
    @callback(
        [Output(INFO, 'data',allow_duplicate=True), Output('long-task', "hidden")],
        Input(adminPanel.get_submit(),'n_clicks'),
        [State(adminPanel.get_email_input(), 'value'), State(adminPanel.get_password_input(), 'value'), State(edit_control, 'geojson'), State('url_data','data'), State(adminPanel.get_avis_input(), 'value')],
        prevent_initial_call=True,
    )
    def __set__(n_clicks, email, password, geojson, data, message):
        if n_clicks is not None:
            print(SavingMode.to_str(adminPanel.get_mode()))
            if (email is None or password is None )and adminPanel.get_mode() != SavingMode.ST_AVIS:
                return [{"message":"Please fill the email and password fields"},dash.no_update]
            if len(geojson['features']) == 0 and (adminPanel.get_mode() == SavingMode.REQUEST_ST or adminPanel.get_mode() == SavingMode.UPDATE):
                return [{"message":"No flight to save"},dash.no_update]

            tmp_geojson = None if len(geojson['features']) == 0 else geojson

            uuid=data['uuid']
            (current_flight,_) = FLIGHT(uuid)
            if 'error' in current_flight:
                return  [{'message':"Invalid uuid : " + uuid}, dash.no_update]
            file = FILE(current_flight['dossier_id'])
            flight = (current_flight,tmp_geojson)
            print(f"Saving flight {uuid} with email {email} and password {password}")
            (out,_) = SAVE_FLIGHT(file, flight, adminPanel.get_mode() , {"email":email,"password":password, "st_token":data['st_token']}, message=message)
            
            if 'error' in out:
                return [{'message':out['error']} , dash.no_update]
            elif len(Background_Task) > 0:
                return [{'message': f'Building PDF please wait'} , True]
            else:
                return [{'message': f'Flight saved with uuid {out["uuid"]}'} , dash.no_update]
            
         
        else:
            return [dash.no_update, dash.no_update]

    @callback(
        [Output('long-task', "children"), Output(INFO, 'data',allow_duplicate=True)],
        Input('long-task', "hidden"),
        State('url_data', "data"),
        prevent_initial_call=True,
        background=True,
        manager=background_callback_manager
    )
    def __set__(hidden, data):
        if hidden:
            print('Building PDF')
            print(Background_Task)
            uuid=data['uuid']
            (current_flight,_) = FLIGHT(uuid)
            if current_flight['uuid'] in Background_Task:
                task = Background_Task[current_flight['uuid']]
                task.start()
                task.join()


            return ["", {"message":"Pdf built !"}]
        else:
            return [dash.no_update, dash.no_update]


      