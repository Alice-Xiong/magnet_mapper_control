
class Mapper():
    """Contains key variables such as filenames and dictionary for configurations that will be shared with all classes.

    Defaults of the class variables are found below.
    """
    config_dict = None
    config_filename = ""
    profile = ""

    def __init__(self, config_filename, profile_name):  
        """Creates an instance of the ``Mapper`` class. 

        The two arguments will be used to update the class variables ``config_filename`` and ``profile``.

        Args:
            config_filename (string): name of the config JSON file, e.g. "config.json"
            profile_name (_type_): name of the profile within the config JSON file, e.g. "custom"
        """
        Mapper.config_filename = config_filename
        Mapper.profile = profile_name
        pass
