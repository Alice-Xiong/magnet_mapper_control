import numpy as np
import csv
import json
from mapper_base import Mapper

class Points_Generator(Mapper):

    def __init__(self):
        super().__init__()
        # Read configurations from 'config.json'
        self.config_filename = Mapper.config_filename
        self.config_changed = Mapper.config_changed
        self.config_dict = Mapper.config_dict

        # Load configurations
        self.path_filename = self.config_dict['path_filename']
        self.radius = self.config_dict['radius']
        self.yz_spacing = self.config_dict['yz_spacing']
        self.depth = self.config_dict['depth']
        self.x_spacing = self.config_dict['x_spacing']
        self.x_offset = self.config_dict['x_offset']
        self.y_offset = self.config_dict['y_offset']
        self.z_offset = self.config_dict['z_offset']
        self.probe_stop_time_sec = self.config_dict['probe_stop_time_sec']

        
    def generate(self):
        # number of columns (= num of rows) under the given radius and spacing
        num_cols_half = int(self.radius/self.yz_spacing)
        num_cols = 2 * num_cols_half + 1

        # possible positions of each column
        pos_yz = np.arange(-self.yz_spacing * num_cols_half, self.yz_spacing * (num_cols_half + 1), self.yz_spacing)

        # Fill all possible x, y values
        points_yz = np.zeros([num_cols * num_cols, 2])
        index = 0
        # Constants for order
        order_inc = True
        order_dec = False
        order = order_inc
        for i in range(num_cols):
            if order == order_inc:
                for j in range(0, num_cols, 1):
                    y = pos_yz[i]
                    z = pos_yz[j]
                    # make sure points are within circle
                    if (z *  z+ y * y < self.radius * self.radius):
                        points_yz[index][0] = y
                        points_yz[index][1] = z
                        index += 1
            if order == order_dec:
                for j in range(num_cols-1, -1, -1):
                    y = pos_yz[i]
                    z = pos_yz[j]
                    if (z * z + y * y < self.radius * self.radius):
                        points_yz[index][0]= y
                        points_yz[index][1] = z
                        index += 1
            # switch increasing/decreasing order for every pass
            order = not(order)

        # trim all zeros and get valid point length
        points_yz_1D_trim = np.trim_zeros(points_yz.flatten(), trim = 'b')
        points_yz = np.reshape(points_yz_1D_trim, (-1, 2))
        num_points_yz = len(points_yz)


        # possible positions in x direction (going into magnet)
        num_x = int(self.depth/self.x_spacing) + 1
        pos_x = np.arange(0, self.x_spacing * num_x, self.x_spacing)

        # z direction points
        self.points = np.zeros([num_points_yz * num_x, 3])
        index = 0
        order = order_inc
        for i in range(num_points_yz):
            if order == order_inc:
                for j in range(0, num_x, 1):
                    self.points[index][0] = pos_x[j] + self.x_offset
                    self.points[index][1] = points_yz[i][0] + self.y_offset
                    self.points[index][2] = points_yz[i][1] + self.z_offset
                    index += 1
            if order == order_dec:
                for j in range(num_x-1, -1, -1):
                    self.points[index][0] = pos_x[j] + self.x_offset
                    self.points[index][1] = points_yz[i][0] + self.y_offset
                    self.points[index][2] = points_yz[i][1] + self.z_offset
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

            inputStr = input('The current mapping sequence will take approximately %d %s. \nDo you wish to continue? True (T) or Return to settings (any key)? ' % (total_time, unit))
            return inputStr


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

        path_ready = self.estimate_time()
        if  path_ready[0] == 'T' or path_ready[0] == 't':
            return True
        else:
            return False
            



