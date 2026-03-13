class MqttMessageOptionsXR:
    """Options for MQTT messaging in XR context.

    Parameters
    ----------
    host : str
        MQTT broker host.
    project_name : str
        Name of the project.
    robot_name : str
        Name of the robot.
    """

    def __init__(self, host, project_name, robot_name):
        self.host = host
        self.project_name = project_name
        self.robot_name = robot_name

    def __str__(self):
        return "Options, host={}, project_name={}, robot_name={}".format(self.host, self.project_name, self.robot_name)
