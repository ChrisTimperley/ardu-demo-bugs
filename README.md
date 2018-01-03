# AFRL Demonstration Instructions

This repository contains instructions for reproducing and repairing the bug
that is to be used as part of a demonstration for the AFRL PI meeting on
January 14th, 2018.

Below is a description of the bug, taken from an email sent by Kevin Leach.

```
The mission plan is specified via the rover-broke.txt file, which is a
list of mission items.  Each mission item contains an 'opcode' to
distinguish the type of command it is as well as several parameters.
For example, a mission item might say 'move to new position' and specify
the desired GPS coordinates as a parameter.  We seed a defect that
exploits an unsanitized input parameter.  The malicious user can specify
a mission item whose parameter is used as an index into a buffer.  If
that parameter is not clamped to the size of the buffer, the malicious
user can overwrite the end of such a buffer.

In commands_logic.cpp, line 140, there is a memset that uses the
parameter of the mission item to write a single byte at the end of the
kleach_ints array.  This array is right next to a fake flag in memory
(called kleach_broken).  If kleach_broken is set, the mission halts.
```

For the purposes of safely and reliably reproducing and fixing the bug, we
use BugZoo to package it into the form of a Docker container. Although these
instructions are primarily intended for those that may wish to demonstrate the
automated repair of the bug, they may also be of interest to others that wish
to perform dynamic analyses (e.g., test generation).

## Demonstration (CMU)

In this section, we briefly describe what technical accomplishments CMU wishes
to exhibit as part of the demonstration.

## Warnings

* **Coverage doesn't work:** For some reason `gcov` produces erroneous coverage
    information for the particular version of ArduPilot that we are using for
    this demonstration. CT has used `gcov` successfully with previous versions
    of ArduPilot but can't figure out why it's not working here. CT used
    `waf` to configure the source code with the following flags:
    `LDFLAGS='--coverage'`,
    `CXXFLAGS='-Wno-error=maybe-uninitialized -fprofile-arcs -ftest-coverage'`.
    Have any of the other performers had success in obtaining coverage for the
    version of ArduPilot used for the demo?
    \
    \
    For now, the repair tool simply treats all lines in the file as suspicious
    locations. (This decision actually alleviates another problem, discussed
    below.)
* **The bug is extremely easy to fix:** Since the fault consists of several
    injected lines of code, removing one or more of them can prevent the bug
    from manifesting. To fix the bug, one simply needs to delete one of several
    critical lines, or alternatively, to replace the contents of that line to
    achieve the same effect.
    \
    \
    This is a bit of a problem since an very easy bug makes it rather difficult
    to demonstrate any sort of improvement in the repair process. To resolve this,
    CT has made the fault localisation artificially worse, which increases the
    expected number of candidate patch evaluations.
* **The test suite is small:** Although the oracle appears to be quite robust,
*   there are few test cases and so a number of potentially dangerous but
*   nonetheless valid patches may be produced (e.g., replacement of a statement
    that is critical to triggering the bug, with one that silently introduces a
    new vulnerability).
* **Clang integration:**



## Internals

### Test Suite

The test suite for the bug is compromised of two tests, provided by Kevin
Leach. Each test takes the form of a mission, written in the WQL waypoint
language. The passing test, `rover.txt`, instructs the rover to navigate a
circuit of waypoints. The failing test, `rover-broke.txt`, is similar, except
that it contains a command that triggers the vulnerability, causing the rover
to prematurely abort its mission.

#### Test Harness

The test harness for the bug scenario is implemented by `test.py`, which relies
on `mission_runner.py` and `helper.py`. `test.py` accepts the name of one of
the two test cases in the standard GenProg format (i.e., `p1` and `n1`). The
script then loads and parses the mission file associated with that script,
before executing the mission and checking the mission outcome against an
expected outcome. For now, the expected outcome is given by a GPS position; if
the rover completes all of the waypoints and comes to rest within two metres
of that position, it is considered to have passed the test.

In the near future, the functionalities implemented by the mission execution
script will be absorbed into CMU's automated testing framework for robotics
systems, "Houston".

## Installation

Below we give instructions on how to prepare one's machine for the purposes of
conducting the demonstration. If these instructions are incomplete or incorrect,
please let CT know.

### Virtual Environment

First, create a virtual environment for Python 3.6, as shown below.
This step avoids the need to perform dangerous updates to your system's
version of Python 3. The last command in this list updates the environmental
variables in your shell to point to your virtual environment.

```
$ cd path-to-this-repo-clone
$ python3.6 -m venv .
$ source bin/activate
```

### BugZoo

Now that you're inside the virtual environment, you'll need to install the
latest version of BugZoo from GitHub.

```
$ git clone https://github.com/squaresLab/BugZoo bugzoo
$ (cd bugzoo && pip install . --upgrade)
```

After installing BugZoo, you can now register the bug for this demonstration
with your local BugZoo installation by following the commands below.

```
$ bugzoo source add https://github.com/ChrisTimperley/ardu-demo-bugs
$ bugzoo bug build ardudemo:ardupilot:overflow
```

### Darjeeling

Finally, let's install Darjeeling, the library responsible for orchestrating the
automated repair process:

```
$ git clone https://github.com/squaresLab/Darjeeling darjeeling
$ (cd darjeeling && pip install . --upgrade)
```

## Usage

```
$ bugzoo 
```
