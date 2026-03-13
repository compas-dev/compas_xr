import io
import json
import os

import pyrebase
from compas.data import json_dumps
from compas.data import json_loads
from compas_xr._path import validate_reference_path

try:
    # from urllib.request import urlopen
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


class Storage:
    """
    A Storage is defined by a Firebase configuration path and a shared storage reference.

    The Storage class is responsible for initializing and managing the connection to a Firebase Storage.
    It ensures that the storage connection is established only once and shared across all instances of the class.

    Parameters
    ----------
    config_path : str
        The path to the Firebase configuration JSON file.

    Attributes
    ----------
    config_path : str
        The path to the Firebase configuration JSON file.
    _shared_storage : pyrebase.Storage, class attribute
        The shared pyrebase.Storage instance representing the connection to the Firebase Storage.
    """

    _shared_storage = None

    def __init__(self, config_path):
        self.config_path = config_path
        self._ensure_storage()

    def _ensure_storage(self):
        """
        Ensures that the storage connection is established.
        If the connection is not yet established, it initializes it.
        If the connection is already established, it returns the existing connection.
        """
        if not Storage._shared_storage:
            path = self.config_path
            if not os.path.exists(path):
                raise Exception("Path Does Not Exist: {}".format(path))
            with open(path) as config_file:
                config = json.load(config_file)
            # TODO: Authorization for storage security (Works for now for us because our Storage is public)
            firebase = pyrebase.initialize_app(config)
            Storage._shared_storage = firebase.storage()

        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

    def _get_file_from_remote(self, url):
        """
        This function is used to get the information form the source url and returns a string
        It also checks if the data is None or == null (firebase return if no data)
        """
        try:
            file_content = urlopen(url).read().decode()
        except Exception as e:
            raise Exception("Unable to get file from url {}. Error={}".format(url, str(e)))

        if file_content is not None and file_content != "null":
            return file_content

        else:
            raise Exception("unable to get file from url {}".format(url))

    def construct_reference(self, path):
        """
        Constructs a storage reference from a slash-delimited path.

        Parameters
        ----------
        path : str
            A storage path like "folder/subfolder/file.json".

        Returns
        -------
        :class: 'pyrebase.pyrebase.Storage'
            The constructed storage reference.

        """
        self._ensure_storage()
        parts = validate_reference_path(path)
        storage_reference = Storage._shared_storage
        for part in parts:
            storage_reference = storage_reference.child(part)
        return storage_reference

    def get_data_from_reference(self, storage_reference):
        """
        Retrieves data from the specified storage reference.

        Parameters
        ----------
        storage_reference : pyrebase.pyrebase.Storage
            The storage reference pointing to the desired data.

        Returns
        -------
        data : dict or Compas Class Object
            The deserialized data retrieved from the storage reference.

        """
        url = storage_reference.get_url(token=None)
        data = self._get_file_from_remote(url)
        deserialized_data = json_loads(data)
        return deserialized_data

    def upload_bytes_to_reference_from_local_file(self, file_path, storage_reference):
        """
        Uploads data from bytes to the specified storage reference from a local file.

        Parameters
        ----------
        file_path : str
            The path to the local file.
        storage_reference : pyrebase.pyrebase.Storage
            The storage reference to upload the byte data to.

        Returns
        ------
        None

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        with open(file_path, "rb") as file:
            byte_data = file.read()
        storage_reference.put(byte_data)

    def upload_data_to_reference(self, data, storage_reference, pretty=True):
        """
        Uploads data to the specified storage reference.

        Parameters
        ----------
        data : Any should be json serializable
            The data to be uploaded.
        storage_reference : pyrebase.pyrebase.Storage
            The storage reference to upload the data to.
        pretty : bool, optional
            Whether to format the JSON data with indentation and line breaks (default is True).

        Returns
        ------
        None

        """
        serialized_data = json_dumps(data, pretty=pretty)
        file_object = io.BytesIO(serialized_data.encode())
        storage_reference.put(file_object)

    def upload_data(self, data, path, pretty=True):
        """
        Uploads data to the Firebase Storage at the specified path.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        path : str
            The path under which the data will be stored.
        pretty : bool, optional
            A boolean that determines if the data should be formatted for readability. Default is True.

        Returns
        -------
        None

        """
        storage_reference = self.construct_reference(path)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_from_json(self, path_local, pretty=True):
        """
        Uploads data to the Firebase Storage from JSON file.

        Parameters
        ----------
        path_local : str (path)
            The local path at which the JSON file is stored.
        pretty : bool, optional
            A boolean that determines if the data should be formatted for readability. Default is True.

        Returns
        -------
        None

        """
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as file:
            data = json.load(file)
        cloud_file_name = os.path.basename(path_local)
        storage_reference = self.construct_reference(cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_file_as_bytes(self, file_path):
        """
        Uploads a file as bytes to the Firebase Storage.

        Parameters
        ----------
        file_path : str
            The local path of the file to be uploaded.

        Returns
        -------
        None

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        file_name = os.path.basename(file_path)
        storage_reference = self.construct_reference(file_name)
        self.upload_bytes_to_reference_from_local_file(file_path, storage_reference)

    def upload_file_as_bytes_to_path(self, file_path, path):
        """
        Uploads a file as bytes to the Firebase Storage to the specified path.

        Parameters
        ----------
        file_path : str
            The local path of the file to be uploaded.
        path : str
            The path under which the file will be stored.

        Returns
        -------
        None

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        storage_reference = self.construct_reference(path)
        self.upload_bytes_to_reference_from_local_file(file_path, storage_reference)

    def get_data(self, path):
        """
        Retrieves data from the Firebase Storage for the specified path.

        Parameters
        ----------
        path : str
            The storage path.

        Returns
        -------
        data : dict or Compas Class Object
            The retrieved data in dictionary format or as Compas Class Object.

        """
        storage_reference = self.construct_reference(path)
        return self.get_data_from_reference(storage_reference)

    def download_data_to_json(self, path, path_local, pretty=True):
        """
        Downloads data from the Firebase Storage for the specified path.

        Parameters
        ----------
        path : str
            The storage path.
        path_local : str (path)
            The local path at which the JSON file will be stored.
        pretty : bool, optional
            A boolean that determines if the data should be formatted for readability. Default is True.

        Returns
        -------
        None

        """
        data = self.get_data(path)
        directory_name = os.path.dirname(path_local)
        if not os.path.exists(directory_name):
            raise FileNotFoundError("Directory {} does not exist!".format(directory_name))
        with open(path_local, "w") as file:
            file.write(json_dumps(data, pretty=pretty))
