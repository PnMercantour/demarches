from dash.dependencies import Output
import dash_leaflet as dl
from dash import html, dcc

from pages.modules.rendering_callback import set_file_info_callback
from pages.modules.config import EDIT_CONTROL, TILE, CENTER, ZOOM, MAP_STYLE, EDIT_CONTROL_ID, EDIT_CONTROL_NO_EDIT_DRAW, EDIT_CONTROL_EDIT_DRAW, SAVE_BUTTON_ID, SavingMode
from pages.modules.data_callback import set_output_if_edit_callback, set_on_save_callback


class Carte(dl.Map):

    def __init__(self, canEdit=False):
        super().__init__(center=CENTER, zoom=ZOOM, id="map", style=MAP_STYLE)
        self.children = []
        self.children.append(TILE)

        if canEdit:
            self.comp_edit = EDIT_CONTROL
            self.children.append(self.comp_edit)

        set_output_if_edit_callback([Output(EDIT_CONTROL_ID, 'draw')], [EDIT_CONTROL_EDIT_DRAW], [EDIT_CONTROL_NO_EDIT_DRAW])


    
    def addGeoJson(self, geojson,id, option=None):
        self.children.append(dl.GeoJSON(data=geojson, id=id, options=option))
        return self
    def addChildren(self, children):
        self.children.append(children)
        return self



class FileInfo(html.Div):
    def __init__(self):
        super().__init__(id="file-info", style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})

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
    def __init__(self, savingType: SavingMode):
        super().__init__(id=SAVE_BUTTON_ID, children=SavingMode.to_str(savingType), style={'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'})
        self.savingType = savingType
        set_on_save_callback(savingType)

        



