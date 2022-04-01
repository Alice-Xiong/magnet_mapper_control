import numpy as np
from csv import reader, writer
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

        # Configurations specific to cylinder
        if self.shape == "cylinder":
            self.radius = self.config_dict['radius']
            self.xy_spacing = self.config_dict['xy_spacing']
            self.rotation_angles = self.config_dict['rotation_points']
        # Configurations specific to rectangle
        elif self.shape == "rectangular":
            self.y_range = self.config_dict['y_range']
            self.y_spacing = self.config_dict['y_spacing']
            self.z_range = self.config_dict['z_range']
            self.z_spacing = self.config_dict['z_spacing']
            self.rotation_angles = self.config_dict['rotation_points']
        elif self.shape == "custom":
            self.custom_path_filename = self.config_dict['custom_xyr_path_filename']

        # offsets in each direction
        self.x_offset = self.config_dict['x_offset']
        self.y_offset = self.config_dict['y_offset']
        self.z_offset = self.config_dict['z_offset']

        # Configurations common to both shapes
        self.x_range = self.config_dict['x_range']
        self.x_spacing = self.config_dict['x_spacing']
        self.probe_stop_time_sec = self.config_dict['probe_stop_time_sec']
        


    def generate_edges(self): 
        if self.shape == "cylinder":
            # generate the points for edges
            self.points_edges = np.zeros([self.num_cols * 4, 4])

        elif (self.shape == "rectangular"):
            # generate the points for edges
            self.points_edges = np.zeros([int(self.num_x * 4 / self.num_angles), 4])

        # start path generation
        j = 0

        # 2D edges path at minimum z position (out of magnet)
        for i in range(int(len(self.points) / self.num_angles)):
            if  (i==0) or (self.points[i][0] != self.points[i-1][0]) or (i==len(self.points)-1) or (self.points[i][0] != self.points[i+1][0]):
                self.points_edges[j][0] = self.points[i][0]
                self.points_edges[j][1] = self.points[i][1]
                self.points_edges[j][2] = -self.z_range/2
                j += 1

        # 2D edges path at maximum z position (into magnet)
        for i in range(int(len(self.points) / self.num_angles)):
            if  (i==0) or (self.points[i][0] != self.points[i-1][0]) or (i==len(self.points)-1) or (self.points[i][0] != self.points[i+1][0]):
                self.points_edges[j][0] = self.points[i][0]
                self.points_edges[j][1] = self.points[i][1]
                self.points_edges[j][2] = self.z_range/2
                j += 1

        
        # store them into a CSV file
        header = ['X', 'Y', 'Z', 'Rotation']
        with open(self.path_edges_filename, 'w', encoding='UTF8', newline='') as f:
            f.truncate()
            writer = writer(f)
            writer.writerow(header)
            writer.writerows(self.points_edges)
            f.close()

        print('\n*************** Path for moving around edges generated ************\n')


    def generate_custom(self): 

        with open(self.custom_path_filename, 'r') as input:
            csv_reader = reader(input)
            header = next(csv_reader)

        points_xyr = np.array([])

        for row in csv_reader:
            if len(row) == 6:
                print(row)
                x, y, r = [float(i) for i in row]
                points_xyr = np.append(points_xyr, [x, y, r])
        num_points_xyr = len(points_xyr)

        # Constants for order
        order_inc = True
        order_dec = False

        # possible positions in z direction (going into magnet)
        num_z = int(self.z_range/self.z_spacing) + 1
        num_z_half = int(self.z_range/self.z_spacing/2) + 1
        pos_z = np.arange(- self.z_spacing * (num_z_half - 1), self.z_spacing * (num_z_half + 1), self.z_spacing)

        # z direction and angular points
        self.points = np.zeros([num_points_xyr * num_z, 4])
        index = 0
        order = order_inc
        for i in range(num_points_xyr):
            # go forward in z direction
            if order == order_inc:
                for j in range(0, num_z, 1):
                    self.points[index][0] = points_xyr[i][0]
                    self.points[index][1] = points_xyr[i][1]
                    self.points[index][2] = pos_z[j]
                    self.points[index][3] = points_xyr[i][2]
                    index += 1
            # reverse in z direction
            if order == order_dec:
                for j in range(num_z-1, -1, -1):
                    self.points[index][0] = points_xyr[i][0]
                    self.points[index][1] = points_xyr[i][1]
                    self.points[index][2] = pos_z[j]
                    self.points[index][3] = points_xyr[i][2]
                    index += 1
            order = not(order)


        
        # store them into a CSV file
        header = ['X', 'Y', 'Z', 'Rotation']
        with open(self.path_edges_filename, 'w', encoding='UTF8', newline='') as f:
            f.truncate()
            writer = writer(f)
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
            num_cols_half = self.radius / self.xy_spacing
            self.num_cols = int(2 * self.radius / self.xy_spacing + 1)

            # possible positions of each column
            pos_xy = np.arange(-self.xy_spacing * num_cols_half, self.xy_spacing * (num_cols_half + 1), self.xy_spacing)

            # Fill all possible y, z values
            points_xy = np.zeros([self.num_cols * self.num_cols, 2])

            # Initialize variables for pathing
            index = 0
            order = order_inc
            for i in range(self.num_cols):
                if order == order_inc:
                    for j in range(0, self.num_cols, 1):
                        x = pos_xy[i]
                        y = pos_xy[j]
                        # make sure points are within circle
                        if (x *  x+ y * y < self.radius * self.radius):
                            points_xy[index][0] = x
                            points_xy[index][1] = y
                            index += 1
                if order == order_dec:
                    for j in range(self.num_cols-1, -1, -1):
                        x = pos_xy[i]
                        y = pos_xy[j]
                        if (x * x + y * y < self.radius * self.radius):
                            points_xy[index][0]= x
                            points_xy[index][1] = y
                            index += 1

                # switch increasing/decreasing order for every pass
                order = not(order)

        # Generate xy points in rectangular coordinates
        elif self.shape == "rectangular":
            # number of columns (= num of rows) under the given radius and spacing
            num_x_half = self.x_range/self.x_spacing/2
            num_y_half = self.y_range/self.y_spacing/2
            self.num_x = int(self.x_range/self.x_spacing) + 1
            self.num_y = int(self.y_range/self.y_spacing) + 1

            # possible positions of each column
            pos_x = np.arange(-self.x_spacing * num_x_half, self.x_spacing * (num_x_half + 1), self.x_spacing)
            pos_y = np.arange(-self.y_spacing * num_y_half, self.y_spacing * (num_y_half + 1), self.y_spacing)

            # Fill all possible y, z values
            points_xy = np.zeros([self.num_x * self.num_y, 2])

            # Initialize variables for pathing
            index = 0
            order = order_inc
            for i in range(self.num_x):
                if order == order_inc:
                    for j in range(0, self.num_y, 1):
                        points_xy[index][0] = pos_x[i]
                        points_xy[index][1] = pos_y[j]
                        index += 1
                if order == order_dec:
                    for j in range(self.num_y-1, -1, -1):
                        points_xy[index][0] = pos_x[i]
                        points_xy[index][1] = pos_y[j]
                        index += 1
                # switch increasing/decreasing order for every pass
                order = not(order)

        # trim all zeros and get valid point length
        points_xy_1D_trim = np.trim_zeros(points_xy.flatten(), trim = 'b')
        # case when y coordinate happen to be zero
        if (len(points_xy_1D_trim) % 2 != 0):
            points_xy_1D_trim = np.append(points_xy_1D_trim, 0)
        points_xy = np.reshape(points_xy_1D_trim, (-1, 2))
        num_points_xy = len(points_xy)

        # possible positions in z direction (going into magnet)
        num_z = int(self.z_range/self.z_spacing) + 1
        num_z_half = int(self.z_range/self.z_spacing/2) + 1
        pos_z = np.arange(- self.z_spacing * (num_z_half - 1), self.z_spacing * (num_z_half + 1), self.z_spacing)

        # z direction and angular points
        self.num_angles = len(self.rotation_angles)
        self.points = np.zeros([num_points_xy * num_z * self.num_angles, 4])
        index = 0
        order = order_inc
        for angle in self.rotation_angles:
            for i in range(num_points_xy):
                if order == order_inc:
                    for j in range(0, num_z, 1):
                        self.points[index][0] = points_xy[i][0]
                        self.points[index][1] = points_xy[i][1]
                        self.points[index][2] = pos_z[j]
                        self.points[index][3] = angle
                        index += 1
                if order == order_dec:
                    for j in range(num_z-1, -1, -1):
                        self.points[index][0] = points_xy[i][0]
                        self.points[index][1] = points_xy[i][1]
                        self.points[index][2] = pos_z[j]
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
            



