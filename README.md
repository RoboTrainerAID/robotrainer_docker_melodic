# robotrainer_docker_melodic

## How to use
1. Put .bag files into the `data/` folder
2. The bag files are mounted into `/home/docker/ros_ws/data/` 
3. Build the docker image with `./build_docker.sh`
4. Start the container with `./start_docker.sh`
   - Executing `./start_docker.sh` again in a new terminal will connect to the already running container.
5. In the Docker, start the data preprocessing:
   ```bash
   python src/main.py
   ```
## Data Preprocessing
The script `main.py` performs two steps::
1. **RosbagTrimmer**
- Reads each `.bag` file in the `data/`.
- Finds the relevant start time:
   - when the force signal (`/base/fts_adaptive_force_controller/debug/force_input_raw`, field `wrench.force.x`) becomes non-zero, **and**
   - when the path index (`/robotrainer_deviation/current_path_index`) changes.
- Creates a new, trimmed bag file containing only the actual experiment phase.
- Output is written to `data/cut/`.

2. **BagProcessor** 
- Reads all trimmed bag files from `data/cut/`.
- Uses `src/config.ini` to know which topics/fields to extract.
- Downsamples the data to a fixed frequency (`bin_size`), specified in the config.
- Extracted signals are stored in a **tabular format (CSV)**.
- Additional metadata (e.g., user ID, path ID, total duration) is added to each row.
- All processed bags are concatenated into one dataset file:
preprocessing:
   ```swift
   data/cut/KATE_AA_dataset_<bin_size>Hz.csv
   ```

## Configuration (`config.ini`)
The `BagProcessor` uses a configuration file (`src/config.ini`) to know **which topics and message fields** to extract from the ROS bags and how to downsample them.

### Sections
- **[SETTINGS]**
   - `bin_size`: Target sampling frequency in Hz (e.g. `10` → data is downsampled to 10 Hz).
   - `max_bins`: Optional limit for the number of bins (can be `None`).
- **[TOPICS]**  
   Each entry defines a column in the output CSV.  
   Format: 
   ```ini
   column_name = /ros/topic/name|field.subfield
   ```
   Examples:  
   - `robot_pose_x = /mobile_robot_pose|pose.x` → extracts the robot’s pose in x-direction.

   - `heart_rate = /biosensors/polar_oh1/hr|data` → extracts the heart rate from Polar OH1 sensor.

### Example (excerpt from `config.ini`)

```ini
[SETTINGS]
bin_size = 10
max_bins = None

[TOPICS]
force_input_raw_x = /base/fts_adaptive_force_controller/debug/force_input_raw|wrench.force.x
force_input_raw_y = /base/fts_adaptive_force_controller/debug/force_input_raw|wrench.force.y
robot_pose_x = /mobile_robot_pose|pose.x
robot_pose_y = /mobile_robot_pose|pose.y
heart_rate = /biosensors/polar_oh1/hr|data
```

## Output
- **Trimmed Ros bags** → `data/cut/*.bag`
- **Final dataset (CSV)** → `data/cut/KATE_AA_dataset_<bin_size>Hz.csv`
