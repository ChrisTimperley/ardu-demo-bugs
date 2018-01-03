#!/usr/bin/env python
import bugzoo
from darjeeling.problem import Problem
from darjeeling.repair import repair


if __name__ == '__main__':
    # how many threads would you like to use?
    threads = 32

    # construct a description of the problem for Darjeeling
    in_files = ['APMrover2/commands_logic.cpp']

    # retrieve the bug that we wish to fix from the BugZoo
    bz = bugzoo.BugZoo()
    bug = bz.bugs["ardudemo:ardupilot:overflow"]

    problem = Problem(bug, in_files)

    # Since we can't obtain coverage information for ArduPilot right now,
    # this isn't actually used.
    metric = bugzoo.localization.suspiciousness.tarantula

    # this will run indefinitely until a repair is found.
    repair(problem, metric, threads=threads)
