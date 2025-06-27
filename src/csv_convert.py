#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import glob
import rosbag
import pandas as pd
import ast

class RosbagToCSVConverter:
    def __init__(self, sample_folder="data/sample", output_folder="data/converted", final_output="data/merged/final_features.csv"):
        self.sample_folder = sample_folder
        self.output_folder = output_folder
        self.final_output = final_output

        if not os.path.isdir(self.sample_folder):
            raise IOError("Sample folder not found: {}".format(self.sample_folder))
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print("[INIT] Created output folder:", self.output_folder)

        final_dir = os.path.dirname(self.final_output)
        if not os.path.exists(final_dir):
            os.makedirs(final_dir)

        # Liste aller relevanten Felder
        self.columns = [
            "ang_x", "ang_y", "ang_z",
            "angle_increment", "angle_max", "angle_min",
            "bag_duration",
            "force_x", "force_y", "force_z",
            "front", "hr", "hrv", "left",
            "lin_x", "lin_y", "lin_z",
            "ppg_ch0", "ppg_ch1", "ppg_ch2", "ppg_ch3",
            "ppi",
            "range_max", "range_min", "right",
            "scan_time", "time_increment",
            "torque_x", "torque_y", "torque_z"
        ]

    def bag_to_csv(self, bag_path):
        records = []
        bag = rosbag.Bag(bag_path, 'r')

        for topic, msg, t in bag.read_messages():
            rec = {}

            if topic == '/bag_duration' and hasattr(msg, 'data'):
                rec['bag_duration'] = msg.data

            elif topic == '/base/fts_adaptive_force_controller/debug/velocity_output':
                v = msg.twist.linear
                a = msg.twist.angular
                rec.update({
                    'lin_x': v.x, 'lin_y': v.y, 'lin_z': v.z,
                    'ang_x': a.x, 'ang_y': a.y, 'ang_z': a.z
                })

            elif topic == '/base/output_data':
                f = msg.wrench.force
                t2 = msg.wrench.torque
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
                    try:
                        rec[name] = list(d) if hasattr(d, '__iter__') and not isinstance(d, str) else [d]
                    except:
                        rec[name] = [d]

            elif topic == '/robotrainer_deviation/robotrainer_deviation':
                rec['front'] = getattr(msg, 'front', None)
                rec['left']  = getattr(msg, 'left', None)
                rec['right'] = getattr(msg, 'right', None)

            else:
                continue

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

    def extract_features_from_csv(self, csv_path):
        df = pd.read_csv(csv_path)
        flattened = []

        for col in self.columns:
            if col not in df.columns:
                continue

            for val in df[col].dropna():
                val = str(val).strip()
                if val.startswith("[") and val.endswith("]"):
                    try:
                        parsed = ast.literal_eval(val)
                        flattened.extend(parsed)
                    except:
                        continue
                else:
                    try:
                        flattened.append(float(val))
                    except:
                        continue
        return flattened

    def get_test_number(self, file_name):
        try:
            parts = os.path.basename(file_name).split("_")
            return int(parts[1])  # z. B. "1_7_..." → 7
        except:
            return -1

    def process_all(self):
        files = sorted(glob.glob(os.path.join(self.sample_folder, "*.bag")))
        if not files:
            print("[PROCESS] No bag files in '{}'.".format(self.sample_folder))
            return

        subject_vectors = {}  # Dictionary: {subject_id: [feature_vectors]}

        for bag_file in files:
            print("[PROCESS] Converting:", bag_file)
            csv_path = self.bag_to_csv(bag_file)
            if not csv_path:
                continue

            features = self.extract_features_from_csv(csv_path)

            # Stelle sicher, dass Feature-Vektor z. B. Länge 47 hat (anpassen je nach Bedarf)
            target_len = 47
            if len(features) < target_len:
                features.extend([0.0] * (target_len - len(features)))
            else:
                features = features[:target_len]

            test_number = self.get_test_number(bag_file)
            features.insert(0, test_number)  # Testnummer vorn

            # Proband ermitteln (erste Zahl im Dateinamen)
            try:
                subject_id = int(os.path.basename(bag_file).split("_")[0])
            except:
                subject_id = 0  # fallback

            if subject_id not in subject_vectors:
                subject_vectors[subject_id] = []

            subject_vectors[subject_id].append(features)

        # Schreibe für jeden Probanden eine Datei
        for subject_id, vectors in subject_vectors.items():
            out_path = os.path.join(os.path.dirname(self.final_output),
                                    "final_features_subject_{}.csv".format(subject_id))
            df_out = pd.DataFrame(vectors)
            df_out.to_csv(out_path, index=False, header=False)
            print("[FINAL] Features gespeichert für Subjekt {} unter: {}".format(subject_id, out_path))




