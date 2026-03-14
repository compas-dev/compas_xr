import io
import json
import os
from typing import Any
from typing import Union

import pyrebase
from compas.data import Data
from compas.data import json_dumps
from compas.data import json_loads

try:
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
    config_path
        The path to the Firebase configuration JSON file.

    Attributes
    ----------
    config_path : str
        The path to the Firebase configuration JSON file.
    """

    _shared_storage = None

    def __init__(self, config_path: str):
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

    def construct_reference(self, cloud_file_name: str) -> pyrebase.pyrebase.Storage:
        """
        Constructs a storage reference for the specified cloud file name.

        Parameters
        ----------
        cloud_file_name
            The name of the cloud file.

        Returns
        -------
        pyrebase.pyrebase.Storage
            The constructed storage reference.

        """
        return Storage._shared_storage.child(cloud_file_name)

    def construct_reference_with_folder(self, cloud_folder_name: str, cloud_file_name: str) -> pyrebase.pyrebase.Storage:
        """
        Constructs a storage reference for the specified cloud folder name and file name.

        Parameters
        ----------
        cloud_folder_name
            The name of the cloud folder.
        cloud_file_name
            The name of the cloud file.

        Returns
        -------
        pyrebase.pyrebase.Storage
            The constructed storage reference.

        """
        return Storage._shared_storage.child(cloud_folder_name).child(cloud_file_name)

    def construct_reference_from_list(self, cloud_path_list: list[str]) -> pyrebase.pyrebase.Storage:
        """
        Constructs a storage reference for consecutive cloud folders in list order.

        Parameters
        ----------
        cloud_path_list
            The list of cloud path names.

        Returns
        -------
        pyrebase.pyrebase.Storage
            The constructed storage reference.

        """
        storage_reference = Storage._shared_storage
        for path in cloud_path_list:
            storage_reference = storage_reference.child(path)
        return storage_reference

    def get_data_from_reference(self, storage_reference: pyrebase.pyrebase.Storage) -> Union[dict, Data]:
        """
        Retrieves data from the specified storage reference.

        Parameters
        ----------
        storage_reference
            The storage reference pointing to the desired data.

        Returns
        -------
        Union[dict, Data]
            The deserialized data retrieved from the storage reference.

        """
        url = storage_reference.get_url(token=None)
        data = self._get_file_from_remote(url)
        deserialized_data = json_loads(data)
        return deserialized_data

    def upload_bytes_to_reference_from_local_file(self, file_path: str, storage_reference: pyrebase.pyrebase.Storage) -> None:
        """
        Uploads data from bytes to the specified storage reference from a local file.

        Parameters
        ----------
        file_path
            The path to the local file.
        storage_reference
            The storage reference to upload the byte data to.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        with open(file_path, "rb") as file:
            byte_data = file.read()
        storage_reference.put(byte_data)

    def upload_data_to_reference(self, data: Any, storage_reference: Any, pretty: bool = True) -> None:
        """
        Uploads data to the specified storage reference.

        Parameters
        ----------
        data
            The data to be uploaded.
        storage_reference
            The storage reference to upload the data to.
        pretty
            Whether to format the JSON data with indentation and line breaks (default is True).

        Returns
        ------
        None

        """
        serialized_data = json_dumps(data, pretty=pretty)
        file_object = io.BytesIO(serialized_data.encode())
        storage_reference.put(file_object)

    def upload_data(self, data: Any, cloud_file_name: str, pretty: bool = True) -> None:
        """
        Uploads data to the Firebase Storage under specified cloud file name.

        Parameters
        ----------
        data
            The data to be uploaded, needs to be JSON serializable.
        cloud_file_name
            The name of the reference under which the data will be stored file type should be specified.(ex: .json)
        pretty
            A boolean that determines if the data should be formatted for readability.
        """
        storage_reference = self.construct_reference(cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_from_json(self, path_local: str, pretty: bool = True):
        """
        Uploads data to the Firebase Storage from JSON file.

        Parameters
        ----------
        path_local
            The local path at which the JSON file is stored.
        pretty
            A boolean that determines if the data should be formatted for readability.

        """
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as file:
            data = json.load(file)
        cloud_file_name = os.path.basename(path_local)
        storage_reference = self.construct_reference(cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_to_folder(self, data: Any, cloud_folder_name: str, cloud_file_name: str, pretty: bool = True):
        """
        Uploads data to the Firebase Storage under specified cloud folder name in cloud file name.

        Parameters
        ----------
        data
            The data to be uploaded, needs to be JSON serializable.
        cloud_folder_name
            The name of the folder under which the data will be stored.
        cloud_file_name
            The name of the reference under which the data will be stored file type should be specified.(ex: .json)
        pretty
            A boolean that determines if the data should be formatted for readability.
        """
        storage_reference = self.construct_reference_with_folder(cloud_folder_name, cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_to_deep_reference(self, data: Any, cloud_path_list: list[str], pretty: bool = True):
        """
        Uploads data to the Firebase Storage under specified reference names in list order.

        Parameters
        ----------
        data
            The data to be uploaded, needs to be JSON serializable.
        cloud_path_list
            The list of reference names under which the data will be stored file type should be specified.(ex: .json)
        pretty
            A boolean that determines if the data should be formatted for readability.
        """
        storage_reference = self.construct_reference_from_list(cloud_path_list)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_file_as_bytes(self, file_path: str) -> None:
        """
        Uploads a file as bytes to the Firebase Storage.

        Parameters
        ----------
        file_path
            The local path of the file to be uploaded.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        file_name = os.path.basename(file_path)
        storage_reference = self.construct_reference(file_name)
        self.upload_bytes_to_reference_from_local_file(file_path, storage_reference)

    def upload_file_as_bytes_to_deep_reference(self, file_path: str, cloud_path_list: list[str]):
        """
        Uploads a file as bytes to the Firebase Storage to specified cloud path.

        Parameters
        ----------
        file_path
            The local path of the file to be uploaded.
        cloud_path_list
            The list of reference names under which the file will be stored.

        Returns
        -------
        None

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        file_name = os.path.basename(file_path)
        new_path_list = list(cloud_path_list)
        new_path_list.append(file_name)

        storage_reference = self.construct_reference_from_list(new_path_list)
        self.upload_bytes_to_reference_from_local_file(file_path, storage_reference)

    def upload_files_as_bytes_from_directory_to_deep_reference(self, directory_path: str, cloud_path_list: list[str]):
        """
        Uploads all files in specified directory as bytes to the Firebase Storage at specified cloud path in list order.

        Parameters
        ----------
        directory_path
            The local path of the directory in which files are stored.
        cloud_path_list
            The list of reference names under which the file will be stored.

        Returns
        -------
        None

        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            raise FileNotFoundError("Directory not found: {}".format(directory_path))
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            self.upload_file_as_bytes_to_deep_reference(file_path, cloud_path_list)

    def get_data(self, cloud_file_name: str):
        """
        Retrieves data from the Firebase Storage for specified cloud file name.

        Parameters
        ----------
        cloud_file_name
            The name of the cloud file.

        Returns
        -------
        data : dict or Compas Class Object
            The retrieved data in dictionary format or as Compas Class Object.

        """
        storage_reference = self.construct_reference(cloud_file_name)
        return self.get_data_from_reference(storage_reference)

    def get_data_from_folder(self, cloud_folder_name: str, cloud_file_name: str) -> Union[dict, Data]:
        """
        Retrieves data from the Firebase Storage for specified cloud folder name and cloud file name.

        Parameters
        ----------
        cloud_folder_name
            The name of the cloud folder.
        cloud_file_name
            The name of the cloud file.

        Returns
        -------
        Union[dict, Data]
            The retrieved data in dictionary format or as Compas Class Object.

        """
        storage_reference = self.construct_reference_with_folder(cloud_folder_name, cloud_file_name)
        return self.get_data_from_reference(storage_reference)

    def get_data_from_deep_reference(self, cloud_path_list: str) -> Union[dict, Data]:
        """
        Retrieves data from the Firebase Storage for specified cloud folder name and cloud file name.

        Parameters
        ----------
        cloud_path_list
            The list of reference names under which the file is stored.

        Returns
        -------
        Union[dict, Data]
            The retrieved data in dictionary format or as Compas Class Object.

        """
        storage_reference = self.construct_reference_from_list(cloud_path_list)
        return self.get_data_from_reference(storage_reference)

    def download_data_to_json(self, cloud_file_name: str, path_local: str, pretty: bool = True):
        """
        Downloads data from the Firebase Storage for specified cloud file name.

        Parameters
        ----------
        cloud_file_name
            The name of the cloud file.
        path_local
            The local path at which the JSON file will be stored.
        pretty
            A boolean that determines if the data should be formatted for readability.

        Returns
        -------
        None

        """
        data = self.get_data(cloud_file_name)
        directory_name = os.path.dirname(path_local)
        if not os.path.exists(directory_name):
            raise FileNotFoundError("Directory {} does not exist!".format(directory_name))
        with open(path_local, "w") as file:
            file.write(json_dumps(data, pretty=pretty))
