# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import rosbag


class RosbagTrimmer:
    """Class to trim a ROS bag file:
       Start = first change in reference_topic AFTER force_input_raw_x != 0.0
       End   = full bag kept 
    """

    def __init__(self, bag_folder, bag_name, force_topic, force_field, reference_topic):
        self.bag_folder = bag_folder
        self.bag_name = bag_name
        self.bag_path = os.path.join(bag_folder, bag_name)
        print("[INIT] Looking for bag file at:", self.bag_path)

        if not os.path.exists(self.bag_path):
            raise IOError("[ERROR] Bag file not found: " + self.bag_path)

        self.force_topic = force_topic
        self.force_field = force_field
        self.reference_topic = reference_topic

        self.output_dir = os.path.join("data", "cut")
        self.output_path = self._create_output_path()
        print("[INIT] Output will be:", self.output_path)

    def _create_output_path(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print("[INIT] Created output directory:", self.output_dir)
        filename = os.path.basename(self.bag_path)
        return os.path.join(self.output_dir, filename)

    def extract_field(self, msg, field_path):
        """Extracts a field such as ‘wrench.force.x’ from the ROS message"""
        obj = msg
        for part in field_path.split("."):
            obj = getattr(obj, part)
        return obj

    def extract_triplet(self, msg):
        """Extract front, left, right values from the reference_topic message"""
        return (msg.front, msg.left, msg.right)

    def find_first_change_timestamp(self):
        """Find the first timestamp when force!=0 and path_index changes"""
        print("[SCAN] Scanning topics '{}' and '{}'...".format(
            self.force_topic, self.reference_topic))

        force_nonzero_seen = False
        path_prev = None

        with rosbag.Bag(self.bag_path, 'r') as bag:
            for topic, msg, t in bag.read_messages(topics=[self.force_topic, self.reference_topic]):

                # Condition 1: force_input_raw_x != 0
                if topic == self.force_topic:
                    try:
                        force_val = float(self.extract_field(msg, self.force_field))
                    except Exception:
                        force_val = 0.0
                    if abs(force_val) > 1e-6:
                        if not force_nonzero_seen:
                            print("[SCAN] Force nonzero detected ({:.4f}) at {:.3f}s".format(
                                force_val, t.to_sec()))
                        force_nonzero_seen = True

                # Condition 2: path_index change AFTER force!=0
                elif topic == self.reference_topic and force_nonzero_seen:
                    current_values = self.extract_triplet(msg)
                    if path_prev is None:
                        path_prev = current_values
                        continue
                    if current_values != path_prev:
                        print("[SCAN] Path change detected: {} → {} at {:.3f}s".format(
                            path_prev, current_values, t.to_sec()))
                        return t
                    path_prev = current_values

        print("[SCAN] No valid trim condition found.")
        return None

    def trim(self):
        """Trims the bag file starting from the first valid condition (force!=0 + path change)."""
        change_time = self.find_first_change_timestamp()
        if change_time is not None:
            time_sec = change_time.to_sec()
            print("[TRIM] Trim start = {:.3f}s".format(time_sec))
        else:
            time_sec = 0.0
            print("[TRIM] No condition found. Copying full bag from start.")

        with rosbag.Bag(self.bag_path, 'r') as inbag, rosbag.Bag(self.output_path, 'w') as outbag:
            for topic, msg, t in inbag.read_messages():
                if t.to_sec() >= time_sec:
                    outbag.write(topic, msg, t)

        print("[TRIM] Successfully wrote trimmed bag to:", self.output_path)
        return True
