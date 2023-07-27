import dash_leaflet as dl
from dash import html
from demarches_simpy import DossierState

from carto_editor import PageConfig,CENTER, ZOOM,TILE, STATE_PROPS, EDIT_CONTROL_EDIT_DRAW, EDIT_CONTROL_NO_EDIT_DRAW

from pages.modules.interfaces import IBaseComponent
from pages.modules.callbacks import CustomCallback


class Carte(dl.Map, IBaseComponent):
    # Style
    FILE_STATE_ITEM_STYLE = lambda state : {'color': STATE_PROPS[state]['color'], 'fontWeight': 'bold', 'fontSize': '100%'}
    FILE_STATE_STYLE = {'position': 'absolute', 'top': '10px', 'right': '10px', 'zIndex': '1000', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px', 'border': '1px solid black', 'opacity': '0.8'}
    ## Declaring neasted components ids
    FILE_STATE_INFO = "file_state_info"
    EDIT_CONTROL = "edit_control"

    def __fnc_edit_control_allow_edit__(self, data):
        flight = self.config.data_manager.get_flight_by_uuid(data['uuid'])
        if flight is None:
            return EDIT_CONTROL_NO_EDIT_DRAW
        dossier = flight.get_attached_dossier()
        secu = not self.config.data_manager.is_file_closed(dossier) and dossier.get_dossier_state() == DossierState.CONSTRUCTION
        return EDIT_CONTROL_EDIT_DRAW if secu else EDIT_CONTROL_NO_EDIT_DRAW

    def __fnc_file_state_info_init__(self, data):
        flight = self.config.data_manager.get_flight_by_uuid(data['uuid'])
        if flight is None:
            return html.Div()
        dossier = flight.get_attached_dossier()
        state = dossier.get_dossier_state().value
        return [html.H3("Etat du dossier :"),html.Div(STATE_PROPS[state]['text'], style=Carte.FILE_STATE_ITEM_STYLE(state))]

    def __get_root_style__(self):
        return {'width': '100%', 'height': '100%', 'margin': "auto", "display": "block"}
    def __init__(self,pageConfig : PageConfig, incoming_data : CustomCallback, forceEdit=False):
        IBaseComponent.__init__(self, pageConfig)
        dl.Map.__init__(self, id=self.get_prefix(), center=CENTER, zoom=ZOOM, style=self.__get_root_style__())
        self.children = []
        self.children.append(TILE)


        self.comp_edit = dl.EditControl(draw=EDIT_CONTROL_EDIT_DRAW, id=self.set_id(Carte.EDIT_CONTROL))
        self.children.append(dl.FeatureGroup([self.comp_edit]))

        # Dossier info state
        self.dossier_state = html.Div(id=self.set_id(Carte.FILE_STATE_INFO),style=self.FILE_STATE_STYLE)
        self.children.append(self.dossier_state)

        incoming_data.set_callback(self.get_id(Carte.FILE_STATE_INFO), self.__fnc_file_state_info_init__)
        if not forceEdit:
            incoming_data.set_callback(self.get_id(Carte.EDIT_CONTROL), self.__fnc_edit_control_allow_edit__, 'draw')
        

        self.set_internal_callback()
    
    def addGeoJson(self, geojson,id, option=None):
        self.children.append(dl.GeoJSON(data=geojson, id=self.set_id(id), options=option))
        return self
    def addChildren(self, children):
        self.children.append(children)
        return self
    
    def get_comp_edit(self):
        return self.get_id(Carte.EDIT_CONTROL)
