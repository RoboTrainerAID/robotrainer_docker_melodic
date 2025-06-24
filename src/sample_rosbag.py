#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import rosbag
import rospy
import numpy as np
from collections import defaultdict

# Standard ROS-Typen
from std_msgs.msg import Float32, Float32MultiArray, Int32
from geometry_msgs.msg import TwistStamped, WrenchStamped, PoseArray
from sensor_msgs.msg import LaserScan
from visualization_msgs.msg import MarkerArray

class RosbagCompressor:
    """Compresses a ROS bag with configurable averaging, including deviation topic."""
    def __init__(self, input_path, output_folder="data/sample",
                 mean_per_second=True, bin_size=1, max_bins=None):
        self.in_path = input_path
        self.output_folder = output_folder
        self.mean_per_second = mean_per_second
        self.bin_size = bin_size
        self.max_bins = max_bins

        self.out_path = self._setup_output()
        print("[INIT] Input:", self.in_path)
        print("[INIT] Output:", self.out_path)

        # Topics to average (backend types)
        self.average_topics = {
            '/biosensors/polar_oh1/hrv': Float32MultiArray,
            '/biosensors/polar_oh1/ppg_ch0': Float32MultiArray,
            '/biosensors/polar_oh1/ppg_ch1': Float32MultiArray,
            '/biosensors/polar_oh1/ppg_ch2': Float32MultiArray,
            '/biosensors/polar_oh1/ppg_ch3': Float32MultiArray,
            '/biosensors/polar_oh1/ppi': Int32,
            '/biosensors/polar_oh1/hr': Float32,
            '/base/fts_adaptive_force_controller/debug/velocity_output': TwistStamped,
            '/base/output_data': WrenchStamped,
            '/robotrainer_deviation/robotrainer_deviation': None,  
            '/robotrainer_deviation/robotrainer_deviation_markers': MarkerArray,
            '/toe_detection/toe_positions': PoseArray,
        }

        # Topics to sample one per bin
        self.sample_topics = {
            '/base_laser_back/scan': LaserScan,
        }

        # Fields kept as is
        self.static_topics = {
            '/bag_duration': Float32,
        }

    def _setup_output(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print("[INIT] Created folder:", self.output_folder)
        base = os.path.basename(self.in_path)
        return os.path.join(self.output_folder, base)

    def compress(self):
        print("[COMPRESS] Opening input bag…")
        inbag = rosbag.Bag(self.in_path, 'r')
        print("[COMPRESS] Creating output bag…")
        outbag = rosbag.Bag(self.out_path, 'w')

        grouped_avg = {t: defaultdict(list) for t in self.average_topics}
        grouped_sample = {t: defaultdict(list) for t in self.sample_topics}
        msg_count = 0

        print("[COMPRESS] Iterating through messages…")
        for topic, msg, t in inbag.read_messages():
            msg_count += 1
            sec = int(t.to_sec() // self.bin_size) * self.bin_size

            if topic in self.average_topics:
                grouped_avg[topic][sec].append(msg)

            elif topic in self.sample_topics:
                grouped_sample[topic][sec].append(msg)

            elif topic in self.static_topics:
                outbag.write(topic, msg, t)

            # all others ignored

        print("[COMPRESS] Processed {} messages.".format(msg_count))

        # Writing averaged messages
        if self.mean_per_second:
            print("[COMPRESS] Writing averaged messages…")
            written_avg = 0
            for topic, bins in grouped_avg.items():
                secs = sorted(bins.keys())
                if self.max_bins and len(secs) > self.max_bins:
                    secs = secs[-self.max_bins:]
                for sec in secs:
                    msgs = bins[sec]
                    avg_msg = self._compute_average_generic(topic, msgs)
                    if avg_msg:
                        outbag.write(topic, avg_msg, rospy.Time(sec))
                        written_avg += 1
            print("[COMPRESS] Wrote {} averaged messages.".format(written_avg))

        # Writing sample messages
        print("[COMPRESS] Writing sample messages…")
        written_samp = 0
        for topic, bins in grouped_sample.items():
            secs = sorted(bins.keys())
            if self.max_bins and len(secs) > self.max_bins:
                secs = secs[-self.max_bins:]
            for sec in secs:
                msg = bins[sec][0]
                outbag.write(topic, msg, rospy.Time(sec))
                written_samp += 1
        print("[COMPRESS] Wrote {} sample messages.".format(written_samp))

        inbag.close()
        outbag.close()
        print("[COMPRESS] Complete:", self.out_path)

    def _compute_average_generic(self, topic, msgs):
        if not msgs:
            return None

        first = msgs[0]
        # Handle custom deviation topic by averaging front/left/right
        if topic == '/robotrainer_deviation/robotrainer_deviation':
            fronts = np.mean([m.front for m in msgs])
            lefts = np.mean([m.left for m in msgs])
            rights = np.mean([m.right for m in msgs])
            avg = type(first)()
            avg.front, avg.left, avg.right = fronts, lefts, rights
            return avg

        msg_type = self.average_topics[topic]
        # standard handling
        if msg_type == Float32MultiArray:
            data = np.mean([m.data for m in msgs], axis=0)
            return Float32MultiArray(data=data.tolist())
        if msg_type == Int32:
            return Int32(data=int(np.mean([m.data for m in msgs])))
        if msg_type == Float32:
            return Float32(data=float(np.mean([m.data for m in msgs])))
        if msg_type == TwistStamped:
            avg = TwistStamped()
            lin = np.mean([[m.twist.linear.x, m.twist.linear.y, m.twist.linear.z] for m in msgs], axis=0)
            ang = np.mean([[m.twist.angular.x, m.twist.angular.y, m.twist.angular.z] for m in msgs], axis=0)
            avg.twist.linear.x, avg.twist.linear.y, avg.twist.linear.z = lin
            avg.twist.angular.x, avg.twist.angular.y, avg.twist.angular.z = ang
            return avg
        if msg_type == WrenchStamped:
            avg = WrenchStamped()
            f = np.mean([[m.wrench.force.x, m.wrench.force.y, m.wrench.force.z] for m in msgs], axis=0)
            t_ = np.mean([[m.wrench.torque.x, m.wrench.torque.y, m.wrench.torque.z] for m in msgs], axis=0)
            avg.wrench.force.x, avg.wrench.force.y, avg.wrench.force.z = f
            avg.wrench.torque.x, avg.wrench.torque.y, avg.wrench.torque.z = t_
            return avg
        if msg_type in (PoseArray, MarkerArray):
            return msgs[-1]
        return None
