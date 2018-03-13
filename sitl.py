# This script is responsible for launching and closing the SITL.
import os

import dronekit_sitl


class SITL(object):
    # TODO: from_file
    # TODO: from_cfg

    def __init__(model='rover', binary='ardurover'):
        self.__dir_base = '/experiment/source'
        self.__name_binary = binary
        self.__model = model
        self.__simulator = None

    def start(self):
        binary = os.path.join(self.__dir_base,
                              'build/sitl/bin',
                              self.__name_binary)

        # TODO parameters!
        args = [
            '--model={}'.format(self.__model),
            '--home={}'.format(','.join(map(str, home))),
            '--defaults=/experiment/source/Tools/autotest/default_params/rover.parm'
        ]

        # TODO we need to use mavproxy
        sitl = dronekit_SITL.SITL(binary)
        sitl.launch([home_arg, model_arg, defaults_arg],
                    verbose=True,
                    await_ready=True,
                    restart=False,
                    speedup=speedup)

    def stop(self):
        self.__simulator.close()
        self.__simulator = None
