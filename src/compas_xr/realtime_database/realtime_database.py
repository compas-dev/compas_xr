import json
import os
from typing import Any
from typing import Callable
from typing import List

import pyrebase
from compas.data import json_dumps

from compas_xr._path import validate_reference_path


class RealtimeDatabase:
    """
    A RealtimeDatabase is defined by a Firebase configuration path and a shared database reference.

    The RealtimeDatabase class is responsible for initializing and managing the connection to a Firebase Realtime Database.
    It ensures that the database connection is established only once and shared across all instances of the class.

    Parameters
    ----------
    config_path
        The path to the Firebase configuration JSON file.

    Attributes
    ----------
    config_path : str
        The path to the Firebase configuration JSON file.
    database : Database
        The Database instance representing the connection to the Firebase Realtime Database.
    _shared_database : Database, class attribute
        The shared Database instance representing the connection to the Firebase Realtime Database.
    """

    _shared_database = None
    _INVALID_KEY_CHARS = set(".#$[]/")

    def __init__(self, config_path: str):
        self.config_path = config_path
        self._ensure_database()

    def _ensure_database(self) -> None:
        """
        Ensures that the database connection is established.
        If the connection is not yet established, it initializes it.
        If the connection is already established, it returns the existing connection.
        """
        if not RealtimeDatabase._shared_database:
            path = self.config_path

            if not os.path.exists(path):
                raise Exception("Could not find config file at path {}!".format(path))
            with open(path) as config_file:
                config = json.load(config_file)
            # TODO: Database Authorization (Works only with public databases)
            firebase = pyrebase.initialize_app(config)
            RealtimeDatabase._shared_database = firebase.database()

        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize database!")

    def construct_reference(self, path: str) -> pyrebase.pyrebase.Database:
        """
        Constructs a database reference from a slash-delimited path.

        Parameters
        ----------
        path : str
            A database path like "parent/child/grandchild".

        Returns
        -------
        pyrebase.pyrebase.Database
            The constructed database reference.

        Raises
        ------
        ValueError
            If the path is empty or contains invalid Firebase key characters.

        """
        self._ensure_database()
        parts = validate_reference_path(path, invalid_chars=RealtimeDatabase._INVALID_KEY_CHARS)
        reference = RealtimeDatabase._shared_database
        for part in parts:
            reference = reference.child(part)
        return reference

    def delete_data_from_reference(self, database_reference: pyrebase.pyrebase.Database) -> None:
        """
        Method for deleting data from a constructed database reference.

        Parameters
        ----------
        database_reference
            Reference to the database location where the data will be deleted from.

        """
        self._ensure_database()
        database_reference.remove()

    def get_data_from_reference(self, database_reference: pyrebase.pyrebase.Database) -> dict:
        """
        Method for retrieving data from a constructed database reference.

        Parameters
        ----------
        database_reference
            Reference to the database location where the data will be retreived from.

        Returns
        -------
        dict
            The retrieved data as a dictionary.

        """
        self._ensure_database()
        database_directory = database_reference.get()
        data = database_directory.val()
        data_dict = dict(data)
        return data_dict

    def stream_data_from_reference(self, callback: Callable, database_reference: pyrebase.pyrebase.Database) -> Any:
        raise NotImplementedError("Function Under Developement")

    def stream_data(self, path: str, callback: Callable) -> Any:
        """
        Streams data from the Firebase Realtime Database at the specified path.

        Parameters
        ----------
        path : str
            The path from which data should be streamed.
        callback : callable
            Callback used by the stream client.

        Returns
        -------
        Any
            Stream handle/object returned by the underlying implementation.

        """
        database_reference = self.construct_reference(path)
        return self.stream_data_from_reference(callback, database_reference)

    def upload_data_to_reference(self, data: Any, database_reference: pyrebase.pyrebase.Database) -> None:
        """
        Method for uploading data to a constructed database reference.

        Parameters
        ----------
        data : Any
            The data to be uploaded. Data should be JSON serializable.
        database_reference: 'pyrebase.pyrebase.Database'
            Reference to the database location where the data will be uploaded.

        Returns
        -------
        None
        """
        self._ensure_database()
        # TODO: Check if this is stupid... it provides the functionality of making it work with compas objects and consistency across both child classes
        json_string = json_dumps(data)
        database_reference.set(json.loads(json_string))

    def upload_data(self, data: Any, path: str) -> None:
        """
        Uploads data to the Firebase Realtime Database at the specified path.

        Parameters
        ----------
        data
            The data to be uploaded, needs to be JSON serializable.
        path : str
            The path under which the data will be stored.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference(path)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_from_file(self, path_local: str, path: str) -> None:
        """
        Uploads data to the Firebase Realtime Database at the specified path from a file.

        Parameters
        ----------
        path_local
            The local path in which the data is stored as a json file.
        path : str
            The path under which the data will be stored.

        Returns
        -------
        None

        """
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as config_file:
            data = json.load(config_file)
        database_reference = self.construct_reference(path)
        self.upload_data_to_reference(data, database_reference)

    def get_data(self, path: str) -> dict:
        """
        Retrieves data from the Firebase Realtime Database at the specified path.

        Parameters
        ----------
        path : str
            The path under which the data is stored.

        Returns
        -------
        dict
            The retrieved data in dictionary format.

        """
        database_reference = self.construct_reference(path)
        return self.get_data_from_reference(database_reference)

    def delete_data(self, path: str) -> None:
        """
        Deletes data from the Firebase Realtime Database at the specified path.

        Parameters
        ----------
        path : str
            The path that should be deleted.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference(path)
        self.delete_data_from_reference(database_reference)
