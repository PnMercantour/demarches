import dash
from dash import html
import dash_leaflet as dl

from pages.modules.config import NS_RENDER, PageConfig
from pages.modules.base_components import IncomingData, Carte, FlightSaver, ControlPanel
from pages.modules.data import APP_INFO_BOX, CACHE
from pages.modules.managers import DataManager, UserSecurity

dash.register_page(__name__, path='/',path_template='/')

## MANAGERS
data_manager = DataManager()
security_manager = UserSecurity(data_manager)

config = PageConfig("create", data_manager, security_manager)

url_data = IncomingData(config)

## CREATE MAP
map = Carte(config,forceEdit=True,incoming_data=url_data)

map.SetAllFeatures(map)

flight_saver = FlightSaver(config, FlightSaver.SAVE_CREATE,map, url_data)

control_panel = ControlPanel(config, map, url_data,True)





def layout():
    data = {
        'uuid':None,
    }
    url_data.set_data(data)
    return html.Div([url_data, control_panel, flight_saver, map], style={'height': '80vh'})