import os
import sys
import time
import json

from compas_xr.realtime_database import RealtimeDatabaseRDB


def test_stream_to_reference(config_fp):
    """
    Simple test that streams to a specific reference (Table) using RethinkDB backend.

    To run this test, ensure that RethinkDB is running. You can use docker to start a new instance:

        docker run -d -P --name rethink1 rethinkdb

    Parameters
    ----------
    config_fp : str
        Path to the RethinkDB configuration JSON file.
    """
    with open(config_fp, "r") as f:
        config = json.load(f)
    db = RealtimeDatabaseRDB(config)

    def stream_callback(message):
        print(f"Event: {message['event']}")
        print(f"Path: {message['path']}")
        print(f"Data: {message['data']}")
        print(f"Message: {message}")
        print("-" * 40)

    # In RethinkDB implementation, reference maps to a Table.
    # Ensure table "Users" exists in "test" db for this to work perfectly,
    # but the stream will just wait or fail silently/loudly in thread if not.
    # For robust test we might want to ensure table exists, but let's follow the pattern.
    reference_name = "Users"
    database_reference = db.construct_reference(reference_name)
    stream = db.stream_data_from_reference(stream_callback, database_reference)

    stream_id = stream._stream_id
    print(f"Streaming started on reference: {reference_name}")
    print(f"Stream ID: {stream_id}")
    print("Waiting for data changes...")
    print("Press Ctrl+C to stop streaming\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping stream...")

    # Close stream via manager
    closed = db.close_stream(stream_id)
    if closed:
        print(f"Stream {stream_id} closed via manager")
    else:
        print(f"Stream {stream_id} not found in active streams")

    # Show remaining active streams
    remaining = len(db._active_streams)
    print(f"Remaining active streams: {remaining}")


if __name__ == "__main__":
    """
    Run streaming test directly with a config file path.
    """

    # Default relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(current_dir, "rethink_config.json")

    if len(sys.argv) >= 2:
        config_fp = sys.argv[1]
    else:
        config_fp = default_config
        print(f"No config path provided, using default: {config_fp}\n")

    if not os.path.exists(config_fp):
        print(f"Config file not found: {config_fp}")
        sys.exit(1)

    test_stream_to_reference(config_fp)
