from __future__ import print_function
from timeit import default_timer as timer
import time

from dronekit import Command, VehicleMode

import helper


class Mission(object):
    @staticmethod
    def __parse_command(s):
        """
        Parses a line from a mission file into its corresponding Command
        object in Dronekit.
        """
        args = s.split()
        arg_index = int(args[0])
        arg_currentwp = 0 #int(args[1])
        arg_frame = int(args[2])
        arg_cmd = int(args[3])
        arg_autocontinue = 0 # not supported by dronekit
        (p1, p2, p3, p4, x, y, z) = [float(x) for x in args[4:11]]
        cmd = Command(0, 0, 0, arg_frame, arg_cmd, arg_currentwp, arg_autocontinue,\
                      p1, p2, p3, p4, x, y, z)
        return cmd

    @staticmethod
    def from_file(fn):
        """
        Loads a mission from a given WPL file.
        """
        cmds = []
        with open(fn, 'r') as f:
            lines = [l.strip() for l in f]
            for line in lines[1:]:
                cmd = Mission.__parse_command(line)
                cmds.append(cmd)
        return Mission(cmds)

    def __init__(self, commands):
        # a list of DroneKit (WPL) commands
        self.__commands = commands[:]

    def __len__(self):
        """
        The length of the mission is given by the number of commands that it
        contains.
        """
        return len(self.__commands)

    def issue(self, vehicle):
        """
        Issues (but does not trigger) a mission, provided as a list of commands,
        to a given vehicle.
        Blocks until the mission has been downloaded onto the vehicle.
        """
        vcmds = vehicle.commands
        vcmds.clear()
        for command in self.__commands:
            vcmds.add(command)
        vcmds.upload()
        vcmds.wait_ready()

    def execute(self, time_limit, vehicle, attacker):
        """
        Executes this mission on a given vehicle.

        Parameters:
            time_limit: the number of seconds that the vehicle should be given
                to finish executing the mission before aborting the mission.
            vehicle: the vehicle that should execute the mission.
            attacker: an optional attacker.

        Returns:
            a sequence of tuples of the form (wp, state), where wp corresponds
            to a given waypoint in the mission, and state describes the state
            of the vehicle when it reached that waypoint. If an attacker is
            provided, and an attack occurred, then an empty list is returned
            (to indicate failure).
        """
        # TODO: add time limit
        while not vehicle.is_armable:
            time.sleep(0.2)

        # TODO: add time limit
        # arm the rover
        vehicle.armed = True
        while not vehicle.armed:
            print("waiting for the vehicle to be armed...")
            time.sleep(0.1)
            vehicle.armed = True

        # TODO: add time limit
        self.issue(vehicle)

        # trigger the mission by switching the vehicle's mode to "AUTO"
        vehicle.mode = VehicleMode("AUTO")

        # monitor the mission
        last_wp = vehicle.commands.count
        mission_complete = [False]
        waypoints_visited = []

        try:
            def on_waypoint(self, name, message):
                wp = int(message.seq)
                # print("Reached WP #{}".format(wp))

                # record the (relevant) state of the vehicle
                snapshot = helper.snapshot(vehicle)
                waypoints_visited.append((wp, snapshot))

                if wp == last_wp:
                    mission_complete[0] = True
            vehicle.add_message_listener('MISSION_ITEM_REACHED', on_waypoint)


            # wait until the last waypoint is reached, the time limit has
            # expired, or the attack was successful
            time_started = timer()
            while not mission_complete[0]:
                time_elapsed = timer() - time_started

                # TODO if the attack was successful, return an empty list of
                # waypoints
                if attacker and attacker.was_successful():
                    return []

                if time_limit and time_elapsed > time_limit:
                    return waypoints_visited[:]
                time.sleep(0.2)

            return waypoints_visited[:]

        # remove the listener
        finally:
            vehicle.remove_message_listener('MISSION_ITEM_REACHED', on_waypoint)
