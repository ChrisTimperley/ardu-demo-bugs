import subprocess
import signal
import socket
import configparser
import os
import tempfile


class Attacker(object):
    @staticmethod
    def from_file(fn):
        config = configparser.SafeConfigParser()
        config.read("/experiment/config/scenario.config.DEFAULT")
        config.read("/experiment/config/scenario.config")
        return Attacker.from_cfg(config)

    @staticmethod
    def from_cfg(cfg):
        return Attacker(script='attack.py',
                        flags=cfg.get('attack_flags', ''),
                        longtitude=float(cfg.get('longitude', 0.0)),
                        latitude=float(cfg.get('latitude', 0.0)),
                        radius=float(cfg.get('radius', 0.0)),
                        port=16666, # we can just run the attack server on a fixed port
                        url_sitl='127.0.0.1:TODO') # the SITL should also be at a fixed URL

    def __init__(self,
                 script,
                 flags,
                 longitude,
                 latitude,
                 radius,
                 url_sitl,
                 port):
        self.__script = script
        self.__url_sitl = url_sitl
        self.__port = port
        self.__script_flags = flags.strip()
        self.__longitude = longitude
        self.__latitude = latitude
        self.__radius = radius
        # FIXME I can't find any documentation or examples for this parameter.
        # The default value in START is -1.
        # From looking at an example attack script, it would seem that this
        # parameter specifies the number of seconds to wait before reporting an
        # attack to the attack server. If set to -1, the attack won't be
        # reported. Presuming that only successful attacks are reported (rather
        # than all attempted attacks), then we probably want the timeout to be
        # zero, since we want to prevent the attack.
        self.__report = 0

        self.__fn_log = None
        self.__fn_mav = None
        self.__connection = None
        self.__process = None

    def prepare(self):
        self.__fn_log = tempfile.NamedTemporaryFile()
        self.__fn_mav = tempfile.NamedTemporaryFile()

        cmd = [
            self.__script,
            "--master={}".format(self.__url_sitl),
            "--baudrate=115200",
            "--port={}".format(self.__port),
            "--report-timeout={}".format(self.__report),
            "--logfile={}".format(self.__fn_log),
            "--mavlog={}".format(self.__fn_mav)
        ]

        if self.__script_flags != '':
            tokens = self.__script_flags.split(",")
            cmd.extend(tokens)

        # launch server
        self.__process = subprocess.Popen(cmd,
                                          preexec_fn=os.setsid,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)

        # connect
        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connection.connect(self.__url_sitl)

    def kill(self):
        # close connection
        self.__connection.write("EXIT\n")
        self.__connection.flush()
        self.__connection.close()
        self.__connection = None

        # TODO why was there a timeout here?

        # kill server
        os.killpg(self.__process.pid, signal.SIGKILL)
        self.__process = None

        # destroy temporary files
        self.__fn_log = None
        self.__fn_mav = None

    def trigger(self):
        self.__connection.write("START\n")
        self.__connection.flush()

    def was_attacked(self):
        self.__connection.write("CHECK\n")
        self.__connection.flush()

        reply = self.__connection.readline().strip()
        return "NO" not in msg
