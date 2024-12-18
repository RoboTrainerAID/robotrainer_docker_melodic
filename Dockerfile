##############################################################################
##                                 Base Image                               ##
##############################################################################
ARG ROS_DISTRO=melodic
FROM osrf/ros:$ROS_DISTRO-desktop-full as ros
ENV TZ=Europe/Berlin
ENV TERM=xterm-256color
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /etc/bash.bashrc

##############################################################################
##                                 Default Dependecies                      ##
##############################################################################
FROM ros as default_dependencies

RUN apt-get update && apt-get install --no-install-recommends -y \
    iputils-ping nano htop git sudo wget curl gedit \
    && rm -rf /var/lib/apt/lists/*

##############################################################################
##                                   User                                   ##
##############################################################################
FROM default_dependencies as user

ARG USER=docker
ARG PASSWORD=docker
ARG UID=1000
ARG GID=1000
ENV USER=$USER
RUN groupadd -g $GID $USER \
    && useradd -m -u $UID -g $GID -p "$(openssl passwd -1 $PASSWORD)" \
    --shell $(which bash) $USER -G sudo
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/sudogrp
RUN usermod -a -G video $USER

USER $USER
RUN mkdir -p /home/$USER/ros_ws/src

##############################################################################
##                                 Custom Dependecies                       ##
##############################################################################
FROM user as custom_dependencies
WORKDIR /home/$USER/ros_ws/src

# COPY host dest
# RUN git clone --branch visualization

##############################################################################
##                                 Build ROS and source                     ##
##############################################################################
WORKDIR /home/$USER/ros_ws
RUN rosdep update --rosdistro $ROS_DISTRO
RUN rosdep install --from-paths src --ignore-src -y
RUN . /opt/ros/$ROS_DISTRO/setup.sh && colcon build --symlink-install \
    --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
RUN echo "source /home/$USER/ros_ws/install/setup.bash" >> /home/$USER/.bashrc

RUN sudo sed --in-place --expression \
    '$isource "/home/$USER/ros_ws/install/setup.bash"' \
    /ros_entrypoint.sh

CMD [bash]