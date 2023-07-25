
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from pages.modules.managers.data_manager import DataManager
    from pages.modules.managers.action_manager import IAction

from pages.modules.config import SecurityLevel
from pages.modules.data import SQL_Fetcher
class ISecurityManager():
    

    def __init__(self, data : DataManager) -> None:
        self.data_manager = data
        self.logged = False


    def perform_action(self, action : IAction) -> any:
        if action.get_security_level() == SecurityLevel.AUTH and not self.logged:
            return {"message":"You are not logged in", "type":"error"}

        if not action.precondition():
            return action.result if action.is_error else {"message":"Precondition failed", "type":"error"}
        
        action.perform()
        return self.action_result(action)

    def action_result(self, action : IAction) -> any:
        if action.get_security_level() == SecurityLevel.AUTH and not self.logged:
            return False
        return action.result

    def login(self, data : dict[str,str]) -> bool:
        '''
        dict must contain the following keys:
        - uuid

        '''
        pass

    def is_logged(self) -> bool:
        return self.logged

    def get_data_ctx(self) -> DataManager:
        return self.data_manager

class AdminSecurity(ISecurityManager):

    def login(self, data) -> bool:
        if not 'email' in data or not 'password' in data:
            return False

        email = data['email']
        password = data['password']
        flight_uuid = data['uuid']
        dossier_ctx = self.data_manager.get_flight_by_uuid(flight_uuid).get_attached_dossier()
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
        dossier = self.data_manager.get_flight_by_uuid(uuid).get_attached_dossier()
        
        resp = self.fetch_sql(sql_file='./sql/check_st_token.sql', request_args=[dossier.get_id(), st_token])

        if self.is_sql_error(resp):
            print(resp['message'])
            return False

        if len(resp) == 0:
            print("No token found")
            return False
        
        self.logged = resp[0][0]
        return self.logged






        




