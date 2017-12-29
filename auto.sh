#!/bin/bash
# mavproxy.py --map
docker build -t overflow .
docker run  --rm \
            -e DISPLAY=$DISPLAY \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            -it overflow \
            /bin/bash
            # python test.py
