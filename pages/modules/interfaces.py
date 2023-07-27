from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pages.modules.config import PageConfig
    from pages.modules.managers import DataManager
    from carto_editor import SecurityLevel



class IBaseComponent():
    def __init__(self, pageConfig: PageConfig):
        component_prefix = str(type(self)).split(".")[-1].replace("'>","")
        self.prefix = pageConfig.page_name+"_"+component_prefix
        self.ids = []
        self.__pageConfig = pageConfig

    def set_id(self, id: str):
        full_id = self.prefix+"_"+id
        if full_id not in self.ids:
            self.ids.append(full_id)
            return full_id
        else:
            return full_id

    def get_id(self, id: str):
        full_id = self.prefix+"_"+id
        if full_id in self.ids:
            return full_id
        else:
            raise Exception(f"id {id} does not exists")

    def get_prefix(self):
        return self.prefix

    def __get_layout__(self):
        pass

    def __get_root_style__(self):
        return {'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px', 'minWidth': '300px', 'margin': '10px', 'minWidth': '300px' }

    @property
    def config(self) -> PageConfig:
        return self.__pageConfig

    @config.setter
    def config(self, pageConfig: PageConfig) -> None:
        self.__pageConfig = pageConfig


    def set_internal_callback(self) -> None:
        '''Set the callback for the component concerning internal changes'''
        pass

class IAction():

    AUTH=0 # Action requires authentication
    NO_AUTH=1 # Action does not require authentication
    def __init__(self, data_manager: DataManager, security_lvl : SecurityLevel = 0) -> None:
        self.data_manager = data_manager
        self.security_lvl = security_lvl
        self.__result = None
        self.__is_error = False

    def get_security_level(self) -> SecurityLevel:
        return self.security_lvl

    def precondition(self) -> bool:
        return True
    def perform(self) -> any:
        pass

    def trigger_error(self, str):
        self.is_error = True
        self.result = {"message" : str, "type" : "error"}
        return self

    def trigger_success(self, str):
        self.is_error = False
        self.result = {"message" : str, "type" : "success"}
        return self
    @property
    def is_error(self) -> bool:
        return self.__is_error
    @is_error.setter
    def is_error(self, value : bool) -> None:
        self.__is_error = value

    @property
    def result(self) -> any:
        return self.__result

    @result.setter
    def result(self, value : any) -> None:
        self.__result = value

class IPackedAction(IAction):
    def __init__(self, data_manager: DataManager, security_lvl : SecurityLevel = 0) -> None:
        IAction.__init__(self, data_manager, security_lvl=security_lvl)
        self.__passed_kwargs = {}
    @property
    def passed_kwargs(self) -> dict:
        return self.__passed_kwargs

    @passed_kwargs.setter
    def passed_kwargs(self, value : dict) -> None:
        self.__passed_kwargs = value

    def trigger_success(self, str, **kwargs):
        self.passed_kwargs = kwargs if self.passed_kwargs == {} else self.passed_kwargs
        return super().trigger_success(str)

    def check_correct_passed_kwargs(self, names : list, kwargs : dict) -> bool:
        for name in names:
            if name not in kwargs:
                self.is_error = True
                self.result = {"message":"Missing argument {}".format(name), "type":"error"}
                return False
        return True



    def perform(self, **kwargs) -> any:
        pass 


class ISecurityManager():
    

    def __init__(self, data : DataManager) -> None:
        self.data_manager = data
        self.logged = False


    def perform_action(self, action : IAction) -> any:
        from carto_editor import SecurityLevel

        if action.get_security_level() == SecurityLevel.AUTH and not self.logged:
            return {"message":"You are not logged in", "type":"error"}

        if not action.precondition():
            return action.result if action.is_error else {"message":"Precondition failed", "type":"error"}
        
        action.perform()
        return self.action_result(action)

    def action_result(self, action : IAction) -> any:
        from carto_editor import SecurityLevel

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