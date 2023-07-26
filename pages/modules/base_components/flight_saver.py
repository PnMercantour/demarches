from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .carte import Carte
    from .incoming_data import IncomingData
    from carto_editor import PageConfig



from demarches_simpy import DossierState

from pages.modules.data import APP_INFO_BOX, LOADING_BOX



from pages.modules.interfaces import *
from pages.modules.flex_components import TriggerCallbackButton





class FlightSaver(TriggerCallbackButton, IBaseComponent):
    ## Style



    ## Mode
    SAVE_CREATE = "save_create"
    SAVE_UPDATE = "save_update"

    def __fnc_save_init__(self, data):
        uuid = data['uuid']
        
        flight = self.config.data_manager.get_flight_by_uuid(uuid)
        if flight == None:
            return True
        dossier = flight.get_attached_dossier()
        return dossier.get_dossier_state() != DossierState.CONSTRUCTION or self.config.data_manager.is_file_closed(dossier)

    def __fnc_save__(self, data, geojson):  
        from pages.modules.managers import SaveFlight

        uuid = data['uuid']
        security_token = data['security_token']

        self.config.security_manager.login({'uuid': uuid, 'security_token': security_token})
        if not self.config.security_manager.is_logged:
            return [{'message' : 'Invalid credentials','type':'error'}, False]

        flight = self.config.data_manager.get_flight_by_uuid(uuid)
        
        if flight == None:
            return [{'message' : 'Invalid flight','type':'error'}, False]

        dossier = flight.get_attached_dossier().force_fetch()

        
        save_flight = SaveFlight(self.config.data_manager, geojson, dossier)
        return [self.config.security_manager.perform_action(save_flight),False]

    def __get_root_style__(self):
        return {'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'}
    def __get_layout__(self):
        return "Continuer sur Démarches Simplifiées" if self.saving_mode == self.SAVE_CREATE else "Mettre à jour"

    def __init__(self, config: PageConfig, saving_mode: str, map: Carte, incoming_data : IncomingData):
        self.saving_mode = saving_mode
        IBaseComponent.__init__(self, config)
        TriggerCallbackButton.__init__(self, id=self.get_prefix(), children=self.__get_layout__(), style=self.__get_root_style__())
        self.map = map
        self.incoming_data = incoming_data

        self.set_internal_callback()

    def set_internal_callback(self) -> None:
        ## Init callback
        self.incoming_data.set_callback(self.get_prefix(), self.__fnc_save_init__, 'hidden')


        self.add_state(self.incoming_data.get_prefix(), 'data')
        self.add_state(self.map.get_comp_edit(), 'geojson')
        self.set_callback([APP_INFO_BOX.get_output(), LOADING_BOX.get_output()], self.__fnc_save__, 'data', prevent_initial_call=True)
