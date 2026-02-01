import json
import os


class Configuration:
    """
    Helper class for loading configuration.
    """

    @staticmethod
    def from_file(path):
        """
        Loads a JSON configuration from a file path.

        Parameters
        ----------
        path : str
            Path to the JSON configuration file.

        Returns
        -------
        dict
            The configuration dictionary.
        """
        if not os.path.exists(path):
            raise Exception("Configuration file not found at path: {}".format(path))

        with open(path, "r") as f:
            return json.load(f)
