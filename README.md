# robotrainer_docker_melodic

## How to use
1. Place your `.bag` files in the folder specified in `config.ini`:
   - Standard bags: `path_to_bag`
   - Gait bags: `path_to_gait_bag` 
2. Build the docker image with `./build_docker.sh`
3. Start the container with `./start_docker.sh`
   - Executing `./start_docker.sh` again in a new terminal will connect to the already running container.
4. In the Docker, start the data preprocessing:
   ```bash
   python src/main.py
   ```
## Processing Pipeline
The script `main.py` performs the following steps:
1. **BagProcessor** 
- Reads all trimmed bag files from `path_to_bag`.
- Uses `src/config.ini` to know which topics/fields to extract.
- Extracted signals are stored in a **tabular format (CSV)**.
- Additional metadata (e.g., user ID, path ID, total duration) is added to each row.
- All processed bags are concatenated into one dataset file:
   ```swift
   data/KATE_AA_dataset.csv
   ```

2. **GaitProcessor**
- Reads `.bag` files from `path_to_gait_bag`.
- Uses the `[TOPICS GAIT]` section in `config.ini`.
- Exports the extracted signals to:
   ```swift
   data/KATE_AA_dataset_gait.csv
   ```

3. **CSVMerger**
- Merges `KATE_AA_dataset.csv` and `KATE_AA_dataset_gait.csv`.
- Joins on (`user`, `path`, `time`) with a tolerance (default: 0.05s).
- The merged dataset is saved as:
   ```swift
   data/KATE_AA_merged.csv
   ```

4. **CsvTrimmer**
- Trims the data for each (user, path) pair:
   - Start: first occurrence where `force_input_raw_x != 0`.
   - Then: whenever there is a change in the reference topics (`path_index_front`, `path_index_left`, `path_index_right`).
- Saves the trimmed CSV to:
   ```swift
   data/KATE_AA_trimmed.csv
   ```

## Configuration (`config.ini`)
### **[DATA]**
Set the paths for the bag data:
```ini
[DATA]
path_to_bag = robotrainer/KATE_AA
path_to_gait_bag = robotrainer/gait
```
### **[TOPICS]**  
Each entry defines a column in the output CSV.  
Format: 
```ini
column_name = /ros/topic/name|field.subfield
```
Examples:  
- `robot_pose_x = /mobile_robot_pose|pose.x` → extracts the robot’s pose in x-direction.

- `heart_rate = /biosensors/polar_oh1/hr|data` → extracts the heart rate from Polar OH1 sensor.

The signals listed in `[TOPICS]` include, among others:
- Forces & torques (`force_input_raw_*`, `torque_input_*`, `output_data_*`)
- Velocity (`velocity_output_*`)
- Virtual forces & velocities (`virtual_force_*`)
- Robot pose (`robot_pose_x/y/theta`)
- Deviation & path indices (`path_index_*`, `robotrainer_deviation_*`)
- Biosensor data (heart rate, HRV, PPG, PPI)

### **[TOPICS GAIT]**
Each entry defines a column in the output CSV.  
Format: 
```ini
column_name = /ros/topic/name|field.subfield
```
Examples:
- `cadence_avg = /gait/cadence/avg|data` → average cadence.
- `left_step_length = /gait/left/raw/step_length|data` → left step length.
- `right_stride_duration_avg = /gait/right/stride_duration/avg|data` → average right stride duration.

The signals listed in `[TOPICS GAIT]` include, among others:
- Step and gait parameters for left and right legs (step_length, stride_duration, stance_time, swing_time)
- Step and gait counters (num_steps, num_strides)
- Average values (e.g., *_avg)
- Speed (speed_avg)

### Example (excerpt from `config.ini`)

```ini
[TOPICS]
force_input_raw_x = /base/fts_adaptive_force_controller/debug/force_input_raw|wrench.force.x
force_input_raw_y = /base/fts_adaptive_force_controller/debug/force_input_raw|wrench.force.y
robot_pose_x = /mobile_robot_pose|pose.x
robot_pose_y = /mobile_robot_pose|pose.y
heart_rate = /biosensors/polar_oh1/hr|data

[TOPICS GAIT]
cadence_avg = /gait/cadence/avg|data
left_num_steps = /gait/left/num_steps|data
left_num_strides = /gait/left/num_strides|data

```

## Output
- **Standard CSV**: `data/KATE_AA_dataset.csv`
- **Gait CSV**: `data/KATE_AA_dataset_gait.csv`
- **Merged CSV**: `data/KATE_AA_merged.csv`
- **Trimmed CSV (Final dataset)**: `data/KATE_AA_trimmed.csv`
