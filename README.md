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
to exhibit as part of the demonstration. The most important and obvious
difference between the repair tooling that CMU previously demonstrated and the
tooling that it intends to demonstrate for the upcoming meeting is its ability
to safely perform the repair across a large number of threads.

Attempting to execute two or more tests in parallel on a single machine can
compromise idempotency and result in test case interference. As such,
attempting to parallelise across tests is unsafe and unable to be applied in
both the general case and in the case of ArduPilot. Instead, CMU's tooling,
known as Darjeeling, uses BugZoo and Docker to safely parallelise the evaluation
of multiple patches. With the proper configuration, Darjeeling can provision
containers on both local and remote machines. In the future, there's a lot
of promise in large-scale distributed evaluation, but in order to achieve that
promise we need to make a few unexpected optimisations (for reasons explained
below).

For more typical repair scenarios (e.g., ManyBugs), one may reasonably hope to
attain a factor of `n` speed-up, where `n` is equal to the number of threads
available to the machine. ArduPilot is a much more interesting and promising
case, however. Neither ArduPilot nor its SITL-based simulator consume many
resources -- most of their time is spent idling. I suppose that upon further
reflection this might not be a complete surprise: ArduPilot was originally
written for highly constrained embedded systems, and its simulator is a very
rudimentary albeit effective one.

On my 4-core, 8-thread laptop, I was able to run a rather astonishing *XXX*
patch evaluation threads in parallel. This improvement completely dominates
our optimisations in terms of improvement, and so I think it deserves to be
the focus of CMU's contribution.

### Answers to potential questions

* **How is this different from the previous demonstration?** Besides being
  based on an entirely different stack, our new system provides safe,
  large-scale parallelism.
* **How much faster is the repair process?** The speed-up is a factor of the
  number of parallel threads that one can reliably use on one's machine.
* **Spinning up Docker containers sounds expensive. Is it?** Nope! It's
  surprisingly fast on my machine at least (0.1--0.2 seconds). The time taken
  to execute the mission dominates the run-time, although one could reduce this
  by tweaking the simulator speed-up (exposed in the test harness).
* **What factors affect performance?** Disk speed and memory are the two
  biggest bottlenecks. For reference, I'm using a blisteringly fast NVME SSD
  and 16GB of memory.
* **Hey! What makes you so sure that running so many threads didn't mess
  things up?** Without conducting an experiment, I can't really be too sure,
  but I've repeated the repair process several times and checked the pass/fail
  results of each patch -- they all seem to be above board. Perhaps I just got
  lucky? Let CT know if you obtain strange results.
* **Why can't you distribute the repair process across multiple EC2
  instances?** It's a little bit of a hassle, but we could. (Although, using
  EC2 might open up a pandora's box of mysterious failure modes.) My bigger
  technical concern is with Darjeeling's exclusive use of Python threads. Due
  to the global interpreter lock, threads only execute on a single core (with
  almost unrestricted shared access to the memory) on most implementations of
  Python. As the threads to (utilised) cores ratio creeps up, the repair
  process incurs more overhead. To alleviate the problem, CT needs to adapt
  Darjeeling to make better use of Python's multiprocessing capabilities.

## Warnings

Below are a few caveats and warnings that apply to both the bug and the repair
process.

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
    there are few test cases and so a number of potentially dangerous but
    nonetheless valid patches may be produced (e.g., replacement of a statement
    that is critical to triggering the bug, with one that silently introduces a
    new vulnerability).
* **The repair tool isn't supposed to be open-source yet:** I've made most of
    the repositories that host the repair tools public, but only so that other
    performers may acquire and use them more easily. Some of them should not be
    treated as public releases (e.g., Darjeeling). Nonetheless, if you have any
    issues, don't hesitate to post to the issue tracker (suspected implementation
    bugs) or to email CT (technical issues).
* **Clang integration:** The software stack used by this demonstration does not
    include Clang, meaning that it does not implement optimisations that are
    afforded by static analysis (i.e., those originally implemented by AE). The
    amount of work required to build an interface between our Clang-based
    analyses is greater than CT first thought. Further, while the optimisations
    achieve a reasonable reduction of the space of candidate patches, they are
    not as pronounced as the introduction of parallelism -- those optimisations
    also make the problem even easier, which makes it harder still to the
    demonstrate the benefits of parallelism.
    \
    In the near term, we plan to combine Rooibos -- a powerful
    language-independent source code rewriting engine -- with lightweight
    static analysis modules with REST interfaces, built atop Clang.

## Internals

Here we provide a few technical details about the bug and the implementation of
its test suite. If anyone wants more technical information about any aspect of
CMU's part of the demonstration, do let CT know.

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

Once all the of the prequisites have been installed, the repair can triggered by
executing a single script, as shown below:

```
$ bugzoo 
```

Before executing the script, as shown above, ensure that you have correctly
sourced the virtual environment that was constructed during the installation
phase:

```
$ cd path-to-dir-containing-virtual-env
$ source bin/activate
```

MODIFICATIONS
