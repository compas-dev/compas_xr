from typing import Union

from compas.datastructures import Assembly
from compas_timber.assembly import TimberAssembly
from compas_timber.planning import BuildingPlan
from compas_timber.planning import SimpleSequenceGenerator
from compas_timber.planning import Step


class BuildingPlanExtensions:
    """
    Extensions for the [BuildingPlan][] class.

    This class provides functionalities to create a building plan from an established assembly sequence.
    """

    # TODO: This makes the building plan in a very manual way
    # TODO: but this needs to be resolved in tandem with building plan revisions.
    def create_buildingplan_from_assembly_sequence(
        self,
        assembly: Union[TimberAssembly, Assembly],
        data_type: int,
        robot_keys: list[str] = None,
        priority_keys_lists: list[list[str]] = None,
    ) -> BuildingPlan:
        """
        Create a [BuildingPlan][] based on the sequence of the assembly parts.

        Parameters
        ----------
        assembly
            The assembly that you want to generate the buiding plan for.
        data_type
            List index of which data type will be loaded on the application side [0: 'Cylinder', 1: 'Box', 2: 'ObjFile']
        robot_keys
            List of keys that are intended to be built by the robot.
        priority_keys_lists
            List in assembly order of lists of assembly keys that can be built in parallel.

        Returns
        -------
        [BuildingPlan][]
            The building plan generated from the assembly sequence.

        """
        data_type_list = ["0.Cylinder", "1.Box", "2.ObjFile"]
        building_plan = SimpleSequenceGenerator(assembly=assembly).result

        for step in building_plan.steps:
            step.geometry = data_type_list[data_type]
            # TODO: These are unused for now, but are expeted on the application side
            step.instructions = ["none"]
            step.elements_held = [0]

            element_key = str(step.element_ids[0])
            if robot_keys:
                if element_key in robot_keys:
                    step.actor = "ROBOT"

            if not priority_keys_lists:
                step.priority = 0
            else:
                for i, keys_list in enumerate(priority_keys_lists):
                    if element_key in keys_list:
                        step.priority = i
                        break

        return building_plan

    def create_buildingplan_from_with_custom_sequence(
        self,
        assembly: Union[TimberAssembly, Assembly],
        sequenced_keys: list[str],
        data_type: int,
        robot_keys: list[str],
        priority_keys_lists: list[list[str]],
    ) -> BuildingPlan:
        """
        Create a [BuildingPlan][] based on the sequence of the assembly parts.

        Parameters
        ----------
        assembly
            The assembly that you want to generate the buiding plan for.
        sequenced_keys
            List of keys that are intended to be built in the order provided.
        data_type
            List index of which data type will be loaded on the application side [0: 'Cylinder', 1: 'Box', 2: 'ObjFile']
        robot_keys
            List of keys that are intended to be built by the robot.
        priority_keys_lists
            List in assembly order of lists of assembly keys that can be built in parallel.

        Returns
        -------
        [BuildingPlan][]
            The building plan generated from the assembly sequence.

        """
        data_type_list = ["0.Cylinder", "1.Box", "2.ObjFile"]
        graph_data = assembly.graph.__data__
        node_data = graph_data["node"]
        building_plan = BuildingPlan()

        for key in sequenced_keys:
            step = Step(key)
            # TODO: This is dumb, but the element_ids are generated incorrectly so they are overwritten here
            step.element_ids = [key]
            step.geometry = data_type_list[data_type]
            # TODO: These are unused for now, but are expeted on the application side
            step.instructions = ["none"]
            step.elements_held = [0]
            step.location = node_data[str(key)]["part"].frame

            if robot_keys:
                if key in robot_keys:
                    step.actor = "ROBOT"
                else:
                    step.actor = "HUMAN"
            else:
                step.actor = "HUMAN"

            if not priority_keys_lists:
                step.priority = 0
            else:
                for i, keys_list in enumerate(priority_keys_lists):
                    if key in keys_list:
                        step.priority = i
                        break
            building_plan.add_step(step)

        return building_plan
