import dash
from dash import html
import dash_leaflet as dl

from carto_editor import NS_RENDER, PageConfig, BuiltInCallbackFnc
from pages.modules.base_components import IncomingData, Carte, FlightSaver
from pages.modules.data import APP_INFO_BOX, CACHE
from pages.modules.managers import DataManager, UserSecurity

dash.register_page(__name__, path='/view',path_template='/')

## MANAGERS
data_manager = DataManager()
security_manager = UserSecurity(data_manager)

config = PageConfig("view", data_manager, security_manager)

url_data = IncomingData(config)

## CREATE MAP
map = Carte(config,forceEdit=True,incoming_data=url_data)

## FETCHING FEATURES
limites_data = CACHE.get_feature('limites', security_manager)
drop_zone_data = CACHE.get_feature('drop_zone', security_manager)

drop_zone = dl.GeoJSON(data=drop_zone_data,id=map.set_id("comp_drop_zone"),options=dict(pointToLayer=NS_RENDER('draw_drop_zone')),cluster=True, superClusterOptions=dict(radius=200))
limites =  dl.GeoJSON(data=limites_data,id=map.set_id("comp_limites"),options=dict(style=NS_RENDER('get_limits_style')))
map = map.addChildren(drop_zone).addChildren(limites)
map.addGeoJson(None,id="flight", option=dict(style={'opacity': 0.8}, onEachFeature=NS_RENDER('draw_arrow')))



callbacks = BuiltInCallbackFnc(data_manager)
url_data.set_callback([map.get_id('flight'), APP_INFO_BOX.get_output()], callbacks.flight_fetch, 'data',prevent_initial_call=True)



def layout(uuid:str = None):
    data = {
        'uuid':uuid,
    }
    url_data.set_data(data)
    return html.Div([url_data, map], style={'height': '80vh'})