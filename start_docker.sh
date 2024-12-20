#!/bin/sh

# Autostart command to run inside the container, default is bash
# Usage1: Modify ./autostart.sh file and add custom command there
# Usage2: Run from cli with ./start_docker "custom command"
COMMAND=${1:-bash}
CONTAINER_NAME=robotrainer:melodic
ROS_DOMAIN_ID=36

# Ensure XAUTHORITY is set
export XAUTHORITY=${XAUTHORITY:-$HOME/.Xauthority}

docker run \
    --name robotrainer_melodic \
    --privileged \
    -it \
    --net host \
    --rm \
    -e DISPLAY=${DISPLAY} \
    -e ROS_DOMAIN_ID=${ROS_DOMAIN_ID} \
    -e QT_X11_NO_MITSHM=1 \
    -e XAUTHORITY=${XAUTHORITY} \
    -v $XAUTHORITY:$XAUTHORITY:rw \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $PWD/src:/home/docker/ros_ws/src:rw \
    -v $PWD/.vscode:/home/docker/ros_ws/src/.vscode \
    -v /dev:/dev  \
    ${CONTAINER_NAME} \
    ${COMMAND}

    # --env-file .env \
    # libEGL for Gazebo needs access to /dev/dri/renderD129
    # -v /dev:/dev \
    # -v /lib/modules:/lib/modules:ro \