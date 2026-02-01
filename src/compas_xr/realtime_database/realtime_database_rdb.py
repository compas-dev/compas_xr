import threading
import uuid

from rethinkdb import r


class RealtimeDatabaseRDB:
    """
    A RealtimeDatabaseRDB is defined by a RethinkDB configuration dict and manages connections to RethinkDB.

    This class mimics the interface of RealtimeDatabase but uses RethinkDB as the backend.

    Parameters
    ----------
    config : dict
        The RethinkDB configuration dictionary.
        The dict should contain "host", "port", and "database".
    """

    def __init__(self, config):
        self.config = config
        self._active_streams = {}  # Track {stream_id: stream_info}
        self._host = config.get("host", "localhost")
        self._port = config.get("port", 28015)
        self._db_name = config.get("database", "test")
        self._ensure_database_connection()

    def _ensure_database_connection(self):
        # RethinkDB connections are lightweight, usually we create one per operation or use a pool.
        # For simple check, we try to connect.
        try:
            conn = r.connect(host=self._host, port=self._port, db=self._db_name)
            conn.close()
        except Exception as e:
            raise Exception("Could not connect to RethinkDB: {}".format(e))

    def construct_reference(self, parentname):
        """
        Constructs a database reference under the specified parent name.
        For RethinkDB, this returns the table name.

        Parameters
        ----------
        parentname : str
            The name of the table mapping to the reference.
        """
        # In this simplified implementation, we assume reference name maps to a Table name.
        return parentname

    def stream_data_from_reference(self, callback, database_reference):
        """
        Streams data from a constructed database reference (Table).

        Parameters
        ----------
        callback : function
            A callback function that will be called whenever data changes.
        database_reference : str
            Reference to the database location (Table Name).

        Returns
        -------
        stream : object
            The stream handle that can be closed later using stream.close().
        """
        stream_id = str(uuid.uuid4())

        class StreamHandle:
            def __init__(self, sid, db_inst):
                self._stream_id = sid
                self.db_inst = db_inst

            def close(self):
                self.db_inst.close_stream(self._stream_id)

        stream_handle = StreamHandle(stream_id, self)

        # Define the listener thread
        def listener():
            conn = None
            try:
                conn = r.connect(host=self._host, port=self._port, db=self._db_name)
                # Store connection to close it later
                if stream_id in self._active_streams:
                    self._active_streams[stream_id]["connection"] = conn

                # We assume the table exists for now as per "construct_reference" logic.
                feed = r.table(database_reference).changes().run(conn)

                for change in feed:
                    # Map RethinkDB change to Firebase message format
                    # Firebase: {'event': 'put', 'path': '/', 'data': ...} (simplified)

                    old_val = change.get("old_val")
                    new_val = change.get("new_val")

                    event_type = "put"  # Default to put basically covers update/create

                    # Firebase path includes the key if it's a child update, but here we watch the table.
                    # Let's say path is the document ID relative to the table.
                    path = "/"
                    data = None

                    if new_val:
                        # Created or Updated
                        doc_id = new_val.get("id")
                        if doc_id:
                            path = "/{}".format(doc_id)
                        data = new_val
                    else:
                        # Deleted
                        doc_id = old_val.get("id") if old_val else None
                        if doc_id:
                            path = "/{}".format(doc_id)
                        data = None

                    message = {
                        "event": event_type,
                        "path": path,
                        "data": data,
                        "raw_rethink_change": change,
                    }

                    try:
                        callback(message)
                    except Exception as e:
                        print(f"Error in stream callback: {e}")

            except r.ReqlDriverError:
                pass
            except Exception as e:
                print(f"Stream error: {e}")
            finally:
                if conn:
                    conn.close()

        t = threading.Thread(target=listener, daemon=True)
        self._active_streams[stream_id] = {
            "thread": t,
            "connection": None,
            "handle": stream_handle,
        }
        t.start()

        return stream_handle

    def close_stream(self, stream_id):
        """
        Closes a specific active stream by its stream ID.
        """
        if stream_id in self._active_streams:
            info = self._active_streams[stream_id]
            conn = info.get("connection")
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")
            del self._active_streams[stream_id]
            return True
        return False
