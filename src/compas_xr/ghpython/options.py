class MqttMessageOptionsXR:
    """Options for MQTT messaging in XR context.

    Parameters
    ----------
    host
        MQTT broker host.
    project_name
        Name of the project.
    robot_name
        Name of the robot.
    """

    def __init__(self, host: str, project_name: str, robot_name: str):
        self.host = host
        self.project_name = project_name
        self.robot_name = robot_name

    def __str__(self) -> str:
        return f"Options, host={self.host}, project_name={self.project_name}, robot_name={self.robot_name}"
