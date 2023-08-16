from dash import html
from dash_bootstrap_components import Offcanvas
import dash_bootstrap_components as dbc

from demarches_simpy import Dossier, DossierState, Field

from carto_editor import PageConfig, CONFIG

from pages.modules.interfaces import *
from pages.modules.callbacks import CustomCallback
from pages.modules.managers.data_manager import Flight


class DossierInfo(Offcanvas, IBaseComponent):
    # Style
    




    def __fnc_panel_init__(self, data):
        uuid=data['uuid']
        flight = self.config.data_manager.get_flight_by_uuid(uuid)
        flight = flight.get_last_flight()
        if flight is None:
            return [html.H3("No flight selected")]
        dossier = flight.get_attached_dossier().force_fetch()
        return self.__get_layout__(dossier, flight)

    def __get_root_style__(self):
        return {}

    def __get_layout__(self, dossier: Dossier = None, flight : Flight = None):
        
        if dossier is None:
            return html.Div('Waiting for data ...')

        from datetime import datetime
        import locale
        locale.setlocale(locale.LC_TIME, "fr_FR")
        ## 2023-08-01 14:21:43.366299
        date = datetime.strptime(flight.get_creation_date(), "%Y-%m-%d %H:%M:%S.%f")
        human_readable_format = date.strftime("%B %d, %Y %H:%M:%S")
        fields : Field = dossier.get_fields()
        look_for_field = lambda field_name : next((field for field in fields if  field.label == field_name), None)

        # 2023-07-27T11:01:44+02:00
        deposit_date_str = dossier.get_deposit_date()
        deposit_date = datetime.strptime(deposit_date_str, "%Y-%m-%dT%H:%M:%S%z")
        deposit_date_human_readable = deposit_date.strftime("%B %d, %Y %H:%M:%S")


        return [
            dbc.Col([
            html.H2(f"Dossier n°{dossier.get_number()} \n {dossier.get_id()}"),
            dbc.Row([
                dbc.Badge(f"{str(dossier.get_dossier_state())}", color="primary", className="mr-1"),
            ], justify="start", align="start"),
            html.P(f"Date de dépôt : {deposit_date_human_readable}"),

            
            html.H2("Informations du vol"),
            html.P(f"Dernière modification : {human_readable_format}"),
            html.P(f"Dropzone de départ: {flight.get_start_dz()} "),
            html.P(f"Dropzones :"),
            ]+[html.P("-> "+dz) for dz in flight.get_dz()] + [ html.P(f"{field_label} : {look_for_field(field_label).stringValue}") for field_label in self.custom_fields])
        ]

        

    def __init__(self,pageConfig: PageConfig, incoming_data : CustomCallback):
        IBaseComponent.__init__(self, pageConfig)
        Offcanvas.__init__(self, children=self.__get_layout__(), id=self.get_prefix(), style=self.__get_root_style__(), is_open=False)
        
        self.custom_fields = CONFIG('info-panel-fields', [])
        

        #Create a skeleton for the file info
        incoming_data.set_callback(self.get_prefix(), self.__fnc_panel_init__)

    

