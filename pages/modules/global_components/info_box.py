from dash import callback, html, dcc, no_update, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from carto_editor import PageConfig

from pages.modules.interfaces import *
from pages.modules.callbacks import CustomCallback



class InfoBox(dbc.Container, IBaseComponent, CustomCallback):
    
    ITEM_CLASS = "d-flex align-items-center justify-content-start"

    # Id
    DATA = "data"
    MESSAGE = "message"
    ALERT = "alert"
    TIMER = "timer"

    def __get_root_class__(self):
        return 'position-fixed fixed-top w-25 mt-4'

    def __get_layout__(self):
        return [

            dcc.Store(id=self.set_id(InfoBox.DATA), data={"message":"", "type":"info"}),
            dbc.Alert([
                dbc.Row([
                    dbc.Col(dbc.Spinner(color="light", type="grow", size="lg"), width=3, class_name=self.ITEM_CLASS),
                    dbc.Col(html.H3(id=self.set_id(InfoBox.MESSAGE)), width=9, class_name=self.ITEM_CLASS)
                ])
            ],id=self.set_id(InfoBox.ALERT)),
            dcc.Interval(id=self.set_id(InfoBox.TIMER), interval=3000, n_intervals=0, disabled=True)
        ]

    def __init__(self, pageConfig: PageConfig):
        self.pageConfig = pageConfig
        IBaseComponent.__init__(self, pageConfig)
        dbc.Container.__init__(self, id=self.get_prefix(), children=self.__get_layout__(), className=self.__get_root_class__(), style={"display":"none"})

        self.set_internal_callback()

    def set_internal_callback(self) -> None:

        @callback(
            [Output(self.get_id(InfoBox.MESSAGE), 'children'), Output(self.get_id(InfoBox.ALERT), 'color'), Output(self.get_id(InfoBox.TIMER), 'disabled', allow_duplicate=True)],
            Input(self.get_id(InfoBox.DATA), 'data'),
            prevent_initial_call=True
        )
        def __set__(data):
            if data is None:
                return ['', 'danger', True]
            if 'message' in data:
                if not 'type' in data:
                    return [[html.I(className="bi bi-info-circle-fill me-2"),data['message']], 'info', False]
                else :
                    if data['type'] == 'error':
                        data['type'] = 'danger'

                    return [data['message'], data['type'], False]
            else:
                print('//!!!\\ Info data sent wasnt in correct format')
                print(data)
                return [no_update, no_update, no_update]

        @callback(
            [Output(self.get_id(InfoBox.TIMER), 'disabled', allow_duplicate=True), Output(self.get_prefix(), 'style')],
            [Input(self.get_id(InfoBox.TIMER), 'n_intervals'), Input(self.get_id(InfoBox.TIMER), 'disabled')],
            prevent_initial_call=True
        )
        def __set__(n, disabled):
            props_id = callback_context.triggered[0]['prop_id']
            if props_id == self.get_id(InfoBox.TIMER) + '.n_intervals':
                return [True, {"display":"none"}]
            elif props_id == self.get_id(InfoBox.TIMER) + '.disabled' and disabled == False:
                return [no_update, {}]
            else:
                return [no_update, no_update]
    
    def build_message(self, message: str, type: str="info"):
        return {"message":message, "type":type}

    def get_output(self):
        '''Get the right data output to use directly in callback'''
        from dash.dependencies import Output
        return Output(self.get_id(InfoBox.DATA), 'data', allow_duplicate=True)
    def get_data_id(self):
        return self.get_id(InfoBox.DATA)
