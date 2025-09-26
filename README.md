# robotrainer_docker_melodic

## How to use
1. Put .bag files into the `data/` folder
2. The bag files are mounted into `/home/docker/ros_ws/data/` 
3. Clone the gait_parameter_estimation package into `src/` folder of the workspace:
   ```bash
   cd src/
   git clone https://github.com/RoboTrainerAID/gait_parameters_estimation.git

   # or use vcs2l to clone complete list from project.repos
   vcs import src < project.repos
   ```
4. Build the docker image with `./build_docker.sh`
5. Start the container with `./start_docker.sh`
   - Executing `./start_docker.sh` again in a new terminal will connect to the already running container.
