# -*- coding: utf-8 -*-
from __future__ import print_function
import os, glob
from bag_processor import BagProcessor
from gait_processor import GaitProcessor
from csv_merger import CSVMerger
from csv_trimmer import CsvTrimmer
import ConfigParser

def main():
    print("[MAIN] Starting BagProcessor...")
    config = ConfigParser.ConfigParser()
    config.read("src/config.ini")
    bag_folder = config.get("DATA", "path_to_bag")
    bag_folder_gait = config.get("DATA", "path_to_gait_bag")

    processor = BagProcessor("src/config.ini")
    processor.process_all_bags(folder=bag_folder)
    print("[MAIN] Done processing all bags.")

    processor_gait = GaitProcessor("src/config.ini")
    processor_gait.process_all_bags(folder=bag_folder_gait)
    print("[MAIN] Done processing all gait bags.")

    # merger = CSVMerger(
    #     base_csv="data/KATE_AA_dataset.csv",
    #     gait_csv="data/KATE_AA_dataset_gait.csv",
    #     output_csv="data/KATE_AA_merged.csv",
    #     tolerance=0.05
    # )
    # merger.merge()

    # trimmer = CsvTrimmer(
    #     csv_path=output_csv,
    #     force_col="force_input_raw_x",
    #     ref_cols=("path_index_front", "path_index_left", "path_index_right"),
    #     out_folder="data"
    # )
    # trimmer.process("KATE_AA_trimmed.csv")


if __name__ == "__main__":
    main()


    
