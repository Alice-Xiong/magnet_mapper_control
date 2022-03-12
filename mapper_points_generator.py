import numpy as np
import csv
import json
from mapper_base import Mapper

class Points_Generator(Mapper):

    def __init__(self):
        super().__init__()
        # Read configurations from 'config.json'
        self.config_filename = Mapper.config_filename
        self.csv_filename = Mapper.csv_filename
        self.config_changed = Mapper.config_changed
        self.config_dict = Mapper.config_dict

        if self.config_changed:
            with open(self.config_filename, 'r') as json_file:
                self.json_load = json.load(json_file)
        
    def generate(self):
        # Load configurations
        self.radius = self.config_dict['radius']
        self.xy_spacing = self.config_dict['xy_spacing']
        self.x_offset = self.config_dict['x_offset']
        self.y_offset = self.config_dict['y_offset']
        self.depth = self.config_dict['depth']
        self.z_spacing = self.config_dict['z_spacing']
        self.z_offset = self.config_dict['z_offset']

        # number of columns (= num of rows) under the given radius and spacing
        num_cols_half = int(self.radius/self.xy_spacing)
        num_cols = 2 * num_cols_half + 1

        # possible positions of each column
        pos_xy = np.arange(-self.xy_spacing * num_cols_half, self.xy_spacing * (num_cols_half + 1), self.xy_spacing)

        # Fill all possible x, y values
        points_xy = np.zeros([num_cols * num_cols, 2])
        index = 0
        # Constants for order
        order_inc = True
        order_dec = False
        order = order_inc
        for i in range(num_cols):
            if order == order_inc:
                for j in range(0, num_cols, 1):
                    x = pos_xy[i]
                    y = pos_xy[j]
                    # make sure points are within circle
                    if (x * x + y * y < self.radius * self.radius):
                        points_xy[index][0] = x
                        points_xy[index][1] = y
                        index += 1
            if order == order_dec:
                for j in range(num_cols-1, -1, -1):
                    x = pos_xy[i]
                    y = pos_xy[j]
                    if (x * x + y * y < self.radius * self.radius):
                        points_xy[index][0]= x
                        points_xy[index][1] = y
                        index += 1
            # switch increasing/decreasing order for every pass
            order = not(order)

        # trim all zeros and get valid point length
        points_xy_1D_trim = np.trim_zeros(points_xy.flatten(), trim = 'b')
        points_xy = np.reshape(points_xy_1D_trim, (-1, 2))
        num_points_xy = len(points_xy)


        # possible positions in z direction (going into magnet)
        num_z = int(self.depth/self.z_spacing) + 1
        pos_z = np.arange(0, self.z_spacing * num_z, self.z_spacing)

        # z direction points
        self.points = np.zeros([num_points_xy * num_z, 3])
        index = 0
        order = order_inc
        for i in range(num_points_xy):
            if order == order_inc:
                for j in range(0, num_z, 1):
                    self.points[index][0] = points_xy[i][0] + self.x_offset
                    self.points[index][1] = points_xy[i][1] + self.y_offset
                    self.points[index][2] = pos_z[j] + self.z_offset
                    index += 1
            if order == order_dec:
                for j in range(num_z-1, -1, -1):
                    self.points[index][0] = points_xy[i][0] + self.x_offset
                    self.points[index][1] = points_xy[i][1] + self.y_offset
                    self.points[index][2] = pos_z[j] + self.z_offset
                    index += 1
            order = not(order)


    '''
    Functions to be accessed from outside 
    '''
    def run(self):
        # Only run script if not using the same path as before, ie a change has been made to configs.
        if not self.config_changed:
            self.generate()
            # Write path to CSV file
            header = ['X', 'Y', 'Z', 'Rotation']
            with open(self.csv_filename, 'w', encoding='UTF8', newline='') as f:
                f.truncate()
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(self.points)
                f.close()

        print('\n*************** Path generation completed. ***************\n')

