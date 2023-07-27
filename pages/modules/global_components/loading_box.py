from dash import dcc, html
from dash.dependencies import Output

from carto_editor import PageConfig

from pages.modules.interfaces import *
from pages.modules.callbacks import CustomCallback

class LoadingBox(dcc.Loading, IBaseComponent, CustomCallback):
    # Style

    # Id
    TRIGGER_LOADING = "trigger_loading"

    def __get_layout__(self):
        return [html.Div(id=self.set_id(LoadingBox.TRIGGER_LOADING), hidden=True)]

    def __get_root_style__(self):
        return {"zIndex":"1000", "position":"absolute", "bottom":"0px", "right":"0px", "width":"100%", "height":"100%"}

    def set_internal_callback(self) -> None:
       pass


    def __init__(self, pageConfig: PageConfig):
        self.pageConfig = pageConfig
        IBaseComponent.__init__(self, pageConfig)
        dcc.Loading.__init__(self, id=self.get_prefix(), children=self.__get_layout__(), style=self.__get_root_style__(), type='circle')

    def get_trigger_id(self):
        return self.get_id(LoadingBox.TRIGGER_LOADING)

    def get_output(self):
        return Output(self.get_trigger_id(), 'hidden', allow_duplicate=True)
