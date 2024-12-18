#!/bin/sh
uid=$(eval "id -u")
gid=$(eval "id -g")

docker build \
    --build-arg UID="$uid" \
    --build-arg GID="$gid" \
    --build-arg ROS_DISTRO=melodic \
    -t robotrainer:melodic \
    .
    # --no-cache \
