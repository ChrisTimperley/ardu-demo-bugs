FROM squareslab/ardubugs:base

RUN rm -rf /experiment/source && \
    git clone https://bitbucket.org/kevinaangstadt/ardupilot source && \
    cd /experiment/source && \
    git checkout cc5920b

# install Python 3.5
RUN sudo add-apt-repository ppa:jonathonf/python-3.5 && \
    sudo apt-get update && \
    sudo apt-get install --no-install-recommends -y python3.5 \
                                                    python3.5-dev && \
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.4 1 && \
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 2

# install pip for Python 3.5
RUN wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py && \
    sudo python3.5 /tmp/get-pip.py && \
    rm /tmp/get-pip.py

# install dronekit
RUN pip3 install dronekit dronekit_sitl --user

ADD test.py test.py
