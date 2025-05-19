#!/bin/sh

CONTAINER_NAME=robotrainer_melodic
CONTAINER_TAG=gait

docker build \
    --build-arg UID="$(id -u)" \
    --build-arg GID="$(id -g)" \
    -t ${CONTAINER_NAME}:${CONTAINER_TAG} \
    --build-arg CACHE_BUST="$(date +%s)" \
    .

    # --no-cache \
    # --progress plain \
