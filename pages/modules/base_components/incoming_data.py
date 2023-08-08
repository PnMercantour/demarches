from typing import Callable
from dash import dcc, callback
from dash.dependencies import Input

from carto_editor import PageConfig

from pages.modules.interfaces import IBaseComponent 
from pages.modules.callbacks import CustomCallback
from dash.dependencies import Output
class IncomingData(dcc.Store,IBaseComponent, CustomCallback):

    def __init__(self, pageConfig: PageConfig,data: dict={}):
        CustomCallback.__init__(self)
        IBaseComponent.__init__(self, pageConfig)
        dcc.Store.__init__(self, id=self.get_prefix(), data=data)

    def set_data(self, **data):
        self.data = data
        if not 'st_token' in data:
            self.data['st_token'] = None
        if not 'uuid' in data:
            self.data['uuid'] = None
        if not 'min_month' in data:
            self.data['min_month'] = 6
        if not 'max_month' in data:
            self.data['max_month'] = 8


    def set_callback(self, output_ids: list, fnc: Callable[[dict], list], output_properties="children", prevent_initial_call=False) -> None:
        @callback(
            super().set_callback(output_ids, fnc, output_properties),
            Input(self.id, 'data'),
            prevent_initial_call=prevent_initial_call
        )
        def __set__(data):
            return fnc(data)
    
    def get_output(self):
        return Output(self.get_prefix(), 'data')
