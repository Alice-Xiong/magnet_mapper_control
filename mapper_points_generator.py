#!/usr/bin/env python3
import numpy as np
import csv
#from csv import reader, writer
from mapper_base import Mapper

class Points_Generator(Mapper):
    """The ``Points_Generator`` class inherits Mapper. It instantiates an object for generated a point cloud in X,Y,Z, and rotation axis.
    The ``Config_Setter`` class should have already updated the config_dict variable in the Mapper object, this 
    will get passed onto the ``Points_Generator``.

    Args:
        Mapper: Mapper class that contains variables with key configurations.
    """
    

    def __init__(self):
        """Creates an instance of the ``Points_Generator`` class.

        Loads configurations from the ``Mapper`` superclass -- in particular, it contains ``self.config_dict`` with key configurations.

        Checks for the shape from the configuration (``self.config_dict['shape']`` can be 'cylinder', 'rectangular', or 'custom').
        These shapes have their own associated configs.

        * General configurations

        ============================   ==============================    =============================================================
        Variable name                  Related setting in config.json    Description
        ============================   ==============================    =============================================================
        ``self.path_filename``         'path_filename'                   Path to the CSV that stores the full mapping path
        ``self.path_edges_filename``   'path_edges_filename'             Path to the CSV that stores the mapping path boundaries
        ``self.shape``                 'shape'                           Shape of path, can be cylinder, rectangular, custom
        ============================   ==============================    =============================================================

        * Cylinder:

        ========================   ==============================    =============================================================
        Variable name              Related setting in config.json    Description
        ========================   ==============================    =============================================================
        ``self.radius``            'radius'                          Radius of the circle in XY plane, in mm  
        ``self.xy_spacing``        'xy_spacing'                      Grid spacing for circle region in XY plane, in mm
        ``self.rotation_points``   'rotation_points'                 A list of angles the probe will rotate to, in degrees
        ========================   ==============================    =============================================================

        * Rectangular:

        ========================   ==============================    =============================================================
        Variable name              Related setting in config.json    Description
        ========================   ==============================    =============================================================
        ``self.x_range``           'x_range'                         Edge to edge distance in X direction in mm. 
        ``self.x_spacing``         'x_spacing'                       Grid spacing in X direction, in mm
        ``self.y_range``           'y_range'                         Edge to edge distance in Y direction in mm. 
        ``self.y_spacing``         'y_spacing'                       Grid spacing in Y direction, in mm
        ``self.rotation_points``   'rotation_points'                 A list of angles the probe will rotate to, in degrees
        ========================   ==============================    =============================================================

        * Custom:

        =============================   ==============================    =====================================================================
        Variable name                   Related setting in config.json    Description
        =============================   ==============================    =====================================================================
        ``self.custom_path_filename``   'custom_xyr_path_filename'        Path to your custom path that specifies points in X, Y, and rotation.

                                                                          e.g. 'path/path_custom_xyr.csv' 

                                                                          Units: mm for X,Y and degrees for rotation. 
        =============================   ==============================    =====================================================================

        There are also configurations common to all path shapes:

        ======================   ==============================    =============================================================
        Variable name            Related setting in config.json    Description
        ======================   ==============================    =============================================================
        ``self.z_range``           'z_range'                       Edge to edge distance in Z direction in mm. 
        ``self.z_spacing``         'z_spacing'                     Grid spacing in Z direction, in mm
        ``self.x_offset``          'x_offset'                      Position of X stage when the tip of the probe is aligned to center of magnet in mm. 
        
                                                                   This is read from Zaber Console.

        ``self.y_offset``          'y_offset'                      Position of Y stage when the tip of the probe is aligned to center of magnet in mm. 
        
                                                                   This is read from Zaber Console.
        
        ``self.z_offset``          'z_offset'                      Position of Z stage when the tip of the probe is aligned to center of magnet in mm. 
        
                                                                   This is read from Zaber Console.
 
        ``self.x_accel``           'x_accel'                       Maximum acceleration in X direction in mm/s^2
        ``self.y_accel``           'y_accel'                       Maximum acceleration in Y direction in mm/s^2
        ``self.z_accel``           'z_accel'                       Maximum acceleration in Z direction in mm/s^2
        ======================   ==============================    =============================================================

        """
        # Read configurations from 'config.json'
        self.config_filename = Mapper.config_filename
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
            self.x_range = self.config_dict['x_range']
            self.x_spacing = self.config_dict['x_spacing']
            self.rotation_angles = self.config_dict['rotation_points']
        elif self.shape == "custom":
            self.custom_path_filename = self.config_dict['custom_xyr_path_filename']

        # offsets in each direction
        self.x_offset = self.config_dict['x_offset']
        self.y_offset = self.config_dict['y_offset']
        self.z_offset = self.config_dict['z_offset']

        # Configurations common to both shapes
        self.z_range = self.config_dict['z_range']
        self.z_spacing = self.config_dict['z_spacing']
        self.probe_stop_time_sec = self.config_dict['probe_stop_time_sec']
        

    def generate(self):
        """This function takes the configurations specified in ``__init__`` and converts it into a path.

        **Modifies** self.points, where it stores the point cloud.

        The code calculates the points such that all points are centered around zero and contains zero. The endpoints are not contained in the
        path unless the spacing divides the range. The range is an edge to edge distance, but the radius (for cylinder only) accounts for half 
        of the edge to edge distance.

        * If `x_range = 100` and `x_spacing = 50`, the possible points in X will be -50, 0, 50.
        * If `x_range = 100` and `x_spacing = 40`, the possible points in X will be -40, 0, 40.
        * If `radius = 100` and `x_spacing = 50`, the possible points in X will be -100, -50, 0, 50, 100.

        The order of point changes follows Z --> Y --> X --> rotation.

        * For each point in XY plane, the mapper will move parallel to the probe in +Z direction from `-self.z_range/2` to `self.z_range/2`. 
        * Then it will move perpendicular to the probe to the next XY point, and then move in -Z direction, from `self.z_range/2` to `-self.z_range/2`. 
        * This is repeated until all the points in XY plane have been passed. 
        * Then the mapper rotates to the next point specified in `self.rotation_points` and repeats the sequence in XYZ space again.

        The code prints 'Path generated for {self.shape} region' after execution.
        """
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
                        if (x *  x+ y * y <= self.radius * self.radius):
                            points_xy[index][0] = x
                            points_xy[index][1] = y
                            index += 1
                if order == order_dec:
                    for j in range(self.num_cols-1, -1, -1):
                        x = pos_xy[i]
                        y = pos_xy[j]
                        if (x * x + y * y <= self.radius * self.radius):
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

        print(f'\n*************** Path generated for {self.shape} region ************\n')


    def generate_custom(self): 
        """This function takes a custome path file that contains points in X, Y, and rotation and converts to a full point cloud with X,Y,Z and rotation.

        **Modifies** self.points, where it stores the point cloud.

        This function requires the shape to be custom and the path to the custom csv file given in `self.custom_path_filename`. The CSV should 
        look like the following:
        
        ===== =====    ===========
        X     Y        Rotation
        ===== =====    ===========
        0     -50      30
        0     0        60
        ===== =====    ===========

        The maximum and minimum X and Y values should be at most 500 apart, so as to not exceed travel bounds. The rotation stage should contain 
        values between 0 to 180 degrees.

        The code prints 'Path generated according to custom XYR path' after execution.

        """
        with open(self.custom_path_filename, 'r') as input:
            csv_reader = csv.reader(input)
            next(csv_reader)

            points_xyr = np.array([])

            # read the csv and dump position vlaues in points_xyr
            for row in csv_reader:
                x, y, r = [float(i) for i in row]
                points_xyr = np.append(points_xyr, [x, y, r])
            points_xyr = np.reshape(points_xyr, (-1, 3))
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

        print('\n*************** Path generated according to custom XYR path ************\n')

        


    def generate_edges(self): 
        """This function takes the points in ``self.points`` and generates a point cloud that represents the edges of the path. This 
        allows the user to run the mapper only along the edges to verify no collision occurs.

        **Modifies** ``self.points_edges`` where the edges path is stored.

        The detailed implementation is specific to the order of points.
        
        * Recall they change in the order of Z --> Y --> X --> rotation.
        * The implementation may need to be updated if a different order is adopted in the future.

        """
        if self.shape == "cylinder":
            # generate the points for edges
            self.points_edges = np.zeros([int(self.num_cols * 4), 4])

        elif self.shape == "rectangular":
            # generate the points for edges
            self.points_edges = np.zeros([self.num_x * 4, 4])
            
        elif self.shape == 'custom':
            # For custom path, path may be different for different angles, so run through all angles
            self.points_edges = np.zeros([len(self.points) , 4])
            self.num_angles = 1

        if self.shape == 'custom':
            # start path generation
            j = 0  # index number of edges array  

            # 2D edges path at minimum z position (out of magnet)
            for i in range(int(len(self.points) / self.num_angles)):
                if (i==0) or (self.points[i][0] != self.points[i-1][0]):
                    self.points_edges[j][0] = self.points[i][0]
                    self.points_edges[j][1] = self.points[i][1]
                    self.points_edges[j][2] = -self.z_range/2
                    self.points_edges[j][3] = self.points[i][3]
                    j += 1

            # 2D edges path at minimum z position (out of magnet)
            for i in range(int(len(self.points) / self.num_angles)-1, 0, -1):
                if (i==len(self.points)-1) or (self.points[i][0] != self.points[i+1][0]):
                    self.points_edges[j][0] = self.points[i][0]
                    self.points_edges[j][1] = self.points[i][1]
                    self.points_edges[j][2] = self.z_range/2
                    self.points_edges[j][3] = self.points[i][3]
                    j += 1

        else:
            # start path generation
            j = 0  # index number of edges array
            k = 0  # helps change order of path      

            # 2D edges path at minimum z position (out of magnet)
            for i in range(int(len(self.points) / self.num_angles)):
                if (i==0) or (self.points[i][0] != self.points[i-1][0]) or (i==len(self.points)-1) or (self.points[i][0] != self.points[i+1][0]):
                    if (k%4 == 0) or (k%4 == 3):
                        self.points_edges[j][0] = self.points[i][0]
                        self.points_edges[j][1] = self.points[i][1]
                        self.points_edges[j][2] = -self.z_range/2
                        self.points_edges[j][3] = self.points[i][3]
                        j += 1
                    k += 1

            k = 0  # helps change order of path
            for i in range(int(len(self.points) / self.num_angles)-1, 0, -1):
                if (i==0) or (self.points[i][0] != self.points[i-1][0]) or (i==len(self.points)-1) or (self.points[i][0] != self.points[i+1][0]):
                    if (k%4 == 0) or (k%4 == 3):
                        self.points_edges[j][0] = self.points[i][0]
                        self.points_edges[j][1] = self.points[i][1]
                        self.points_edges[j][2] = -self.z_range/2
                        self.points_edges[j][3] = self.points[i][3]
                        j += 1
                    k += 1

            k = 0  # helps change order of path
            # 2D edges path at minimum z position (out of magnet)
            for i in range(int(len(self.points) / self.num_angles)):
                if (i==0) or (self.points[i][0] != self.points[i-1][0]) or (i==len(self.points)-1) or (self.points[i][0] != self.points[i+1][0]):
                    if (k%4 == 0) or (k%4 == 3):
                        self.points_edges[j][0] = self.points[i][0]
                        self.points_edges[j][1] = self.points[i][1]
                        self.points_edges[j][2] = self.z_range/2
                        self.points_edges[j][3] = self.points[i][3]
                        j += 1
                    k += 1

            k = 0  # helps change order of path
            for i in range(int(len(self.points) / self.num_angles)-1, 0, -1):
                if (i==0) or (self.points[i][0] != self.points[i-1][0]) or (i==len(self.points)-1) or (self.points[i][0] != self.points[i+1][0]):
                    if (k%4 == 0) or (k%4 == 3):
                        self.points_edges[j][0] = self.points[i][0]
                        self.points_edges[j][1] = self.points[i][1]
                        self.points_edges[j][2] = self.z_range/2
                        self.points_edges[j][3] = self.points[i][3]
                        j += 1
                    k += 1

        print('\n*************** Path for moving around edges generated ************\n')


    def estimate_time(self, path_filename, wait_time):
        """This function estimates the amount of time until motion completion. 
        It does not account for time for linear stages to travel. This is because typically we stop for 5 seconds at each point for probe and oscillations
        to settle, which is much longer than the time of travelling between points.

        The function takes in the time to stop at each point.

        * For the full path, ``wait_time = self.probe_stop_time_sec`` 
        * For edges path, ``wait_time = 1`` to get a fast verification

        The unit for time estimate will auto adjust to the largest unit, rounded to 1 decimal place. (e.g. 1.2 hours instead of 72 minutes).

        Args:
            path_filename (string): path to file that contains the mapping path/point cloud
            wait_time (int/float): time to stop at each point in seconds
        """
        # Prints the estimated time 
        with open(path_filename, 'r', encoding='UTF8', newline='') as f:
            reader = csv.reader(f)
            unit = 'seconds'
            total_time = len(list(reader)) * (wait_time + 1)
            if total_time >= 60:
                total_time = total_time/60
                unit = 'minutes'

                if total_time >= 60:
                    total_time = total_time/60
                    unit = 'hours'

            total_time = "{:.1f}".format(total_time)
            print('The current mapping sequence will take approximately %s %s. \n' % (total_time, unit))


    # store them into a CSV file
    def write_CSV(self, filename, points):
        """This is a helper function that writes a list of points into the specified CSV file.

        **The CSV file must be closed and available for writing during execution.**

        Args:
            filename (string): CSV file to save the points to, e.g. 'path/path.csv'
            points (list): A list with 4 columns, each containing x, y, z, rotation data. This list is typically either `self.points` or `self.points_edges`.
        """
        header = ['X', 'Y', 'Z', 'Rotation']
        with open(filename, 'w', encoding='UTF8', newline='') as f:
            f.truncate()
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(points)



    def run(self):
        """This is the main function accessed from the outside.

        This function checks the shape from configurations and generates the associated path and edges path. 
        It also writes the CSV files as specified by ``self.path_filename`` and ``self.path_edges_filename``.
        At the end of execution, it provides the estimated time for both the full path and the edges path.
        """
        if self.shape == 'custom':
            self.generate_custom()
        elif self.shape == 'rectangular' or self.shape == 'cylinder':
            self.generate()
        else:
            print('\nShape not recognized. Please change your configurations and try again.\n')
        
        # Generate full path
        self.write_CSV(self.path_filename, self.points)
        self.estimate_time(self.path_filename,self.probe_stop_time_sec)

        # Generate edges path
        self.generate_edges()
        self.write_CSV(self.path_edges_filename, self.points_edges)
        self.estimate_time(self.path_edges_filename, 1)
            



