import dash
from dash import html
import dash_leaflet as dl

from pages.modules.data import BuiltInCallbackFnc
from pages.modules.config import NS_RENDER, PageConfig
from pages.modules.base_components import IncomingData, Carte, DossierInfo,AdminPanel
from pages.modules.data import APP_INFO_BOX, CACHE
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
limites_data = CACHE.get_feature('limites', admin_security_manager) 
drop_zone_data = CACHE.get_feature('drop_zone', admin_security_manager)

drop_zone = dl.GeoJSON(data=drop_zone_data,id=map.set_id("comp_drop_zone"),options=dict(pointToLayer=NS_RENDER('draw_drop_zone')),cluster=True, superClusterOptions=dict(radius=200))
limites =  dl.GeoJSON(data=limites_data,id=map.set_id("comp_limites"),options=dict(style=NS_RENDER('get_limits_style')))

## ADD FEATURES TO MAP
map = map.addChildren(drop_zone).addChildren(limites)



map.addGeoJson(None,id="flight", option=dict(style={'opacity': 0.8}, onEachFeature=NS_RENDER('draw_arrow')))


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
