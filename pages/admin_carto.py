import dash
from dash import html, callback
from dash.dependencies import Output, Input
import dash_leaflet as dl

from pages.modules.data import DROP_ZONE_GEOJSON, URL_DATA_COMP, INFO_BOX_COMP, LIMITES_GEOJSON,FLIGHT,Flight
from pages.modules.config import NS_RENDER, SavingMode,INFO, PageConfig
from pages.modules.components import Carte, FileInfo, FlightSaver,AdminPanel
from pages.modules.components_temp.data_components import IncomingData
from pages.modules.components_temp.global_components import APP_INFO_BOX, CACHE
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
map.addChildren(drop_zone).addChildren(limites)



map = map.addGeoJson(None,id="flight", option=dict(style={'opacity': 0.8}, onEachFeature=NS_RENDER('draw_arrow')))


##  flight
def edit_flight_callback(data):
   flight = data_manager.get_flight_by_uuid(data['uuid']).get_last_flight()
   if flight == None:
      return [None, APP_INFO_BOX.build_message("Flight not found", 'error')]
   return [Flight.build_complete_geojson(flight), APP_INFO_BOX.build_message("Flight found")]

url_data.set_callback([map.get_id('flight'), APP_INFO_BOX.get_output()] , edit_flight_callback, 'data', prevent_initial_call=True)


file_info = FileInfo(config, incoming_data=url_data)
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
      return html.Div([url_data, URL_DATA_COMP(uuid=uuid,security_token=security_token, st_token=st_token), admin_panel,html.Div([map,file_info], style={'display': 'flex', 'flexDirection': 'row', 'height': '100vh'})])
