
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from pages.modules.managers.data_manager import DataManager
    from pages.modules.managers.action_manager import IAction

from pages.modules.config import SecurityLevel, CONFIG
from pages.modules.utils import SQL_Fetcher
from demarches_simpy import Dossier, DossierState

from pages.modules.interfaces import ISecurityManager


class AdminSecurity(ISecurityManager):

    def login(self, data) -> bool:
        if not 'email' in data or not 'password' in data:
            return False
        email = data['email']
        password = data['password']
        flight_uuid = data['uuid']
        dossier_ctx = self.data_manager.get_flight_by_uuid(flight_uuid).get_attached_dossier()
        dossier_ctx.get_attached_instructeurs_info()
        dossier_ctx.force_fetch()
        instructeurs = dossier_ctx.get_attached_instructeurs_info()
        for instructeur in instructeurs:
            if instructeur['email'] == email and instructeur['id'] == password:
                self.logged = True
                return True
        return False

class STSecurity(ISecurityManager, SQL_Fetcher):

    def __init__(self, data: DataManager) -> None:
        ISecurityManager.__init__(self, data)
        SQL_Fetcher.__init__(self)
    
    def login(self, data):
        if not 'st_token' in data and not 'uuid' in data:
            return False


        uuid = data['uuid']
        st_token = data['st_token']
        dossier = self.get_data_ctx().get_flight_by_uuid(uuid).get_attached_dossier()
        
        if self.get_data_ctx().is_file_closed(dossier):
            return False

        resp = self.fetch_sql(sql_file='./sql/check_st_token.sql', request_args=[dossier.get_id(), st_token])

        if self.is_sql_error(resp) or len(resp) == 0:
            print(resp['message'])
            return False
        

        
        self.logged = resp[0][0]
        return self.logged

class UserSecurity(ISecurityManager):
    
    def login(self, data):
        if not 'uuid' in data and not 'security_token' in data:
            return False

        uuid = data['uuid']
        security_token = data['security_token']
        flight = self.data_manager.get_flight_by_uuid(uuid)
        if flight is None:
            return False

        dossier = flight.get_attached_dossier()
        
        if self.get_data_ctx().is_file_closed(dossier):
            return False

        if dossier.get_dossier_state() != DossierState.CONSTRUCTION:
            return False




        field_label = CONFIG('label-field/security-token', 'security-token')

        annotations = dossier.get_annotations()

        if not field_label in annotations:
            return False

        token_field = annotations[field_label]

        self.logged = token_field["stringValue"] == security_token
        return self.logged


               
        




        




