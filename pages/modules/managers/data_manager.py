from pages.modules.components_temp.data_components import IncomingData
from pages.modules.config import CONFIG
from pages.modules.data import Flight
from demarches_simpy import Dossier, Demarche, Profile


class DataManager():
    def __init__(self, incomingData: IncomingData):
        self.incomingData = incomingData
        self.profile = Profile('OGM3NDUzNjAtZDM2MS00NGY4LWEyNTAtOTUyY2FjZmM1MTU1O2VNTnVKb3hnMWVCQXRtSENNdlVIRXJ4Yw==', verbose = bool(CONFIG('verbose')) , warning = True)

    
    def get_dossier_by_id(self, id: str) -> Dossier:
        pass
    def get_dossier_by_number(self, number: str) -> Dossier:
        pass
    def get_flight_by_uuid(self, uuid: str) -> Flight:
        pass
    def get_attached_dossier(self, flight: Flight) -> Dossier:
        pass
    def get_last_flight(self, dossier: Dossier) -> Flight:
        pass

