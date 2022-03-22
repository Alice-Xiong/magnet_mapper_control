
class Mapper():
    config_changed = False
    config_dict = None
    profile = ""
    config_filename = ""

    def __init__(self, config_filename, profile_name):  
        Mapper.config_filename = config_filename
        Mapper.profile = profile_name
        pass

    def stop(self):
        pass