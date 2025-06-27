#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import glob
import rosbag
import pandas as pd

class RosbagToCSVConverter:
    """
    Converts individual ROS bag files to CSV, exporting only relevant fields.
    """
    def __init__(self, sample_folder="data/sample", output_folder="data/converted"):
        self.sample_folder = sample_folder
        self.output_folder = output_folder

        if not os.path.isdir(self.sample_folder):
            raise IOError("Sample folder not found: {}".format(self.sample_folder))
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print("[INIT] Created output folder:", self.output_folder)

    def bag_to_csv(self, bag_path):
        records = []
        bag = rosbag.Bag(bag_path, 'r')

        for topic, msg, t in bag.read_messages():
            rec = {}

            if topic == '/bag_duration' and hasattr(msg, 'data'):
                rec['bag_duration'] = msg.data

            elif topic == '/base/fts_adaptive_force_controller/debug/velocity_output':
                v = msg.twist.linear; a = msg.twist.angular
                rec.update({
                    'lin_x': v.x, 'lin_y': v.y, 'lin_z': v.z,
                    'ang_x': a.x, 'ang_y': a.y, 'ang_z': a.z
                })

            elif topic == '/base/output_data':
                f = msg.wrench.force; t2 = msg.wrench.torque
                rec.update({
                    'force_x': f.x, 'force_y': f.y, 'force_z': f.z,
                    'torque_x': t2.x, 'torque_y': t2.y, 'torque_z': t2.z
                })

            elif topic == '/base_laser_back/scan':
                rec.update({
                    'angle_min': msg.angle_min,
                    'angle_max': msg.angle_max,
                    'angle_increment': msg.angle_increment,
                    'time_increment': msg.time_increment,
                    'scan_time': msg.scan_time,
                    'range_min': msg.range_min,
                    'range_max': msg.range_max,
                })

            elif topic.startswith('/biosensors/polar_oh1/'):
                name = topic.split('/')[-1]
                if hasattr(msg, 'data'):
                    d = msg.data
                    rec[name] = list(d) if hasattr(d, '__iter__') else [d]

            elif topic == '/robotrainer_deviation/robotrainer_deviation':
                rec['front'] = getattr(msg, 'front', None)
                rec['left']  = getattr(msg, 'left', None)
                rec['right'] = getattr(msg, 'right', None)

            else:
                continue  # Skip all other topics

            if rec:
                records.append(rec)

        bag.close()
        if not records:
            print("[CSV] No records in:", bag_path)
            return None

        df = pd.DataFrame(records)
        csv_name = os.path.splitext(os.path.basename(bag_path))[0] + ".csv"
        csv_path = os.path.join(self.output_folder, csv_name)
        df.to_csv(csv_path, index=False)
        print("[CSV] Written:", csv_path)
        return csv_path

    def process_all(self):
        files = sorted(glob.glob(os.path.join(self.sample_folder, "*.bag")))
        if not files:
            print("[PROCESS] No bag files in '{}'.".format(self.sample_folder))
            return

        for bag_file in files:
            print("[PROCESS] Converting:", bag_file)
            self.bag_to_csv(bag_file)
