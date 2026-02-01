"""
********************************************************************************
compas_xr.realtime_database
********************************************************************************

This package contains classes for using Firebase realtime database.

.. currentmodule:: compas_xr.realtime_database

Classes
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    RealtimeDatabase
    RealtimeDatabase
    RealtimeDatabaseRDB

"""

from compas_xr.realtime_database.realtime_database import RealtimeDatabase
from compas_xr.realtime_database.realtime_database_rdb import RealtimeDatabaseRDB

__all__ = ["RealtimeDatabase", "RealtimeDatabaseRDB"]
