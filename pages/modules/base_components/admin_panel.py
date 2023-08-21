from __future__ import annotations
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .carte import Carte
    from .incoming_data import IncomingData
    from carto_editor import PageConfig

from dash import html, dcc
import dash_bootstrap_components as dbc

from demarches_simpy import DossierState

from carto_editor import APP_INFO_BOX, LOADING_BOX, CONFIG, SELECTOR, BUILD_URL
from pages.modules.managers import Flight
from pages.modules.utils import GetAttestationApercuURL, ExtractPointFromGeoJSON,MergeGeoJSON, GetDSRedirectionURL

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
        self.security_manager.login({
                'uuid':uuid,
                'email':email,
                'password':password,
                'st_token': st_token
            })


    def __fnc_init__(self, data):
        from pages.modules.managers import STSecurity
        self.is_st = 'st_token' in data and data['st_token'] != None
        if self.is_st:
            self.__security_manager = STSecurity(self.config.data_manager)
        else:
            self.__security_manager = self.config.security_manager ## AdminSecurity


        return self.__get_layout__(data['uuid'])


    ## FONCTION HANDLING THE PRESCRIPTION REQUEST FOR THE ST
    def __fnc_st_request_trigger__(self, data, packed_actions, avis, uuid, dossier):
        from pages.modules.managers import GenerateSTToken, SendMailTo
        from pages.modules.config import CONFIG

        flight = self.config.data_manager.get_flight_by_uuid(uuid).get_last_flight()
        #Get the correct message skeleton from config
        min_month = data['min_month'] if 'min_month' in data else 6
        max_month = data['max_month'] if 'max_month' in data else 8
        skeleton = CONFIG("email-templates/st-requesting")
        url = BUILD_URL("admin?uuid={flight_id}&st_token={st_token}&min_month={min_month}&max_month={max_month}")

        st_token = GenerateSTToken(self.config.data_manager, dossier)
        packed_actions.add_action(st_token)

        for region in flight.regions:
            tos = CONFIG(f'email-route/{region}',CONFIG('email-route/default'))
            for to in tos:
                with open(skeleton['body-path'],'r', encoding='utf-8') as f:
                    req = SendMailTo(self.config.data_manager,to , skeleton['subject'], f.read(), avis=avis, url=url, min_month=min_month, max_month=max_month)
                packed_actions.add_action(req)





        return [self.security_manager.perform_action(packed_actions),True]

    ## FONCTION HANDLING THE PRESCRIPTION SEND BY THE ST
    def __fnc_st_prescription_trigger__(self, data, packed_actions, avis, uuid, dossier):
        from pages.modules.managers import SendMailTo, SetAnnotation
        from pages.modules.config import CONFIG

        #Get the correct message skeleton from config
        skeleton = CONFIG("email-templates/st-prescription")
        min_month = data['min_month'] if 'min_month' in data else 6
        max_month = data['max_month'] if 'max_month' in data else 8
        url =  BUILD_URL('admin?uuid={flight_id}&min_month={min_month}&max_month={max_month}').format(flight_id=uuid,min_month=min_month,max_month=max_month)
        with open(skeleton['body-path'],'r', encoding='utf-8') as f:
            st_prescription = SendMailTo(self.config.data_manager,dossier.get_attached_instructeurs_info()[0]['email'],skeleton['subject'],f.read(), prescription=avis,url=url)
        set_annotation = SetAnnotation(self.config.data_manager, dossier, avis, CONFIG("label-field/st-prescription"))

        packed_actions.add_action(set_annotation)
        packed_actions.add_action(st_prescription)

        return [self.security_manager.perform_action(packed_actions),True]
    
    ## FUNCTION WHICH TAKE THE SAME BUTTON INPUT AND REDIRECT IF IT'S THE ST OR THE INSTRUCT WHICH TRIGGERED THE ACTION
    def __fnc_st_redirection_trigger__(self, data, geojson, email, password, avis, selected):
        from pages.modules.managers import PackedActions, SaveFlight

        uuid = data['uuid']
        flight = self.config.data_manager.get_flight_by_uuid(uuid).get_last_flight()
        dossier =  flight.get_attached_dossier().force_fetch()
        
        self.process_connection(data, email, password)
        if not self.security_manager.is_logged():
            return [{"message" : "Invalid credentials", 'type':"error"}, False]
        
        packed_actions = PackedActions(self.config.data_manager, start_values={'uuid':uuid, 'dossier':dossier}, verbose=True)
        
        # Common Actions
        saving_flight = SaveFlight(self.config.data_manager, geojson, dossier)

        #Check if the geojson fetched by the edit component is valid, if not, it means there is no new flight
        if saving_flight.precondition():
            packed_actions.add_action(saving_flight)
        #Check if the flight selected is not the current one, if not, it means the user wants to change the flight and treat if it's a template
        elif flight.get_id() != selected:
            #Get the new flight
            new_flight = self.config.data_manager.get_flight_by_uuid(selected)
            final_geojson = Flight.build_complete_geojson(new_flight)
            if(len(geojson['features']) != 0):
                final_geojson = MergeGeoJSON(final_geojson, ExtractPointFromGeoJSON(geojson))
            packed_actions.add_action(SaveFlight(self.config.data_manager, final_geojson, dossier, new_flight.get_id() if new_flight.is_template() else None))


        if not self.is_st:
            return self.__fnc_st_request_trigger__(data, packed_actions, avis, uuid, dossier)
        else:
            return self.__fnc_st_prescription_trigger__(data, packed_actions, avis, uuid, dossier)
    ### RETURN THE TMP FUNCTION AS THE CALLBACK WHICH WILL BE BUILT IN FUNCTION OF THE STATE (AVOID REDUNDANCY)
    def build_fnc_finalized_state(self, state : DossierState):
        if state != DossierState.ACCEPTE and state != DossierState.REFUSE and state != DossierState.SANS_SUITE:
            state = DossierState.REFUSE
        '''Return the custom function based on the state'''
        def __tmp__(self, data, geojson, email, password, avis, selected):
            from pages.modules.managers import PackedActions, SaveFlight, SetAnnotation, SendMailTo, BuildPdf, DeleteSTToken, ChangeDossierState, SaveNewTemplate
            from pages.modules.config import CONFIG

            uuid = data['uuid']
            months = (data['min_month'], data['max_month'])
            flight : Flight = self.config.data_manager.get_flight_by_uuid(uuid).get_last_flight()
            dossier = flight.get_attached_dossier().force_fetch()
            skeleton = CONFIG("email-templates/dossier-accepted") if state == DossierState.ACCEPTE else CONFIG("email-templates/dossier-rejected")
            pdf_url = BUILD_URL('pdf/flight_{dossier_id}.pdf').format(dossier_id=dossier.get_id())
            attestation_url=lambda dossier : dossier.force_fetch().get_data()['dossier']['attestation']['url'] if state == DossierState.ACCEPTE else ""
            self.process_connection(data, email, password)
            print(type(self.security_manager))
            if not self.security_manager.is_logged():
                return [{"message" : "Invalid credentials", 'type':"error"}, False]

            packed_actions = PackedActions(self.config.data_manager, start_values={'uuid' : uuid}, verbose=True)

            # Common Actions
            saving_flight = SaveFlight(self.config.data_manager, geojson, dossier)

            ## Check if the geojson fetched by the edit component is valid, if not, it means there is no new flight edited by the user
            new_flight = saving_flight.precondition()

            delete_st_token = DeleteSTToken(self.config.data_manager, dossier)
            add_pdf_url_to_dossier = SetAnnotation(self.config.data_manager, dossier, pdf_url, CONFIG("label-field/flight-pdf-url", "plan-de-vol"))
            change_dossier_state = ChangeDossierState(self.config.data_manager, dossier, state)
            build_pdf = BuildPdf(self.config.data_manager, dossier, flight, months)
            with open(skeleton['body-path'],"r",encoding='utf-8') as f:
                send_instruct = SendMailTo(self.config.data_manager, dossier.get_attached_instructeurs_info()[0]['email'],skeleton['subject'], f.read(), avis=avis, pdf_url=pdf_url, attestation_url=attestation_url )
            save_new_template = SaveNewTemplate(self.config.data_manager)

            if new_flight:
                packed_actions.add_action(saving_flight)


            #Check if the flight selected is not the current one, if not, it means the user wants to change the flight and treat if it's a template
            elif flight.get_id() != selected:
                #Get the new flight
                new_flight = self.config.data_manager.get_flight_by_uuid(selected)
                final_geojson = Flight.build_complete_geojson(new_flight)
                packed_actions.add_action(SaveFlight(self.config.data_manager, final_geojson, dossier, new_flight.get_id() if new_flight.is_template() else None))

            packed_actions.add_action(delete_st_token)
            if state == DossierState.ACCEPTE:
                packed_actions.add_action(save_new_template).add_action(add_pdf_url_to_dossier).add_action(change_dossier_state).add_action(build_pdf)
            else:
                packed_actions.add_action(change_dossier_state)
            packed_actions.add_action(send_instruct)

            return [self.security_manager.perform_action(packed_actions),True]
        return __tmp__
    ## REDIRECT THE ACTION TRIGGERED BY THE SAME SUBMIT BUTTON WHICH IS THE BUTTON IN THE DIALOG BOX
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
        ds_url = ""


        is_hidden = lambda x : "d-none" if x else ""
        ## CHECK THE FLIGHT VALIDITY
        if self.config.data_manager.is_flight_uuid_valid(uuid):
            flight = self.config.data_manager.get_flight_by_uuid(uuid)
            dossier = flight.get_attached_dossier() 
            disabled_block = self.is_st or self.config.data_manager.is_file_closed(dossier)
            disabled_submit = (self.config.data_manager.is_st_token_already_exists(dossier) and not self.is_st) or self.config.data_manager.is_file_closed(dossier)
            attestation_url = GetAttestationApercuURL(os.getenv('DEMARCHE_NUMBER', 000000), dossier.get_number())
            ds_url = GetDSRedirectionURL(os.getenv('DEMARCHE_NUMBER', 000000), dossier.get_number())
        st_label = "Avis ST" if not self.is_st else "Valider"

        ## BUILD THE LAYOUT
        layout = html.Div([
            dbc.InputGroup([
                html.Div([
                    dbc.Input(type="email", placeholder="Instructeur Email", className=f"{is_hidden(disabled_block)} {self.FIELD_CLASS}",style=AdminPanel.FIELD_STYLE, disabled=disabled_block, id=self.set_id(AdminPanel.F_EMAIL)),
                    dbc.Input(type="password", placeholder="Instructeur Password", className=f"{is_hidden(disabled_block)} {self.FIELD_CLASS}", style=AdminPanel.FIELD_STYLE, disabled=disabled_block, id=self.set_id(AdminPanel.F_PASSWORD)),
                ],id=self.set_id(AdminPanel.LOGIN_FIELD), className="self.GROUP_CLASS"),
                html.Div([
                    dbc.Button(st_label, style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_TRIGGER_DIALOG),className=f"{is_hidden(disabled_submit)} {self.BUTTON_CLASS}", color='warning' if not self.is_st else 'success'),
                ],  className=self.GROUP_CLASS),
                html.Div([
                    dbc.Button("Accepter", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_ACCEPTER), className=f"{is_hidden(disabled_block)} {self.BUTTON_CLASS}", color="success"),
                    dbc.Button("Refuser", style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_REFUSER), className=f"{is_hidden(disabled_block)} {self.BUTTON_CLASS}", color="danger"),
                    dbc.Button("Attestation", className=f"{is_hidden(disabled_block)} {self.BUTTON_CLASS}"+' btn-primary', style=AdminPanel.BUTTON_STYLE, id=self.set_id(AdminPanel.B_ATTESTATION), href=attestation_url),
                    dbc.Button([
                        "DS  ",
                        html.I(className="bi bi-arrow-up-right-circle-fill")
                    ], className=f"{is_hidden(disabled_block)} {self.BUTTON_CLASS}"+' btn-primary ', style=AdminPanel.BUTTON_STYLE, id=self.set_id('ds'), href=ds_url),

                ], className=self.GROUP_CLASS),
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
        def __test__(data, geojson):
            from pages.modules.managers.action_manager import SaveFlight
            # save_flight = SaveFlight(self.config.data_manager, geojson)
            uuid = data['uuid']
            flight = self.config.data_manager.get_flight_by_uuid(uuid).get_last_flight()
            from pages.modules.managers.action_manager import BuildPdf

            pdf = BuildPdf(self.config.data_manager, flight.get_attached_dossier(), flight, [5,8])
            return pdf.perform().result
            return save_flight.perform().result

        
        test.add_state(self.incoming_data.get_prefix() , "data")
        test.add_state(self.map.get_comp_edit(), "geojson")
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


    @property
    def security_manager(self):
        return self.__security_manager
