from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .carte import Carte
    from .incoming_data import IncomingData
    from carto_editor import PageConfig



from demarches_simpy import DossierState

from carto_editor import APP_INFO_BOX, LOADING_BOX, SecurityLevel



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
        is_hidden = dossier.get_dossier_state() != DossierState.CONSTRUCTION or self.config.data_manager.is_file_closed(dossier)
        return {'display': 'none'} if is_hidden else {}
    def __fnc_update__(self, data, geojson):  
        from pages.modules.managers import SaveFlight

        uuid = data['uuid']
        security_token = data['security_token']

        self.config.security_manager.login({'uuid': uuid, 'security_token': security_token})
        if not self.config.security_manager.is_logged():
            return [{'message' : 'Invalid credentials','type':'error'}, False]

        flight = self.config.data_manager.get_flight_by_uuid(uuid)
        
        if flight == None:
            return [{'message' : 'Invalid flight','type':'error'}, False]

        dossier = flight.get_attached_dossier().force_fetch()

        save_flight = SaveFlight(self.config.data_manager, geojson, dossier)
        return [self.config.security_manager.perform_action(save_flight),False]

    def __fnc_create(self, geojson):
        from pages.modules.managers import CreatePrefilledDossier, SaveFlight, UpdateFlightDossier, PackedActions
        from dash import dcc, no_update
        save_flight = SaveFlight(self.config.data_manager, geojson)
        create_dossier = CreatePrefilledDossier(self.config.data_manager)
        update_flight = UpdateFlightDossier(self.config.data_manager)

        packed_actions = PackedActions(self.config.data_manager,{}, SecurityLevel.NO_AUTH)
        packed_actions.add_action(save_flight)
        packed_actions.add_action(create_dossier)
        packed_actions.add_action(update_flight)

        result = self.config.security_manager.perform_action(packed_actions)
        url = packed_actions.returned_value['dossier_url'] if 'dossier_url' in packed_actions.returned_value else None
        return [dcc.Location(href=url, id="finalized", refresh=True) if url != None else no_update,result, False]


    def __get_layout__(self):
        return "Continuer sur Démarches Simplifiées" if self.saving_mode == self.SAVE_CREATE else "Mettre à jour"

    def __get_root_class__(self):
        return "m-1"

    def __init__(self, config: PageConfig, saving_mode: str, map: Carte, incoming_data : IncomingData):
        self.saving_mode = saving_mode
        IBaseComponent.__init__(self, config)
        TriggerCallbackButton.__init__(self, id=self.get_prefix(), children=self.__get_layout__(), style=self.__get_root_style__(), class_name=self.__get_root_class__())
        self.map = map
        self.incoming_data = incoming_data

        self.set_internal_callback()

    def set_internal_callback(self) -> None:
        ## Init callback

        if self.saving_mode == self.SAVE_UPDATE:
            self.incoming_data.set_callback(self.get_prefix(), self.__fnc_save_init__, 'style')

            self.add_state(self.incoming_data.get_prefix(), 'data')
            self.add_state(self.map.get_comp_edit(), 'geojson')
            self.set_callback([APP_INFO_BOX.get_output(), LOADING_BOX.get_output()], self.__fnc_update__, 'data', prevent_initial_call=True)
        elif self.saving_mode == self.SAVE_CREATE:
            self.add_state(self.map.get_comp_edit(), 'geojson')
            self.set_callback([self.get_prefix(), APP_INFO_BOX.get_output(), LOADING_BOX.get_output()], self.__fnc_create, 'children', prevent_initial_call=True)