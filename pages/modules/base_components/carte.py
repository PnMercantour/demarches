from __future__ import annotations
import dash_leaflet as dl
from dash import html, dcc
import dash_bootstrap_components as dbc
from demarches_simpy import DossierState

from carto_editor import PageConfig ,TILE, STATE_PROPS, CACHE,NS_RENDER

from pages.modules.interfaces import IBaseComponent
from pages.modules.callbacks import CustomCallback


class Carte(dl.Map, IBaseComponent):
    # Style
    FILE_STATE_ITEM_STYLE = lambda state : {'color': STATE_PROPS[state]['color'], 'fontWeight': 'bold', 'fontSize': '100%'}
    FILE_STATE_CLASS = "position-absolute top-0 end-0 m-2"
    
    ## ID
    FILE_STATE_INFO = "file_state_info"
    EDIT_CONTROL = "edit_control"

    FEATURE_DZ = "feature_dz"
    FEATURE_ZONE_SENSIBLE = "feature_zone_sensible"
    FEATURE_LIMITES = "feature_limites"

    ## EDIT STATE
    EDIT_CONTROL_EDIT_DRAW = {
                'polyline':{'shapeOptions':{
                        'color':'#ff7777',
                        'weight':6,
                        'opacity':1
                    },
                },
                'polygon':False,
                'rectangle':False,
                'circle':False,
                'marker':False,
                'circlemarker':False
            }
    EDIT_CONTROL_NO_EDIT_DRAW = {
                    'polyline':False,
                    'polygon':False,
                    'rectangle':False,
                    'circle':False,
                    'marker':False,
                    'circlemarker':False
    }

    # MAP CONFIG
    CENTER = [44.13211482938621, 7.093281566795227]
    ZOOM = 9



    def __fnc_edit_control_allow_edit__(self, data):
        flight = self.config.data_manager.get_flight_by_uuid(data['uuid'])
        if flight is None:
            return self.EDIT_CONTROL_NO_EDIT_DRAW
        dossier = flight.get_attached_dossier()
        secu = not self.config.data_manager.is_file_closed(dossier) and dossier.get_dossier_state() == DossierState.CONSTRUCTION
        return self.EDIT_CONTROL_EDIT_DRAW if secu else self.EDIT_CONTROL_NO_EDIT_DRAW

    def __fnc_file_state_info_init__(self, data):
        flight = self.config.data_manager.get_flight_by_uuid(data['uuid'])
        if flight is None:
            return html.Div()
        dossier = flight.get_attached_dossier()
        state = dossier.get_dossier_state().value
        return dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4(f"Dossier n°{dossier.get_number()}"),
                            html.Div([
                            html.P("Etat du dossier : "),
                            html.Div(STATE_PROPS[state]['text'], style=Carte.FILE_STATE_ITEM_STYLE(state))
                            ], className='d-flex flex-row'),
                        ],
                        style={'textAlign': 'start'}
                    ),
                )

    def __fnc_center_on_flight__(self, data):
        flight = self.config.data_manager.get_flight_by_uuid(data['uuid'])
        if flight is None:
            return [self.CENTER, self.ZOOM]
        geojson = flight.get_geojson()
        #Inverse lat long
        return [[geojson["geometry"]["coordinates"][0][1], geojson["geometry"]["coordinates"][0][0]], 12]


    def __get_root_style__(self):
        return {'width': '100%', 'height': '100%', 'margin': "auto", "display": "block"}

    def __get_layout__(self):
        self.comp_edit = dl.EditControl(draw=self.EDIT_CONTROL_EDIT_DRAW, id=self.set_id(Carte.EDIT_CONTROL))
        return [
            TILE,
            dl.FeatureGroup([self.comp_edit]),
            html.Div(id=self.set_id(Carte.FILE_STATE_INFO),className=Carte.FILE_STATE_CLASS, style={'zIndex': 1000})    
        ]
        
    def __init__(self,pageConfig : PageConfig, incoming_data : CustomCallback, forceEdit=False):
        IBaseComponent.__init__(self, pageConfig)
        dl.Map.__init__(self,children=self.__get_layout__(), id=self.get_prefix(), center=self.CENTER, zoom=self.ZOOM, style=self.__get_root_style__())


        incoming_data.set_callback(self.get_id(Carte.FILE_STATE_INFO), self.__fnc_file_state_info_init__)
        incoming_data.set_callback([self.get_prefix(), self.get_prefix()], self.__fnc_center_on_flight__, ['center','zoom'])
        if not forceEdit:
            incoming_data.set_callback(self.get_id(Carte.EDIT_CONTROL), self.__fnc_edit_control_allow_edit__, 'draw')
        

        self.set_internal_callback()
    
    def addGeoJson(self, geojson,id, **kwargs):
        if not self.get_prefix() in id:
            id = self.set_id(id)
        self.children.append(dl.GeoJSON(data=geojson, id=id, **kwargs))
        return self
    def addChildren(self, children):
        self.children.append(children)
        return self
    
    def get_comp_edit(self):
        return self.get_id(Carte.EDIT_CONTROL)

    @staticmethod
    def SetAllFeatures(map : Carte):
        from carto_editor import FEATURE_LIMITES_STYLE, FEATURE_ZONE_SENSIBLE_OPTION
        
        options_dz = dict(pointToLayer=NS_RENDER('draw_drop_zone'), filter=NS_RENDER('common_filter'))
        options_limites = dict(style=FEATURE_LIMITES_STYLE,filter=NS_RENDER('common_filter'))
        options_zone_sensible = FEATURE_ZONE_SENSIBLE_OPTION

        ## FETCHING FEATURES
        zone_sensible = CACHE.get_feature('zone_sensible', map.config.security_manager)
        limites_data = CACHE.get_feature('limites', map.config.security_manager)
        drop_zone_data = CACHE.get_feature('drop_zone', map.config.security_manager)

        map.addGeoJson(limites_data,id=map.FEATURE_LIMITES,options=options_limites)
        map.addGeoJson(drop_zone_data,id=map.FEATURE_DZ,options=options_dz, cluster=True,clusterToLayer=NS_RENDER('draw_drop_zone'), superClusterOptions=dict(radius=200))
        map.addGeoJson(zone_sensible,id=map.FEATURE_ZONE_SENSIBLE, options=options_zone_sensible, hideout=dict(minMonth=6, maxMonth=8))

    

