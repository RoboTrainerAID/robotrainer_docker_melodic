# robotrainer_docker_melodic

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


roslaunch gait_parameters_estimation collect_data.launch
```


## How to Start
```bash
rosbag play src/bags/gait_data_2025-03-28-17-39-05.bag --topics /base/fts_adaptive_force_controller/debug/velocity_output /mobile_robot_pose /leg_detection/people_msg_stamped /base/output_data /right_toe /left_toe /human_body_detection/points

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
