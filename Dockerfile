FROM squareslab/ardubugs:base

RUN rm -rf /experiment/source && \
    git clone https://bitbucket.org/kevinaangstadt/ardupilot source && \
    cd /experiment/source && \
    git checkout cc5920b

# install Python 3.5
RUN sudo add-apt-repository ppa:jonathonf/python-3.5 && \
    sudo apt-get update && \
    sudo apt-get install --no-install-recommends -y python3.5 \
                                                    python3.5-dev

# install pip for Python 3.5
RUN wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py && \
    sudo python3.5 /tmp/get-pip.py && \
    rm /tmp/get-pip.py

# install dronekit
RUN pip3 install dronekit dronekit_sitl --user

# install gcc-5/g++-5 (required by newer versions of ArduPilot)
RUN sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test && \
    sudo apt-get update && \
    sudo apt-get install -y gcc-5 g++-5 && \
    sudo update-alternatives \
      --install /usr/bin/gcc gcc /usr/bin/gcc-5 60 \
      --slave /usr/bin/g++ g++ /usr/bin/g++-5

# build
RUN cd source && \
    ./waf configure && \
    ./waf configure && \
    ./waf build -j$(nproc)

# https://raw.githubusercontent.com/dronekit/dronekit-python/master/examples/vehicle_state/vehicle_state.py

ADD missions missions
ADD helper.py helper.py
ADD test.py test.py
ADD mission_runner.py mission_runner.py
ADD fix.diff fix.diff
