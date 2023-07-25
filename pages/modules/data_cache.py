from pages.modules.managers import FeatureFetching
from pages.modules.managers.security_manager import ISecurityManager

class DataCache():
    def __init__(self):
        self.features = {}
        print("DataCache created")
    

    def get_feature(self, feature_name : str, security : ISecurityManager) -> any:
        if feature_name not in self.features:
            self.features[feature_name] = FeatureFetching(security.get_data_ctx(), feature_name)
            security.perform_action(self.features[feature_name])
        return security.action_result(self.features[feature_name])
        


