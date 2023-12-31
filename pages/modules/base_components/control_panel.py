from dash import no_update, callback, html, dcc, callback_context, Patch
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from carto_editor import PageConfig,NS_RENDER, CACHE, FEATURE_ZONE_SENSIBLE_STYLE
from pages.modules.base_components import IncomingData, Carte, DossierInfo

from pages.modules.interfaces import IBaseComponent

class ControlPanel(dbc.Container, IBaseComponent):
    ##
    MONTH_SLIDER_CLASS = ""
    CONTROL_ITEM_CLASS = "d-flex align-items-center justify-content-center"

    ## ID
    BUTTON_INFO = "button_info"
    MONTH_SLIDER = "month_slider"
    MAP_OPTIONS = "map_options"


        

    def __get_layout__(self):

        if not self.disable_info_panel:
            self.dossier_info = DossierInfo(self.config, self.incoming_data)
        else:
            self.dossier_info = None
        return [
            self.dossier_info,
            dbc.Row([
                dbc.Col([
                        dbc.Col(dbc.Button("Info", id=self.set_id(ControlPanel.BUTTON_INFO), className="mr-1", color="primary" if not self.disable_info_panel else 'dark' , disabled=self.disable_info_panel), width = 4),
                        dbc.Col(dbc.Button([
                            html.I(className="bi bi-info-circle me-1"),
                            " Aide"
                        ], id=self.set_id("button_help"), className="mr-1", color="primary", href="/docs/index"), width=4),
                ], width=2, class_name=self.CONTROL_ITEM_CLASS),
                dbc.Col([
                    dbc.Form([
                        dbc.Label('Options'),
                        dbc.Checklist(
                            options=[
                                {"label":"Drop zone","value": 1},
                                {"label":"Zone sensible","value": 2},
                                {"label":"Limites","value": 3},
                            ],
                            value=[1,2,3],
                            id=self.set_id(self.MAP_OPTIONS),
                            inline=True,
                            switch=True
                        )
                    ])
                ], width=4),
                dbc.Col([html.Div('Affichage des zones sensibles par mois'),dcc.RangeSlider(1,12,1,value=[6,8],id=self.set_id(ControlPanel.MONTH_SLIDER))
                ],width=4)
            ])

        ]

    def set_internal_callback(self) -> None:  
        ## UTILS
        map = self.map
        map_id = lambda x: map.get_id(x)

        ## DOSSIER INFO CALLBACKS
        if self.dossier_info is not None:
            @callback(
                Output(self.dossier_info.get_prefix(), "is_open"),
                Input(self.get_id(self.BUTTON_INFO), "n_clicks"),
                [State(self.dossier_info.get_prefix(), "is_open")],
            )
            def toggle_offcanvas(n1, is_open):
                if n1:
                    return not is_open
                return is_open

        from pages.modules.callbacks import SingleInputCallback
  
        
        ##MONTH SLIDER

        from carto_editor import FEATURE_ZONE_SENSIBLE_OPTION


        @callback(
            [Output(map_id(map.FEATURE_ZONE_SENSIBLE), 'options'),
            Output(map_id(map.FEATURE_ZONE_SENSIBLE), 'hideout'),
            Output(self.incoming_data.get_prefix(), 'data'),
            Output(self.get_id(self.MONTH_SLIDER), 'value')
            ],
            Input(self.get_id(self.MONTH_SLIDER), 'value'),
            State(self.incoming_data.get_prefix(), 'data'),
        )
        def __slider_month_update__(value,data):
            trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]

            min = value[0]
            max = value[1]
            if trigger_id == self.get_id(self.MONTH_SLIDER):
                data['min_month'] = min
                data['max_month'] = max
            else:
                min = data['min_month'] if 'min_month' in data else min
                max = data['max_month'] if 'max_month' in data else max
            patched_data = Patch()
            patched_data['min_month'] = data['min_month']
            patched_data['max_month'] = data['max_month']
            return [FEATURE_ZONE_SENSIBLE_OPTION, dict(minMonth=min, maxMonth=max),patched_data, [int(min),int(max)]]
      
        ## MAP OPTIONS CONTROL CALLBACKS
        def __map_options__(values, zs_dict):
            fblock_all = lambda x : True if not x in values else False


            dz_dict = dict(block_all = fblock_all(1))
            zs_tmp = dict(block_all = fblock_all(2))
            zs_dict.update(zs_tmp)
            limites_dict = dict(block_all = fblock_all(3))
            return [dz_dict, zs_dict, limites_dict]



        map_options = SingleInputCallback(self.get_id(self.MAP_OPTIONS), 'value')
        map_options.add_state(map_id(map.FEATURE_ZONE_SENSIBLE),'hideout')
        map_options.set_callback([map_id(map.FEATURE_DZ), Output(map_id(map.FEATURE_ZONE_SENSIBLE), 'hideout',allow_duplicate=True), map_id(map.FEATURE_LIMITES)], __map_options__, 'hideout', prevent_initial_call=True)
    


    def __get_root_class__(self):
        return 'm-2 shadow-sm p-2'

    def __init__(self, config: PageConfig, map: Carte, incoming_data: IncomingData, disable_info_panel: bool = False):
        self.map = map
        self.incoming_data = incoming_data
        self.disable_info_panel = disable_info_panel
        IBaseComponent.__init__(self, config)
        dbc.Container.__init__(self, id=self.get_prefix(), fluid=True, children=self.__get_layout__(), style=self.__get_root_style__(), class_name=self.__get_root_class__())

        self.set_internal_callback()

        