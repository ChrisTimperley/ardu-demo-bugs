FROM ubuntu:14.04
MAINTAINER Chris Timperley "christimperley@gmail.com"

# Create docker user
RUN apt-get update && \
    apt-get install --no-install-recommends -y sudo && \
    useradd -ms /bin/bash docker && \
    echo 'docker ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    adduser docker sudo && \
    apt-get clean && \
    mkdir -p /home/docker && \
    sudo chown -R docker /home/docker && \
    sudo chown -R docker /usr/local/bin && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
USER docker

# install basic packages
RUN sudo apt-get update && \
    sudo apt-get install --no-install-recommends -y build-essential \
                                                    curl \
                                                    libcap-dev \
                                                    git \
                                                    cmake \
                                                    vim \
                                                    jq \
                                                    wget \
                                                    zip \
                                                    unzip \
                                                    python3-setuptools \
                                                    software-properties-common \
                                                    libncurses5-dev && \
    sudo apt-get autoremove -y && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN sudo apt-get update
RUN sudo apt-get install -y libtool
RUN sudo apt-get install -y automake
RUN sudo apt-get install -y automake
RUN sudo apt-get install -y pkg-config
RUN sudo apt-get install -y autoconf
RUN sudo apt-get install -y gcc
RUN sudo apt-get install -y g++
RUN sudo apt-get install -y libexpat1-dev
RUN sudo apt-get install -y python-matplotlib
RUN sudo apt-get install -y python-serial
RUN sudo apt-get install -y python-wxgtk2.8
RUN sudo apt-get install -y python-wxtools
RUN sudo apt-get install -y python-lxml
RUN sudo apt-get install -y python-scipy
RUN sudo apt-get install -y python-opencv
RUN sudo apt-get install -y ccache
RUN sudo apt-get install -y gawk
RUN sudo apt-get install -y python-pip
RUN sudo apt-get install -y --no-install-recommends flightgear-data-base
RUN sudo apt-get install -y --no-install-recommends flightgear-data-ai
RUN sudo apt-get install -y flightgear
RUN sudo apt-get install -y python-pexpect
RUN sudo apt-get install -y bash
RUN sudo pip install future
RUN sudo pip install mavproxy
RUN sudo pip install --upgrade pexpect

# download and install jsbsim
WORKDIR /experiment
ENV JSBSIM_REVISION 9cc2bf1
RUN sudo chown -R $(whoami):$(whoami) /experiment && \
    git clone https://github.com/arktools/jsbsim /experiment/jsbsim && \
    cd jsbsim && \
    git checkout "${JSBSIM_REVISION}" && \
    ./autogen.sh --enable-libraries && \
    make -j

ENV PATH "${PATH}:/experiment/jsbsim/src"
ENV PATH "${PATH}:/experiment/source/Tools/autotest"
ENV PATH "${PATH}:/usr/lib/ccache:${PATH}"
ENV PATH "/usr/games:${PATH}"

# download ArduPilot source code
# ENV ARDUPILOT_REVISION 7173025
RUN git clone https://github.com/ArduPilot/ardupilot source --depth 30
RUN cd source && \
    git submodule update --init --recursive && \
    sudo chown -R $(whoami):$(whoami) /experiment

RUN sudo pip install dronekit \
                     statistics \
                     geopy

ENV ARDUPILOT_LOCATION "/experiment/source"

ADD docker/default.parm /experiment/
ADD docker/default_eeprom.bin /experiment/
RUN cp /experiment/default_eeprom.bin /experiment/eeprom.bin

# install dronekit SITL
RUN git clone https://github.com/dronekit/dronekit-sitl.git /experiment/dronekit-sitl && \
    cd /experiment/dronekit-sitl && \
    git checkout 2d854af && \
    sudo python setup.py install

# compile ArduPilot
# RUN cd "${ARDUPILOT_LOCATION}" && \
#     ./waf configure && \
#     ./waf build -j$(nproc)

RUN sudo chown -R $(whoami):$(whoami) source

# fixes indefinite timeout in default test harness
RUN sudo pip uninstall -y pymavlink && \
    sudo pip install pymavlink

# install Python 3
RUN sudo apt-get update && \
    sudo apt-get install -y python3

# install gcc-5/g++-5 (required by newer versions of ArduPilot)
RUN sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test && \
    sudo apt-get update
RUN sudo apt-get install -y gcc-5
RUN sudo apt-get install -y g++-5
RUN sudo update-alternatives \
      --install /usr/bin/gcc gcc /usr/bin/gcc-5 60 \
      --slave /usr/bin/g++ g++ /usr/bin/g++-5

# build
RUN cd source && \
    ./waf configure && \
    ./waf configure && \
    ./waf build -j$(nproc)

# TODO: missing rsync
RUN sudo apt-get install -y rsync

# https://raw.githubusercontent.com/dronekit/dronekit-python/master/examples/vehicle_state/vehicle_state.py
ADD missions missions
ADD helper.py helper.py
ADD test.py test.py
ADD config /experiment/config
