# r: compas_xr>=2.0.0
"""
Application Settings.

COMPAS XR v1.0.0
"""

import Grasshopper

from compas_xr.ghpython.app_settings import AppSettings
from compas_xr.project import ProjectManager


class ApplicationSettingsComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, config_filepath, project_name, storage_folder, z_to_y_remap, write):
        if not (config_filepath):
            self.Message = "Missing Config"

        elif not (project_name):
            self.Message = "Missing Settings Data"

        else:
            app_settings = AppSettings(project_name, storage_folder, z_to_y_remap)
            pm = ProjectManager(config_filepath)
            self.Message = None

            if write:
                pm.application_settings_writer(app_settings.project_name, app_settings.storage_folder, app_settings.z_to_y_remap)
