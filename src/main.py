#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os

from cut_rosbag import RosbagTrimmer
from sample_rosbag import RosbagCompressor
from csv_convert import RosbagMerger
from csv_1 import RosbagToCSVConverter

def main():
    bag_folder = "data"
    cut_folder = os.path.join(bag_folder, "cut")
    sample_output = "data/sample"

    # Check if CUT folder has already been populated
    cut_files = []
    if os.path.isdir(cut_folder):
        cut_files = [
            f for f in os.listdir(cut_folder)
            if f.endswith(".bag") and os.path.isfile(os.path.join(cut_folder, f))
        ]

    if cut_files:
        print("[MAIN] Found {} .bag files in 'data/Cut' – skipping trimming.".format(len(cut_files)))
    else:
        print("[MAIN] 'data/Cut' is empty. Will run trimming step.")

    # Decide which folder to read from
    bag_files = cut_files if cut_files else [
        f for f in os.listdir(bag_folder)
        if f.endswith(".bag") and os.path.isfile(os.path.join(bag_folder, f))
    ]

    if not bag_files:
        print("[MAIN] No .bag files to process.")
        return

    print("[MAIN] Processing {} file(s).".format(len(bag_files)))

    for bag_name in sorted(bag_files):
        print("\n[MAIN] === File: {} ===".format(bag_name))

        # STEP 1: Trimming (only if cut folder was initially empty)
        if not cut_files:
            trimmer = RosbagTrimmer(bag_folder, bag_name)
            success = trimmer.trim()
            if success:
                print("[MAIN] Trimming done for:", bag_name)
            else:
                print("[MAIN] Trimming skipped or failed for:", bag_name)
        else:
            print("[MAIN] Skipping trimming (Cut folder already populated).")

        # STEP 2: Sampling
        trimmed_path = os.path.join(cut_folder, bag_name)
        if not os.path.isfile(trimmed_path):
            print("[MAIN][WARN] No trimmed file found at '{}'. Skipping sampling.".format(trimmed_path))
            continue

        sampler = RosbagCompressor(
            input_path=trimmed_path,
            output_folder=sample_output,
            mean_per_second=True,
            bin_size= 1,
            max_bins= 1
        )
        sampler.compress()
        print("[MAIN] Sampling done for:", bag_name)

    # merger = RosbagMerger(
    #     sample_folder="data/sample",
    #     output_folder="data/merged"
    # )
    merger = RosbagToCSVConverter(
        sample_folder="data/sample",
        output_folder="data/merged"
    )
    merger.process_all()
    print("Merge and CSV conversion complete.")

    print("\n[MAIN] Pipeline finished – samples saved in:", sample_output)

if __name__ == "__main__":
    main()
