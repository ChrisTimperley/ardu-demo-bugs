#!/usr/bin/env python3
#
# Uses Dronekit to interact with the SITL (software-based simulator) and to
# issue commands/missions to the rover.
#
import time
import dronekit
from typing import List
from dronekit_sitl import SITL
from dronekit import Vehicle, Command, CommandSequence


def parse_command(s: str) -> Command:
    """
    Parses a line from a mission file into its corresponding Command
    object in Dronekit.
    """
    args = [float(x) for x in s.split()]
    return Command(0, 0, *args)


def load_mission(fn: str) -> List[Command]:
    """
    Loads a mission from a given file and converts it into a list of
    Command objects.
    """
    cmds = []
    with open(fn, 'r') as f:
        lines = [l.strip() for l in f]
        for line in lines[1:]:
            cmd = parse_command(line)
            cmds.append(cmd)
    return cmds


def issue_mission(vehicle: Vehicle, commands: List[Command]) -> None:
    """
    Issues (but does not trigger) a mission, provided as a list of commands,
    to a given vehicle.
    Blocks until the mission has been downloaded onto the vehicle.
    """
    vcmds = vehicle.commands
    vcmds.clear()
    for command in commands:
        vcmds.add(command)
    vcmds.download()
    vcmds.wait_ready()


def execute_mission(fn: str) -> bool:
    # TODO: allow 'binary' to be passed as an argument
    binary = '/experiment/source/'
    mission = load_mission(fn)
    vehicle = sitl = None
    try:
        sitl = SITL(binary)
        vehicle = dronekit.connect(sitl.connection_string(), wait_ready=True)
        issue_mission(vehicle, mission)

        # trigger the mission by switching the vehicle's mode to "AUTO"
        vehicle.mode = dronekit.Mode("AUTO")

        # monitor the mission
        # could use "add_attribute_listener" to listen to next_waypoint attribute?
        while True:
            print("Global Location: {}".format(vehicle.location.global_frame))
            time.sleep(2)


    finally:
        if vehicle:
            vehicle.close()
        if sitl:
            sitl.stop()


if __name__ == '__main__':
    execute_mission('missions/rover-broke.txt')
