from dash.dependencies import Output
import dash_leaflet as dl
from dash import html, dcc
import dash_bootstrap_components as dbc


from pages.modules.rendering_callback import set_trigger_dialog_box, set_init_admin_panel_callback
from pages.modules.config import PageConfig, TILE, CENTER, ZOOM, MAP_STYLE, EDIT_CONTROL_NO_EDIT_DRAW, EDIT_CONTROL_EDIT_DRAW, SAVE_BUTTON_ID, SavingMode, STATE_PROPS, EDIT_STATE
from pages.modules.data_callback import set_on_save_callback, set_admin_panel_callback
from pages.modules.interfaces import IBaseComponent
from pages.modules.data import FILE, FLIGHT, SECURITY_CHECK
from pages.modules.callback_system import CustomCallback

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
            incoming_data.set_callback([self.get_id(Carte.FILE_STATE_INFO)], Carte.__fnx_file_state_info_init__)
            if not forceEdit:
                incoming_data.set_callback([self.get_id(Carte.EDIT_CONTROL)], Carte.__fnc_edit_control_allow_edit__, ['draw'])
           

        self.set_internal_callback()
    
    def addGeoJson(self, geojson,id, option=None):
        self.children.append(dl.GeoJSON(data=geojson, id=id, options=option))
        return self
    def addChildren(self, children):
        self.children.append(children)
        return self
    
    def get_comp_edit(self):
        return self.comp_edit



class FileInfo(html.Div, IBaseComponent):
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



    def __init__(self,pageConfig: PageConfig, incoming_data : CustomCallback = None):
        IBaseComponent.__init__(self, pageConfig)
        html.Div.__init__(self, id=self.get_prefix(), style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px', 'minWidth': '300px', 'margin': '10px', 'minWidth': '300px' })

        #Create a skeleton for the file info
        self.children = [
            html.Div(id = self.set_id(FileInfo.F_CAN_EDIT)),
            html.H2("File Info"),
            html.H3("File number : "),
            html.Div(id = self.set_id(FileInfo.F_NUMBER)),
            html.H3("State : "),
            html.Div(id = self.set_id(FileInfo.F_STATE)),
            html.H3("Creation date : "),
            html.Div(id = self.set_id(FileInfo.F_CREATION_DATE))
        ]

        if incoming_data != None:
            incoming_data.set_callback([self.get_id(FileInfo.F_STATE), self.get_id(FileInfo.F_NUMBER),self.get_id(FileInfo.F_CREATION_DATE),self.get_id(FileInfo.F_CAN_EDIT)], FileInfo.__fnc_panel_init__)


class FlightSaver(html.Button):
    def __init__(self, savingType: SavingMode, map: Carte):
        super().__init__(id=SAVE_BUTTON_ID, children=SavingMode.to_str(savingType), style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.savingType = savingType
        set_on_save_callback(savingType, map.get_comp_edit())

        
class AdminPanel(html.Div):
    def __init__(self, map: Carte):
        super().__init__(id="admin-panel", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px', 'margin': '10px', 'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', 'minWidth': '300px'})
       

        
        self.trigger_dialog_button = html.Button("...", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.submit = html.Button("...",id="zaezreaz", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.admin_email = dcc.Input(type="email", placeholder="Instructeur Email", style={'margin': '10px'})
        self.admin_password = dcc.Input(type="password", placeholder="Instructeur Password", style={'margin': '10px'})
        self.accepter = html.Button("Accepter", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.refuser = html.Button("Refuser", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.avis = dcc.Input(type="text", placeholder="...", style={'margin': '10px'})
        self.cancel = html.Button("Cancel", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.login_field = html.Div([
            self.admin_email,
            self.admin_password,
        ])

        
        self.dialog = html.Dialog([
            html.H3("Prescription ? :"),
            self.avis,
            self.submit,
            self.cancel,

        ], style={"zIndex":"900"}, open=False)
        self.form = dbc.Form([
            self.login_field,
            self.trigger_dialog_button,
            self.accepter,
            self.refuser,
        ])
        self.children = [
            self.dialog,
            self.form,
        ]
        
        set_init_admin_panel_callback(self)
        set_trigger_dialog_box(self)
        set_admin_panel_callback(self, map.get_comp_edit())

    def init_dialog(self, title="Prescription ?"):
        return html.Div([
            html.H3(title),
            self.avis,
            self.submit,
            self.cancel,
        ])

    def init_output(self, mode: SavingMode, title="Prescription ?"):
        self.mode = mode
        return html.Div([
            self.login_field,
            self.trigger_dialog_button,
            self.accepter,
            self.refuser,
        ])

    def set_mode(self, mode: SavingMode):
        self.mode = mode
    
    def get_login_field(self):
        return self.login_field
    def get_children(self):
        return self.children
    def get_mode(self):
        return self.mode
    def get_email_input(self):
        return self.admin_email
    def get_password_input(self):
        return self.admin_password
    def get_submit(self):
        return self.submit
    def get_accepter_button(self):
        return self.accepter
    def get_refuser_button(self):
        return self.refuser
    def get_form(self):
        return self.form
    def get_avis_input(self):
        return self.avis
    def get_trigger_dialog_button(self):
        return self.trigger_dialog_button
    def get_dialog(self):
        return self.dialog
    def get_cancel_button(self):
        return self.cancel

