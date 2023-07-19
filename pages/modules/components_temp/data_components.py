from pages.modules.config import PageConfig
from pages.modules.callback_system import CustomCallback
from pages.modules.interfaces import IBaseComponent
from dash import dcc, callback, Output, Input
from collections.abc import Callable


class IncomingData(dcc.Store,IBaseComponent, CustomCallback):
    def __init__(self, pageConfig: PageConfig,data: dict={}):
        IBaseComponent.__init__(self, pageConfig)
        dcc.Store.__init__(self, id=self.get_prefix(), data=data)

    def set_data(self, data: dict):
        self.data = data

    def set_callback(self, output_ids: list, fnc: Callable[[dict], list], output_properties="children") -> None:
        output_properties = self.__process_properties__(output_ids, output_properties)
        @callback(
            [Output(output_id, output_property) for output_id, output_property in zip(output_ids, output_properties)] if len(output_ids) > 1 else Output(output_ids[0], output_properties[0]),
            Input(self.id, 'data')
        )
        def __set__(data):
            return fnc(data)
