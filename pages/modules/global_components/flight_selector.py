from carto_editor import PageConfig
from pages.modules.callbacks import SingleInputCallback
from pages.modules.interfaces import IBaseComponent

from dash import no_update, dcc
from dash.dependencies import Output

class FlightSelector(dcc.Store, IBaseComponent, SingleInputCallback):


    def __on_features_click__(self, feature : str):
        if feature is not None:
            flight = self.config.data_manager.get_flight_by_uuid(feature['properties']['id'])
            if flight is not None:
                return flight.get_id()
            else:
                return no_update
        else:
            return no_update


    def __init__(self, pageConfig: PageConfig, current_flight_id : str = None):
        IBaseComponent.__init__(self, pageConfig)
        dcc.Store.__init__(self, id=self.get_prefix(), storage_type='memory', data=current_flight_id if current_flight_id is not None else None)
        SingleInputCallback.__init__(self, self.get_prefix(), 'data')







    def add_geojson(self, id : str):
        '''Id of the geojson feature component'''
        self.set_geojson_callback(id)
  
    def get_output(self):
        return Output(self.get_prefix(),'data', allow_duplicate=True)

    def set_geojson_callback(self, id):
        callback = SingleInputCallback(id, 'click_feature')
        callback.set_callback(Output(self.get_prefix(),'data', allow_duplicate=True), self.__on_features_click__,'data', prevent_initial_call=True)



    


    

