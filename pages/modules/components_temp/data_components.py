from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pages.modules.managers.security_manager import ISecurityManager
    from pages.modules.managers.data_manager import DataManager
    from pages.modules.config import PageConfig


from pages.modules.callback_system import CustomCallback
from pages.modules.interfaces import IBaseComponent
from dash import dcc, callback, Output, Input, html, State, no_update
from collections.abc import Callable



class IncomingData(dcc.Store,IBaseComponent, CustomCallback):

    def __init__(self, pageConfig: PageConfig,data: dict={}):
        CustomCallback.__init__(self)
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

class TriggerCallbackButton(html.Button, CustomCallback):

    def __init__(self, id: str, **kwargs):
        html.Button.__init__(self, id=id, n_clicks=0, **kwargs)
        CustomCallback.__init__(self)



    def set_callback(self, output_ids: list, fnc: Callable[[any], list], output_properties="children", prevent_initial_call=False) -> None:
        if self.is_callback_set:
            print("Callback already set")
            return
        @callback(
            super().set_callback(output_ids, fnc, output_properties),
            Input(self.id, 'n_clicks'),
            self.states,
            prevent_initial_call=prevent_initial_call
        )
        def __set__(n_clicks, *args):
            if n_clicks is not None and n_clicks > 0:
               return fnc(*args)
            return no_update