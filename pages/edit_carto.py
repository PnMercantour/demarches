import dash
from dash import html
import dash_leaflet as dl
from pages.modules.config import NS_RENDER, arrow_function, CONTENT_STYLE
from pages.modules.base_components import IncomingData, Carte, FlightSaver, ControlPanel, Manager
from pages.modules.data import APP_INFO_BOX, BuiltInCallbackFnc, DATA_MANAGER
from pages.modules.managers import  UserSecurity
dash.register_page(__name__, path='/edit',path_template='/edit')


manager = Manager('edit', DATA_MANAGER, UserSecurity(DATA_MANAGER))
data_manager = manager.data_manager
config = manager.config
# #CREATE MAP
url_data = IncomingData(config)
map = Carte(config, incoming_data=url_data)

## FETCHING FEATURES
Carte.SetAllFeatures(map)


map.addGeoJson(None,id="flight",
options=dict(style=NS_RENDER('flight_style'), onEachFeature=NS_RENDER('flight_init')),
hoverStyle=arrow_function(dict(weight=8, color='#ff9999', dashArray='')),
)


flight_saver = FlightSaver(config, FlightSaver.SAVE_UPDATE, map, url_data)
control_panel = ControlPanel(config, map, url_data, True)


callbacks = BuiltInCallbackFnc(data_manager)

url_data.set_callback([map.get_id('flight'), APP_INFO_BOX.get_output()],callbacks.flight_fetch, 'data', prevent_initial_call=True)


def layout(**kwargs):
      url_data.set_data(**kwargs)
      return html.Div([manager, url_data, control_panel,flight_saver, map], style=CONTENT_STYLE)

