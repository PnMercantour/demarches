from dash.dependencies import Output
import dash_leaflet as dl
from dash import html, dcc
import dash_bootstrap_components as dbc


from pages.modules.rendering_callback import set_file_info_callback, set_file_state_comp
from pages.modules.config import EDIT_CONTROL, TILE, CENTER, ZOOM, MAP_STYLE, EDIT_CONTROL_NO_EDIT_DRAW, EDIT_CONTROL_EDIT_DRAW, SAVE_BUTTON_ID, SavingMode, STATE_PROPS
from pages.modules.data_callback import set_output_if_edit_callback, set_on_save_callback, set_admin_panel_callback


class Carte(dl.Map):

    def __init__(self, forceEdit=False):
        super().__init__(center=CENTER, zoom=ZOOM, style=MAP_STYLE)
        self.children = []
        self.children.append(TILE)


        self.comp_edit = EDIT_CONTROL()
        self.children.append(dl.FeatureGroup([self.comp_edit]))


        # Dossier info state
        self.dossier_state = html.Div(style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000", "backgroundColor": "white", "borderRadius": "5px", "boxShadow": "2px 2px 2px lightgrey", "padding": "10px","opacity":"0.8"})
        self.children.append(self.dossier_state)

        def state_fnc(file):
            return [html.H3("Etat du dossier :"),html.Div(STATE_PROPS[file['state']]['text'], style={'color': STATE_PROPS[file['state']]['color'], 'font-weight': 'bold', 'font-size': '100%'})]

        set_file_state_comp(self.dossier_state, state_fnc)
        if not forceEdit:
            set_output_if_edit_callback([Output(self.comp_edit, 'draw')], [EDIT_CONTROL_EDIT_DRAW], [EDIT_CONTROL_NO_EDIT_DRAW])


    
    def addGeoJson(self, geojson,id, option=None):
        self.children.append(dl.GeoJSON(data=geojson, id=id, options=option))
        return self
    def addChildren(self, children):
        self.children.append(children)
        return self
    
    def get_comp_edit(self):
        return self.comp_edit



class FileInfo(html.Div):
    def __init__(self):
        super().__init__(id="file-info", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px', 'min-width': '300px', 'margin': '10px', 'min-width': '300px' })

        #Create a skeleton for the file info
        self.number_comp = html.Div()
        self.state_comp = html.Div()
        self.creation_date_comp = html.Div()
        self.can_edit = html.Div(style={'color': 'red'})
        self.children = [
            self.can_edit,
            html.H2("File Info"),
            html.H3("File number : "),
            self.number_comp,
            html.H3("State : "),
            self.state_comp,
            html.H3("Creation date : "),
            self.creation_date_comp
        ]

        set_file_info_callback(self.output())

    def output(self):
        return [Output(self.state_comp, 'children'),Output(self.number_comp, 'children'),Output(self.creation_date_comp, 'children'),Output(self.can_edit, 'children')]




class FlightSaver(html.Button):
    def __init__(self, savingType: SavingMode, map: Carte):
        super().__init__(id=SAVE_BUTTON_ID, children=SavingMode.to_str(savingType), style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.savingType = savingType
        set_on_save_callback(savingType, map.get_comp_edit())

        
class AdminPanel(html.Div):
    def __init__(self, map: Carte):
        super().__init__(id="admin-panel", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px', 'margin': '10px', 'display': 'flex', 'flex-direction': 'row', 'align-items': 'center', 'min-width': '300px'})
        self.admin_email = dcc.Input(type="email", placeholder="Instructeur Email", style={'margin': '10px'})
        self.admin_password = dcc.Input(type="password", placeholder="Instructeur Password", style={'margin': '10px'})


        #Action
        self.request_for_edit = html.Button("Request for edit", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.accepter = html.Button("Accepter", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.refuser = html.Button("Refuser", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})

        self.form = dbc.Form([
                    self.admin_email,
                    self.admin_password,
                    self.request_for_edit,
                    self.accepter,
                    self.refuser
                    ])
        self.children = [
            self.form
        ]

        set_admin_panel_callback(self, map.get_comp_edit())

    
    def get_email_input(self):
        return self.admin_email
    def get_password_input(self):
        return self.admin_password
    def get_request_for_edit_button(self):
        return self.request_for_edit
    def get_accepter_button(self):
        return self.accepter
    def get_refuser_button(self):
        return self.refuser
    def get_form(self):
        return self.form

