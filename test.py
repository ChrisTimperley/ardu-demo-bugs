#!/usr/bin/env python
#
# This file is responsible for implementing a GenProg-style test harness for
# a given scenario.
#
from __future__ import print_function
import math
import sys

import dronekit

import sitl
import mission
import attacker
import helper


class TestCase(object):
    def __init__(self, filename, time_limit, end_pos, use_attacker):
        """
        Constructs a new test case.

        Parameters:
            filename: the location of the WPL file (i.e., mission file) for
                this test case.
            time_limit: the number of seconds that this test is allowed to
                run without completing before it is considered to have failed.
            end_pos: the expected position of the vehicle following the
                completion of the test.
            use_attacker: a flag indicating whether this test case should
                perform the attack.
        """
        assert isinstance(end_pos, LocationGlobal)
        assert time_limit > 0
        self.__end_pos = end_pos
        self.__time_limit = time_limit
        self.__attacker = ""
        self.__mission = mission.Mission.from_file(filename)
        # TODO load from a config file
        self.__sitl = sitl.SITL(binary='ardurover',
                                model='rover')
        self.__attacker = # TODO

    @property
    def time_limit(self):
        """
        The number of seconds that this test case is allowed to run without
        completing before it is considered to be a failure.
        """
        return self.__time_limit

    @property
    def mission(self):
        """
        The mission that should be executed by the vehicle during this test.
        """
        return self.__mission

    @property
    def end_pos(self):
        """
        The intended location of the vehicle after completing the mission.
        """
        return self.__end_pos

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
        try:
            self.__sitl.start()

            # connect to the vehicle
            # dronekit is broken! it always tries to connect to 127.0.0.1:5760
            print("try to connect to vehicle...")
            dronekit_connects_to = 'tcp:127.0.0.1:5760'
            vehicle = dronekit.connect(dronekit_connects_to, wait_ready=True)

            # launch the attack, if enabled
            # TODO how does this work?
            if self.__attacker:
                self.__attacker.start()

            trace = self.__mission.execute(time_limit=self.time_limit,
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

        pos = LocationGlobal(snapshot['lat'], snapshot['lon'], snapshot['alt'])
        dist = helper.distance(self.end_pos, pos)
        if dist < 2.0:
            return (True, None)
        else:
            return (False, "too far away from expected position: {} metres".format(dist))


if __name__ == '__main__':
    # construct the test suite
    tests = {
        'p1': TestCase('missions/scenario.wpl', 60,
                       end_pos=dronekit.LocationGlobal(40.0713758, -105.2297839, 1583.67)),
        'n1': TestCase('missions/scenario.wpl', 60,
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
