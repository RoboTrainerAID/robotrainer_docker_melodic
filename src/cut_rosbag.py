# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import subprocess
import rosbag
import rospy
from std_msgs.msg import Float32

class RosbagTrimmer:
    """ Class to trim a ROS bag file based on the first change in a specified topic."""
    
    def __init__(self, bag_folder, bag_name, reference_topic="/robotrainer_deviation/current_path_index"):
        self.bag_folder = bag_folder
        self.bag_name = bag_name
        self.bag_path = os.path.join(bag_folder, bag_name)
        print("[INIT] Looking for bag file at: " + self.bag_path)

        if not os.path.exists(self.bag_path):
            raise IOError("[ERROR] Bag file not found: " + self.bag_path)

        self.reference_topic = reference_topic
        self.output_dir = os.path.join(self.bag_folder, "cut")
        self.output_path = self._create_output_path()
        print("[INIT] Output will be: " + self.output_path)

    def _create_output_path(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print("[INIT] Created output directory: " + self.output_dir)
        filename = os.path.basename(self.bag_path)
        return os.path.join(self.output_dir, filename)
    
    def extract_triplet(self, msg):
        return (msg.front, msg.left, msg.right)
    
    def find_first_change_timestamp(self):
        print("[SCAN] Scanning topic '" + self.reference_topic + "' for first change...")
        with rosbag.Bag(self.bag_path, 'r') as bag:
            last_values = None
            for topic_name, msg, t in bag.read_messages(topics=[self.reference_topic]):
                current_values = self.extract_triplet(msg)
                if last_values is None:
                    last_values = current_values
                    print("[SCAN] First values: {} at {:.3f}s".format(last_values, t.to_sec()))
                elif current_values != last_values:
                    print("[SCAN] Change detected: {} → {} at {:.3f}s".format(last_values, current_values, t.to_sec()))
                    return t       
        print("[SCAN] No change detected in topic.")
        return None

    def trim(self):    
        """" Trims the bag file starting from the first change in the reference topic."""
        change_time = self.find_first_change_timestamp()
        if change_time is not None:
            time_sec = change_time.to_sec()
            print("[TRIM] Change detected. Trimming from {:.3f}s onwards.".format(time_sec))
        else:
            # Kein Change gefunden → ab Anfang (t = 0)
            time_sec = 0.0
            print("[TRIM] No changes in topic. Copying selected topics from beginning.")

        allowed_topics = [
            '/base/fts_adaptive_force_controller/debug/velocity_output',
            '/base/output_data',
            '/base_laser_back/scan',
            '/biosensors/polar_oh1/hr',
            '/biosensors/polar_oh1/hrv',
            '/biosensors/polar_oh1/ppg_ch0',
            '/biosensors/polar_oh1/ppg_ch1',
            '/biosensors/polar_oh1/ppg_ch2',
            '/biosensors/polar_oh1/ppg_ch3',
            '/biosensors/polar_oh1/ppi',
            '/robotrainer_deviation/robotrainer_deviation',
            '/robotrainer_deviation/robotrainer_deviation_markers',
            '/toe_detection/toe_positions'
        ]

        topic_check = " or ".join(["topic == '{}'".format(t) for t in allowed_topics])
        expression = "(t.to_sec() >= {}) and ({})".format(time_sec, topic_check)

        print("[TRIM] Using rosbag filter with expression:\n  {}".format(expression))
        cmd = [
            "rosbag", "filter",
            self.bag_path,
            self.output_path,
            expression
        ]

        try:
            subprocess.check_call(cmd)
            print("[TRIM] Successfully wrote trimmed bag to: " + self.output_path)
            
            # Bag-Dauer anhängen
            with rosbag.Bag(self.output_path, 'a') as outbag:
                start_time = outbag.get_start_time()
                end_time = outbag.get_end_time()
                duration = end_time - start_time
                duration_msg = Float32(data=duration)
                outbag.write('/bag_duration', duration_msg, rospy.Time(int(end_time)))
                print("[TRIM] Wrote duration {:.2f}s to /bag_duration at t={:.2f}s".format(duration, end_time))

            return True
        except subprocess.CalledProcessError as e:
            print("[ERROR] rosbag filter failed: {}".format(str(e)))
            return False

        

