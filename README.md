# AFRL Demonstration

Could copy the description of the bug from Kevin's email?

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

Darjeeling.

```

```

## Usage

```
$ bugzoo 
```
