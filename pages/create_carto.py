import dash
from dash import html


from pages.modules.config import  CONTENT_STYLE
from pages.modules.base_components import IncomingData, Carte, FlightSaver, ControlPanel, Manager
from pages.modules.data import DATA_MANAGER
from pages.modules.managers import  UserSecurity

dash.register_page(__name__, path='/',path_template='/')

## MANAGERS
manager = Manager('create', DATA_MANAGER, UserSecurity(DATA_MANAGER))
data_manager = manager.data_manager
config = manager.config

url_data = IncomingData(config)

## CREATE MAP
map = Carte(config,forceEdit=True,incoming_data=url_data)

map.SetAllFeatures(map)

flight_saver = FlightSaver(config, FlightSaver.SAVE_CREATE,map, url_data)

control_panel = ControlPanel(config, map, url_data,True)





def layout(**kwargs):
    url_data.set_data(**kwargs)
    return html.Div([manager, url_data, control_panel, flight_saver, map], style=CONTENT_STYLE)