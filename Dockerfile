##############################################################################
##                                 Base Image                               ##
##############################################################################
# Ubuntu 18.04. prebuild
FROM andreaszachariae/robotrainer_docker:melodic

# Install custom dependencies
# RUN apt-get update && apt-get install --no-install-recommends -y \
#     <YOUR_PACKAGE> \
#     && rm -rf /var/lib/apt/lists/*

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
    mv ./robotrainer_control/robotrainer_panel . && \
    mv ./robotrainer_control/robotrainer_data_service . && \
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