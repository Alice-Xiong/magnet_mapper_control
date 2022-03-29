import numpy as np
import csv
import json
from mapper_base import Mapper

class Points_Generator(Mapper):

    def __init__(self):
        # Read configurations from 'config.json'
        self.config_filename = Mapper.config_filename
        self.config_changed = Mapper.config_changed
        self.config_dict = Mapper.config_dict

        # Load configurations
        self.path_filename = self.config_dict['path_filename']
        self.path_edges_filename = self.config_dict['path_edges_filename']
        self.shape = self.config_dict['shape']

        # Configurations specific to cylinder and rectangle
        if self.shape == "cylinder":
            self.radius = self.config_dict['radius']
            self.yz_spacing = self.config_dict['yz_spacing']
        elif self.shape == "rectangular":
            self.y_range = self.config_dict['y_range']
            self.y_spacing = self.config_dict['y_spacing']
            self.z_range = self.config_dict['z_range']
            self.z_spacing = self.config_dict['z_spacing']

        # Configurations common to both shapes
        self.x_range = self.config_dict['x_range']
        self.x_spacing = self.config_dict['x_spacing']
        self.x_offset = self.config_dict['x_offset']
        self.y_offset = self.config_dict['y_offset']
        self.z_offset = self.config_dict['z_offset']
        self.probe_stop_time_sec = self.config_dict['probe_stop_time_sec']
        self.rotation_angles = self.config_dict['rotation_points']


    def generate_edges(self): 
        if self.shape == "cylinder":
            # generate the points for edges
            self.points_edges = np.zeros([self.num_cols * 4, 4])

        elif (self.shape == "rectangular"):
            # generate the points for edges
            self.points_edges = np.zeros([int(self.num_cols_Y * 4 / self.num_angles), 4])

        # start path generation
        j = 0

        self.xmin = self.x_offset
        self.xmax = self.x_range + self.x_offset

        # 2D edges path at minimum x position (out of magnet)
        for i in range(int(len(self.points) / self.num_angles)):
            if  (i==0) or (self.points[i][1] != self.points[i-1][1]) or (i==len(self.points)-1) or (self.points[i][1] != self.points[i+1][1]):
                self.points_edges[j][0] = self.xmin
                self.points_edges[j][1] = self.points[i][1]
                self.points_edges[j][2] = self.points[i][2]
                j += 1

        # 2D edges path at maximum x position (into magnet)
        for i in range(int(len(self.points) / self.num_angles)):
            if  (i==0) or (self.points[i][1] != self.points[i-1][1]) or (i==len(self.points)-1) or (self.points[i][1] != self.points[i+1][1]):
                self.points_edges[j][0] = self.xmax
                self.points_edges[j][1] = self.points[i][1]
                self.points_edges[j][2] = self.points[i][2]
                j += 1

        
        # store them into a CSV file
        header = ['X', 'Y', 'Z', 'Rotation']
        with open(self.path_edges_filename, 'w', encoding='UTF8', newline='') as f:
            f.truncate()
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(self.points_edges)
            f.close()

        print('\n*************** Path for moving around edges generated ************\n')

        
    def generate(self):
        # Constants for order
        order_inc = True
        order_dec = False

        # Generate xy points in cylindrical coordinates
        if self.shape == "cylinder":
            # number of columns (= num of rows) under the given radius and spacing
            num_cols_half = int(self.radius/self.yz_spacing)
            self.num_cols = 2 * num_cols_half + 1

            # possible positions of each column
            pos_yz = np.arange(-self.yz_spacing * num_cols_half, self.yz_spacing * (num_cols_half + 1), self.yz_spacing)

            # Fill all possible y, z values
            points_yz = np.zeros([self.num_cols * self.num_cols, 2])

            # Initialize variables for pathing
            index = 0
            order = order_inc
            for i in range(self.num_cols):
                if order == order_inc:
                    for j in range(0, self.num_cols, 1):
                        y = pos_yz[i]
                        z = pos_yz[j]
                        # make sure points are within circle
                        if (z *  z+ y * y < self.radius * self.radius):
                            points_yz[index][0] = y
                            points_yz[index][1] = z
                            index += 1
                if order == order_dec:
                    for j in range(self.num_cols-1, -1, -1):
                        y = pos_yz[i]
                        z = pos_yz[j]
                        if (z * z + y * y < self.radius * self.radius):
                            points_yz[index][0]= y
                            points_yz[index][1] = z
                            index += 1

                # switch increasing/decreasing order for every pass
                order = not(order)

        # Generate xy points in rectangular coordinates
        elif self.shape == "rectangular":
            # number of columns (= num of rows) under the given radius and spacing
            num_cols_half_Y = int(self.y_range/self.y_spacing/2)
            num_cols_half_Z = int(self.z_range/self.z_spacing/2)
            num_cols_Y = int(self.y_range/self.y_spacing) + 1
            num_cols_Z = int(self.z_range/self.z_spacing) + 1
            self.num_cols_Y = num_cols_Y #save this for other function

            # possible positions of each column
            pos_Y = np.arange(-self.y_spacing * num_cols_half_Y, self.y_spacing * (num_cols_half_Y + 1), self.y_spacing)
            pos_Z = np.arange(-self.z_spacing * num_cols_half_Z, self.z_spacing * (num_cols_half_Z + 1), self.z_spacing)

            # Fill all possible y, z values
            points_yz = np.zeros([num_cols_Y * num_cols_Z, 2])

            # Initialize variables for pathing
            index = 0
            order = order_inc
            for i in range(num_cols_Y):
                if order == order_inc:
                    for j in range(0, num_cols_Z, 1):
                        points_yz[index][0] = pos_Y[i]
                        points_yz[index][1] = pos_Z[j]
                        index += 1
                if order == order_dec:
                    for j in range(num_cols_Z-1, -1, -1):
                        points_yz[index][0] = pos_Y[i]
                        points_yz[index][1] = pos_Z[j]
                        index += 1
                # switch increasing/decreasing order for every pass
                order = not(order)

        # trim all zeros and get valid point length
        points_yz_1D_trim = np.trim_zeros(points_yz.flatten(), trim = 'b')
        points_yz = np.reshape(points_yz_1D_trim, (-1, 2))
        num_points_yz = len(points_yz)

        # possible positions in x direction (going into magnet)
        num_x = int(self.x_range/self.x_spacing)
        pos_x = np.arange(0, self.x_spacing * num_x, self.x_spacing)

        # z direction and angular points
        self.num_angles = len(self.rotation_angles)
        self.points = np.zeros([num_points_yz * num_x * self.num_angles, 4])
        index = 0
        order = order_inc
        for angle in self.rotation_angles:
            for i in range(num_points_yz):
                if order == order_inc:
                    for j in range(0, num_x, 1):
                        self.points[index][0] = pos_x[j] + self.x_offset
                        self.points[index][1] = points_yz[i][0] + self.y_offset
                        self.points[index][2] = points_yz[i][1] + self.z_offset
                        self.points[index][3] = angle
                        index += 1
                if order == order_dec:
                    for j in range(num_x-1, -1, -1):
                        self.points[index][0] = pos_x[j] + self.x_offset
                        self.points[index][1] = points_yz[i][0] + self.y_offset
                        self.points[index][2] = points_yz[i][1] + self.z_offset
                        self.points[index][3] = angle
                        index += 1
                order = not(order)


    def estimate_time(self):
        # Prints the estimated time
        with open(self.path_filename, 'r', encoding='UTF8', newline='') as f:
            reader = csv.reader(f)

            unit = 'seconds'
            total_time = len(list(reader)) * (self.probe_stop_time_sec + 1)
            if total_time >= 60:
                total_time = total_time/60
                unit = 'minutes'

                if total_time >= 60:
                    total_time = total_time/60
                    unit = 'hours'

            print('The current mapping sequence will take approximately %d %s. \n' % (total_time, unit))

    '''
    Functions to be accessed from outside 
    '''
    def run(self):
        # Only run script if not using the same path as before, ie a change has been made to configs.
        if not self.config_changed:
            self.generate()
            # Write path to CSV file
            header = ['X', 'Y', 'Z', 'Rotation']
            with open(self.path_filename, 'w', encoding='UTF8', newline='') as f:
                f.truncate()
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(self.points)
                f.close()
        print('\n*************** Path generation completed. ***************\n')

        self.estimate_time()
            



