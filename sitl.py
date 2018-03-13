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

        # TODO this needs to work
        # launch mavproxy -- ports aren't being forwarded!
        # sim_uri = sitl.connection_string()
        # mavproxy_cmd = \
        #     "mavproxy.py --console --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out localhost:14550 & /bin/bash"
        # subprocess.call(mavproxy_cmd, shell=True)
        # time.sleep(1)

        # TODO allow home to be specified
        home = [40.071374969556928, -105.22978898137808, 1583.702759, 246]

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
