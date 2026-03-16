import os

from compas.datastructures import Assembly
from compas.datastructures import Mesh
from compas.datastructures import Part
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Transformation
from compas.geometry import Vector
from compas_timber.assembly import TimberAssembly
from compas_timber.consumers import BrepGeometryConsumer


class AssemblyExtensions:
    """
    AssemblyExtensions is a class for extending the functionality of the [Assembly][] class.

    The AssemblyExtensions class provides additional functionalities such as exporting parts as .obj files
    and creating a frame assembly from a list of [Frame][] with a specific data structure
    for localization information.
    """

    def export_timberassembly_objs(self, assembly: TimberAssembly, folder_path: str, new_folder_name: str, z_to_y_remap: bool = False) -> None:
        """
        Export timber assembly beams as `.obj` files to a folder path.

        Parameters
        ----------
        assembly
            The assembly that you want to export beams from.
        folder_path
            The path in which you would like to create a storage folder.
        new_folder_name
            The name of the folder you would like to create.
        z_to_y_remap
            A boolean that determines if the z-axis should be remapped to the y-axis for `.obj` export.
        """
        target_folder_path = os.path.join(folder_path, new_folder_name)
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        if z_to_y_remap:
            frame = Frame(Point(0, 0, 0), Vector.Xaxis(), Vector.Zaxis())
        else:
            frame = Frame.worldXY()

        for result in BrepGeometryConsumer(assembly).result:
            brep = result.geometry
            beam_frame = result.beam.frame
            key = result.beam.key

            brep_meshes = brep.to_meshes()
            compas_mesh = Mesh()
            for mesh in brep_meshes:
                compas_mesh.join(mesh)
            mesh_transformed = compas_mesh.transformed(Transformation.from_frame_to_frame(beam_frame, frame))

            filename = "{}.obj".format(str(key))
            mesh_transformed.to_obj(os.path.join(target_folder_path, filename))

    def export_mesh_assembly_objs(self, assembly: Assembly, folder_path: str, new_folder_name: str, z_to_y_remap: bool = False) -> None:
        """
        Export Mesh assembly parts as `.obj` files to a folder path.

        Parameters
        ----------
        assembly
            The Mesh assembly that you want to export parts from.
        folder_path
            The path in which you would like to create a storage folder.
        new_folder_name
            The name of the folder you would like to create.
        z_to_y_remap
            A boolean that determines if the z-axis should be remapped to the y-axis for `.obj` export.
        """
        target_folder_path = os.path.join(folder_path, new_folder_name)
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        if z_to_y_remap:
            frame = Frame(Point(0, 0, 0), Vector.Xaxis(), Vector.Zaxis())
        else:
            frame = Frame.worldXY()

        for part in assembly.parts():
            # Mesh assembly can be made with or without a frame (ex. assembly.add_part(Mesh)) try & default to worldXY
            if hasattr(part, "frame"):
                part_frame = part.frame
            else:
                part_frame = Frame.worldXY()

            # TODO: This is weird, but I can't transform a Part object, so I need to check if it's a Part or a Mesh
            transformation = Transformation.from_frame_to_frame(part_frame, frame)
            if isinstance(part, Part):
                part_transformed = part.attributes["shape"].transformed(transformation)
            else:
                part_transformed = part.transformed(transformation)

            filename = "{}.obj".format(str(part.key))
            part_transformed.to_obj(os.path.join(target_folder_path, filename))

    def create_qr_assembly(self, qr_frames: list[Frame]) -> Assembly:
        """
        Create a frame assembly from a list of [Frame][] with a specific data structure for localization.

        Parameters
        ----------
        qr_frames
            A list of frames at specific locations for localization data.

        Returns
        -------
        Assembly
            The constructed database reference.

        """
        assembly = Assembly()
        for i, frame in enumerate(qr_frames):
            name = "QR_{}".format(i)
            part = Part(name=name, frame=frame, shape=frame)
            assembly.add_part(part)
        return assembly
