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
    ros-${ROS_DISTRO}-plotjuggler-ros \
    && rm -rf /var/lib/apt/lists/*

# Install custom dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-melodic-cob-default-env-config \
    ros-melodic-cob-voltage-control \
    ros-melodic-cob-frame-tracker \
    ros-melodic-cob-navigation-global \
    ros-melodic-cob-twist-controller \
    ros-melodic-cob-teleop \
    ros-melodic-cob-collision-velocity-filter \
    ros-melodic-cob-control-mode-adapter \
    ros-melodic-cob-image-flip \
    ros-melodic-canopen-motor-node \
    ros-melodic-cob-phidgets \
    ros-melodic-cob-base-controller-utils \
    ros-melodic-cob-base-velocity-smoother \
    ros-melodic-rosserial-python \
    ros-melodic-cob-cam3d-throttle \
    ros-melodic-cob-script-server \
    ros-melodic-cob-obstacle-distance \
    ros-melodic-cob-supported-robots \
    ros-melodic-cob-light \
    ros-melodic-rplidar-ros \
    ros-melodic-rosserial-server \
    ros-melodic-cob-safety-controller \
    ros-melodic-spacenav-node \
    ros-melodic-cob-sick-s300 \
    ros-melodic-cob-linear-nav \
    ros-melodic-cob-hand-bridge \
    ros-melodic-joy \
    ros-melodic-velocity-controllers \
    ros-melodic-cob-gazebo-worlds \
    ros-melodic-cob-sound \
    ros-melodic-rosparam-handler \
    ros-melodic-sick-safetyscanners \
    ros-melodic-cob-phidget-em-state \
    ros-melodic-twist-mux \
    ros-melodic-cob-bms-driver \
    ros-melodic-usb-cam \
    ros-melodic-cob-command-gui \
    ros-melodic-cob-docker-control \
    ros-melodic-cob-mapping-slam \
    ros-melodic-cob-scan-unifier \
    ros-melodic-cob-monitoring \
    ros-melodic-teleop-twist-joy \
    ros-melodic-ati-force-torque \
    ros-melodic-cob-reflector-referencing \
    ros-melodic-costmap-2d \
    ros-melodic-cob-omni-drive-controller \
    ros-melodic-generic-throttle \
    ros-melodic-openni2-launch \
    ros-melodic-joint-state-publisher-gui \
    ros-melodic-openni-launch \
    ros-melodic-cob-mecanum-controller \
    ros-melodic-cob-android-script-server \
    ros-melodic-canopen-chain-node \
    ros-melodic-cob-mimic \
    ros-melodic-cob-sick-lms1xx \
    ros-melodic-cob-helper-tools \
    ros-melodic-joint-trajectory-controller \
    ros-melodic-cob-dashboard \
    ros-melodic-cob-phidget-power-state \
    && rm -rf /var/lib/apt/lists/*

# RUN pip install \
#     <YOUR_PACKAGE>
RUN pip install \
    pyyaml \
    scipy

##############################################################################
##                                 dependencies_ws                          ##
##############################################################################
USER ${USER}
RUN mkdir -p /home/${USER}/dependencies_ws/src
WORKDIR /home/${USER}/dependencies_ws/src

ARG CACHE_BUST
# RUN git clone --branch <BRANCH> <REPO_URL>

# Necessary for standalone urdf
RUN git clone --branch main https://github.com/RoboTrainerAID/za_experimental.git
RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_robots.git
RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_calibration_data.git
RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/cob_common.git
RUN git clone --branch robotrainer2 https://github.com/RoboTrainerAID/sr2_bringup.git
RUN git clone --branch melodic https://github.com/RoboTrainerAID/robotrainer.git

# Gait related repos
RUN git clone --branch main https://github.com/RoboTrainerAID/human_body_detection.git
RUN git clone --branch melodic_robotrainer2 https://github.com/RoboTrainerAID/iirob_filters.git
RUN git clone --branch melodic https://github.com/RoboTrainerAID/ipr_helpers.git
RUN git clone --branch melodic https://github.com/RoboTrainerAID/iirob_led.git
RUN git clone --branch melodic https://github.com/RoboTrainerAID/robotrainer_control.git
RUN mv ./robotrainer_control/robotrainer_parameters . && \
    rm -rf ./robotrainer_control

# Repos cloned in docker ws
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/gait_parameters_estimation.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/leg_tracker.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/camera_lower_leg_tracking.git
# RUN git clone --branch melodic https://github.com/RoboTrainerAID/robotrainer_user_performance.git

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

ARG CACHE_BUST
# COPY <HOST_PATH> <CONTAINER_PATH>
COPY ./src ./src

USER root
RUN apt-get update 
RUN rosdep install --from-paths src --ignore-src -r -y
RUN rm -rf /var/lib/apt/lists/*
USER ${USER}

# Build ros_ws
RUN . /home/${USER}/dependencies_ws/devel/setup.sh && \
    catkin config --merge-devel && catkin init && catkin build --cmake-args -DCMAKE_BUILD_TYPE=Debug
# RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
#     catkin config --merge-devel && catkin init && catkin build --cmake-args -DCMAKE_BUILD_TYPE=Debug
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