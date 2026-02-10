# -*- coding: utf-8 -*-
from __future__ import print_function
import ConfigParser
import rosbag
import os
import sys
import glob
import re
import json
import numpy as np
from collections import defaultdict
from rosbag.bag import ROSBagUnindexedException


class BagToNumpyDataset(object):
    """
    Convert ROS bag files into structured numpy dataset:

        dataset/
            UXXX/
                path_YY/
                    config_key.npy
                    meta.json

    Each .npy file has shape:
        (N, 2 + D)

    Columns:
        0 → raw ROS timestamp (float)
        1 → relative timestamp (float)
        2+ → extracted field values
    """

    def __init__(self, config_path="config.ini"):
        self.config_path = config_path
        self.specs_normal = self._parse_topic_section(config_path, "TOPICS")
        self.specs_gait = self._parse_topic_section(config_path, "TOPICS GAIT")
        self.bag_folder_normal, self.bag_folder_gait = self._parse_data_paths(config_path)
        print("[INIT] Normal topic specs:", self.specs_normal)
        print("[INIT] Gait topic specs:", self.specs_gait)

    # --------------------------------------------------------
    # CONFIG PARSING
    # --------------------------------------------------------

    def _parse_topic_section(self, path, section):
        cfg = ConfigParser.ConfigParser()
        if not cfg.read(path):
            raise IOError("Config file not found: %s" % path)

        specs = {}
        if not cfg.has_section(section):
            print("[WARN] Section '%s' not found in config" % section)
            return specs
        for col, v in cfg.items(section):
            if "|" not in v:
                continue
            topic, field = v.split("|", 1)
            specs[col] = (topic.strip(), field.strip())
        return specs

    def _parse_data_paths(self, path):
        cfg = ConfigParser.ConfigParser()
        if not cfg.read(path):
            raise IOError("Config file not found: %s" % path)

        bag_normal = cfg.get("DATA", "path_to_bag") if cfg.has_option("DATA", "path_to_bag") else None
        bag_gait = cfg.get("DATA", "path_to_gait_bag") if cfg.has_option("DATA", "path_to_gait_bag") else None
        return bag_normal, bag_gait

    # --------------------------------------------------------
    # UTILITIES
    # --------------------------------------------------------

    def extract_field(self, msg, field_path):
        try:
            obj = msg
            for part in field_path.split("."):
                obj = getattr(obj, part)

            if hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
                vals = list(obj)
                if len(vals) == 0:
                    return None
                if len(vals) == 1:
                    return vals[0]
                return vals  # multiple values → separate columns
            return obj
        except Exception:
            return None

    def parse_user_path(self, filename):
        """
        Example filename:
        KATE_U003_14_session1.bag
        """
        match = re.search(r'U(\d+)_([0-9]+)_', filename)
        if match:
            return match.group(1), match.group(2)
        return None, None

    # --------------------------------------------------------
    # CORE PROCESSING
    # --------------------------------------------------------

    def process_bag(self, bag_path, output_root, mode="normal"):

        specs = self.specs_gait if mode == "gait" else self.specs_normal
        topics = set(tp for tp, _ in specs.values())

        base = os.path.splitext(os.path.basename(bag_path))[0]
        user, path = self.parse_user_path(base)

        if user is None:
            print("[SKIP] Could not parse user/path:", base)
            return

        print("[PROCESS][%s] User: %s  Path: %s" % (mode.upper(), user, path))

        # Storage per config key
        key_data = defaultdict(list)

        try:
            with rosbag.Bag(bag_path) as bag:

                # --------------------------------------------------
                # Determine global start time for entire bag
                # --------------------------------------------------
                start_time = None
                end_time = None

                for _, _, t in bag.read_messages():
                    ts = t.to_sec()
                    start_time = ts
                    break

                if start_time is None:
                    print("[WARN] Empty bag:", bag_path)
                    return

                # --------------------------------------------------
                # Extract relevant topics
                # --------------------------------------------------
                for topic, msg, t in bag.read_messages(topics=topics):

                    raw_ts = t.to_sec()
                    rel_time = raw_ts - start_time
                    end_time = raw_ts

                    # For each config key mapped to this topic
                    for key, (cfg_topic, field_path) in specs.items():

                        if cfg_topic != topic:
                            continue

                        value = self.extract_field(msg, field_path)

                        row = [raw_ts, rel_time]
                        if value is None:
                            row.append(np.nan)
                        elif isinstance(value, list):
                            row.extend([v if v is not None else np.nan for v in value])
                        else:
                            row.append(value)

                        key_data[key].append(row)

        except ROSBagUnindexedException:
            print("[ERROR] Unindexed bag:", bag_path)
            return
        except Exception as e:
            print("[ERROR] Failed:", bag_path, e)
            return

        if not key_data:
            print("[WARN] No data extracted:", bag_path)
            return

        # --------------------------------------------------------
        # SAVE STRUCTURE
        # --------------------------------------------------------

        user_folder = os.path.join(output_root, "U" + user)
        path_folder = os.path.join(user_folder, "path_" + path)

        if not os.path.exists(path_folder):
            os.makedirs(path_folder)

        for key, rows in key_data.items():

            if not rows:
                continue

            arr = np.array(rows, dtype=np.float64)

            out_file = os.path.join(path_folder, key + ".npy")
            np.save(out_file, arr)

        # Save metadata
        meta = {
            "user": user,
            "path": path,
            "duration": float(end_time - start_time) if end_time else 0.0,
            "bag_name": base,
            "start_bag_timestamp": float(start_time)
        }

        with open(os.path.join(path_folder, "meta.json"), "w") as f:
            json.dump(meta, f, indent=4)

    # --------------------------------------------------------
    # PROCESS ALL
    # --------------------------------------------------------

    def process_all(self, output_root="dataset", pattern="*.bag", mode="normal"):

        if mode == "normal":
            bag_folder = self.bag_folder_normal
        elif mode == "gait":
            bag_folder = self.bag_folder_gait

        bag_files = glob.glob(os.path.join(bag_folder, pattern))

        if not bag_files:
            raise IOError("No bag files found in: {}".format(bag_folder))

        # Filter by user ID range (U003 to U019)
        # def user_in_range(filename):
        #     match = re.search(r'U(\d+)', filename)
        #     if match:
        #         uid = int(match.group(1))
        #         return 20 <= uid <= 28
        #     return False

        # bag_files = [f for f in bag_files if user_in_range(os.path.basename(f))]

        print("[INFO] Mode: %s | Found %d bag files to process" % (mode.upper(), len(bag_files)))

        for bag_path in bag_files:
            self.process_bag(bag_path, output_root, mode=mode)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":

    config_path = "src/config.ini"
    output_root = "data/timeseries_numpy"

    processor = BagToNumpyDataset(config_path)

    processor.process_all(output_root, mode="normal")
    processor.process_all(output_root, mode="gait")
