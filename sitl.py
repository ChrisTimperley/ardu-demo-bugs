# This script is responsible for launching and closing the SITL.
import subprocess
import os
import signal

import dronekit_sitl


class SITL(object):
    def from_cfg(cfg):
        vehicle = cfg.get("Mission", "vehicle")
        home_lat = cfg.getfloat("Mission", "latitude")
        home_lon = cfg.getfloat("Mission", "longitude")
        home_alt = cfg.getfloat("Mission", "altitude")
        home_heading = cfg.getfloat("Mission", "heading")

        return SITL(vehicle=vehicle,
                    home_lat=home_lat,
                    home_lon=home_lon,
                    home_heading=home_heading)

    def __init__(vehicle,
                 model,
                 binary,
                 home_lat,
                 home_lon,
                 home_alt,
                 home_heading):
        self.__dir_base = '/experiment/source'
        self.__vehicle = vehicle
        self.__model = model
        self.__process = None
        self.__home_loc = (home_lat, home_lon, home_alt, home_heading)
        self.__binary = os.path.join(self.__dir_base, 'build/sitl/bin', binary)

    def start(self):
        script_sim = os.path.join(self.__dir_base, 'Tools/autotest/sim_vehicle.py')
        cmd = [
            script_sim,
            "-l",
            "{},{},{},{}".format(*self.__home_loc),
            "-v",
            self.__vehicle,
            "-w",
            "--no-rebuild "
            "--ardu-dir ",
            self.__dir_base,
            "--ardu-binary",
            self.__binary,
            "--mavproxy-args=--state-basedir={}".format(
                os.path.join(self.experiment_base, "run{}".format(
                    self.run_count)))
        ]

        self.__process = subprocess.Popen(cmd,
                                          preexec_fn=os.setsid,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)

    def stop(self):
        os.killpg(self.__process.pid, signal.SIGKILL)
        self.__process = None
