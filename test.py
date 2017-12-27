#!/usr/bin/env python3
#
# Uses Dronekit to interact with the SITL (software-based simulator) and to
# issue commands/missions to the rover.
#
import dronekit
from dronekit_sitl import SITL
from dronekit import Command, CommandSequence


def parse_command(s: str) -> Command:
    """
    Parses a line from a mission file into its corresponding Command
    object in Dronekit.
    """
    args = [float(x) for x in s.split()]
    return Command(0, 0, *args)


def load_mission(fn: str) -> CommandSequence:
    """
    Loads a mission from a given file and converts it into a
    CommandSequence object.
    """
    cmds = []
    with open(fn, 'r') as f:
        for line in f[1:]:
            cmd = parse_command(line)
            cmds.append(cmd)
    return CommandSequence(cmds)


try:
    sitl = SITL(binary)
    vehicle = connect(sitl.connection_string(), wait_ready=True)

    # download the mission
    # (note: 'wait_ready' blocks until mission has finished downloading)
    cmds = BLAH
    cmds.download()
    cmds.wait_ready()

    # trigger by the mission by switching the vehicle's mode to "AUTO"
    vehicle.mode = dronekit.Mode("AUTO")

    # monitor the mission
    # could use "add_attribute_listener" to listen to next_waypoint attribute?


finally:
    if vehicle:
        vehicle.close()
    sitl.stop()
