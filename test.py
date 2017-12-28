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
    args = s.split()
    seq = 0             # API will automatically set sequence numbers
    frame = int(args[2])
    cmd_id = int(args[3])
    current = 0         # not supported by dronekit
    autocontinue = 0    # not supported by dronekit
    (p1, p2, p3, p4, x, y, z) = [float(x) for x in args[4:11]]

    cmd = Command(0, 0, seq, frame, cmd_id, current, autocontinue, \
                  p1, p2, p3, p4, x, y, z)
    return cmd


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
    vcmds.upload()
    vcmds.wait_ready()


def execute_mission(fn):
    # TODO: allow 'binary' and 'speedup' to be passed as arguments
    home = [40.071374969556928, -105.22978898137808, 1583.702759, 246]
    speedup = 10
    binary = '/experiment/source/build/sitl/bin/ardurover'
    mission = load_mission(fn)
    vehicle = sitl = None
    try:
        home_arg = '--home={}'.format(','.join(map(str, home)))
        print(home_arg)
        sitl = SITL(binary)
        sitl.launch([home_arg],
                    verbose=False,
                    await_ready=True,
                    restart=True,
                    speedup=speedup)
        vehicle = dronekit.connect(sitl.connection_string(), wait_ready=True)

        while not vehicle.is_armable:
            time.sleep(0.2)

        issue_mission(vehicle, mission)

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
    execute_mission('missions/rover-not-broke.txt')
