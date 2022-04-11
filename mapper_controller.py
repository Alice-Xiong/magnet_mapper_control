#!/usr/bin/env python3
from time import sleep
from rx import throw
from zaber_motion import Units, Library
from zaber_motion.ascii import Connection
from zaber_motion.ascii import WarningFlags
from zaber_motion.ascii import SettingConstants
from csv import reader, writer
from mapper_base import Mapper
from mapper_datalogger import Datalogger
import serial
import re

class Controller (Mapper):
    """The Controller class inherits ``Mapper``. This class contains functions that home and move the Zaber stages.
    The Controller class assumes that configuration setting and path generation have already been completed.

    Args:
        Mapper: Mapper class that contains variables with key configurations.
    """
    def __init__(self): 
        """Creates an instance of the Controller class.

        Loads configurations from the Mapper superclass -- in particular, it contains ``self.config_dict`` with key configurations.

        Information about the settings in code:

        * General configurations:

        ============================   ==============================    =============================================================
        Variable name                  Related setting in config.json    Description
        ============================   ==============================    =============================================================
        ``self.path_filename``         'path_filename'                   Path to the CSV that stores the full mapping path
        ``self.path_edges_filename``   'path_edges_filename'             Path to the CSV that stores the mapping path boundaries
        ``self.data_filename``         'data_filename'                   Path to CSV that stores mapping data
        ``self.comm_port_zaber``       'comm_port_zaber'                 COMM port that connects to Zaber device
        ``self.comm_port_probe``       'comm_port_probe'                 COMM port that connects to the probe/Arduino interface
        ============================   ==============================    =============================================================

        * Motion related configurations:

        ========================   ==============================    =============================================================
        Variable name              Related setting in config.json    Description
        ========================   ==============================    =============================================================
        ``self.x_offset``          'x_offset'                        Position of X stage (float) when the tip of the probe is aligned to center of magnet in mm. 
        
                                                                     This is read from Zaber Launcher.

        ``self.y_offset``          'y_offset'                        Position of Y stage (float) when the tip of the probe is aligned to center of magnet in mm. 
        
                                                                     This is read from Zaber Launcher.
        
        ``self.z_offset``          'z_offset'                        Position of Z stage (float) when the tip of the probe is aligned to center of magnet in mm. 
        
                                                                     This is read from Zaber Launcher.
 
        ``self.max_accelX``        'x_accel'                         Maximum acceleration of the X direction stage in mm/s^2
        ``self.max_accelY``        'y_accel'                         Maximum acceleration of the Y direction stage in mm/s^2
        ``self.max_accelZ``        'z_accel'                         Maximum acceleration of the Z direction stage in mm/s^2
        ========================   ==============================    =============================================================
        
        * Data collection related configurations:

        =========================   ==============================    =============================================================
        Variable name               Related setting in config.json    Description
        =========================   ==============================    =============================================================
        ``self.probe_stop_time``      'probe_stop_time_sec'             Time probe pauses at each spot in seconds (float value)
        ``self.collect_data``         'collect_data'                    True if probe is installed and taking data
                                                                      False if you do not wish to take data
        =========================   ==============================    =============================================================

        The class also instantiates a ``datalogger`` class on startup. The datalogger class is based on the COMM ports and data path specified.
        """
        super().__init__
        # general configurations
        self.config_dict = Mapper.config_dict
        self.path_filename = self.config_dict['path_filename']
        self.path_edges_filename = self.config_dict['path_edges_filename']
        self.data_filename = self.config_dict['data_filename']
        self.comm_port_zaber = self.config_dict['comm_port_zaber']
        self.comm_port_probe = self.config_dict['comm_port_probe']

        # offset values ie origin
        self.x_offset = self.config_dict['x_offset']
        self.y_offset = self.config_dict['y_offset']
        self.z_offset = self.config_dict['z_offset']

        # xyz stage settings
        self.max_accelX = self.config_dict['x_accel']
        self.max_accelY = self.config_dict['y_accel']
        self.max_accelZ = self.config_dict['z_accel']

        # data collection
        self.probe_stop_time = self.config_dict['probe_stop_time_sec']
        if self.config_dict['collect_data'][0] == 'F' or self.config_dict['collect_data'][0] == 'f':
            self.collect_data = False
        else:
            self.collect_data = True

        # datalogger instance
        self.datalogger = Datalogger(self.data_filename, self.comm_port_probe)

       
    # Function to home the staegs
    def home(self):
        Library.enable_device_db_store()
        with Connection.open_serial_port(self.comm_port_zaber) as connection:
            # establish serial connections
            self.device_list = connection.detect_devices()
            print("Found {} devices".format(len(self.device_list)))

            # home all devices 
            for device in self.device_list:
                print("Homing all axes of device with address {}.".format(device.device_address))
                device.all_axes.home()
                self.check_warnings()


    # Function for moving in XYZ
    def moveXYZR(self, Xval, Yval, Zval, angle, unitXYZ, unitR):
        """Move the linear stages according to the position and rotation values given. The positions given are absolute.

        This function converts mapper/magnet coordinates (i.e. with (0,0,0) at the center of magnet) to Zaber stages 
        coordinates (i.e. with (0,0,0) at the edges of each stage). 

        The ``axis.wait_until_idle()`` command blocks until motion on this axis is complete. Currently, we have the X,Y,rotation 
        stages moving together, blocking the funtion, and Z stage only moves after the other three motions have completed.
        This order of movements helps avoid collision with the magnet surface while moving into position.

        Args:
            Xval (float/int): targeted position on X axis in mapper coordinates
            Yval (float/int): targeted position on Y axis in mapper coordinates
            Zval (float/int): targeted position on Z axis in mapper coordinates
            angle (float/int): targeted position on rotation stage 
            unitXYZ (Units): unit for linear motion, must be a Zaber Units type, e.g. Units.LENGTH_MILLIMETRES
            unitR (Units): unit for rotational motion, must be a Zaber Units type, e.g. Units.ANGLE_DEGREES
        """
        self.axisX.move_absolute(self.x_offset + Xval, unitXYZ, wait_until_idle=False)
        # Y axis is vertical stage. Since our motor is mount at the top of the stage, a smaller commanded position 
        # corresponds to a higher position, we thus subtract the commanded position instead of adding it to the y offset
        self.axisY.move_absolute(self.y_offset - Yval, unitXYZ, wait_until_idle=False)
        self.axisR.move_absolute(angle, unitR, wait_until_idle=False)
        self.axisX.wait_until_idle()
        self.axisY.wait_until_idle()
        self.axisR.wait_until_idle()

        self.axisZ.move_absolute(Zval + self.z_offset, unitXYZ, wait_until_idle=False)
        self.axisZ.wait_until_idle()
        


    def verify_bounds(self, Xval, Yval, Zval, angle):
        """Verify whether the commanded position is within range of motion. The bounds are:

        * 1000 mm for X
        * 500 mm for Y
        * 500 mm for Z
        * 0 to 360 degrees for rotation

        Args:
            Xval (int/float): Commanded position in X direction in mm (magnet coordinates)
            Yval (int/float): Commanded position in Y direction in mm (magnet coordinates)
            Zval (int/float): Commanded position in Z direction in mm (magnet coordinates)
            angle (float): Commanded angle in degrees

        Returns:
            boolean: True if commanded position is within range of motion, False otherwise
        """
        if Xval + self.x_offset > 500 or Xval + self.x_offset < 0:
            return False
        elif self.y_offset - Yval > 500 or self.y_offset - Yval  < 0:
            return False
        elif Zval + self.z_offset > 1000 or Zval + self.z_offset < 0:
            return False
        elif angle > 360 or angle < 0: 
            return False
        else:
            return True

    # Get warning flags
    def check_warnings(self):
        """Checks for Zaber warning flags across all Zaber devices and prints them to user console.
        """
        for dev in self.device_list:
            warning_flags = dev.warnings.get_flags()
            if len(warning_flags) > 0:
                print(f"Device is stalling (or flag: {warning_flags})!")
            

    def run_edges(self):
        """This function runs the mapper through the edges of the mapping path. 

        This function will require connection to Zaber stages. It does not home any stages automatically. The acceleration will 
        be limited to that of ``self.max_accelX``, ``self.max_accelY``, ``self.max_accelZ`` respectively. 

        This function will also be reading the CSV filespecified in ``self.points_edges``, which contains the edges path. The program 
        will pause and give an error if the CSV file is accessed by other processes.

        When running the edges path, 1 second of damping time is used. This time is currently not configurable. It is chosen so the 
        mapper can move quickly through all points on the edges. No data is taken and connection to the probe is not required.
        """
        Library.enable_device_db_store()

        with Connection.open_serial_port(self.comm_port_zaber) as connection:
            # establish serial connections
            self.device_list = connection.detect_devices()

            # initialize structures for devices and axis
            deviceX = self.device_list[1] # transverse horizontal, second stage
            deviceY = self.device_list[2] # transverse vertical, third stage
            deviceZ = self.device_list[0] # parallel to beamline, first stage
            deviceR = self.device_list[3] # last rotation stage

            self.axisX = deviceX.get_axis(1)
            self.axisY = deviceY.get_axis(1)
            self.axisZ = deviceZ.get_axis(1)
            self.axisR = deviceR.get_axis(1)

            # set max acceleration in each direction
            deviceX.settings.set('accel', self.max_accelX, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
            deviceY.settings.set('accel', self.max_accelY, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
            deviceZ.settings.set('accel', self.max_accelZ, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

            # actually run the stages
            with open(self.path_edges_filename, 'r') as read_obj:
                csv_reader = reader(read_obj)
                header = next(csv_reader)

                # Check file is not empty
                if header != None:
                    for row in csv_reader:
                        x,y,z,rot = [float(i) for i in row]
                        # move the mapper to position
                        self.moveXYZR(x,y,z, rot, Units.LENGTH_MILLIMETRES, Units.ANGLE_DEGREES)
                        self.check_warnings()
                        # Wait for oscillation to damp out
                        sleep(1)

            

    # Main function to be accessed outside
    def run(self):
        """This function runs the mapper through the full mapping path.

        This function will require connection to Zaber stages. It does not home any stages automatically. The acceleration will 
        be limited to that of ``self.max_accelX``, ``self.max_accelY``, ``self.max_accelZ`` respectively. 

        This function will also be reading the CSV file whose name is give by ``self.points``, which contains the mapping path. The program 
        will pause and give an error if the CSV file is accessed by other processes.

        This functions calls ``self.moveXYZR`` and moves to every point specified in the CSV file. At each step, X,Y,Rotation movements occur 
        simultaneously, followed by separate Z direction motion. Due to the path setup, Z direction motion is maximized, X,Y, and rotation motions 
        are minimized. To change this order, make changes in the ``Points_Generator`` class.

        """
        # Reading from a CSV file and moving the gantry
        # Initialize all stages
        Library.enable_device_db_store()

        with Connection.open_serial_port(self.comm_port_zaber) as connection:
            # establish serial connections
            self.device_list = connection.detect_devices()
            
            # initialize structures for devices and axis
            deviceX = self.device_list[1] # parallel to magnet, horizontal, second stage
            deviceY = self.device_list[2] # parallel to magnet, vertical, third stage
            deviceZ = self.device_list[0] # orthogonal to magnet, first stage
            deviceR = self.device_list[3] # last rotation stage

            self.axisX = deviceX.get_axis(1)
            self.axisY = deviceY.get_axis(1)
            self.axisZ = deviceZ.get_axis(1)
            self.axisR = deviceR.get_axis(1)

            # set max velocity in each direction
            deviceX.settings.set('accel', self.max_accelX, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
            deviceY.settings.set('accel', self.max_accelY, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
            deviceZ.settings.set('accel', self.max_accelZ, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

            # actually run the stages
            with open(self.path_filename, 'r') as read_obj:
                csv_reader = reader(read_obj)
                header = next(csv_reader)

                if self.collect_data:
                    # open the data csv and write the header
                    # newline = '' prevents extra lines between data points
                    with open(self.data_filename, 'w', newline='') as write_obj:
                        csv_writer = writer(write_obj)
                        data = ['X', 'Y', 'Z', 'Rotation', 'Data', 'Unit']
                        csv_writer.writerow(data)

                    # Check file is not empty
                    if header != None:
                        for row in csv_reader:
                            x,y,z,rot = [float(i) for i in row]
                            if self.verify_bounds(x,y,z,rot):
                                # move the mapper to position
                                self.moveXYZR(x,y,z,rot, Units.LENGTH_MILLIMETRES, Units.ANGLE_DEGREES)
                                self.check_warnings()
                                # Wait for oscillation to damp out
                                sleep(self.probe_stop_time)
                                # Write data into new csv file
                                self.datalogger.log_data(x,y,z,rot)
                            else:
                                self.datalogger.log_data(x,y,z,rot, in_bounds=False)

                # not saving data case
                else:
                    # Check file is not empty
                    if header != None:
                        for row in csv_reader:
                            x,y,z,rot = [float(i) for i in row]
                            # move the mapper to position
                            self.moveXYZR(x,y,z,rot, Units.LENGTH_MILLIMETRES, Units.ANGLE_DEGREES)
                            self.check_warnings()
                            # Wait for oscillation to damp out
                            sleep(self.probe_stop_time)



    




