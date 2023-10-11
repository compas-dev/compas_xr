from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from compas_xr import SCRIPT

from compas.rpc import Proxy

import os
import json
import pyrebase


class RealtimeDatabase(object):

    # Class attribute for the shared firebase database reference
    _shared_database = None

    def __init__(self, default_config_path = None, config_path=None):
        self.config_path = config_path
        self.default_config_path = default_config_path
        self._ensure_database()

    def _ensure_database(self):
        # Initialize firebase connection and storage only once
        if not RealtimeDatabase._shared_database:
            path = self.config_path or self.default_config_path

            # Load the firebase configuration file from the JSON file if it exists: Else: Print.
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)

            firebase = pyrebase.initialize_app(config)
            RealtimeDatabase._shared_database = firebase.database()

        # Still no Database? Fail, we can't do anything
        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize database!")


    def stream_handler(self,message):
        self._ensure_database()
        print(message["event"])
        print(message["path"])
        print(message["data"])


    def set_json_data(self, json_f, parentname, keys):
        self._ensure_database()
        with open(json_f) as json_file:
            json_data = json.load(json_file)
            children = []
            for key in keys:
                values = json_data[key]
                children.append(values)

        for child, key in zip(children, keys):
            RealtimeDatabase._shared_database.child(parentname).child(key).set(child)


    def set_json_data_joints(self, json_f):
        self._ensure_database()
        with open(json_f) as json_file:
            json_data = json.load(json_file)

        RealtimeDatabase._shared_database.child("Joints").set(json_data)


    # def set_qr_frames(json_fr): 
    #     with open(json_fr) as json_file:
    #         json_data = json.load(json_file)

    #     db.child("QRFrames").set(json_data)


    def set_qr_frames(self, data, parent_name):
        self._ensure_database() 
        RealtimeDatabase._shared_database.child(parent_name).set(data)


    def set_data(self, childname, data):
        self._ensure_database() 
        RealtimeDatabase._shared_database.child(childname).set(data)

    # get keys_built
    def get_keys_built(self):
        self._ensure_database()
        keys_built = []
        keys = RealtimeDatabase._shared_database.child("Built Keys").get()
        if keys.each():
            for key in keys.each():
                # print("key to built key ", key.key())
                keys_built.append(key.val())
        return keys_built


    def set_keys_built(self, keys):
        self._ensure_database()
        data = {}
        for key in keys:
            data[str(key)] = str(key)
        RealtimeDatabase._shared_database.child("Built Keys").set(data)


    def remove_key_built(self, key):
        self._ensure_database()
        RealtimeDatabase._shared_database.child("Built Keys").child(str(key)).remove()

    # update data


    def add_key_built(self, new_key_built):
        self._ensure_database()
        RealtimeDatabase._shared_database.child("Built Keys").update({str(new_key_built): str(new_key_built)})

    # get users' ids
    def get_users(self):
        self._ensure_database()
        users_ids = []
        users = RealtimeDatabase._shared_database.child("Users").get()
        for user in users.each():
            print(user.key())
            users_ids.append(user.key())
            # print("Selected Key is ", user.val()["selectedKey"])
            # print("Selected by user Nr.", user.val()["userID"])
        return users_ids


    def get_users_attribute(self, attribute):
        self._ensure_database()
        users_attributes = []
        users = RealtimeDatabase._shared_database.child("user").get()
        for user in users.each():
            users_attributes.append(user.val()[attribute])
        return users_attributes


    def get_json_data(self, name, childname):
        self._ensure_database()
        json_data = {}
        data = RealtimeDatabase._shared_database.child(name).child(childname).get()
        if data.each():
            for d in data.each():
                json_data[d.key()] = d.val()
            return json_data
        else:
            dt = RealtimeDatabase._shared_database.child(name).child(childname).get().val()
            return dt
        
    def get_json_data_qr(self, name):
        self._ensure_database()
        json_data = {}
        data = RealtimeDatabase._shared_database.child(name).get()
        if data.each():
            for d in data.each():
                json_data[d.key()] = d.val()
            return json_data
        else:
            dt = RealtimeDatabase._shared_database.child(name).get().val()
            return dt


    def listen():
        pass
        # my_stream = db.child("Built Keys").stream(stream_handler)

    # add a stream_id for multiple streams
    # my_stream = db.child("posts").stream(stream_handler, stream_id="new_post")


    def close_stream(my_stream):
        my_stream.close()

