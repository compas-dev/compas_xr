class AppSettings:
    """Class representing application settings for the XR project.

    Parameters
    ----------
    project_name
        Name of the project.
    storage_folder
        Folder for storage.
    z_to_y_remap
        Whether to remap Z axis to Y axis.
    """

    def __init__(self, project_name: str, storage_folder: str = None, z_to_y_remap: bool = None) -> None:
        self.project_name = project_name
        self.storage_folder = storage_folder or "None"
        self.z_to_y_remap = z_to_y_remap or False

    def __str__(self) -> str:
        return f"AppSettings, project_name={self.project_name}, storage_folder={self.storage_folder}, z_to_y_remap={self.z_to_y_remap}"

    def __data__(self) -> dict:
        return {
            "project_name": self.project_name,
            "storage_folder": self.storage_folder,
            "z_to_y_remap": self.z_to_y_remap,
        }
