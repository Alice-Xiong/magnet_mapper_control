from time import sleep
from zaber_motion import Units, Library
from zaber_motion.ascii import Connection
from zaber_motion.ascii import WarningFlags
from zaber_motion.ascii import SettingConstants
from csv import reader, writer
from mapper_base import Mapper
import serial

class Controller (Mapper):
    def __init__(self): 
        super().__init__
        self.config_dict = Mapper.config_dict
        self.path_filename = self.config_dict['path_filename']
        self.path_edges_filename = self.config_dict['path_edges_filename']
        self.data_filename = self.config_dict['data_filename']
        self.comm_port_zaber = self.config_dict['comm_port_zaber']
        self.comm_port_probe = self.config_dict['comm_port_probe']

        # xyz stage settings
        self.probe_stop_time = self.config_dict['probe_stop_time_sec']
        self.maxspeedX = self.config_dict['x_maxspeed']
        self.maxspeedY = self.config_dict['y_maxspeed']
        self.maxspeedZ = self.config_dict['z_maxspeed']

        # data collection
        if self.config_dict['collect_data'][0] == 'F' or self.config_dict['collect_data'][0] == 'f':
            self.collect_data = False
        else:
            self.collect_data = True

       
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
        self.axisX.move_absolute(Xval, unitXYZ, wait_until_idle=False)
        self.axisY.move_absolute(Yval, unitXYZ, wait_until_idle=False)
        self.axisZ.move_absolute(Zval, unitXYZ, wait_until_idle=False)
        self.axisR.move_absolute(angle, unitR, wait_until_idle=False)

        self.axisX.wait_until_idle()
        self.axisY.wait_until_idle()
        self.axisZ.wait_until_idle()
        self.axisR.wait_until_idle()


    # Get warning flags
    def check_warnings(self):
        for dev in self.device_list:
            warning_flags = dev.warnings.get_flags()
            if len(warning_flags) > 0:
                print("Device is stalling (or doing something bad)!")


    # Collect data from serial port and write one line into the Excel sheet
    def log_data(self, csv_writer, x, y, z, rot):
        field = self.ser.readline().strip() # probe reading
        data = [x, y, z, rot, field]
        csv_writer.writerow(data)


    def run_edges(self):
        Library.enable_device_db_store()

        with Connection.open_serial_port(self.comm_port_zaber) as connection:
            # establish serial connections
            self.device_list = connection.detect_devices()
            
            # TODO：Add this order to configs
            # initialize structures for devices and axis
            deviceX = self.device_list[0] # orthogonal to magnet, first stage
            deviceY = self.device_list[1] # parallel to magnet, horizontal, second stage
            deviceZ = self.device_list[2] # parallel to magnet, vertical, third stage
            deviceR = self.device_list[3] # last rotation stage

            self.axisX = deviceX.get_axis(1)
            self.axisY = deviceY.get_axis(1)
            self.axisZ = deviceZ.get_axis(1)
            self.axisR = deviceR.get_axis(1)

            # set max velocity in each direction
            deviceX.settings.set('maxspeed', self.maxspeedX, Units.VELOCITY_MILLIMETRES_PER_SECOND)
            deviceY.settings.set('maxspeed', self.maxspeedY, Units.VELOCITY_MILLIMETRES_PER_SECOND)
            deviceZ.settings.set('maxspeed', self.maxspeedZ, Units.VELOCITY_MILLIMETRES_PER_SECOND)

            # actually run the stages
            with open(self.path_edges_filename, 'r') as read_obj:
                csv_reader = reader(read_obj)
                header = next(csv_reader)

                # Check file is not empty
                if header != None:
                    for row in csv_reader:
                        # move the mapper to position
                        self.moveXYZR(float(row[0]), float(row[1]), float(row[2]), 0, Units.LENGTH_MILLIMETRES, Units.ANGLE_DEGREES)
                        self.check_warnings()
                        # Wait for oscillation to damp out
                        sleep(self.probe_stop_time)

            

    # Main function to be accessed outside
    def run(self):
        # Reading from a CSV file and moving the gantry
        # Initialize all stages
        Library.enable_device_db_store()

        # configure the serial connections to the probe/Arduino
        self.ser = serial.Serial(
            port=self.comm_port_probe,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

        with Connection.open_serial_port(self.comm_port_zaber) as connection:
            # establish serial connections
            self.device_list = connection.detect_devices()
            
            # TODO：Add this order to configs
            # initialize structures for devices and axis
            deviceX = self.device_list[0] # orthogonal to magnet, first stage
            deviceY = self.device_list[1] # parallel to magnet, horizontal, second stage
            deviceZ = self.device_list[2] # parallel to magnet, vertical, third stage
            deviceR = self.device_list[3] # last rotation stage

            self.axisX = deviceX.get_axis(1)
            self.axisY = deviceY.get_axis(1)
            self.axisZ = deviceZ.get_axis(1)
            self.axisR = deviceR.get_axis(1)

            # set max velocity in each direction
            deviceX.settings.set('maxspeed', self.maxspeedX, Units.VELOCITY_MILLIMETRES_PER_SECOND)
            deviceY.settings.set('maxspeed', self.maxspeedY, Units.VELOCITY_MILLIMETRES_PER_SECOND)
            deviceZ.settings.set('maxspeed', self.maxspeedZ, Units.VELOCITY_MILLIMETRES_PER_SECOND)

            # actually run the stages
            with open(self.path_filename, 'r') as read_obj:
                csv_reader = reader(read_obj)
                header = next(csv_reader)

                if self.collect_data:
                    # open the data csv and write the header
                    with open(self.data_filename, 'w') as write_obj:
                        self.csv_writer = writer(write_obj)
                        data = ['X', 'Y', 'Z', 'Rotation', 'Data']
                        self.csv_writer.writerow(data)

                        # Check file is not empty
                        if header != None:
                            for row in csv_reader:
                                # move the mapper to position
                                self.moveXYZR(float(row[0]), float(row[1]), float(row[2]), float(row[3]), Units.LENGTH_MILLIMETRES, Units.ANGLE_DEGREES)
                                self.check_warnings()
                                # Wait for oscillation to damp out
                                sleep(self.probe_stop_time)
                                # Write data into new csv file
                                self.log_data(self.csv_writer, float(row[0]), float(row[1]), float(row[2]), float(row[3]))

                # not saving data case
                else:
                    # Check file is not empty
                    if header != None:
                        for row in csv_reader:
                            # move the mapper to position
                            self.moveXYZR(float(row[0]), float(row[1]), float(row[2]), float(row[3]), Units.LENGTH_MILLIMETRES, Units.ANGLE_DEGREES)
                            self.check_warnings()
                            # Wait for oscillation to damp out
                            sleep(self.probe_stop_time)

        print('\n*************** Program finished ***************\n')

    




