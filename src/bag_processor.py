# -*- coding: utf-8 -*-
from __future__ import print_function
import ConfigParser
import rosbag
import pandas as pd
import os, glob, re


class BagProcessor:
    """Process ROS bags: extract topics, downsample, and save CSV."""

    def __init__(self, config_path="src/config.ini"):
        self.config_path = config_path
        self.bin_size, self.specs = self.parse_config(config_path)
        print("[INIT] Downsample:", self.bin_size)
        print("[INIT] Columns:", self.specs)

    def parse_config(self, path):
        cfg = ConfigParser.ConfigParser()
        if not cfg.read(path):
            raise IOError("Config file not found: %s" % path)

        bin_size = int(cfg.get("SETTINGS", "bin_size"))
        specs = {}
        for col, v in cfg.items("TOPICS"):
            if "|" not in v:
                raise ValueError("Topic entry must contain 'topic|field': %s" % v)
            topic, field = v.split("|", 1)
            specs[col] = (topic.strip(), field.strip())
        return bin_size, specs

    def extract_field(self, msg, field_path):
        """Extracts nested fields from ROS message."""
        try:
            obj = msg
            for part in field_path.split("."):
                obj = getattr(obj, part)
            if isinstance(obj, (list, tuple)):
                return obj[0] if obj else ""
            return obj
        except Exception:
            return ""

    def process_bag(self, bag_path):
        """Read bag, extract topics, and save all messages without downsampling."""
        rows = []
        last_values = {col: "" for col in self.specs.keys()}  

        with rosbag.Bag(bag_path) as bag:
            start_time = None
            end_time = None

            for topic, msg, t in bag.read_messages(topics=set(tp for tp, _ in self.specs.values())):
                ts = t.to_sec()
                if start_time is None:
                    start_time = ts
                end_time = ts
                rel_time = ts - start_time

                updated = False
                for col, (tp, field) in self.specs.items():
                    if tp == topic:
                        last_values[col] = self.extract_field(msg, field)
                        updated = True

                if updated:
                    row = {"time": rel_time}
                    row.update(last_values)  
                    rows.append(row)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df["total_duration"] = end_time - start_time
        return df

    def parse_user_path(self, filename):
        match = re.search(r'U(\d+)_([0-9]+)_', filename)
        if match:
            return match.group(1), match.group(2)
        else:
            return "", ""

    def process_all_bags(self, folder="data", pattern="KATE*.bag"):
        bag_files = glob.glob(os.path.join(folder, pattern))
        if not bag_files:
            raise IOError("No bag files found in folder: {}".format(folder))

        all_dfs = []

        for bag_path in bag_files:
            base = os.path.splitext(os.path.basename(bag_path))[0]
            user, path = self.parse_user_path(base)
            print("[PROCESS] Processing bag:", bag_path)

            df = self.process_bag(bag_path)

            cols = ["time"] + list(self.specs.keys())
            for col in cols:
                if col not in df.columns:
                    df[col] = ""

            df["user"] = user
            df["path"] = path
            df = df[["time"] + list(self.specs.keys()) + ["user", "path", "total_duration"]]
            all_dfs.append(df)

        df_all = pd.concat(all_dfs, ignore_index=True)
        out_csv = os.path.join(folder, "KATE_AA_dataset.csv".format(self.bin_size))
        df_all.to_csv(out_csv, index=False)
        print("[PROCESS] All bags saved to CSV:", out_csv)
        return out_csv
