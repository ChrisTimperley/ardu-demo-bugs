#!/bin/bash
docker build -t overflow .
docker run  --rm \
            -e DISPLAY=$DISPLAY \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            -w /experiment/source/APMrover2 \
            -it overflow \
            ../Tools/autotest/sim_vehicle.py -l 40.071374969556928,-105.22978898137808,1583.702759,246 -f rover --map --console
