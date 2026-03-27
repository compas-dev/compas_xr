# r: compas_xr>=2.0.0
"""
Component to stream data from Realtime Database.

Streams updates from Firebase Realtime Database using a background worker.

COMPAS XR v1.0.0
"""

import time

import Grasshopper
from compas_eve.ghpython import BackgroundWorker

from compas_xr.realtime_database import RealtimeDatabase


def start_rtdb_stream(worker, config_filepath, rtdb_path, return_full_data):
    worker.config_filepath = config_filepath
    worker.rtdb_path = rtdb_path
    worker.return_full_data = bool(return_full_data)
    worker.db = RealtimeDatabase(config_filepath)
    worker.stream_id = None
    worker.update_count = 0
    worker.display_message("Connecting...")

    def on_message(message):
        evt = message.get("event")
        pth = message.get("path")
        raw_dat = message.get("data")

        if worker.return_full_data:
            # Pull the full current subtree from the subscribed path.
            try:
                dat = worker.db.get_data(worker.rtdb_path)
            except Exception:
                dat = raw_dat
        else:
            # Use raw event delta payload.
            dat = raw_dat

        worker.update_count += 1
        worker.update_result((evt, pth, dat), delay=1)

        mode = "full" if worker.return_full_data else "delta"
        worker.display_message("Received Update #{} ({})".format(worker.update_count, mode))

    stream_obj = worker.db.stream_data(rtdb_path, on_message)
    worker.stream_id = getattr(stream_obj, "_stream_id", None)

    mode = "full" if worker.return_full_data else "delta"
    worker.display_message("Streaming... waiting for updates ({})".format(mode))

    while not worker.has_requested_cancellation():
        time.sleep(0.1)

    return None


def stop_rtdb_stream(worker):
    # Called by worker.dispose().
    if hasattr(worker, "db") and worker.db and hasattr(worker, "stream_id") and worker.stream_id:
        try:
            worker.db.close_stream(worker.stream_id)
        except Exception as e:
            worker.display_message("Stop error: {}".format(e))
    worker.display_message("Stopped")


class StreamRealtimeDatabaseComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, config_filepath, path, stream, return_full_data):
        event = None
        event_path = None
        data = None
        status = "stopped"

        if stream is None:
            stream = False

        if return_full_data is None:
            return_full_data = True

        if not stream:
            BackgroundWorker.stop_instance_by_component(ghenv)  # noqa: F821
            return event, event_path, data, status

        if not config_filepath or not path:
            status = "error: provide config_filepath and path"
            return event, event_path, data, status

        worker = BackgroundWorker.instance_by_component(
            ghenv,  # noqa: F821
            start_rtdb_stream,
            dispose_function=stop_rtdb_stream,
            auto_set_done=False,
            force_new=False,
            args=(config_filepath, path, return_full_data),
        )

        must_restart = False
        if hasattr(worker, "config_filepath") and hasattr(worker, "rtdb_path"):
            if worker.config_filepath != config_filepath or worker.rtdb_path != path:
                must_restart = True
            elif hasattr(worker, "return_full_data") and worker.return_full_data != bool(return_full_data):
                must_restart = True

        if must_restart:
            worker = BackgroundWorker.instance_by_component(
                ghenv,  # noqa: F821
                start_rtdb_stream,
                dispose_function=stop_rtdb_stream,
                auto_set_done=False,
                force_new=True,
                args=(config_filepath, path, return_full_data),
            )

        if not worker.is_working():
            worker.start_work()

        if hasattr(worker, "result") and worker.result:
            event, event_path, data = worker.result

        if worker.is_working():
            mode = "full" if bool(return_full_data) else "delta"
            status = "streaming ({}, {})".format(getattr(worker, "stream_id", None), mode)
        elif worker.is_done():
            status = "done"
        else:
            status = "idle"

        return event, event_path, data, status
