# AFRL Demonstration

Could copy the description of the bug from Kevin's email?

## Warnings

Things that don't work:

* **Coverage generation:** For some reason `gcov` produces erroneous coverage
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
* **Clang integration:**

## Installation

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
