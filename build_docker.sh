#!/bin/sh

CONTAINER_NAME=robotrainer_melodic
CONTAINER_TAG=melodic

docker build \
    --build-arg UID="$(id -u)" \
    --build-arg GID="$(id -g)" \
    -t ${CONTAINER_NAME}:${CONTAINER_TAG} \
    .

    # --no-cache \
    # --progress plain \
    # --build-arg CACHE_BUST="$(date +%s)" \
