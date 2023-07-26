from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .carte import Carte
    from .incoming_data import IncomingData
    from carto_editor import PageConfig

from dash import html, dcc
import dash_bootstrap_components as dbc

from pages.modules.data import APP_INFO_BOX, LOADING_BOX


from pages.modules.interfaces import *
from pages.modules.flex_components import TriggerCallbackButton


class AdminPanel(html.Div, IBaseComponent):
    ## STYLE
    BUTTON_STYLE = {'margin':'1vh','backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px'}
    FIELD_STYLE = {'margin':'1vh','height': '30px', 'lineHeight': '30px', 'borderRadius': '5px', 'border': '1px solid lightgrey', 'padding': '0px 10px'}
    ## ID
    B_TRIGGER_DIALOG = 'b_trigger_dialog'
    B_SUBMIT = 'b_submit'
    B_CANCEL = 'b_cancel'
    B_REFUSER = 'b_reject'
    B_ACCEPTER = 'b_accept'
    F_EMAIL = 'f_email'
    F_PASSWORD = 'f_password'
    F_AVIS = 'f_avis'
    LOGIN_FIELD = 'login_field'
    DIALOG_BOX = 'dialog_box'
    FORM = 'form'

    #MODE
    ACCEPTER_ACTION = 0
    REFUSER_ACTION = 1
    SUBMIT_ACTION = 2




    def process_connection(self, data, email, password):
        uuid = data['uuid']
        st_token = data['st_token']

        self.config.security_manager.login({
                'uuid':uuid,
                'email':email,
                'password':password,
                'st_token': st_token
            })


    def __fnc_init__(self, data):
        self.is_st = data['st_token'] != None
        return self.__get_layout__(data['uuid'])


    ## REDIRECTION FNC
    def __fnc_st_request_trigger__(self, packed_actions, avis, uuid, dossier):
        from pages.modules.managers import SendSTRequest, GenerateSTToken
        from pages.modules.config import CONFIG


        #Get the correct message skeleton from config

        skeleton = CONFIG("email-templates/st-requesting")

        st_request = SendSTRequest(self.config.data_manager,skeleton['subject'],open(skeleton['body-path'],'r', encoding='utf-8').read(), avis)
        st_token = GenerateSTToken(self.config.data_manager, dossier)
        

        packed_actions.add_action(st_token)
        packed_actions.add_action(st_request)



        return [self.config.security_manager.perform_action(packed_actions),True]

    def __fnc_st_prescription_trigger__(self, packed_actions, avis, uuid, dossier):
        from pages.modules.managers import SendInstruct, SetAnnotation
        from pages.modules.config import CONFIG

        #Get the correct message skeleton from config
        skeleton = CONFIG("email-templates/st-prescription")

        st_prescription = SendInstruct(self.config.data_manager,skeleton['subject'],open(skeleton['body-path'],'r', encoding='utf-8').read(), avis)
        set_annotation = SetAnnotation(self.config.data_manager, dossier, avis, CONFIG("ds_label_field/st-prescription"))

        packed_actions.add_action(set_annotation)
        packed_actions.add_action(st_prescription)

        return [self.config.security_manager.perform_action(packed_actions),True]
    
    def __fnc_st_redirection_trigger__(self, data, geojson, email, password, avis):
        from pages.modules.managers import PackedActions, SaveFlight

        uuid = data['uuid']
        dossier =  self.config.data_manager.get_flight_by_uuid(uuid).get_attached_dossier().force_fetch()
        st_token = data['st_token']

        self.process_connection(data, email, password)
        if not self.config.security_manager.is_logged:
            return [{"message" : "Invalid credentials", 'type':"error"}, False]
        
        packed_actions = PackedActions(self.config.data_manager, start_values={'uuid':uuid, 'dossier':dossier})
        
        # Common Actions
        
        saving_flight = SaveFlight(self.config.data_manager, geojson)

        if saving_flight.precondition():
            packed_actions.add_action(saving_flight)


        if st_token is None:
            return self.__fnc_st_request_trigger__(packed_actions, avis, uuid, dossier)
        else:
            return self.__fnc_st_prescription_trigger__(packed_actions, avis, uuid, dossier)

    def __fnc_accept_trigger__(self, data, geojson, email, password, avis):
        from pages.modules.managers import PackedActions, SaveFlight, SendInstruct, BuildPdf, DeleteSTToken, ChangeDossierState
        from demarches_simpy import DossierState
        from pages.modules.config import CONFIG

        uuid = data['uuid']
        flight = self.config.data_manager.get_flight_by_uuid(uuid)
        dossier = flight.get_attached_dossier().force_fetch()
        skeleton = CONFIG("email-templates/dossier-accepted")
        pdf_url = CONFIG("url-template/pdf-path").format(dossier_id=dossier.get_id())

        self.process_connection(data, email, password)
        if not self.config.security_manager.is_logged:
            return [{"message" : "Invalid credentials", 'type':"error"}, False]

        packed_actions = PackedActions(self.config.data_manager, start_values={'uuid' : uuid})

        # Common Actions
        saving_flight = SaveFlight(self.config.data_manager, geojson)

        new_flight = saving_flight.precondition()

        delete_st_token = DeleteSTToken(self.config.data_manager, dossier)
        change_dossier_state = ChangeDossierState(self.config.data_manager, dossier, DossierState.ACCEPTE)
        build_pdf = BuildPdf(self.config.data_manager, dossier, geojson if new_flight else Flight.build_complete_geojson(flight))
        send_instruct = SendInstruct(self.config.data_manager, skeleton['subject'], open(skeleton['body-path'],"r",encoding='utf-8').read(), avis, pdf_url=pdf_url, attestation_url=lambda dossier : dossier.force_fetch().get_data()['dossier']['attestation']['url'])


        if new_flight:
            packed_actions.add_action(saving_flight)

        packed_actions.add_action(delete_st_token)
        packed_actions.add_action(change_dossier_state)
        packed_actions.add_action(build_pdf)
        packed_actions.add_action(send_instruct)

        return [self.config.security_manager.perform_action(packed_actions),True]


    def __fnc_submit_trigger__(self, data, geojson, email, password, avis):
        if self.mode == self.ACCEPTER_ACTION:
            return self.__fnc_accept_trigger__(data, geojson, email, password, avis)
        elif self.mode == self.SUBMIT_ACTION:
            return self.__fnc_st_redirection_trigger__(data, geojson, email, password, avis)


    def __init__(self,pageConfig: PageConfig, map: Carte, incoming_data : IncomingData):
        self.is_st = False
        self.incoming_data = incoming_data
        self.map = map
        IBaseComponent.__init__(self, pageConfig)
        html.Div.__init__(self, children=self.__get_layout__(), id=self.get_prefix(), style=self.__get_root_style__())

        
        self.set_internal_callback()
        incoming_data.set_callback(self.get_prefix(), self.__fnc_init__, "children")



    def __get_layout__(self, uuid=None):
        #TODO: refacto STATE COMPONENT
        disabled_block = True
        disabled_submit = True
        disabled_block = True
        


        if self.config.data_manager.is_flight_uuid_valid(uuid):
            flight = self.config.data_manager.get_flight_by_uuid(uuid)
            dossier = flight.get_attached_dossier() 
            disabled_block = self.is_st or self.config.data_manager.is_file_closed(dossier)
            disabled_submit = (self.config.data_manager.is_st_token_already_exists(dossier) and not self.is_st) or self.config.data_manager.is_file_closed(dossier)

        st_label = "Avis ST" if not self.is_st else "Valider"


        layout = html.Div([
            dbc.Form([
                html.Div([
                    dcc.Input(type="email", placeholder="Instructeur Email", style=AdminPanel.FIELD_STYLE, disabled=disabled_block, id=self.set_id(AdminPanel.F_EMAIL)),
                    dcc.Input(type="password", placeholder="Instructeur Password", style=AdminPanel.FIELD_STYLE, disabled=disabled_block, id=self.set_id(AdminPanel.F_PASSWORD)),
                ],id=self.set_id(AdminPanel.LOGIN_FIELD), hidden=disabled_block),
                html.Button(st_label, style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_TRIGGER_DIALOG), hidden=disabled_submit),
                html.Button("Accepter", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_ACCEPTER), hidden=disabled_block),
                html.Button("Refuser", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_REFUSER), hidden=disabled_block),
            ],id=self.set_id(AdminPanel.FORM)),
            html.Dialog([
                html.H3("Prescription ? :" if self.is_st else "Commentaire ? :"),
                dcc.Input(type="text", placeholder="", style=AdminPanel.FIELD_STYLE, id=self.set_id(AdminPanel.F_AVIS)),
                submit_button := TriggerCallbackButton(self.set_id(self.B_SUBMIT), children = "Envoyer", style=AdminPanel.BUTTON_STYLE),
                html.Button("Annuler", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_CANCEL))
            ], style={"zIndex":"900"},id=self.set_id(AdminPanel.DIALOG_BOX),open=False)
        ])

        ## ADD SUBMIT CALLBACK
        submit_button.add_state(self.incoming_data.get_prefix() , "data")
        submit_button.add_state(self.map.get_comp_edit(), "geojson")
        submit_button.add_state(self.get_id(self.F_EMAIL), "value")
        submit_button.add_state(self.get_id(self.F_PASSWORD), "value")
        submit_button.add_state(self.get_id(self.F_AVIS), "value")
        submit_button.set_callback([APP_INFO_BOX.get_output(), LOADING_BOX.get_output()] , self.__fnc_submit_trigger__, ['data','hidden'], prevent_initial_call=True)


        return layout





    def set_internal_callback(self):
        from dash import callback, no_update
        from dash import callback_context as ctx
        from dash.dependencies import Input, Output, State

        ## INIT DIALOG
        @callback(
        Output(self.get_id(AdminPanel.DIALOG_BOX), 'open'),
        [Input(self.get_id(AdminPanel.B_TRIGGER_DIALOG),'n_clicks'), Input(self.get_id(AdminPanel.B_CANCEL),'n_clicks'), Input(self.get_id(AdminPanel.B_ACCEPTER),'n_clicks'), Input(self.get_id(AdminPanel.B_REFUSER),'n_clicks'), Input(self.get_id(AdminPanel.B_SUBMIT),'n_clicks')],
        prevent_initial_call=True,
        )
        def __set__(*args):
            #TODO: refacto STATE COMPONENT
            print(ctx.triggered_id)
            if args[0] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_TRIGGER_DIALOG):
                self.mode = AdminPanel.SUBMIT_ACTION
                return True
            elif args[2] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_ACCEPTER):
                self.mode = AdminPanel.ACCEPTER_ACTION
                return True
            elif args[3] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_REFUSER):
                self.mode = AdminPanel.REFUSER_ACTION
                return True
            elif args[1] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_CANCEL):
                return False
            elif args[4] is not None and ctx.triggered_id == self.get_id(AdminPanel.B_SUBMIT):
                return False
            else:
                return False
    @property
    def is_st(self) -> bool:
        return self.__is_st

    @is_st.setter
    def is_st(self, value):
        self.__is_st = value
