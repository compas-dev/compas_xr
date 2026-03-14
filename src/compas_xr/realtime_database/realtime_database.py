import json
import os
from typing import Any
from typing import List

import pyrebase
from compas.data import json_dumps


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

    def __init__(self, config_path: str):
        self.config_path = config_path
        self._ensure_database()

    def _ensure_database(self):
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

    def construct_reference(self, parentname: str) -> Any:
        """
        Constructs a database reference under the specified parent name.

        Parameters
        ----------
        parentname
            The name of the parent under which the reference will be constructed.

        Returns
        -------
        pyrebase.pyrebase.Database
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname)

    def construct_child_refrence(self, parentname: str, childname: str) -> Any:
        """
        Constructs a database reference under the specified parent name & child name.

        Parameters
        ----------
        parentname
            The name of the parent under which the reference will be constructed.
        childname
            The name of the child under which the reference will be constructed.

        Returns
        -------
        pyrebase.pyrebase.Database
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname).child(childname)

    def construct_grandchild_refrence(self, parentname: str, childname: str, grandchildname: str) -> Any:
        """
        Constructs a database reference under the specified parent name, child name, & grandchild name.

        Parameters
        ----------
        parentname
            The name of the parent under which the reference will be constructed.
        childname
            The name of the child under which the reference will be constructed.
        grandchildname
            The name of the grandchild under which the reference will be constructed.

        Returns
        -------
        pyrebase.pyrebase.Database
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname).child(childname).child(grandchildname)

    def construct_reference_from_list(self, reference_list: List[str]) -> Any:
        """
        Constructs a database reference under the specified refrences in list order.

        Parameters
        ----------
        reference_list
            The name of the parent under which the reference will be constructed.

        Returns
        -------
        pyrebase.pyrebase.Database
            The constructed database reference.

        """
        reference = RealtimeDatabase._shared_database
        for ref in reference_list:
            reference = reference.child(ref)
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

    def stream_data_from_reference(self, callback, database_reference):
        raise NotImplementedError("Function Under Developement")

    def upload_data_to_reference(self, data: Any, database_reference: pyrebase.pyrebase.Database):
        """
        Method for uploading data to a constructed database reference.

        Parameters
        ----------
        data
            The data to be uploaded. Data should be JSON serializable.
        database_reference
            Reference to the database location where the data will be uploaded.

        """
        self._ensure_database()
        # TODO: Check if this is stupid... it provides the functionality of making it work with compas objects and consistency across both child classes
        json_string = json_dumps(data)
        database_reference.set(json.loads(json_string))

    def upload_data(self, data: Any, reference_name: str) -> None:
        """
        Uploads data to the Firebase Realtime Database under specified reference name.

        Parameters
        ----------
        data
            The data to be uploaded, needs to be JSON serializable.
        reference_name
            The name of the reference under which the data will be stored.

        """
        database_reference = self.construct_reference(reference_name)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_to_reference_as_child(
        self,
        data: Any,
        reference_name: str,
        child_name: str,
    ) -> None:
        """
        Uploads data to the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        data
            The data to be uploaded, needs to be JSON serializable.
        reference_name
            The name of the reference under which the child should exist.
        child_name
            The name of the reference under which the data will be stored.
        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_to_deep_reference(self, data: Any, reference_list: list[str]) -> None:
        """
        Uploads data to the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        data
            The data to be uploaded, needs to be JSON serializable.
        reference_list
            The names in sequence order in which the data should be nested for upload.
        """
        database_reference = self.construct_reference_from_list(reference_list)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_from_file(self, path_local: str, reference_name: str) -> None:
        """
        Uploads data to the Firebase Realtime Database under specified reference name from a file.

        Parameters
        ----------
        path_local
            The local path in which the data is stored as a json file.
        reference_name
            The name of the reference under which the data will be stored.
        """
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as config_file:
            data = json.load(config_file)
        database_reference = self.construct_reference(reference_name)
        self.upload_data_to_reference(data, database_reference)

    def get_data(self, reference_name: str) -> dict:
        """
        Retrieves data from the Firebase Realtime Database under the specified reference name.

        Parameters
        ----------
        reference_name
            The name of the reference under which the data is stored.

        Returns
        -------
        dict
            The retrieved data in dictionary format.

        """
        database_reference = self.construct_reference(reference_name)
        return self.get_data_from_reference(database_reference)

    def get_data_from_child_reference(self, reference_name: str, child_name: str) -> dict:
        """
        Retreives data from the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        reference_name
            The name of the reference under which the child exists.
        child_name
            The name of the reference under which the data is stored.

        Returns
        -------
        dict
            The retrieved data in dictionary format.

        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        return self.get_data_from_reference(database_reference)

    def get_data_from_deep_reference(self, reference_list: list[str]) -> dict:
        """
        Retreives data from the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        reference_list
            The names in sequence order in which the is nested.

        Returns
        -------
        dict
            The retrieved data in dictionary format.
        """
        database_reference = self.construct_reference_from_list(reference_list)
        return self.get_data_from_reference(database_reference)

    def delete_data(self, reference_name: str) -> None:
        """
        Deletes data from the Firebase Realtime Database under specified reference name.

        Parameters
        ----------
        reference_name
            The name of the reference under which the child should exist.
        """
        database_reference = self.construct_reference(reference_name)
        self.delete_data_from_reference(database_reference)

    def delete_data_from_child_reference(self, reference_name: str, child_name: str) -> None:
        """
        Deletes data from the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        reference_name
            The name of the reference under which the child should exist.
        child_name
            The name of the reference under which the data will be stored.
        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        self.delete_data_from_reference(database_reference)

    def delete_data_from_deep_reference(self, reference_list: list[str]):
        """
        Deletes data from the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        reference_list
            The names in sequence order in which the data should be nested for upload.
        """
        database_reference = self.construct_reference_from_list(reference_list)
        self.delete_data_from_reference(database_reference)
