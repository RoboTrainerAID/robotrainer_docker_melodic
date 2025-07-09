
import numpy as np
import pandas as pd
from rosbags.rosbag1 import Reader


class MessageReader:

    def __init__(self):

        self.readers = {
            'geometry_msgs/msg/WrenchStamped': self.read_wrench_stamped,
            'geometry_msgs/msg/Vector3': self.read_vector3,
            'robotrainer_deviation/msg/RobotrainerUserDeviation': self.read_robotrainer_deviation,
            'std_msgs/msg/String': self.read_data,
            'std_msgs/msg/Int32': self.read_data,
        }

    def read_wrench_stamped(self, topic, msg):

        record = {
            'topic': topic,
            'wrench_force_x': msg.wrench.force.x,
            'wrench_force_y': msg.wrench.force.y,
            'wrench_force_z': msg.wrench.force.z,
            'wrench_torque_x': msg.wrench.torque.x,
            'wrench_torque_y': msg.wrench.torque.y,
            'wrench_torque_z': msg.wrench.torque.z,
        }
        return record

    def read_vector3(self, topic, msg):

        record = {
                'topic': topic,
                'x': msg.x,
                'y': msg.y,
                'z': msg.z,
            }
        return record

    def read_robotrainer_deviation(self, topic, msg):

        record = {
                'topic': topic,
                'front': msg.front,
                'left': msg.left,
                'right': msg.right,
            }
        return record

    def read_data(self, topic, msg):

        key = topic.split("/")[-1]
        record = {
                'topic': topic,
                key: msg.data,
            }
        return record

    def read_message(self, msgtype, topic, msg):

        try:
            record = self.readers[msgtype](topic, msg)
        except KeyError:
            print(f"Cannot read the message of type {msgtype}. This message type has not yet been implemented.")
            record = {}
        except Exception as e:
            print(f"Cannot read the message of type {msgtype}. The error is {e}")
            record = {}
        return record


class DataFrameProcessing:

    def __init__(self, df):
        self.df = df
        try:
            self.status_df = self.df[self.df['status'].notna()].copy()
        except:
            pass

    def create_mean_df(self):
        try:
            mean_df = self.df.drop(columns=['status'])
        except:
            mean_df = self.df.copy()
        mean_df['timestamp'] = mean_df['timestamp'] // 1_000_000_000
        mean_df = mean_df.groupby(['topic', 'timestamp']).mean()
        mean_df.reset_index(inplace=True)
        mean_df['timestamp'] = (mean_df['timestamp'] + 0.5) * 1_000_000_000
        return mean_df

    def create_median_df(self):
        try:
            median_df = self.df.drop(columns=['status'])
        except:
            median_df = self.df.copy()
        median_df['timestamp'] = median_df['timestamp'] // 1_000_000_000
        median_df = median_df.groupby(['topic', 'timestamp']).median()
        median_df.reset_index(inplace=True)
        median_df['timestamp'] = (median_df['timestamp'] + 0.5) * 1_000_000_000
        return median_df

    def create_virtual_force_df(self):
        start_index = self.df.apply(pd.Series.first_valid_index)['x']
        end_index = self.df.apply(pd.Series.last_valid_index)['x']
        force_started = self.df['timestamp'][start_index]
        force_stopped = self.df['timestamp'][end_index]
        virtual_force_df = self.df.drop(self.df.loc[(self.df['timestamp']<force_started) | (self.df['timestamp']>force_stopped)].index)
        return virtual_force_df

    def create_df_without_virtual_force(self):
        start_index = self.df.apply(pd.Series.first_valid_index)['x']
        force_started = self.df['timestamp'][start_index]
        df_without_virtual_force = self.df.drop(self.df.loc[(self.df['timestamp']>=force_started)].index)
        return df_without_virtual_force

    def mean_values(self):
        mean_values = {}
        columns = self.df.columns
        for key in columns:
            try:
                mean_values[key] = self.df[key].mean()
            except:
                continue
        return mean_values

    def median_values(self):
        median_values = {}
        columns = self.df.columns
        for key in columns:
            try:
                median_values[key] = self.df[key].median()
            except:
                continue
        return median_values
    

class BagReader:

    def __init__(self, selected_topics, typestore):
        self.selected_topics = selected_topics
        self.message_reader = MessageReader()
        self.typestore = typestore

    def read_bag_file(self, bag_file_path):
        bag_data = []
        with Reader(bag_file_path) as reader:
            for connection, timestamp, rawdata in reader.messages():
                if connection.topic in self.selected_topics:
                    msg = self.typestore.deserialize_ros1(rawdata, connection.msgtype)
                    record = self.message_reader.read_message(connection.msgtype, connection.topic, msg)
                    record['timestamp'] = timestamp
                    bag_data.append(record)
        bag_data_df = pd.DataFrame(bag_data)
        try:
            bag_data_df['x'] = np.where(bag_data_df['topic'] == '/base/virtual_forces/modalities_debug/resulting_force', bag_data_df['x']*100, bag_data_df['x'])
            bag_data_df['y'] = np.where(bag_data_df['topic'] == '/base/virtual_forces/modalities_debug/resulting_force', bag_data_df['y']*100, bag_data_df['y'])
            bag_data_df['z'] = np.where(bag_data_df['topic'] == '/base/virtual_forces/modalities_debug/resulting_force', bag_data_df['z']*100, bag_data_df['z'])
            bag_data_df['resulting_force'] = np.nan
            bag_data_df['resulting_force'] = np.where(
                bag_data_df['topic'] == '/base/virtual_forces/modalities_debug/resulting_force', 
                np.sqrt(bag_data_df['x'] ** 2 + bag_data_df['y'] ** 2), 
                np.nan
            )
        except:
            pass
        try:
            bag_data_df['wrench_force'] = np.nan
            bag_data_df['wrench_force'] =  np.where(
                bag_data_df['topic'] == '/base/output_data', 
                np.sqrt(bag_data_df['wrench_force_x'] ** 2 + bag_data_df['wrench_force_y'] ** 2), 
                np.nan
            )
        except:
            pass

        return bag_data_df
