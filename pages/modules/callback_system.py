from dash.dependencies import Input, Output
from collections.abc import Callable
class CustomCallback():

    def __process_properties__(self, output_ids, output_properties) -> list:
        if isinstance(output_properties, str):
            output_properties = [output_properties for _ in range(len(output_ids))]
        else:
            if len(output_ids) != len(output_properties):
                raise Exception("output_ids and output_properties must have the same length")
        return output_properties
    def set_callback(self, output_ids: list, fnc: Callable[[], list],output_properties="children") -> None:
        pass




    


