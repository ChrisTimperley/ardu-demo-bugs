#!/usr/bin/env python
#
# This file is responsible for implementing a GenProg-style test harness for
# a given scenario.
#
from __future__ import print_function
import math
import sys
import os
import configparser

import dronekit

import sitl
import mission
import attacker
import helper


class TestCase(object):
    def __init__(self, end_pos, use_attacker):
        """
        Constructs a new test case.

        Parameters:
            end_pos: the expected position of the vehicle following the
                completion of the test.
            use_attacker: a flag indicating whether this test case should
                perform the attack.

        TODO:
            accept a scenario file
        """
        assert isinstance(end_pos, dronekit.LocationGlobal)

        self.__end_pos = end_pos
        self.__time_limit = 120 # FIXME should be passed in configuration file

        # load the config file for this scenario
        self.__cfg = configparser.SafeConfigParser()
        self.__cfg.read("/experiment/config/default.cfg")
        self.__cfg.read("/experiment/config/scenario.cfg")

        self.__mission = mission.Mission.from_file("/experiment/mission.txt")
        self.__sitl = sitl.SITL.from_cfg(self.__cfg)

        if use_attacker:
            self.__attacker = attacker.Attacker.from_cfg(self.__cfg)
        else:
            self.__attacker = None

    def execute(self):
        """
        Executes the test.

        Returns:
            a tuple of the form `(passed, reason)`, where `passed` is a flag
            that indicates whether or not the test succeeded, and `reason` is
            an optional string that is used to describe the reason for the
            test failure (if indeed there was a failure).
        """
        # sitl, vehicle, attacker
        trace = []
        vehicle = None
        try:
            self.__sitl.start()

            # connect to the vehicle
            # dronekit is broken! it always tries to connect to 127.0.0.1:5760
            print("try to connect to vehicle...")
            dronekit_connects_to = 'udp:0.0.0.0:14550'
            vehicle = dronekit.connect(dronekit_connects_to, wait_ready=True)

            # launch the attack, if enabled
            # TODO how does this work?
            if self.__attacker:
                self.__attacker.start()

            trace = self.__mission.execute(time_limit=self.__time_limit,
                                           vehicle=vehicle,
                                           attacker=self.__attacker)
        finally:
            if self.__attacker:
                self.__attacker.stop()
            if vehicle:
                vehicle.close()
            self.__sitl.stop()

        if not trace:
            return (False, "failed to navigate to any waypoints")

        (last_wp, snapshot) = trace[-1]
        if last_wp != len(self.__mission) - 1:
            return (False, "failed to reach last waypoint within time limit")

        pos = dronekit.LocationGlobal(snapshot['lat'], snapshot['lon'], snapshot['alt'])
        dist = helper.distance(self.end_pos, pos)
        if dist < 2.0:
            return (True, None)
        else:
            return (False, "too far away from expected position: {} metres".format(dist))


if __name__ == '__main__':
    # construct the test suite
    # TODO locations are borked
    tests = {
        'p1': TestCase(use_attacker=False,
                       end_pos=dronekit.LocationGlobal(40.0713758, -105.2297839, 1583.67)),
        'n1': TestCase(use_attacker=True,
                       end_pos=dronekit.LocationGlobal(40.0713758, -105.2297839, 1583.67))
    }

    # which test does the user wish to execute?
    if len(sys.argv) != 2:
        print("USAGE: ./test.py [test-id]")
        sys.exit(2)

    test_id = sys.argv[1]
    if test_id not in tests:
        print("Unrecognised test identifier provided.")
        sys.exit(2)

    # execute the specified test
    test = tests[test_id]
    (status, msg) = test.execute()
    if status:
        print("PASSED")
    else:
        print("FAILED: {}".format(msg))
        sys.exit(1)
