# This script is responsible for launching and closing the SITL.
import subprocess
import os
import signal
import configparser

import dronekit_sitl


class SITL(object):
    @staticmethod
    def from_cfg(cfg):
        vehicle = cfg.get("General", "vehicle")
        home_lat = cfg.getfloat("Mission", "latitude")
        home_lon = cfg.getfloat("Mission", "longitude")
        home_alt = cfg.getfloat("Mission", "altitude")
        home_heading = cfg.getfloat("Mission", "heading")

        return SITL(vehicle=vehicle,
                    home_lat=home_lat,
                    home_lon=home_lon,
                    home_alt=home_alt,
                    home_heading=home_heading)

    def __init__(self,
                 vehicle,
                 home_lat,
                 home_lon,
                 home_alt,
                 home_heading):
        binary_name = ({
            'APMrover2': 'ardurover',
            'ArduCopter': 'arducopter',
            'ArduPlane': 'arduplane'
        })[vehicle]

        self.__dir_base = '/experiment/source'
        self.__vehicle = vehicle
        self.__process = None
        self.__home_loc = (home_lat, home_lon, home_alt, home_heading)
        self.__path_binary = os.path.join(self.__dir_base, 'build/sitl/bin', binary_name)

    @property
    def command(self):
        script_sim = os.path.join(self.__dir_base, 'Tools/autotest/sim_vehicle.py')
        cmd = [
            script_sim,
            "-l", "{},{},{},{}".format(*self.__home_loc),
            "-v", self.__vehicle,
            "-w",
            "--no-rebuild "
            # "--ardu-dir ", self.__dir_base, # BAD: no longer supported
            # "--ardu-binary", self.__path_binary # BAD: no longer supported
        ]
        return ' '.join(cmd)

    def start(self):
        print(self.command)
        self.__process = subprocess.Popen(self.command,
                                          shell=True,
                                          preexec_fn=os.setsid,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)

    def stop(self):
        if self.__process:
            os.killpg(self.__process.pid, signal.SIGKILL)
        self.__process = None


if __name__ == '__main__':
    cfg = configparser.SafeConfigParser()
    cfg.read('/experiment/config/scenario.cfg')
    sitl = SITL.from_cfg(cfg)
    print(sitl.command)
