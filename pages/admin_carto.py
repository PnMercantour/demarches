import dash
from dash import html, callback
from dash.dependencies import Output, Input
import dash_leaflet as dl

from pages.modules.data import DROP_ZONE_GEOJSON, URL_DATA_COMP, INFO_BOX_COMP, LIMITES_GEOJSON
from pages.modules.config import NS_RENDER, SavingMode,INFO, PageConfig
from pages.modules.components import Carte, FileInfo, FlightSaver,AdminPanel

from pages.modules.components_temp.data_components import IncomingData


dash.register_page(__name__, path='/admin',path_template='/admin/<uuid>')
config = PageConfig("admin")
# #CREATE MAP
map = Carte(config,forceEdit=True).addChildren(DROP_ZONE_GEOJSON).addChildren(LIMITES_GEOJSON)
map = map.addGeoJson(None,id="flight", option=dict(style={'opacity': 0.8}, onEachFeature=NS_RENDER('draw_arrow')))
file_info = FileInfo(config)
admin_panel = AdminPanel(map)
url_data = IncomingData(config)


def test(data):
   print(data)
   return [{'message': 'test'}]

url_data.set_callback([INFO], test, 'data')

def layout(uuid=None,security_token=None,st_token=None,**kwargs):
      data = {
            'uuid':uuid,
            'security_token':security_token,
            'st_token':st_token
      }
      url_data.set_data(data)
      return html.Div([url_data, URL_DATA_COMP(uuid=uuid,security_token=security_token, st_token=st_token), admin_panel,html.Div([map,file_info], style={'display': 'flex', 'flexDirection': 'row', 'height': '100vh'})])
