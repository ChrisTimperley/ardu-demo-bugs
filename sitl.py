# This script is responsible for launching and closing the SITL.
import os

import dronekit_sitl


class SITL(object):
    def from_cfg(cfg):
        # TODO which other vehicles do we need to support?
        vehicle = cfg.get("Mission", "vehicle")
        if vehicle == 'APMRover2':
            binary = 'ardurover'
            model = 'rover'
        elif vehicle == 'ArduCopter':
            binary = 'arducopter'
            model = 'copter'

        home_lat = cfg.getfloat("Mission", "latitude")
        home_lon = cfg.getfloat("Mission", "longitude")
        home_alt = cfg.getfloat("Mission", "altitude")
        home_heading = cfg.getfloat("Mission", "heading")

        return SITL(vehicle=vehicle,
                    model=model,
                    binary=binary,
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
        self.__simulator = None
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

        # args_dronekit = [
        #     '--model={}'.format(self.__model),
        #     '--home={}'.format(','.join(map(str, self.__home_loc))),
        #     '--defaults=/experiment/source/Tools/autotest/default_params/rover.parm' # TODO fix!
        # ]
        #
        # sitl = dronekit_SITL.SITL(binary)
        # sitl.launch(args_dronekit,
        #             verbose=True,
        #             await_ready=True,
        #             restart=False,
        #             speedup=speedup)

    def stop(self):
        self.__simulator.close()
        self.__simulator = None
