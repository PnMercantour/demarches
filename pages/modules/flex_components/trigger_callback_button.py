from dash import html, callback, no_update
from dash.dependencies import Input
import dash_bootstrap_components as dbc

from typing import Callable


from pages.modules.callbacks import CustomCallback

class TriggerCallbackButton(dbc.Button, CustomCallback):

    def __init__(self, id: str, **kwargs):
        if 'hidden' in kwargs:
            kwargs['style'] = {'display': 'none'}
            del kwargs['hidden']
        dbc.Button.__init__(self, id=id, n_clicks=0, **kwargs)
        CustomCallback.__init__(self)



    def set_callback(self, output_ids: list, fnc: Callable[[any], list], output_properties="children", prevent_initial_call=False, **kwargs) -> None:
        if self.is_callback_set:
            print("Callback already set")
            return
        @callback(
            outputs := super().set_callback(output_ids, fnc, output_properties),
            Input(self.id, 'n_clicks'),
            self.states,
            prevent_initial_call=prevent_initial_call,
            **kwargs
        )
        def __set__(n_clicks, *args):
            if n_clicks is not None and n_clicks > 0:
                return fnc(*args)
            return [no_update for _ in range(len(outputs) if isinstance(outputs, list) else 1)]

