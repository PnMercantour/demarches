from dash.dependencies import Input, Output
from dash import callback
class CustomCallback():
    def __init__(self,output : Output, input : Input):
        self.output = output


    def __set_callback__(self) -> None:
        pass
    
    

    def build(output_objs, input_objs, properties, **kwargs) -> object :
        pass

class BooleanCallback(CustomCallback):
    def __init__(self,output : Output, input : Input, boolean):
        super().__init__(output,input)

    def __set_callback__(self) -> None:
        pass

    def build(output_objs, input_objs, properties, boolean, **kwargs) -> object :
        pass




class CallBackManager():
    pass