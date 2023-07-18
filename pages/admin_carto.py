import dash
from dash import html, callback
from dash.dependencies import Output, Input
import dash_leaflet as dl

from pages.modules.data import DROP_ZONE_GEOJSON, URL_DATA_COMP, INFO_BOX_COMP, LIMITES_GEOJSON
from pages.modules.config import NS_RENDER, SavingMode
from pages.modules.components import Carte, FileInfo, FlightSaver,AdminPanel
from pages.modules.rendering_callback import set_flight_callback, set_info_listener_callback
dash.register_page(__name__, path='/admin',path_template='/admin/<uuid>')

# #CREATE MAP
map = Carte(forceEdit=True).addChildren(DROP_ZONE_GEOJSON).addChildren(LIMITES_GEOJSON)
map = map.addGeoJson(None,id="flight", option=dict(style={'opacity': 0.8}, onEachFeature=NS_RENDER('draw_arrow')))
file_info = FileInfo()
admin_panel = AdminPanel(map)

def layout(uuid=None,security_token=None,st_token=None,**kwargs):
   return html.Div([URL_DATA_COMP(uuid=uuid,security_token=security_token, st_token=st_token), admin_panel,html.Div([map,file_info], style={'display': 'flex', 'flexDirection': 'row', 'height': '100vh'})])
