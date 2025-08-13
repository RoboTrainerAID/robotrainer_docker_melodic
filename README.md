# robotrainer_docker_melodic

## How to use
1. Put .bag files into the `data/` folder
2. The bag files are mounted into `/home/docker/ros_ws/data/` 
3. Clone the gait_parameter_estimation package into `src/` folder of the workspace:
   ```bash
   cd src/
   git clone https://github.com/RoboTrainerAID/gait_parameters_estimation.git
   ```
4. Build the docker image with `./build_docker.sh`
5. Start the container with `./start_docker.sh`
   - Executing `./start_docker.sh` again in a new terminal will connect to the already running container.
6. Launch robot URDF and gait_estimation with:
   ```bash
   roslaunch gait_parameters_estimation launch_from_bag_urdf_and_tf.launch
   ```
7. Launch RViz for visualization with:
   ```bash
   roslaunch za_experimental rviz.launch
   ```
8. A: Play the .bag file directly with `rosbag play data/your_bag_file.bag`
   <!-- B: Play the .bag file with plotjuggler and have more control about playback and data plotting
   - Start plotjuggler with `rosrun plotjuggler plotjuggler`
   - Open the bag file with `File -> Data: Load data from file` and select the .bag file, Select all topics
   - Select the predefined layout with `Layout -> Load Layout` and choose `src/gait_parameters_estimation/include/plotjuggler_config.xml`
   - Tick `Publishers -> ROS Topic Re-Publisher` to stream from bag to rviz -->
9. With Plotjuggler all other topics that can not be visualized can be plotted in graphs (e.g. Heart rate).
   - Start Plotjuggler with `rosrun plotjuggler plotjuggler`
   - Select `Streaming -> ROS Topic Subscriber` Press START and select all topics
   - Increase the buffer size from 5 -> 20
   - Drag and drop the topics into the graph area

```bash
# (Option 1)
# If bag is recorded without /tf
# launch urdf and robot description publisher (for tfs)
roslaunch gait_parameters_estimation launch_from_bag_urdf_and_tf.launch
roslaunch za_experimental rviz.launch

# (Option 2)
# Also publish scenario data in rviz
roslaunch robotrainer_study_automatic_assessment rviz_scenario_and_data.launch

# (Option 3)
# If bag is recorded with /tf
roslaunch gait_parameters_estimation rviz_with_urdf.launch

# (Finally)
rosbag play /path/to/your.bag
```

## Topics to record:
- /base/fts_adaptive_force_controller/debug/velocity_output
- /base/output_data
- /base/virtual_forces/modalities_debug/position
- /base/virtual_forces/modalities_debug/velocity_in
- /base/virtual_forces/modalities_debug/velocity_out
- /base/virtual_forces/modalities_debug/resulting_velocity
- /base/virtual_forces/modalities_debug/resulting_force
    - Diese Kraft ist skaliert auf max_force (default 100N), das heißt alles x100 ergibt die aktuell wirkende Kraft in Newton
- /base/virtual_forces/modalities_debug/status
- /base_laser_back/scan
- /biosensors/polar_oh1/hr
- /biosensors/polar_oh1/ppg_ch0
- /biosensors/polar_oh1/ppg_ch1
- /biosensors/polar_oh1/ppg_ch2
- /biosensors/polar_oh1/ppg_ch3
- /biosensors/polar_oh1/ppi
- /biosensors/polar_oh1/hrv
- /lower_legs_camera/depth_registered/points
- /map
- /mobile_robot_pose
- /robotrainer_deviation/current_path_index
- /robotrainer_deviation/robotrainer_deviation
- /robotrainer_deviation/robotrainer_deviation_markers
- /toe_detection/toe_positions

## How to collect data
```bash
# Nodes to run:
srt
rt2.launch
camera_lower_body.launch
extract_mobile_robot_base.launch
leg_tracker_one_person.launch 
toe_detection.launch OR feet_detection.launch
gait_estimator.launch

# Record only raw data
rosbag record /base/fts_adaptive_force_controller/debug/velocity_output /mobile_robot_pose /base/output_data /lower_legs_camera/depth_registered/points /base_laser_back/scan /map

# Record all data with processed and output data
rosbag record /base/fts_adaptive_force_controller/debug/velocity_output /mobile_robot_pose /map /leg_detection/people_msg_stamped /base/output_data /right_toe /left_toe /human_body_detection/points /lower_legs_camera/depth_registered/points /base_laser_back/scan /camera_lower_leg_tracking/right_toe /camera_lower_leg_tracking/left_toe /camera_lower_leg_tracking/right_heel /camera_lower_leg_tracking/left_heel /camera_lower_leg_tracking/right_ankle /camera_lower_leg_tracking/left_ankle /camera_lower_leg_tracking/right_foot_axis /camera_lower_leg_tracking/left_foot_axis /camera_lower_leg_tracking/right_Foot /camera_lower_leg_tracking/left_Foot /camera_lower_leg_tracking/right_Leg_icp /camera_lower_leg_tracking/left_Leg_icp /footStrip -e "(.*)gait(.*)"

# copy data with scp and ssh with laptop
scp robotrainer_iras:/home/robotrainer/workspace/ros_ws_melodic_robotrainer/src/za_experimental/data/2025-X.bag /home/andreas/code/robotrainer/bags/
```


