# -*- coding: utf-8 -*-
from __future__ import print_function
import os, glob
from rosbag_trimmer import RosbagTrimmer
from bag_processor import BagProcessor
from gait_processor import GaitProcessor
from csv_merger import CsvMerger
from csv_trimmer import CsvTrimmer
from configparser import ConfigParser

def main():
    print("[MAIN] Starting BagProcessor...")
    config = ConfigParser()
    config.read("src/config.ini")
    bag_folder = config.get("DATA", "path_to_bag")
    bag_folder_gait = config.get("DATA", "path_to_bag_gait")

    processor = BagProcessor("src/config.ini")
    processor.process_all_bags(folder=bag_folder)
    print("[MAIN] Done processing all bags.")

    processor_gait = GaitProcessor("src/config.ini")
    processor_gait.process_all_bags(folder=bag_folder_gait)
    print("[MAIN] Done processing all gait bags.")

    merger = CsvMerger(folder="data", pattern="*.csv")
    merger.process("KATE_AA_merged.csv")

    trimmer = CsvTrimmer(
    csv_path="data/KATE_AA_merged.csv",
    force_col="force_input_raw_x",
    ref_cols=("path_index_front", "path_index_left", "path_index_right")
    )
    trimmer.process("KATE_AA_trimmed.csv")


if __name__ == "__main__":
    main()
