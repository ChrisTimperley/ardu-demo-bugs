#!/usr/bin/env python
#
# Uses Dronekit to interact with the SITL (software-based simulator) and to
# issue commands/missions to the rover.
#
from __future__ import print_function
import time
import dronekit
import dronekit_sitl
from helper import adds_square_mission
from dronekit_sitl import SITL
from dronekit import Vehicle, \
                     VehicleMode, \
                     Command, \
                     CommandSequence, \
                     LocationGlobal


def parse_command(s):
    """
    Parses a line from a mission file into its corresponding Command
    object in Dronekit.
    """
    args = [float(x) for x in s.split()]
    return Command(0, 0, *args)


def load_mission(fn):
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


def issue_mission(vehicle, commands):
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


def execute_mission(fn):
    # TODO: allow 'binary' to be passed as an argument
    binary = '/experiment/source/build/sitl/bin/ardurover'
    mission = load_mission(fn)
    vehicle = sitl = None
    try:
        sitl = SITL(binary)
        sitl.launch([], verbose=False, await_ready=True, restart=True)
        vehicle = dronekit.connect(sitl.connection_string(), wait_ready=True)

        while not vehicle.is_armable:
            time.sleep(0.2)

        # issue_mission(vehicle, mission)
        adds_square_mission(vehicle, vehicle.location.global_frame, 50)

        # trigger the mission by switching the vehicle's mode to "AUTO"
        vehicle.mode = VehicleMode("AUTO")

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
