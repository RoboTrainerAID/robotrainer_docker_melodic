#!/bin/sh

# Autostart command to run inside the container, default is bash
# Usage1: Modify ./autostart.sh file and add custom command there
# Usage2: Run from cli with ./start_docker "custom command"
COMMAND=${1:-bash}
CONTAINER_NAME=robotrainer_melodic
CONTAINER_TAG=melodic
ROS_DOMAIN_ID=36

# Check if the container is already running
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container ${CONTAINER_NAME} is already running. Attaching to it..."
    docker exec -it ${CONTAINER_NAME} ${COMMAND}
    exit 0
fi

# Ensure XAUTHORITY is set
export XAUTHORITY=${XAUTHORITY:-$HOME/.Xauthority}

docker run \
    --name ${CONTAINER_NAME} \
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
    -v $PWD/src:/home/docker/ros_ws/src \
    -v /dev:/dev  \
    ${CONTAINER_NAME}:${CONTAINER_TAG} \
    ${COMMAND}

    # --env-file .env \
    # libEGL for Gazebo needs access to /dev/dri/renderD129
    # -v /dev:/dev \
    # -v /lib/modules:/lib/modules:ro \