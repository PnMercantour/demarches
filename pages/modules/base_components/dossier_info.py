from dash import html

from demarches_simpy import Dossier, DossierState

from carto_editor import PageConfig

from pages.modules.interfaces import *
from pages.modules.callbacks import CustomCallback
from pages.modules.managers.data_manager import Flight


class DossierInfo(html.Div, IBaseComponent):
    # Style
    
    # ID
    F_NUMBER = 'field_number'
    F_STATE = 'field_state'
    F_CREATION_DATE = 'field_creation_date'
    F_CAN_EDIT = 'field_can_edit'
    F_FLIGHT_UUID = 'field_flight_uuid'
    F_FLIGHT_START_DZ = 'field_flight_start_dz'
    F_FLIGHT_END_DZ = 'field_flight_end_dz'


    def __fnc_panel_init__(self, data):
        uuid=data['uuid']
        flight = self.config.data_manager.get_flight_by_uuid(uuid)
        flight = flight.get_last_flight()
        if flight is None:
            return [html.H3("No flight selected")]
        dossier = flight.get_attached_dossier().force_fetch()
        return self.__get_layout__(dossier, flight)

    def __get_root_style__(self):
        return {"position": "absolute", "top": "40%", "right": "10px", "zIndex": "1000", "backgroundColor": "white", "borderRadius": "5px", "boxShadow": "2px 2px 2px lightgrey", "padding": "10px","opacity":"0.8"}

    def __get_layout__(self, dossier: Dossier = None, flight : Flight = None):
        
        if dossier is None:
            return html.Div('Waiting for data ...')


        return [
            html.H2("Dossier Info"),
            html.H3(f"Can edit : {dossier.get_dossier_state() == DossierState.CONSTRUCTION}",id = self.set_id(DossierInfo.F_CAN_EDIT)),
            html.H3(f"File number : {dossier.get_number()}",id = self.set_id(DossierInfo.F_NUMBER)),
            html.H3(f"State : {str(dossier.get_dossier_state())}",id = self.set_id(DossierInfo.F_STATE)),
            html.H2("Flight Info"),
            html.H3(f"Creation date : {flight.creation_date}",id = self.set_id(DossierInfo.F_CREATION_DATE)),
            html.H3(f"UUID : {flight.get_id()}",id = self.set_id(DossierInfo.F_FLIGHT_UUID)),
            html.H3(f"Start DZ : {flight.get_start_dz()}",id = self.set_id(DossierInfo.F_FLIGHT_START_DZ)),
            html.H3(f"End DZ : {flight.get_end_dz()}",id = self.set_id(DossierInfo.F_FLIGHT_END_DZ)),

        ]

        

    def __init__(self,pageConfig: PageConfig, incoming_data : CustomCallback):
        IBaseComponent.__init__(self, pageConfig)
        html.Div.__init__(self, children=self.__get_layout__(), id=self.get_prefix(), style=self.__get_root_style__())

        #Create a skeleton for the file info
        incoming_data.set_callback(self.get_prefix(), self.__fnc_panel_init__)

