#!/usr/bin/env python
from __future__ import print_function
from sys import exit
import math
from pprint import pprint as pp
from mission_runner import execute_mission
from dronekit import LocationGlobal


def fail(msg):
    print("FAIL: {}".format(msg))
    exit(1)


def success():
    print("SUCCESS")
    exit(0)


def distance(loc_x, loc_y):
    """
    Returns the ground distance in metres between two `LocationGlobal` or `LocationGlobalRelative` objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    d_lat = loc_y.lat - loc_x.lat
    d_long = loc_y.lon - loc_x.lon
    return math.sqrt((d_lat*d_lat) + (d_long*d_long)) * 1.113195e5


if __name__ == '__main__':
    trace = execute_mission('missions/rover-not-broke.txt')
    if len(trace) < 0:
        fail("failed to navigate to any waypoints")

    (last_wp, snapshot) = trace[-1]
    if last_wp != 22:
        fail("failed to reach last waypoint within time limit")

    # check state
    # - position
    pp(snapshot)

    expected_pos = LocationGlobal(40.0713758,
                                  -105.2297839,
                                  1583.67)
    actual_pos = LocationGlobal(snapshot['lat'],
                                snapshot['lon'],
                                snapshot['alt'])

    dist = distance(expected_pos, actual_pos)
    print("Distance: {} metres".format(dist))
    success() if dist < 2.0 else fail()
