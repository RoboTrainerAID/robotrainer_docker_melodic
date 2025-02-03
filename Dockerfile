##############################################################################
##                                 Base Image                               ##
##############################################################################
ARG ROS_DISTRO=melodic
# Ubuntu 18.04.
FROM osrf/ros:${ROS_DISTRO}-desktop-full
ENV TZ=Europe/Berlin
ENV TERM=xterm-256color
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /etc/bash.bashrc

##############################################################################
##                                   User                                   ##
##############################################################################
ARG USER=docker
ARG PASSWORD=docker
ARG UID=1000
ARG GID=1000
ENV USER=${USER}
RUN groupadd -g ${GID} ${USER} \
    && useradd -m -u ${UID} -g ${GID} -p "$(openssl passwd -1 ${PASSWORD})" \
    --shell $(which bash) ${USER} -G sudo
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/sudogrp
RUN usermod -a -G video ${USER}

##############################################################################
##                                 Global Dependecies                       ##
##############################################################################
# Install default packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    iputils-ping nano htop git sudo wget curl gedit \
    python-pip \
    python-catkin-tools \
    gdb \
    && rm -rf /var/lib/apt/lists/*

# Install custom dependencies
# RUN apt-get update && apt-get install --no-install-recommends -y \
#     <YOUR_PACKAGE> \
#     && rm -rf /var/lib/apt/lists/*

# RUN pip install \
#     <YOUR_PACKAGE>
RUN pip install \
    pyyaml

##############################################################################
##                                 dependencies_ws                          ##
##############################################################################
USER ${USER}
RUN mkdir -p /home/${USER}/dependencies_ws/src
WORKDIR /home/${USER}/dependencies_ws/src

# ARG CACHE_BUST
# RUN git clone --branch <BRANCH> <REPO_URL>

# RUN git clone --branch melodic https://github.com/RoboTrainerAID/ati_force_torque.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/camera_lower_leg_tracking.git
RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_calibration_data.git
RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_common.git
RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_control.git
# RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_driver.git
RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_environments.git
# RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_robots.git
RUN git clone --branch melodic https://github.com/RoboTrainerAID/force_torque_sensor.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/gait_parameters_estimation.git
# RUN git clone --branch main https://github.com/RoboTrainerAID/human_body_detection.git
RUN git clone --branch melodic_robotrainer2 https://github.com/RoboTrainerAID/iirob_filters.git
RUN git clone --branch melodic https://github.com/RoboTrainerAID/iirob_led.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/ipr_helpers.git
RUN git clone --branch melodic https://github.com/RoboTrainerAID/leg_tracker.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/robotrainer.git

# This is also copied to ros_ws
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/robotrainer_control.git

# RUN git clone --branch melodic https://github.com/RoboTrainerAID/robotrainer_user_performance.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/ros_canopen.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/ros_opcua_communication.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/setup_cob4.git
# RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/sr2_bringup.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/sr2_dashboard.git

# Build dependencies_ws
WORKDIR /home/${USER}/dependencies_ws
RUN rosdep update --rosdistro ${ROS_DISTRO}
USER root
RUN apt-get update 
RUN rosdep install --from-paths src --ignore-src -r -y
RUN rm -rf /var/lib/apt/lists/*
USER ${USER}
RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
    catkin config --merge-devel && catkin init && catkin build
RUN echo "source /home/${USER}/dependencies_ws/devel/setup.bash" >> /home/${USER}/.bashrc

##############################################################################
##                                 ros_ws                                   ##
##############################################################################
RUN mkdir -p /home/${USER}/ros_ws/src
WORKDIR /home/${USER}/ros_ws

# COPY <HOST_PATH> <CONTAINER_PATH>
COPY ./src ./src

# Build ros_ws
RUN . /home/${USER}/dependencies_ws/devel/setup.sh && \
    catkin config --merge-devel && catkin init && catkin build --cmake-args -DCMAKE_BUILD_TYPE=Debug
RUN echo "source /home/${USER}/ros_ws/devel/setup.bash" >> /home/${USER}/.bashrc

##############################################################################
##                                 Autostart                                ##
##############################################################################
RUN sudo sed --in-place --expression \
    '$isource "/home/${USER}/dependencies_ws/devel/setup.bash"' \
    /ros_entrypoint.sh

RUN sudo sed --in-place --expression \
    '$isource "/home/${USER}/ros_ws/devel/setup.bash"' \
    /ros_entrypoint.sh

CMD ["bash"]