from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import uuid

import pyrebase
from compas.data import json_dumps


class RealtimeDatabase:
    """
    A RealtimeDatabase is defined by a Firebase configuration dict and a shared database reference.

    The RealtimeDatabase class is responsible for initializing and managing the connection to a Firebase Realtime Database.
    It ensures that the database connection is established only once and shared across all instances of the class.

    Parameters
    ----------
    config : dict
        The Firebase configuration dictionary.

    Attributes
    ----------
    config : dict
        The Firebase configuration dictionary.
    database : Database
        The Database instance representing the connection to the Firebase Realtime Database.
    _shared_database : Database, class attribute
        The shared Database instance representing the connection to the Firebase Realtime Database.
    """

    _shared_database = None

    def __init__(self, config):
        self.config = config
        self._active_streams = {}  # Track {stream_id: stream_object}
        self._ensure_database()

    def _ensure_database(self):
        """
        Ensures that the database connection is established.
        If the connection is not yet established, it initializes it.
        If the connection is already established, it returns the existing connection.
        """
        if not RealtimeDatabase._shared_database:
            # TODO: Database Authorization (Works only with public databases)
            firebase = pyrebase.initialize_app(self.config)
            RealtimeDatabase._shared_database = firebase.database()

        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize database!")

    def construct_reference(self, parentname):
        """
        Constructs a database reference under the specified parent name.

        Parameters
        ----------
        parentname : str
            The name of the parent under which the reference will be constructed.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Database'
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname)

    def construct_child_refrence(self, parentname, childname):
        """
        Constructs a database reference under the specified parent name & child name.

        Parameters
        ----------
        parentname : str
            The name of the parent under which the reference will be constructed.
        childname : str
            The name of the child under which the reference will be constructed.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Database'
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname).child(childname)

    def construct_grandchild_refrence(self, parentname, childname, grandchildname):
        """
        Constructs a database reference under the specified parent name, child name, & grandchild name.

        Parameters
        ----------
        parentname : str
            The name of the parent under which the reference will be constructed.
        childname : str
            The name of the child under which the reference will be constructed.
        grandchildname : str
            The name of the grandchild under which the reference will be constructed.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Database'
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname).child(childname).child(grandchildname)

    def construct_reference_from_list(self, reference_list):
        """
        Constructs a database reference under the specified refrences in list order.

        Parameters
        ----------
        reference_list : list of str
            The name of the parent under which the reference will be constructed.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Database'
            The constructed database reference.

        """
        reference = RealtimeDatabase._shared_database
        for ref in reference_list:
            reference = reference.child(ref)
        return reference

    def delete_data_from_reference(self, database_reference):
        """
        Method for deleting data from a constructed database reference.

        Parameters
        ----------
        database_reference: 'pyrebase.pyrebase.Database'
            Reference to the database location where the data will be deleted from.

        Returns
        -------
        None
        """
        self._ensure_database()
        database_reference.remove()

    def get_data_from_reference(self, database_reference):
        """
        Method for retrieving data from a constructed database reference.

        Parameters
        ----------
        database_reference: 'pyrebase.pyrebase.Database'
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
        """
        Streams data from a constructed database reference.

        Parameters
        ----------
        callback : function
            A callback function that will be called whenever data changes.
            The function should accept one parameter: message (dict with 'event', 'path', 'data').
        database_reference: 'pyrebase.pyrebase.Database'
            Reference to the database location where the data will be streamed from.

        Returns
        -------
        stream : object
            The stream object that can be closed later using stream.close().
            The stream is automatically tracked internally by stream_id.

        """
        self._ensure_database()
        stream = database_reference.stream(callback)
        stream_id = str(uuid.uuid4())
        self._active_streams[stream_id] = stream
        stream._stream_id = stream_id  # Attach ID to stream object for reference
        return stream

    def upload_data_to_reference(self, data, database_reference):
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

    def stream_data(self, callback, reference_name):
        """
        Streams data from the Firebase Realtime Database under the specified reference name.

        The callback function is invoked whenever data at the reference changes.

        Parameters
        ----------
        callback : function
            A callback function that will be called whenever data changes.
            The function should accept one parameter: message (dict with 'event', 'path', 'data').
        reference_name : str
            The name of the reference to stream from.

        Returns
        -------
        stream : object
            The stream object that can be closed later using stream.close().

        """
        database_reference = self.construct_reference(reference_name)
        return self.stream_data_from_reference(callback, database_reference)

    def stream_child_data(self, callback, reference_name, child_name):
        """
        Streams data from the Firebase Realtime Database under specified reference & child name.

        Parameters
        ----------
        callback : function
            A callback function that will be called whenever data changes.
        reference_name : str
            The name of the reference under which the child exists.
        child_name : str
            The name of the child reference to stream from.

        Returns
        -------
        stream : object
            The stream object that can be closed later using stream.close().
        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        return self.stream_data_from_reference(callback, database_reference)

    def stream_deep_reference(self, callback, reference_list):
        """
        Streams data from the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        callback : function
            A callback function that will be called whenever data changes.
        reference_list : list of str
            The names in sequence order for the nested reference path.

        Returns
        -------
        stream : object
            The stream object that can be closed later using stream.close().
        """
        database_reference = self.construct_reference_from_list(reference_list)
        return self.stream_data_from_reference(callback, database_reference)

    def upload_data(self, data, reference_name):
        """
        Uploads data to the Firebase Realtime Database under specified reference name.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        reference_name : str
            The name of the reference under which the data will be stored.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference(reference_name)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_to_reference_as_child(self, data, reference_name, child_name):
        """
        Uploads data to the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        reference_name : str
            The name of the reference under which the child should exist.
        child_name : str
            The name of the reference under which the data will be stored.

        Returns
        -------
        None

        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_to_deep_reference(self, data, reference_list):
        """
        Uploads data to the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        reference_list : list of str
            The names in sequence order in which the data should be nested for upload.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference_from_list(reference_list)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_from_file(self, path_local, refernce_name):
        """
        Uploads data to the Firebase Realtime Database under specified reference name from a file.

        Parameters
        ----------
        path_local : str
            The local path in which the data is stored as a json file.
        reference_name : str
            The name of the reference under which the data will be stored.

        Returns
        -------
        None

        """
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as config_file:
            data = json.load(config_file)
        database_reference = self.construct_reference(refernce_name)
        self.upload_data_to_reference(data, database_reference)

    def get_data(self, reference_name):
        """
        Retrieves data from the Firebase Realtime Database under the specified reference name.

        Parameters
        ----------
        reference_name : str
            The name of the reference under which the data is stored.

        Returns
        -------
        data : dict
            The retrieved data in dictionary format.

        """
        database_reference = self.construct_reference(reference_name)
        return self.get_data_from_reference(database_reference)

    def get_data_from_child_reference(self, reference_name, child_name):
        """
        Retreives data from the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        reference_name : str
            The name of the reference under which the child exists.
        child_name : str
            The name of the reference under which the data is stored.

        Returns
        -------
        data : dict
            The retrieved data in dictionary format.

        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        return self.get_data_from_reference(database_reference)

    def get_data_from_deep_reference(self, reference_list):
        """
        Retreives data from the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        reference_list : list of str
            The names in sequence order in which the is nested.

        Returns
        -------
        data : dict
            The retrieved data in dictionary format.
        """
        database_reference = self.construct_reference_from_list(reference_list)
        return self.get_data_from_reference(database_reference)

    def delete_data(self, reference_name):
        """
        Deletes data from the Firebase Realtime Database under specified reference name.

        Parameters
        ----------
        reference_name : str
            The name of the reference under which the child should exist.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference(reference_name)
        self.delete_data_from_reference(database_reference)

    def delete_data_from_child_reference(self, reference_name, child_name):
        """
        Deletes data from the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        reference_name : str
            The name of the reference under which the child should exist.
        child_name : str
            The name of the reference under which the data will be stored.

        Returns
        -------
        None

        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        self.delete_data_from_reference(database_reference)

    def delete_data_from_deep_reference(self, reference_list):
        """
        Deletes data from the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        reference_list : list of str
            The names in sequence order in which the data should be nested for upload.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference_from_list(reference_list)
        self.delete_data_from_reference(database_reference)

    def close_stream(self, stream_id):
        """
        Closes a specific active stream by its stream ID.

        Parameters
        ----------
        stream_id : str
            The unique identifier of the stream to close.

        Returns
        -------
        bool
            True if stream was closed, False if stream_id not found.

        """
        if stream_id in self._active_streams:
            self._active_streams[stream_id].close()
            del self._active_streams[stream_id]
            return True
        return False

    def close_all_streams(self):
        """
        Closes all active streams managed by this RealtimeDatabase instance.

        Returns
        -------
        int
            The number of streams closed.

        """
        count = len(self._active_streams)
        for stream in list(self._active_streams.values()):
            stream.close()
        self._active_streams.clear()
        return count
