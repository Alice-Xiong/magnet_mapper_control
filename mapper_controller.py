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
    def __init__(self): 
        super().__init__
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
        self.probe_stop_time = self.config_dict['probe_stop_time_sec']
        self.max_accelX = self.config_dict['x_accel']
        self.max_accelY = self.config_dict['y_accel']
        self.max_accelZ = self.config_dict['z_accel']

        # data collection
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
        """Verify whether the commanded position is within range of motion

        Args:
            Xval (int): Commanded position in X direction in mm (magnet coordinates)
            Yval (int): Commanded position in Y direction in mm (magnet coordinates)
            Zval (int): Commanded position in Z direction in mm (magnet coordinates)
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
        for dev in self.device_list:
            warning_flags = dev.warnings.get_flags()
            if len(warning_flags) > 0:
                print(f"Device is stalling (or flag: {warning_flags})!")
            

    def run_edges(self):
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



    




