FROM squareslab/ardubugs:base

RUN rm -rf /experiment/source && \
    git clone https://bitbucket.org/kevinaangstadt/ardupilot source && \
    cd /experiment/source && \
    git checkout cc5920b
