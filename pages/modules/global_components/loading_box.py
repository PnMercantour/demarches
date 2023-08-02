from dash import dcc, html
from dash.dependencies import Output

from carto_editor import PageConfig

from pages.modules.interfaces import *
from pages.modules.callbacks import CustomCallback
import dash_bootstrap_components as dbc

class LoadingBox(dbc.Spinner, IBaseComponent, CustomCallback):
    # Style

    # Id
    TRIGGER_LOADING = "trigger_loading"

    def __get_layout__(self):
        return [html.Div(id=self.set_id(LoadingBox.TRIGGER_LOADING), hidden=True)]

    def __get_root_style__(self):
        # Put it in bottom left corner
        return {
            "zIndex": "2000",
            'width': '3rem',
            'height': '3rem',
        }

    def __get_root_class__(self):
        return "position-fixed bg-primary fixed-bottom mb-4 ms-4 shadow"

    def set_internal_callback(self) -> None:
       pass


    def __init__(self, pageConfig: PageConfig):
        self.pageConfig = pageConfig
        IBaseComponent.__init__(self, pageConfig)
        dbc.Spinner.__init__(self, id=self.get_prefix(), children=self.__get_layout__(), spinner_style=self.__get_root_style__(), spinner_class_name=self.__get_root_class__(), color="light", type="border")

    def get_trigger_id(self):
        return self.get_id(LoadingBox.TRIGGER_LOADING)

    def get_output(self):
        return Output(self.get_trigger_id(), 'hidden', allow_duplicate=True)
