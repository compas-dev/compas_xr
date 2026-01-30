import os
import sys
import time

from compas_xr.realtime_database import RealtimeDatabase


def test_stream_to_reference(config_fp):
    """
    Simple test that streams to a specific reference.

    Parameters
    ----------
    config_fp : str
        Path to the Firebase configuration JSON file.
    """
    db = RealtimeDatabase(config_fp)

    def stream_callback(message):
        print(f"Event: {message['event']}")
        print(f"Path: {message['path']}")
        print(f"Data: {message['data']}")
        print(f"Message: {message}")
        print("-" * 40)

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

    Usage:
        python test_streaming.py [path/to/firebase_config.json]
    """
    #TODO: Test Compas Eve for a python env.

    default_config = (
        r"C:\Users\jk6372\Desktop\00_princeton_projects\00_robotic_territories"
        r"\00_git\compas_xr_robotic_territories\dev\performance_operations"
        r"\fb_config\robotic_territories_fb.json"
    )

    if len(sys.argv) >= 2:
        config_fp = sys.argv[1]
    else:
        config_fp = default_config
        print(f"No config path provided, using default: {config_fp}\n")

    if not os.path.exists(config_fp):
        print(f"Config file not found: {config_fp}")
        sys.exit(1)

    test_stream_to_reference(config_fp)
