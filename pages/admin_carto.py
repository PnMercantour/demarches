import dash
from dash import html
import dash_leaflet as dl

from pages.modules.data import BuiltInCallbackFnc
from pages.modules.config import NS_RENDER, PageConfig, arrow_function, CONTENT_STYLE
from pages.modules.base_components import IncomingData, Carte, DossierInfo,AdminPanel, ControlPanel, Manager
from pages.modules.data import APP_INFO_BOX, SELECTOR, DATA_MANAGER
from pages.modules.managers import AdminSecurity, STSecurity

dash.register_page(__name__, path='/admin',path_template='/admin')

## MANAGERS
manager = Manager("admin", DATA_MANAGER, AdminSecurity(DATA_MANAGER))

config = manager.config
data_manager = manager.data_manager
url_data = IncomingData(config)






## CREATE MAP
map = Carte(config,forceEdit=True,incoming_data=url_data)

## FETCHING FEATURES
Carte.SetAllFeatures(map)

map.addGeoJson(None,id="flight",
options=dict(style=NS_RENDER('flight_style'), onEachFeature=NS_RENDER('flight_init')),
hoverStyle=arrow_function(dict(weight=8, color='#ff9999', dashArray='')),
hideout=dict(selected='none')
)

SELECTOR.add_geojson(map.get_id('flight'))
SELECTOR.set_callback(map.get_id('flight'), lambda selected : dict(selected=selected), 'hideout', prevent_initial_call=True)

callbacks = BuiltInCallbackFnc(data_manager)


url_data.set_callback([map.get_id('flight'), APP_INFO_BOX.get_output(), SELECTOR.get_output()] , callbacks.flight_and_similar_fetch, 'data', prevent_initial_call=True)


control_panel = ControlPanel(config, map, url_data)
admin_panel = AdminPanel(config, map, url_data)

def layout(**kwargs):
      url_data.set_data(**kwargs)
      return html.Div([manager, url_data,control_panel, admin_panel, map], style=CONTENT_STYLE)
