from dash import callback, html, dcc
from dash.dependencies import Input, Output, State
from carto_editor import PageConfig

from pages.modules.interfaces import *
from pages.modules.callbacks import CustomCallback



class InfoBox(html.Div, IBaseComponent, CustomCallback):
    # Style
    DIV_STYLE={
        "display": "flex",
        "flex-direction": "row",
        "justify-content": "center",
        "align-items": "center",
    }

    BASE_MESSAGE_STYLE={
        "background-color": "white",
        "border-radius": "5px",
        "padding": "10px",
        "border": "1px solid black",
        "boxShadow": "2px 2px 2px lightgrey",
    }

    INFO_MESSAGE_STYLE={
        "color": "black",
    }

    ERROR_MESSAGE_STYLE={
        "color": "red",
    }

    SUCCESS_MESSAGE_STYLE={
        "color": "green",
    }


    # Id
    DATA = "data"
    MESSAGE = "message"

    def __get_layout__(self):
        return [
            dcc.Store(id=self.set_id(InfoBox.DATA), data={"message":"", "type":"info"}),
            html.Div(id=self.set_id(InfoBox.MESSAGE), style=InfoBox.BASE_MESSAGE_STYLE)
        ]

    def __init__(self, pageConfig: PageConfig):
        self.pageConfig = pageConfig
        IBaseComponent.__init__(self, pageConfig)
        html.Div.__init__(self, id=self.get_prefix(), children=self.__get_layout__(), style=InfoBox.DIV_STYLE)

        self.set_internal_callback()

    def set_internal_callback(self) -> None:

        @callback(
            [Output(self.get_id(InfoBox.MESSAGE), 'children'), Output(self.get_id(InfoBox.MESSAGE), 'style')],
            Input(self.get_id(InfoBox.DATA), 'data')
        )
        def __set__(data):
            if data is None:
                return ['', InfoBox.BASE_MESSAGE_STYLE]
            if 'message' in data:
                if not 'type' in data:
                    return [data['message'], InfoBox.BASE_MESSAGE_STYLE]
                if data['type'] == "info":
                    style = InfoBox.BASE_MESSAGE_STYLE.copy()
                    style.update(InfoBox.INFO_MESSAGE_STYLE)
                    return [data['message'], style]
                elif data['type'] == "error":
                    style = InfoBox.BASE_MESSAGE_STYLE.copy()
                    style.update(InfoBox.ERROR_MESSAGE_STYLE)
                    return [data['message'], style]
                elif data['type'] == "success":
                    style = InfoBox.BASE_MESSAGE_STYLE.copy()
                    style.update(InfoBox.SUCCESS_MESSAGE_STYLE)
                    return [data['message'], style]
                else :
                    return [data['message'], InfoBox.BASE_MESSAGE_STYLE]
            else:
                return ['Info data sent wasnt in correct format', InfoBox.BASE_MESSAGE_STYLE]
    
    
    def build_message(self, message: str, type: str="info"):
        return {"message":message, "type":type}

    def get_output(self):
        '''Get the right data output to use directly in callback'''
        from dash.dependencies import Output
        return Output(self.get_id(InfoBox.DATA), 'data', allow_duplicate=True)
    def get_data_id(self):
        return self.get_id(InfoBox.DATA)
