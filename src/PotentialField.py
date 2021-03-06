#!/usr/bin/env python

import rospy
from ackermann_msgs.msg import AckermannDriveStamped
from sensor_msgs.msg import LaserScan
import std_msgs
import math
import numpy as np


class altPotential:
    def __init__(self):
        self.node_name = "altPotential"
        rospy.Subscriber('racecar/laser/scan', LaserScan, self.scan_callback, queue_size=10)
        self.publisher = rospy.Publisher('/racecar/ackermann_cmd_mux/input/navigation', AckermannDriveStamped, queue_size=10)
        self.drive_msg = AckermannDriveStamped()

        #Global values
        self.a = 1.0 #these are both silly arbitrary values, we can empirically weight them after testing
        self.k = 1.0
        self.obstaclePointMatchThreshold = 6
        self.obstacleDistanceThreshold = 1

        self.publish()

    def scan_callback(self, msg):
        goal_dist_x = 0
        goal_dist_y = 0
        ranges = msg.ranges
        checkArr = []
        angArr = []
        x_dist_arr = []
        y_dist_arr = []
        for i in range(len(ranges)):
            if ranges[i] <= .3:
                check_arr[i] = ranges[i]
                ang_arr[i] = -2.356 + .00581*i
                x_dist_arr[i] = ranges[i] * math.sin(ang_arr[i])
                y_dist_arr[i] = ranges[i] * math.cos(ang_arr[i])
        magn_vec_arr = []
        for curr in range(len(x_dist_arr)):
            magn_vec_arr[curr] = x_dist_arr[curr]*x_dist_arr[curr] + y_dist_arr[curr]*y_dist_arr[curr]
        denom_net_arr = []
        for magn in range(len(magn_vec_arr)):
            denom_net_arr[magn] = magn_vec_arr[magn]*magn_vec_arr[magn]
        top_wek_range = msg.range_max
        ang_grav = 0.0
        for i in ranges:
            if i == top_wek_range:
                ang_grav = -2.356 + .00581*i
            grav_dist_x = top_wek_range * math.sin(ang_grav)
        grav_dist_y = top_wek_range * math.cos(ang_grav)
        #here, check around the car for array of close points under a certain value

        #gradient descent algorithm
        des_x = self.k*grav_dist_x #+ (a*grav_dist_x)/((obst_dist_x * obst_dist_x + obst_dist_y * obst_dist_y)*(obst_dist_x * obst_dist_x + obst_dist_y * obst_dist_y))
        des_y = self.k*grav_dist_y #+ (a*goal_dist_y)/((obst_dist_x * obst_dist_x + obst_dist_y * obst_dist_y) * (obst_dist_x * obst_dist_x + obst_dist_y * obst_dist_y))
        for q in range(len(denom_net_arr)):
            des_x = des_x + (self.a*grav_dist_x)/denom_net_arr[q]
            des_y = des_y + (self.a*grav_dist_y)/denom_net_arr[q]
            #publishable math
            vec_ang = math.atan2(des_y, des_x)
            vec_mag = math.sqrt(des_x*des_x + des_y * des_y)
            self.drive_msg = AckermannDriveStamped()
            self.drive_msg.drive.speed = vec_mag
            self.drive_msg.drive.steering_angle = vec_ang

    def publish(self):
        while not rospy.is_shutdown():
            self.publisher.publish(self.drive_msg)
            rospy.Rate(8).sleep()

if __name__ == "__main__":
    rospy.init_node("altPotential")
    e = altPotential()
    rospy.spin()
