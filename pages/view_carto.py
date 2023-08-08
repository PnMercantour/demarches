import dash
from dash import html
import dash_leaflet as dl

from carto_editor import NS_RENDER, BuiltInCallbackFnc, arrow_function, CONTENT_STYLE, DATA_MANAGER
from pages.modules.base_components import IncomingData, Carte, ControlPanel, Manager
from pages.modules.data import APP_INFO_BOX
from pages.modules.managers import UserSecurity

dash.register_page(__name__, path='/view',path_template='/')

## MANAGERS
manager = Manager('view', DATA_MANAGER, UserSecurity(DATA_MANAGER))


data_manager = manager.data_manager
config = manager.config

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

control_panel = ControlPanel(config, map, url_data,True)


def layout(**kwargs):
    url_data.set_data(**kwargs)
    return html.Div([manager, url_data, control_panel,map], style=CONTENT_STYLE)