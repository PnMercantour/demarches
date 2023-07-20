from pages.modules.config import PageConfig
class IBaseComponent():
    def __init__(self, pageConfig: PageConfig):
        component_prefix = str(type(self)).split(".")[-1].replace("'>","")
        self.prefix = pageConfig.page_name+"_"+component_prefix
        self.ids = []

    def set_id(self, id: str):
        full_id = self.prefix+"_"+id
        if full_id not in self.ids:
            self.ids.append(full_id)
            return full_id
        else:
            return full_id

    def get_id(self, id: str):
        full_id = self.prefix+"_"+id
        if full_id in self.ids:
            return full_id
        else:
            raise Exception(f"id {id} does not exists")

    def get_prefix(self):
        return self.prefix

    def __get_layout__(self):
        pass

    def __get_root_style__(self):
        return {'backgroundColor': 'white', 'borderRadius': '5px', 'boxShadow': '2px 2px 2px lightgrey', 'padding': '10px', 'minWidth': '300px', 'margin': '10px', 'minWidth': '300px' }


    def set_internal_callback(self) -> None:
        '''Set the callback for the component concerning internal changes'''
        pass

        