import dash
from dash import html
import dash_leaflet as dl

from carto_editor import NS_RENDER, PageConfig, BuiltInCallbackFnc, arrow_function
from pages.modules.base_components import IncomingData, Carte
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

Carte.SetAllFeatures(map)

map.addGeoJson(None,id="flight",
options=dict(style=NS_RENDER('flight_style'), onEachFeature=NS_RENDER('flight_init')),
hoverStyle=arrow_function(dict(weight=8, color='#ff9999', dashArray='')),
)


callbacks = BuiltInCallbackFnc(data_manager)
url_data.set_callback([map.get_id('flight'), APP_INFO_BOX.get_output()], callbacks.flight_fetch, 'data',prevent_initial_call=True)



def layout(uuid:str = None):
    data = {
        'uuid':uuid,
    }
    url_data.set_data(data)
    return html.Div([url_data, map], style={'height': '80vh'})