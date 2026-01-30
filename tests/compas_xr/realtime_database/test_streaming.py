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

    print(f"Streaming started on reference: {reference_name}")
    print("Waiting for data changes...")
    print("Press Ctrl+C to stop streaming\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping stream...")

    stream.close()
    print("Stream closed")


if __name__ == "__main__":
    """
    Run streaming test directly with a config file path.

    Usage:
        python test_streaming.py [path/to/firebase_config.json]
    """
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
