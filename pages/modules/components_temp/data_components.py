from pages.modules.callback_system import CustomCallback
from pages.modules.interfaces import IBaseComponent
from dash import dcc, callback, Output, Input, html, State, no_update
from collections.abc import Callable

from pages.modules.managers.security_manager import ISecurityManager
from pages.modules.managers.data_manager import DataManager
from pages.modules.managers.action_manager import IAction


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

class TriggerActionButton(html.Button, CustomCallback):
    from pages.modules.config import PageConfig

    def __init__(self, incoming_data: IncomingData, id: str, data_manager : DataManager, security_ctx : ISecurityManager, action : IAction):
        html.Button.__init__(self, id=id, n_clicks=0)
        CustomCallback.__init__(self)

        self.incoming_data = incoming_data
        self.data_manager = data_manager
        self.security_ctx = security_ctx
        self.action = action

    def set_callback(self, fnc prevent_initial_call=False) -> None:
        from pages.modules.components_temp.global_components import APP_INFO_BOX
        @callback(
            APP_INFO_BOX.get_output(),
            Input(self.id, 'n_clicks'),
            [State(self.incoming_data.get_prefix(), 'data')]+self.states,
            prevent_initial_call=prevent_initial_call
        )
        def __set__(n_clicks,data, *args):
            #Looking for either 
            if n_clicks is not None:
                temp = {}
                temp.update(data)
                for arg in args:
                    temp.update(arg)

                if not self.security_ctx.login(data):
                    APP_INFO_BOX.build_message("Login failed","error")

                return self.security_ctx.perform_action(self.action)
            else:
                return no_update