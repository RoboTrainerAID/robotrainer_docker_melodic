# -*- coding: utf-8 -*-
from __future__ import print_function
import os, glob
from rosbag_trimmer import RosbagTrimmer
from bag_processor import BagProcessor

def main():
    bag_folder = "data"   
    bag_files = glob.glob(os.path.join(bag_folder, "*.bag"))

    # if not bag_files:
    #     print("[MAIN] No bag files found in:", bag_folder)
    #     return

    # print("[MAIN] Bag files found:", bag_files)

    # for bag_path in bag_files:
    #     bag_name = os.path.basename(bag_path)
    #     print("\n[MAIN] >>> Start Trim for:", bag_name)

    #     trimmer = RosbagTrimmer(
    #         bag_folder=bag_folder,
    #         bag_name=bag_name,
    #         force_topic="/base/fts_adaptive_force_controller/debug/force_input_raw",
    #         force_field="wrench.force.x",
    #         reference_topic="/robotrainer_deviation/current_path_index"
    #     )

    #     ok = trimmer.trim()
    #     if ok:
    #         print("[MAIN] Done:", trimmer.output_path)
    #     else:
    #         print("[MAIN] Trim failed for:", bag_name)

    print("[MAIN] Starting BagProcessor...")
    processor = BagProcessor("src/config.ini")
    processor.process_all_bags(folder="data/cut")
    print("[MAIN] Done processing all bags.")


if __name__ == "__main__":
    main()
