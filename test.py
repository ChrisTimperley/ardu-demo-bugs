#!/usr/bin/env python
from __future__ import print_function
from sys import exit
import math
from pprint import pprint as pp
from helper import distance
from mission_runner import load_mission, execute_mission
from dronekit import LocationGlobal


class TestCase(object):
    # TODO: add time limit
    def __init__(self, filename, end_pos):
        assert isinstance(end_pos, LocationGlobal)
        self.__filename = filename
        self.__end_pos = end_pos
        self.__mission = load_mission(filename)

    @property
    def filename(self):
        return self.__filename

    @property
    def mission(self):
        return self.__mission

    @property
    def end_pos(self):
        return self.__end_pos

    def execute(self):
        trace = execute_mission(self.__mission)
        if len(trace) < 0:
            return (False, "failed to navigate to any waypoints")

        (last_wp, snapshot) = trace[-1]
        if last_wp != len(self.__mission) - 1:
            return (False, "failed to reach last waypoint within time limit")

        pos = LocationGlobal(snapshot['lat'], snapshot['lon'], snapshot['alt'])
        dist = distance(self.end_pos, pos)
        if dist < 2.0:
            return (True, None)
        else:
            return (False, "too far away from expected position: {} metres".format(dist))


if __name__ == '__main__':
    tests = [
        TestCase('missions/rover-not-broke.txt',
                 LocationGlobal(40.0713758, -105.2297839, 1583.67))
    ]

    # execute the specified test
    test = tests[0]
    (status, msg) = test.execute()
    if status:
        print("PASSED")
    else:
        print("FAILED: {}".format(msg))
        exit(1)
