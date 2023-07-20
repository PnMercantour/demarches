from pages.modules.callback_system import CustomCallback
from pages.modules.interfaces import IBaseComponent
from dash import dcc, callback, Output, Input
from collections.abc import Callable


class IncomingData(dcc.Store,IBaseComponent, CustomCallback):
    from pages.modules.config import PageConfig

    def __init__(self, pageConfig: PageConfig,data: dict={}):
        IBaseComponent.__init__(self, pageConfig)
        dcc.Store.__init__(self, id=self.get_prefix(), data=data)

    def set_data(self, data: dict):
        self.data = data

    def set_callback(self, output_ids: list, fnc: Callable[[dict], list], output_properties="children", prevent_initial_call=False) -> None:
        @callback(
            super().set_callback(output_ids, fnc, output_properties),
            Input(self.id, 'data'),
            prevent_initial_call=prevent_initial_call
        )
        def __set__(data):
            return fnc(data)

