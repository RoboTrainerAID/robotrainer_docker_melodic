#!/bin/bash

INPUT_DIR="/home/docker/ros_ws/robotrainer/KATE_AA"
OUTPUT_DIR="/home/docker/ros_ws/robotrainer/KATE_AA_reduced"

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory '$INPUT_DIR' does not exist."
    exit 1
fi

# Create the output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Enable nullglob to handle the case where no bag files exist
shopt -s nullglob

# Iterate through all .bag files in the input directory
for bag_file in "$INPUT_DIR"/*.bag; do
    # Extract just the filename (e.g., "drive1.bag")
    filename=$(basename "$bag_file")
    
    # Define the full output path
    output_path="$OUTPUT_DIR/$filename"
    
    # Run rosbag filter
    # Logic: Keep message ONLY if 'camera' is NOT in topic AND 'scan' is NOT in topic
    rosbag filter "$bag_file" "$output_path" "'camera' not in topic and 'scan' not in topic"

    if [ $? -eq 0 ]; then
        echo "Saved to: $output_path"
    else
        echo "Error filtering $filename"
    fi
done

echo "------------------------------------------------"
echo "Batch processing complete."