import dash
from dash import html
import dash_leaflet as dl

from pages.modules.data import BuiltInCallbackFnc
from pages.modules.config import NS_RENDER, PageConfig
from pages.modules.base_components import IncomingData, Carte, DossierInfo,AdminPanel
from pages.modules.data import APP_INFO_BOX
from pages.modules.managers import DataManager, AdminSecurity, STSecurity

dash.register_page(__name__, path='/admin',path_template='/admin/<uuid>')

## MANAGERS
data_manager = DataManager()
admin_security_manager = AdminSecurity(data_manager)
st_security_manager = STSecurity(data_manager)


config = PageConfig("admin", data_manager, admin_security_manager)
url_data = IncomingData(config)






## CREATE MAP
map = Carte(config,forceEdit=True,incoming_data=url_data)

## FETCHING FEATURES
Carte.SetAllFeatures(map)

map.addGeoJson(None,id="flight", options=dict(style={'opacity': 0.8}, onEachFeature=NS_RENDER('draw_arrow')))


callbacks = BuiltInCallbackFnc(data_manager)


url_data.set_callback([map.get_id('flight'), APP_INFO_BOX.get_output()] , callbacks.flight_fetch, 'data', prevent_initial_call=True)


file_info = DossierInfo(config, incoming_data=url_data)
admin_panel = AdminPanel(config, map, url_data)

def layout(uuid=None,security_token=None,st_token=None,**kwargs):
      data = {
            'uuid':uuid,
            'security_token':security_token,
            'st_token':st_token
      }
      if st_token != None:
            config.security_manager = st_security_manager
      url_data.set_data(data)
      return html.Div([url_data, admin_panel,html.Div([map,file_info], style={'display': 'flex', 'flexDirection': 'row', 'height':"60vh"})],style={'height':'80vh'})
