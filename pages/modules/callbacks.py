from dash.dependencies import Input, Output, State
from collections.abc import Callable
from dash import callback


class CustomCallback():
    def __init__(self, allow_duplicate=False):
        self.states = []
        self.is_callback_set = False
        self.allow_duplicate = allow_duplicate
    def __process_properties__(self, output_ids, output_properties) -> list:
        if not isinstance(output_ids, list):
            return [output_properties]

        if isinstance(output_properties, str):
            output_properties = [output_properties for _ in range(len(output_ids))]
        else:
            if len(output_ids) != len(output_properties):
                raise Exception("output_ids and output_properties must have the same length")
        return output_properties

    def __process_output__(self, output_ids, output_properties: list) -> list:
        #if output_ids is not list:
        if not isinstance(output_ids, list):
            #check if output_id is not an Output
            if not isinstance(output_ids, Output):
                return Output(output_ids, output_properties[0])
            return output_ids
        else:
            outputs = []
            for output_id, output_property in zip(output_ids, output_properties):
                #check if output_id is not an Output
                if not isinstance(output_id, Output):
                    outputs.append(Output(output_id, output_property))
                else:
                    outputs.append(output_id)
            return outputs
    def set_callback(self, output_ids: list, fnc: Callable[[], list],output_properties="children",prevent_initial_call=False) -> list[Output]:
        self.is_callback_set = True if not self.allow_duplicate else False
        output_properties = self.__process_properties__(output_ids, output_properties)
        return self.__process_output__(output_ids, output_properties)

    def add_state(self, id: str, prop: str):
        self.states.append(State(id, prop))


class SingleInputCallback(CustomCallback):
    def __init__(self, input_id, input_prop="children"):
        super().__init__()
        from dash.dependencies import Input
        self.input_id = input_id
        self.input_prop = input_prop

        self.input = Input(input_id, input_prop)

    def set_callback(self, output_ids: list, fnc: Callable[[any,], list], output_properties="children", prevent_initial_call=True, **kwargs) -> None:
        @callback(
            super().set_callback(output_ids, fnc, output_properties),
            self.input,
            self.states,
            prevent_initial_call=prevent_initial_call,
            **kwargs
        )
        def __set__(data, *args):
            return fnc(data, *args)

