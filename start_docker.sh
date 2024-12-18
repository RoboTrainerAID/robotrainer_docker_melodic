#!/bin/sh

# Autostart command to run inside the container, default is bash
# Usage: Modify ./autostart.sh file
# Usage: Run from cli with ./start_docker "custom command"
COMMAND=${1:-bash}

# Custom domain id
ROS_DOMAIN_ID=36

uid=$(eval "id -u")
gid=$(eval "id -g")

docker run \
    --name robotrainer_melodic \
    --privileged \
    -it \
    --net host \
    --rm \
    -e DISPLAY=$DISPLAY \
    -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
    -v $PWD/src:/home/docker/ros_ws/src:rw \
    -v $PWD/.vscode:/home/docker/ros_ws/src/.vscode \
    -v /dev:/dev  \
    robotrainer:melodic \
    $COMMAND
    # --env-file .env \