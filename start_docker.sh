#!/bin/bash

# Name des Containers
CONTAINER_NAME="robotrainer_melodic"

# Docker-Image
IMAGE_NAME="robotrainer_melodic:gait"

# ROS Workspace im Container
WORKSPACE="/home/docker/ros_ws"

# Container starten
docker run -it --name $CONTAINER_NAME --rm \
  --entrypoint /bin/bash \
  -v ${PWD}/src:$WORKSPACE/src \
  -v ${PWD}/data:$WORKSPACE/data \
  -v /iras/users/zaan0001/robotrainer:$WORKSPACE/robotrainer \
  $IMAGE_NAME
#!/bin/bash

