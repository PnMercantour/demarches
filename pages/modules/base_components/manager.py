from dash import dcc
from carto_editor import PageConfig
from pages.modules.interfaces import IBaseComponent, ISecurityManager
from pages.modules.managers import DataManager
from typing import Callable
class Manager(dcc.Store, IBaseComponent):
    
    def __init__(self, prefix,data_manager : DataManager, security_manager : ISecurityManager):
        self.__data_manager = data_manager
        self.__security_manager = security_manager
        self.__config = PageConfig(prefix, self.data_manager, self.security_manager)
        IBaseComponent.__init__(self, self.config)
        dcc.Store.__init__(self, id=self.get_prefix(), data={})



    @property
    def config(self) -> PageConfig:
        return self.__config
    @property
    def data_manager(self) -> DataManager:
        return self.__data_manager
    @property
    def security_manager(self) -> ISecurityManager:
        return self.__security_manager
    @security_manager.setter
    def security_manager(self, security_manager: ISecurityManager) -> None:
        self.__config.security_manager = security_manager
        self.__security_manager = security_manager

        