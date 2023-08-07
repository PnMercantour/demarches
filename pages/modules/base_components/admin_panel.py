from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .carte import Carte
    from .incoming_data import IncomingData
    from carto_editor import PageConfig

from dash import html, dcc
import dash_bootstrap_components as dbc

from demarches_simpy import DossierState

from carto_editor import APP_INFO_BOX, LOADING_BOX, CONFIG, SELECTOR
from pages.modules.managers import Flight
from pages.modules.utils import GetAttestationApercuURL

from pages.modules.interfaces import *
from pages.modules.flex_components import TriggerCallbackButton


class AdminPanel(html.Div, IBaseComponent):
    ## STYLE
    BUTTON_STYLE = {'margin':'1vh'}
    FIELD_STYLE = {'margin':'1vh'}

    BUTTON_CLASS = ''
    FIELD_CLASS = ''
    GROUP_CLASS = 'm-3 d-flex align-items-center justify-content-center'
    ## ID
    B_TRIGGER_DIALOG = 'b_trigger_dialog'
    B_SUBMIT = 'b_submit'
    B_CANCEL = 'b_cancel'
    B_REFUSER = 'b_reject'
    B_ATTESTATION = 'b_attestation'
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
        set_annotation = SetAnnotation(self.config.data_manager, dossier, avis, CONFIG("label-field/st-prescription"))

        packed_actions.add_action(set_annotation)
        packed_actions.add_action(st_prescription)

        return [self.config.security_manager.perform_action(packed_actions),True]
    
    def __fnc_st_redirection_trigger__(self, data, geojson, email, password, avis, selected):
        from pages.modules.managers import PackedActions, SaveFlight

        uuid = data['uuid']
        flight = self.config.data_manager.get_flight_by_uuid(uuid).get_last_flight()
        dossier =  flight.get_attached_dossier().force_fetch()
        st_token = data['st_token']

        self.process_connection(data, email, password)
        if not self.config.security_manager.is_logged:
            return [{"message" : "Invalid credentials", 'type':"error"}, False]
        
        packed_actions = PackedActions(self.config.data_manager, start_values={'uuid':uuid, 'dossier':dossier}, verbose=True)
        
        # Common Actions
        saving_flight = SaveFlight(self.config.data_manager, geojson, dossier)

        #Check if the geojson fetched by the edit component is valid, if not, it means there is no new flight
        if saving_flight.precondition():
            packed_actions.add_action(saving_flight)
        #Check if the flight selected is not the current one, if not, it means the user wants to change the flight
        elif flight.get_last_flight().get_id() != selected:
            #Get the new flight
            new_flight = self.config.data_manager.get_flight_by_uuid(selected)
            packed_actions.add_action(SaveFlight(self.config.data_manager, Flight.build_complete_geojson(new_flight), dossier, new_flight.get_id() if new_flight.is_template() else None))


        if st_token is None:
            return self.__fnc_st_request_trigger__(packed_actions, avis, uuid, dossier)
        else:
            return self.__fnc_st_prescription_trigger__(packed_actions, avis, uuid, dossier)

    def build_fnc_finalized_state(self, state : DossierState):
        if state != DossierState.ACCEPTE and state != DossierState.REFUSE and state != DossierState.SANS_SUITE:
            state = DossierState.REFUSE
        '''Return the custom function based on the state'''
        def __tmp__(self, data, geojson, email, password, avis, selected):
            from pages.modules.managers import PackedActions, SaveFlight, SetAnnotation, SendInstruct, BuildPdf, DeleteSTToken, ChangeDossierState, SaveNewTemplate
            from pages.modules.config import CONFIG

            uuid = data['uuid']
            flight = self.config.data_manager.get_flight_by_uuid(uuid).get_last_flight()
            dossier = flight.get_attached_dossier().force_fetch()
            skeleton = CONFIG("email-templates/dossier-accepted") if state == DossierState.ACCEPTE else CONFIG("email-templates/dossier-refused")
            pdf_url = CONFIG("url-template/pdf-path").format(dossier_id=dossier.get_id())
            attestation_url=lambda dossier : dossier.force_fetch().get_data()['dossier']['attestation']['url'] if state == DossierState.ACCEPTE else ""
            self.process_connection(data, email, password)
            if not self.config.security_manager.is_logged():
                return [{"message" : "Invalid credentials", 'type':"error"}, False]

            packed_actions = PackedActions(self.config.data_manager, start_values={'uuid' : uuid}, verbose=True)

            # Common Actions
            saving_flight = SaveFlight(self.config.data_manager, geojson, dossier)

            new_flight = saving_flight.precondition()

            delete_st_token = DeleteSTToken(self.config.data_manager, dossier)
            add_pdf_url_to_dossier = SetAnnotation(self.config.data_manager, dossier, pdf_url, CONFIG("label-field/flight-pdf-url", "plan-de-vol"))
            change_dossier_state = ChangeDossierState(self.config.data_manager, dossier, state)
            build_pdf = BuildPdf(self.config.data_manager, dossier, flight)
            send_instruct = SendInstruct(self.config.data_manager, skeleton['subject'], open(skeleton['body-path'],"r",encoding='utf-8').read(), avis, pdf_url=pdf_url, attestation_url=attestation_url )
            save_new_template = SaveNewTemplate(self.config.data_manager)

            if new_flight:
                packed_actions.add_action(saving_flight)
            #Check if the flight selected is not the current one, if not, it means the user wants to change the flight
            elif flight.get_last_flight().get_id() != selected:
                #Get the new flight
                new_flight = self.config.data_manager.get_flight_by_uuid(selected)
                packed_actions.add_action(SaveFlight(self.config.data_manager, Flight.build_complete_geojson(new_flight), dossier, new_flight.get_id() if new_flight.is_template() else None))

            packed_actions.add_action(delete_st_token)
            if state == DossierState.ACCEPTE:
                packed_actions.add_action(save_new_template).add_action(add_pdf_url_to_dossier).add_action(change_dossier_state).add_action(build_pdf)
            else:
                packed_actions.add_action(change_dossier_state)
            packed_actions.add_action(send_instruct)

            return [self.config.security_manager.perform_action(packed_actions),True]
        return __tmp__

    def __fnc_submit_trigger__(self, data, geojson, email, password, avis, selected):
        if self.mode == self.ACCEPTER_ACTION:
            return self.build_fnc_finalized_state(DossierState.ACCEPTE)(self, data, geojson, email, password, avis, selected)
        elif self.mode == self.REFUSER_ACTION:
            return self.build_fnc_finalized_state(DossierState.REFUSE)(self, data, geojson, email, password, avis, selected)
        elif self.mode == self.SUBMIT_ACTION:
            return self.__fnc_st_redirection_trigger__(data, geojson, email, password, avis, selected)


    def __init__(self,pageConfig: PageConfig, map: Carte, incoming_data : IncomingData):
        self.is_st = False
        self.incoming_data = incoming_data
        self.map = map
        IBaseComponent.__init__(self, pageConfig)
        html.Div.__init__(self, children=self.__get_layout__(), id=self.get_prefix(), style=self.__get_root_style__(), className=self.__get_root_class__())

        
        self.set_internal_callback()
        incoming_data.set_callback(self.get_prefix(), self.__fnc_init__, "children")



    def __get_layout__(self, uuid=None):
        #TODO: refacto STATE COMPONENT
        disabled_block = True
        disabled_submit = True
        disabled_block = True
        attestation_url = ""


        is_hidden = lambda x : "d-none" if x else ""
        ## CHECK THE FLIGHT VALIDITY
        if self.config.data_manager.is_flight_uuid_valid(uuid):
            flight = self.config.data_manager.get_flight_by_uuid(uuid)
            dossier = flight.get_attached_dossier() 
            disabled_block = self.is_st or self.config.data_manager.is_file_closed(dossier)
            disabled_submit = (self.config.data_manager.is_st_token_already_exists(dossier) and not self.is_st) or self.config.data_manager.is_file_closed(dossier)
            attestation_url = GetAttestationApercuURL(CONFIG('general/demarche-number'), dossier.get_number())

        st_label = "Avis ST" if not self.is_st else "Valider"

        ## BUILD THE LAYOUT
        layout = html.Div([
            dbc.InputGroup([
                html.Div([
                    dbc.Input(type="email", placeholder="Instructeur Email", className=self.FIELD_CLASS,style=AdminPanel.FIELD_STYLE, disabled=disabled_block, id=self.set_id(AdminPanel.F_EMAIL)),
                    dbc.Input(type="password", placeholder="Instructeur Password", className=self.FIELD_CLASS, style=AdminPanel.FIELD_STYLE, disabled=disabled_block, id=self.set_id(AdminPanel.F_PASSWORD)),
                ],id=self.set_id(AdminPanel.LOGIN_FIELD), className=f"{is_hidden(disabled_block)} {self.GROUP_CLASS}"),
                html.Div([
                    dbc.Button(st_label, style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_TRIGGER_DIALOG),className=self.BUTTON_CLASS, color='warning' if not self.is_st else 'success'),
                ], className=f"{is_hidden(disabled_submit)} {self.GROUP_CLASS}"),
                html.Div([
                    dbc.Button("Accepter", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_ACCEPTER), className=self.BUTTON_CLASS, color="success"),
                    dbc.Button("Refuser", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_REFUSER), className=self.BUTTON_CLASS, color="danger"),
                    dbc.Button("Attestation", className=self.BUTTON_CLASS+' btn-primary', style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_ATTESTATION), href=attestation_url),
                ], className=f"{is_hidden(disabled_block)} {self.GROUP_CLASS}"),
                test := TriggerCallbackButton(self.set_id('test'), children='test')
            ],id=self.set_id(AdminPanel.FORM)),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Prescription ?" if self.is_st else "Commentaire ?")),
                dbc.ModalBody([
                dbc.Input(type="text", placeholder="", style=AdminPanel.FIELD_STYLE, id=self.set_id(AdminPanel.F_AVIS)),
                ]),
                dbc.ModalFooter([
                submit_button := TriggerCallbackButton(self.set_id(self.B_SUBMIT), children = "Envoyer", style=AdminPanel.BUTTON_STYLE),
                dbc.Button("Annuler", style=AdminPanel.BUTTON_STYLE, color='danger', id=self.set_id(AdminPanel.B_CANCEL))
                ])
            ],id=self.set_id(AdminPanel.DIALOG_BOX),is_open=False)
        ])

        ## ADD SUBMIT CALLBACK
        submit_button.add_state(self.incoming_data.get_prefix() , "data")
        submit_button.add_state(self.map.get_comp_edit(), "geojson")
        submit_button.add_state(self.get_id(self.F_EMAIL), "value")
        submit_button.add_state(self.get_id(self.F_PASSWORD), "value")
        submit_button.add_state(self.get_id(self.F_AVIS), "value")
        submit_button.add_state(SELECTOR.get_prefix(), "data")
        submit_button.set_callback([APP_INFO_BOX.get_output(), LOADING_BOX.get_output()] , self.__fnc_submit_trigger__, ['data','hidden'], prevent_initial_call=True)

        ## ADD TEST CALLBACK
        def __test__(data):
            uuid = data['uuid']
            flight = self.config.data_manager.get_flight_by_uuid(uuid).get_last_flight()
            from pages.modules.managers.action_manager import BuildPdf

            pdf = BuildPdf(self.config.data_manager, flight.get_attached_dossier(), flight)
            return pdf.perform(uuid=flight.get_id()).result

        
        test.add_state(self.incoming_data.get_prefix() , "data")
        test.set_callback(APP_INFO_BOX.get_output() , __test__, 'data', prevent_initial_call=True)


        return layout



    def set_internal_callback(self):
        from dash import callback, no_update
        from dash import callback_context as ctx
        from dash.dependencies import Input, Output, State

        ## INIT DIALOG
        @callback(
        Output(self.get_id(AdminPanel.DIALOG_BOX), 'is_open'),
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
