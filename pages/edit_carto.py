import dash
from dash import html
import dash_leaflet as dl
from pages.modules.config import NS_RENDER, PageConfig
from pages.modules.base_components import IncomingData, Carte, DossierInfo, FlightSaver
from pages.modules.data import APP_INFO_BOX, BuiltInCallbackFnc
from pages.modules.managers import DataManager, UserSecurity
dash.register_page(__name__, path='/edit',path_template='/edit/<uuid>')

data_manager = DataManager()
security_manager = UserSecurity(data_manager)

config = PageConfig("edit",data_manager=data_manager, security_manager=security_manager)
# #CREATE MAP
url_data = IncomingData(config)
map = Carte(config, incoming_data=url_data)

## FETCHING FEATURES
Carte.SetAllFeatures(map)

map = map.addGeoJson(None,id="flight", options=dict(style={'opacity': 0.8}, onEachFeature=NS_RENDER('draw_arrow')))



file_info = DossierInfo(config, incoming_data=url_data)
flight_saver = FlightSaver(config, FlightSaver.SAVE_UPDATE, map, url_data)


callbacks = BuiltInCallbackFnc(data_manager)

url_data.set_callback([map.get_id('flight'), APP_INFO_BOX.get_output()],callbacks.flight_fetch, 'data', prevent_initial_call=True)


def layout(uuid=None,security_token=None):
      data = {
            'uuid':uuid,
            'security_token':security_token
      }
      url_data.set_data(data)
      return html.Div([url_data, flight_saver, html.Div([map, file_info], style={'display': 'flex', 'flexDirection': 'row', 'height': '80vh'})])

