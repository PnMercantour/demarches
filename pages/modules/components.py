from dash.dependencies import Output
import dash_leaflet as dl
from dash import html, dcc, DiskcacheManager
import dash_bootstrap_components as dbc


from pages.modules.config import PageConfig, TILE, CENTER, ZOOM, MAP_STYLE, EDIT_CONTROL_NO_EDIT_DRAW, EDIT_CONTROL_EDIT_DRAW, SAVE_BUTTON_ID, SavingMode, STATE_PROPS, EDIT_STATE
from pages.modules.data_callback import set_on_save_callback
from pages.modules.interfaces import IBaseComponent
from pages.modules.data import FILE, FLIGHT, SECURITY_CHECK, IS_FILE_CLOSED, IS_ST_ALREADY_REQUESTED, SAVE_FLIGHT
from pages.modules.callback_system import CustomCallback, SingleInputCallback
from pages.modules.components_temp.global_components import LOADING_BOX, APP_INFO_BOX


import diskcache
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

class Carte(dl.Map, IBaseComponent):
    ## Declaring neasted components ids
    FILE_STATE_INFO = "file_state_info"
    EDIT_CONTROL = "edit_control"

    def __fnc_edit_control_allow_edit__(data):
        #TODO: refacto
        (flight,_) = FLIGHT(data['uuid'])
        if 'error' in flight:
            return EDIT_CONTROL_NO_EDIT_DRAW
        file = FILE(flight['dossier_id'])
        secu = EDIT_STATE[file['state']] and SECURITY_CHECK(file['number'], {"security-token":data['security_token']})
        print("Is secu : ",secu)
        return EDIT_CONTROL_EDIT_DRAW if secu else EDIT_CONTROL_NO_EDIT_DRAW

    def __fnx_file_state_info_init__(data):
        #TODO: refacto
        (info,_) = FLIGHT(data['uuid'])
        if 'error' in info:
            return None
        file = FILE(info['dossier_id'], force_update=True)
        return [html.H3("Etat du dossier :"),html.Div(STATE_PROPS[file['state']]['text'], style={'color': STATE_PROPS[file['state']]['color'], 'fontWeight': 'bold', 'fontSize': '100%'})]


    def __init__(self,pageConfig : PageConfig, forceEdit=False, incoming_data : CustomCallback = None):
        IBaseComponent.__init__(self, pageConfig)
        dl.Map.__init__(self, id=self.get_prefix(), center=CENTER, zoom=ZOOM, style=MAP_STYLE)
        self.children = []
        self.children.append(TILE)


        self.comp_edit = dl.EditControl(draw=EDIT_CONTROL_EDIT_DRAW, id=self.set_id(Carte.EDIT_CONTROL))
        self.children.append(dl.FeatureGroup([self.comp_edit]))


        # Dossier info state
        self.dossier_state = html.Div(id=self.set_id(Carte.FILE_STATE_INFO),style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000", "backgroundColor": "white", "borderRadius": "5px", "boxShadow": "2px 2px 2px lightgrey", "padding": "10px","opacity":"0.8"})
        self.children.append(self.dossier_state)

        if incoming_data != None:
            incoming_data.set_callback(self.get_id(Carte.FILE_STATE_INFO), Carte.__fnx_file_state_info_init__)
            if not forceEdit:
                incoming_data.set_callback([self.get_id(Carte.EDIT_CONTROL)], Carte.__fnc_edit_control_allow_edit__, ['draw'])
           

        self.set_internal_callback()
    
    def addGeoJson(self, geojson,id, option=None):
        self.children.append(dl.GeoJSON(data=geojson, id=self.set_id(id), options=option))
        return self
    def addChildren(self, children):
        self.children.append(children)
        return self
    
    def get_comp_edit(self):
        return self.get_id(Carte.EDIT_CONTROL)



class FileInfo(html.Div, IBaseComponent):
    # Style
    
    # ID
    F_NUMBER = 'field_number'
    F_STATE = 'field_state'
    F_CREATION_DATE = 'field_creation_date'
    F_CAN_EDIT = 'field_can_edit'


    def __fnc_panel_init__(data):
        #TODO: refacto
        (info,_) = FLIGHT(data['uuid'])
        if 'error' in info:
            return ["None","None","None","Invalid uuid"]
        data = FILE(info['dossier_id'])
        return [data['state'],data['number'],data['creation_date'], f"Can edit : {EDIT_STATE[data['state']]}"]

    def __get_layout__(self):
        return [
            html.Div(id = self.set_id(FileInfo.F_CAN_EDIT)),
            html.H2("File Info"),
            html.H3("File number : "),
            html.Div(id = self.set_id(FileInfo.F_NUMBER)),
            html.H3("State : "),
            html.Div(id = self.set_id(FileInfo.F_STATE)),
            html.H3("Creation date : "),
            html.Div(id = self.set_id(FileInfo.F_CREATION_DATE))
        ]

        

    def __init__(self,pageConfig: PageConfig, incoming_data : CustomCallback):
        IBaseComponent.__init__(self, pageConfig)
        html.Div.__init__(self, children=self.__get_layout__(), id=self.get_prefix(), style=self.__get_root_style__())

        #Create a skeleton for the file info
        incoming_data.set_callback([self.get_id(FileInfo.F_STATE), self.get_id(FileInfo.F_NUMBER),self.get_id(FileInfo.F_CREATION_DATE),self.get_id(FileInfo.F_CAN_EDIT)], FileInfo.__fnc_panel_init__)


class FlightSaver(html.Button):
    def __init__(self, savingType: SavingMode, map: Carte):
        super().__init__(id=SAVE_BUTTON_ID, children=SavingMode.to_str(savingType), style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.savingType = savingType
        set_on_save_callback(savingType, map.get_comp_edit())

        
class AdminPanel(html.Div, IBaseComponent):
    ## STYLE
    BUTTON_STYLE = {'margin':'1vh','backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'}
    FIELD_STYLE = {'margin':'1vh','height': '30px', 'lineHeight': '30px', 'borderRadius': '5px', 'border': '1px solid lightgrey', 'padding': '0px 10px'}
    ## ID
    B_TRIGGER_DIALOG = 'b_trigger_dialog'
    B_SUBMIT = 'b_submit'
    B_CANCEL = 'b_cancel'
    B_REFUSER = 'b_reject'
    B_ACCEPTER = 'b_accept'
    F_EMAIL = 'f_email'
    F_PASSWORD = 'f_password'
    F_AVIS = 'f_avis'
    LOGIN_FIELD = 'login_field'
    DIALOG_BOX = 'dialog_box'
    FORM = 'form'

    def __fnc_admin_panel_init__(self, data):
        #TODO: refacto STATE COMPONENT
        st_token = data['st_token']
        print(st_token)
        mode = SavingMode.ST_AVIS if data['st_token'] is not None else SavingMode.REQUEST_ST
        return self.init_output(mode,data)

    def __init__(self,pageConfig: PageConfig, map: Carte, incoming_data : CustomCallback):
        IBaseComponent.__init__(self, pageConfig)
        super().__init__(children=self.init_output(SavingMode.REQUEST_ST), id=self.get_prefix(), style=self.__get_root_style__())
        self.incoming_data = incoming_data
        self.map = map
        
        # self.trigger_dialog_button = html.Button("...", style=AdminPanel.BUTTON_STYLE)
        # self.submit = html.Button("...", style=AdminPanel.BUTTON_STYLE)
        # self.admin_email = dcc.Input(type="email", placeholder="Instructeur Email", style=AdminPanel.FIELD_STYLE)
        # self.admin_password = dcc.Input(type="password", placeholder="Instructeur Password", style=AdminPanel.FIELD_STYLE)
        # self.accepter = html.Button(id=self.set_id(AdminPanel.B_ACCEPTER),children="Accepter", style=AdminPanel.BUTTON_STYLE)
        # self.refuser = html.Button("Refuser", style=AdminPanel.BUTTON_STYLE)
        # self.avis = dcc.Input(type="text", placeholder="...", style=AdminPanel.FIELD_STYLE)
        # self.cancel = html.Button("Cancel", style=AdminPanel.BUTTON_STYLE)
        # self.login_field = html.Div([
        #     self.admin_email,
        #     self.admin_password,
        # ])

        
        # self.dialog = html.Dialog([
        #     html.H3("Prescription ? :"),
        #     self.avis,
        #     self.submit,
        #     self.cancel,

        # ], style={"zIndex":"900"},id=self.set_id(AdminPanel.DIALOG_BOX),open=False)
        # self.form = dbc.Form([
        #     self.login_field,
        #     self.trigger_dialog_button,
        #     self.accepter,
        #     self.refuser,
        # ], id=self.set_id(AdminPanel.FORM))
        # self.children = [
        #     self.dialog,
        #     self.form,
        # ]

        self.set_internal_callback()
        
        # set_init_admin_panel_callback(self)
        incoming_data.set_callback(self.get_prefix(), self.__fnc_admin_panel_init__, "children")
        

        # set_trigger_dialog_box(self)
        # set_admin_panel_callback(self, map.get_comp_edit())
        self.set_submit_action()
    # def init_dialog(self, title="Prescription ?"):
    #     return html.Div([
    #         html.H3(title),
    #         self.avis,
    #         self.submit,
    #         self.cancel,
    #     ])

    def set_submit_action(self):
        from pages.modules.data import Background_Task
        from dash import no_update
        import time
        callback_builder = SingleInputCallback(self.get_id(AdminPanel.B_SUBMIT),input_prop = "n_clicks")
        callback_builder.add_state(self.get_id(AdminPanel.F_EMAIL), "value")
        callback_builder.add_state(self.get_id(AdminPanel.F_PASSWORD), "value")
        callback_builder.add_state(self.map.get_comp_edit(), "geojson")
        callback_builder.add_state(self.incoming_data, "data")
        callback_builder.add_state(self.get_id(AdminPanel.F_AVIS), "value")


        def __set__(n_clicks, email, password, geojson, data, message):
            if n_clicks is not None:
                print(SavingMode.to_str(self.get_mode()))
                if (email is None or password is None )and self.get_mode() != SavingMode.ST_AVIS:
                    return [{"message":"Please fill the email and password fields", "type":"error"},no_update]
                if len(geojson['features']) == 0 and (self.get_mode() == SavingMode.REQUEST_ST or self.get_mode() == SavingMode.UPDATE):
                    return [{"message":"No flight to save", "type":"error"},no_update]

                tmp_geojson = None if len(geojson['features']) == 0 else geojson

                uuid=data['uuid']
                (current_flight,_) = FLIGHT(uuid)
                if 'error' in current_flight:
                    return  [{'message':"Invalid uuid : " + uuid, "type":"error"}, no_update]
                file = FILE(current_flight['dossier_id'])
                flight = (current_flight,tmp_geojson)
                print(f"Saving flight {uuid} with email {email} and password {password}")
                (out,_) = SAVE_FLIGHT(file, flight, self.get_mode() , {"email":email,"password":password, "st_token":data['st_token']}, message=message)
                
                if 'error' in out:
                    return [{'message':out['error'], "type":"error"} , no_update]
                elif len(Background_Task) > 0:
                    return [{'message': f'Building PDF please wait'} , True]
                else:
                    return [{'message': f'Flight saved with uuid {out["uuid"]}'} , no_update]
            else:
                return [no_update, no_update]
        callback_builder.set_callback([APP_INFO_BOX.get_output(), LOADING_BOX.get_trigger_id()], __set__, ['data', 'hidden'], prevent_initial_call=True)

        from pages.modules.data import Background_Task

        callback_builder_long = SingleInputCallback(LOADING_BOX.get_trigger_id(),input_prop = "hidden")
        callback_builder_long.add_state(self.incoming_data, "data")
        def __set_long_callback_(hidden, data):
            if hidden:
                print('Building PDF')
                print(Background_Task)
                uuid=data['uuid']
                (current_flight,_) = FLIGHT(uuid)
                if current_flight['uuid'] in Background_Task:
                    task = Background_Task[current_flight['uuid']]
                    task.start()
                    task.join()


                return ["", {"message":"Pdf built !", 'type':'success'}]
            else:
                return [no_update, no_update]

        callback_builder_long.set_callback([LOADING_BOX.get_trigger_id(),APP_INFO_BOX.get_output()], __set_long_callback_, ['children', 'data'], prevent_initial_call=True, background=True, manager=background_callback_manager)



    def init_output(self, mode: SavingMode, data=None):
        #TODO: refacto STATE COMPONENT
        disabled_block = True
        disabled_submit = True
        disabled_login = True
        
        if data != None:
            disabled_login = (mode == SavingMode.ST_AVIS) or IS_FILE_CLOSED(data['uuid'])
            disabled_submit = (IS_ST_ALREADY_REQUESTED(data['uuid']) and mode == SavingMode.REQUEST_ST) or  IS_FILE_CLOSED(data['uuid'])
            disabled_block = IS_FILE_CLOSED(data['uuid']) or mode == SavingMode.ST_AVIS
        self.mode = mode
        return html.Div([
            dbc.Form([
                html.Div([
                    dcc.Input(type="email", placeholder="Instructeur Email", style=AdminPanel.FIELD_STYLE, disabled=disabled_login, id=self.set_id(AdminPanel.F_EMAIL)),
                    dcc.Input(type="password", placeholder="Instructeur Password", style=AdminPanel.FIELD_STYLE, disabled=disabled_login, id=self.set_id(AdminPanel.F_PASSWORD)),
                ],id=self.set_id(AdminPanel.LOGIN_FIELD), hidden=disabled_login),
                html.Button(SavingMode.to_str(mode), style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_TRIGGER_DIALOG), hidden=disabled_submit),
                html.Button(id=self.set_id(AdminPanel.B_ACCEPTER),children="Accepter", style=AdminPanel.BUTTON_STYLE, hidden=disabled_block),
                html.Button("Refuser", style=AdminPanel.BUTTON_STYLE, hidden=disabled_block, id=self.set_id(AdminPanel.B_REFUSER)),
            ],id=self.set_id(AdminPanel.FORM)),
            html.Dialog([
                html.H3("Prescription ? :" if mode == SavingMode.ST_AVIS else "Commentaire ? :"),
                dcc.Input(type="text", placeholder="", style=AdminPanel.FIELD_STYLE, id=self.set_id(AdminPanel.F_AVIS)),
                html.Button("Envoyer", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_SUBMIT)),
                html.Button("Annuler", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_CANCEL))
            ], style={"zIndex":"900"},id=self.set_id(AdminPanel.DIALOG_BOX),open=False)
        ])

    def set_internal_callback(self):
        from dash import callback, no_update
        from dash import callback_context as ctx
        from dash.dependencies import Input, Output, State

        ## INIT DIALOG
        @callback(
        Output(self.get_id(AdminPanel.DIALOG_BOX), 'open'),
        [Input(self.get_id(AdminPanel.B_TRIGGER_DIALOG),'n_clicks'), Input(self.get_id(AdminPanel.B_CANCEL),'n_clicks'), Input(self.get_id(AdminPanel.B_ACCEPTER),'n_clicks'), Input(self.get_id(AdminPanel.B_REFUSER),'n_clicks'), Input(self.get_id(AdminPanel.B_SUBMIT),'n_clicks')],
        prevent_initial_call=True,
        )
        def __set__(*args):
            #TODO: refacto STATE COMPONENT
            print(ctx.triggered_id)
            if args[0] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_TRIGGER_DIALOG):

                return True
            elif args[2] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_ACCEPTER):
                self.mode = SavingMode.BLOCK_ACCEPTED
                return True
            elif args[3] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_REFUSER):
                self.mode = SavingMode.BLOCK_REFUSED
                return True
            elif args[1] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_CANCEL):
                return False
            elif args[4] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_SUBMIT):
                return False
            else:
                return False

    def set_mode(self, mode: SavingMode):
        self.mode = mode
    
    # def get_login_field(self):
    #     return self.get_id(AdminPanel.LOGIN_FIELD)
    # def get_children(self):
    #     return self.children
    # def get_mode(self):
    #     return self.mode
    # def get_email_input(self):
    #     return self.get_id(AdminPanel.F_EMAIL)
    # def get_password_input(self):
    #     return self.get_id(AdminPanel.F_PASSWORD)
    # def get_submit(self):
    #     return self.get_id(AdminPanel.B_SUBMIT)
    # def get_accepter_button(self):
    #     return self.get_id(AdminPanel.B_ACCEPTER)
    # def get_refuser_button(self):
    #     return self.get_id(AdminPanel.B_REFUSER)
    # def get_form(self):
    #     return self.get_id(AdminPanel.FORM)
    # def get_avis_input(self):
    #     return self.get_id(AdminPanel.F_AVIS)
    # def get_trigger_dialog_button(self):
    #     return self.get_id(AdminPanel.B_TRIGGER_DIALOG)
    # def get_dialog(self):
    #     return self.get_id(AdminPanel.DIALOG_BOX)
    # def get_cancel_button(self):
    #     return self.get_id(AdminPanel.B_CANCEL)

