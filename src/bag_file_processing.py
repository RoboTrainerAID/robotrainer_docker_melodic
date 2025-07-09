from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.msg import get_types_from_msg

from utils import BagReader, DataFrameProcessing

ROBOTRAINER_DEVIATION_PATHINDEX_MSG = """
int16 front
int16 left
int16 right
"""
ROBOTRAINER_DEVIATION_ROBOTRAINERUSERDEVIATION_MSG = """
float64 front
float64 left
float64 right
"""
IPR_HELPERS_POSE2DSTAMPED_MSG = """
std_msgs/Header header
geometry_msgs/Pose2D pose
"""

# Create a typestore and register custom mesages
typestore = get_typestore(Stores.ROS1_NOETIC)
typestore.register(get_types_from_msg(
    ROBOTRAINER_DEVIATION_PATHINDEX_MSG,
    'robotrainer_deviation/msg/PathIndex'
))
typestore.register(get_types_from_msg(
    ROBOTRAINER_DEVIATION_ROBOTRAINERUSERDEVIATION_MSG,
    'robotrainer_deviation/msg/RobotrainerUserDeviation'
))
typestore.register(get_types_from_msg(
    IPR_HELPERS_POSE2DSTAMPED_MSG,
    'ipr_helpers/msg/Pose2DStamped'
))

# Read selected topics from bag file in pandas DataFrame
selected_topics = [
    '/base/output_data',
    '/base/virtual_forces/modalities_debug/resulting_force',
    '/base/virtual_forces/modalities_debug/status',
    '/robotrainer_deviation/robotrainer_deviation',
    '/biosensors/polar_oh1/hr',
]
bagfile_path = r"..\data\green_line_80_2_2025-05-29-20-26-43.bag"
bag_reader = BagReader(typestore=typestore, selected_topics=selected_topics)
bag_data_df = bag_reader.read_bag_file(bagfile_path)

df_processing = DataFrameProcessing(bag_data_df)
bag_data_df_virtual_force = df_processing.create_virtual_force_df()
virtual_force_df_processing = DataFrameProcessing(bag_data_df_virtual_force)
mean_values = virtual_force_df_processing.mean_values()
print('Mean values for each topic in virtual force area:')
for key in mean_values:
    print(f'{key}: {mean_values[key]}')
