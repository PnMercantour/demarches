import dash
from dash import html, callback
from dash.dependencies import Output, Input
import dash_leaflet as dl

from pages.modules.data import DROP_ZONE_GEOJSON, URL_DATA_COMP, INFO_BOX_COMP, LIMITES_GEOJSON
from pages.modules.config import NS_RENDER, SavingMode, PageConfig
from pages.modules.components import Carte, FileInfo, FlightSaver
from pages.modules.rendering_callback import set_flight_callback, set_info_listener_callback
from pages.modules.components_temp.data_components import IncomingData
dash.register_page(__name__, path='/edit',path_template='/edit/<uuid>/<security_token>')

config = PageConfig("edit")
# #CREATE MAP
url_data = IncomingData(config)
map = Carte(config, incoming_data=url_data).addChildren(DROP_ZONE_GEOJSON).addChildren(LIMITES_GEOJSON)
map = map.addGeoJson(None,id="flight", option=dict(style={'opacity': 0.8}, onEachFeature=NS_RENDER('draw_arrow')))
file_info = FileInfo(config, incoming_data=url_data)
flight_saver = FlightSaver(SavingMode.UPDATE, map)


def layout(uuid=None,security_token=None):
   data = {
         'uuid':uuid,
         'security_token':security_token
   }
   url_data.set_data(data)


   return html.Div([url_data, URL_DATA_COMP(uuid=uuid,security_token=security_token),map, flight_saver,file_info], style={'display': 'flex', 'flexDirection': 'row', 'height': '100vh'})

## CALLBACKS

set_info_listener_callback()
set_flight_callback()