## How to Start
```bash
rosbag play src/data/gait_data_2025-03-28-17-39-05.bag --topics /base/fts_adaptive_force_controller/debug/velocity_output /mobile_robot_pose /leg_detection/people_msg_stamped /base/output_data /right_toe /left_toe /human_body_detection/points

roslaunch gait_parameters_estimation gait_estimation.launch
```

`gait_estimation.py` is outdated!  
Only use `gait_estimation_node.py`

## ROS Interface
### Node: gait_estimation_node.py
Class: EstimatorBase
- Input Speed: /base/fts_adaptive_force_controller/debug/velocity_output (geometry_msgs/TwistStamped)(50 Hz)
- Input Pose: /mobile_robot_pose (ipr_helpers/Pose2DStamped)(500 Hz)

Class: EstimatorLegs (Laserscanner)
- Input Leg: /leg_detection/people_msg_stamped (leg_tracker/PersonMsg)(24 Hz)

Class: EstimatorForce (Force-Torque Sensor)
- Input Force: /base/output_data (geometry_msgs/WrenchStamped)(200 Hz)

Class: EstimatorToe (Lower Depth Camera)
- Input Toe: /right_toe, /left_toe (geometry_msgs/PointStamped)(0.8 - 1.2 Hz)

Class: EstimatorShoulder (Upper Depth Camera)
- Input Shoulders: /human_body_detection/points

### Node: toe_detection_node.cpp
```bash
rosbag play raw_image_data_2025-04-10-18-28-41.bag --topics /lower_legs_camera/depth_registered/points

# in rviz choose base_link frame

roslaunch gait_parameters_estimation toe_detection.launch
# Was ist der Unterschied?
# Toe detection uses a simple algorithm to detect the toe position
# based on the point cloud data from the lower legs camera.
# It does not use a Kalman filter or any initialization process.
```

- Input PointCloud: /lower_legs_camera/depth_registered/points (sensor_msgs/PointCloud2)
- Output Toe: /right_toe, /left_toe (geometry_msgs/PointStamped)
  
### Node: feet_detection_node.cpp
```bash
# in rviz choose base_link frame

roslaunch gait_parameters_estimation feet_detection.launch
# Was ist der Unterschied?
# Feet detection uses kalman filter and an initialization process to detect heel, ankle, toes and leg axis
```

- Input PointCloud: /lower_legs_camera/depth_registered/points (sensor_msgs/PointCloud2)
- Output Toe: /camera_lower_leg_tracking/right_toe, /camera_lower_leg_tracking/left_toe (geometry_msgs/PointStamped)
- Output Heel: /camera_lower_leg_tracking/right_heel, /camera_lower_leg_tracking/left_heel (geometry_msgs/PointStamped)
- Output Ankle: /camera_lower_leg_tracking/right_ankle, /camera_lower_leg_tracking/left_ankle (geometry_msgs/PointStamped)
- Output Foot Axis: /camera_lower_leg_tracking/right_foot_axis, /camera_lower_leg_tracking/left_foot_axis (visualization_msgs/Marker)
- Output Foot: /camera_lower_leg_tracking/right_Foot, /camera_lower_leg_tracking/left_Foot (sensor_msgs/PointCloud2)
- Output Leg: /camera_lower_leg_tracking/right_Leg_icp, /camera_lower_leg_tracking/left_Leg_icp (sensor_msgs/PointCloud2)
- Output Foot Strip: /footStrip (sensor_msgs/PointCloud2)
- Service Reset: /camera_lower_leg_tracking/init_reset (std_srvs/Trigger)

### Node: leg_tracker

```bash
roslaunch gait_parameters_estimation leg_tracker_one_person.launch
```
- Input Laserscan: /base_laser_back/scan (sensor_msgs/LaserScan)
- Output Legs: /leg_detection/people_msg_stamped (leg_tracker/PersonMsg)
- Output Body Center: /leg_detection/body_center_stamped (geometry_msgs/PointStamped)


## Related Resources
- weighted Fourier linear combiner (WFLC)
- https://www.cs.cmu.edu/~micron/filtering.htm
- fs = sampling frequency
- dst = double support time (currently not used)

### For ROS Debugging
- Install the ROS vscode extension
- Downgrade the python extension to support Python 2.7/3.6
- Click on the arrow next to "uninstall", install specific version and select 2021.5.9...
- Then create a roslaunch task and run the debugger.
