#!/usr/bin/env python
#
# This file is responsible for implementing a GenProg-style test harness for
# a given scenario.
#
from __future__ import print_function
from pprint import pprint as pp
import math
import sys

from dronekit import LocationGlobal

import mission
import helper


class TestCase(object):
    def __init__(self, filename, time_limit, end_pos):
        """
        Constructs a new test case.

        Parameters:
            filename: the location of the WPL file (i.e., mission file) for
                this test case.
            time_limit: the number of seconds that this test is allowed to
                run without completing before it is considered to have failed.
            end_pos: the expected position of the vehicle following the
                completion of the test.
        """
        assert isinstance(end_pos, LocationGlobal)
        self.__filename = filename
        self.__end_pos = end_pos
        self.__time_limit = time_limit
        self.__mission = mission.Mission.from_file(filename)

    @property
    def time_limit(self):
        """
        The number of seconds that this test case is allowed to run without
        completing before it is considered to be a failure.
        """
        return self.__time_limit

    @property
    def mission(self):
        return self.__mission

    @property
    def end_pos(self):
        """
        The intended location of the vehicle after completing the mission.
        """
        return self.__end_pos

    def execute(self):
        trace = execute_mission(self.__mission,
                                time_limit=self.time_limit)
        if len(trace) < 0:
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
                       end_pos=LocationGlobal(40.0713758, -105.2297839, 1583.67)),
        'n1': TestCase('missions/scenario.wpl', 60,
                       end_pos=LocationGlobal(40.0713758, -105.2297839, 1583.67))
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
