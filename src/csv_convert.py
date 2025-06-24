#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import rosbag
import rospy
import glob
import pandas as pd
import rosbag_pandas

class RosbagMerger:
    """
    Merges multiple ROS bag files with the same prefix and converts the merged bag to CSV.
    """
    def __init__(self, sample_folder="data/sample", output_folder="data/merged"):
        self.sample_folder = sample_folder
        self.output_folder = output_folder

        if not os.path.isdir(self.sample_folder):
            raise IOError("Sample folder not found: {}".format(self.sample_folder))
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print("[INIT] Created output folder:", self.output_folder)

    def merge_prefix(self, prefix):
        pattern = os.path.join(self.sample_folder, "{}*.bag".format(prefix))
        files = sorted(glob.glob(pattern))
        if not files:
            print("[MERGE] No bags found for prefix '{}'.".format(prefix))
            return None

        merged_name = "{}_merged.bag".format(prefix)
        out_path = os.path.join(self.output_folder, merged_name)

        print("[MERGE] Merging {} files with prefix '{}' → {}".format(
            len(files), prefix, merged_name))
        with rosbag.Bag(out_path, 'w') as outbag:
            for fb in files:
                print("  - Adding", fb)
                for topic, msg, t in rosbag.Bag(fb).read_messages():
                    outbag.write(topic, msg, t)
        return out_path

    def bag_to_csv(self, bag_path):
        csv_name = os.path.splitext(os.path.basename(bag_path))[0] + ".csv"
        csv_path = os.path.join(self.output_folder, csv_name)

        print("[CSV] Reading bag into DataFrame...")
        df = rosbag_pandas.bag_to_dataframe(bag_path)
        print("[CSV] Writing CSV:", csv_path)
        df.to_csv(csv_path, index=False)
        print("[CSV] Done.")
        return csv_path

    def process_all(self):
        files = sorted(glob.glob(os.path.join(self.sample_folder, "*.bag")))
        prefixes = set(os.path.basename(f).split(".bag")[0].split("_")[0] for f in files)

        for prefix in prefixes:
            merged = self.merge_prefix(prefix)
            if merged:
                self.bag_to_csv(merged)
