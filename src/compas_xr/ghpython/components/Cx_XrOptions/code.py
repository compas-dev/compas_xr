# r: compas_xr>=2.0.0
"""
Component to define COMPAS XR options.

COMPAS XR v1.0.0
"""

import Grasshopper

from compas_xr.ghpython import MqttMessageOptionsXR


class XrOptionsComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, host, project_name, robot_name):
        return MqttMessageOptionsXR(host, project_name, robot_name)
