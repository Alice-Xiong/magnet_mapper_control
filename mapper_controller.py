from time import sleep
from rx import throw
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
        self.axisX.move_absolute(Xval + self.x_offset, unitXYZ, wait_until_idle=False)
        self.axisY.move_absolute(Yval + self.y_offset, unitXYZ, wait_until_idle=False)
        self.axisZ.move_absolute(Zval + self.z_offset, unitXYZ, wait_until_idle=False)
        self.axisR.move_absolute(angle, unitR, wait_until_idle=False)

        self.axisX.wait_until_idle()
        self.axisY.wait_until_idle()
        self.axisZ.wait_until_idle()
        self.axisR.wait_until_idle()


    def verify_bounds(self, Xval, Yval, Zval, angle):
        if Xval + self.x_offset > 1000 or Xval + self.x_offset < 0:
            return False
        elif Yval + self.y_offset > 500 or Yval + self.y_offset < 0:
            return False
        elif Zval + self.z_offset > 500 or Zval + self.z_offset < 0:
            return False
        elif angle > 180 or angle < 0: 
            return False
        else:
            return True


    # Get warning flags
    def check_warnings(self):
        for dev in self.device_list:
            warning_flags = dev.warnings.get_flags()
            if len(warning_flags) > 0:
                print(f"Device is stalling (or flag: {warning_flags})!")


    # Collect data from serial port and write one line into the Excel sheet
    def log_data(self, csv_writer, x, y, z, rot, in_bounds = True):
        if not in_bounds:
            data = [x, y, z, rot, 'out of motion bounds']
            print(data)
            csv_writer.writerow(data)
            return

        # configure the serial connections to the probe/Arduino
        with serial.Serial(self.comm_port_probe, 9600, timeout=None) as ser:
            while (True):
                try:
                    ser.readline().decode('ascii').strip() # do not keep the first probe reading
                    field = ser.readline().decode('ascii').strip() # probe reading
                    field_val = field[:-1]
                    field_unit = field[-1]
                    data = [x, y, z, rot, field_val, field_unit]
                    print(data)

                    if (len(field_val) >= 5):
                        csv_writer.writerow(data)
                        ser.flush()
                        break
                except Exception as e:
                    pass
            

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
            deviceX.settings.set('accel', self.max_accelX, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
            deviceY.settings.set('accel', self.max_accelY, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
            deviceZ.settings.set('accel', self.max_accelZ, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

            # actually run the stages
            with open(self.path_filename, 'r') as read_obj:
                csv_reader = reader(read_obj)
                header = next(csv_reader)

                if self.collect_data:
                    # open the data csv and write the header
                    with open(self.data_filename, 'w') as write_obj:
                        self.csv_writer = writer(write_obj)
                        data = ['X', 'Y', 'Z', 'Rotation', 'Data', 'Unit']
                        self.csv_writer.writerow(data)

                        # Check file is not empty
                        if header != None:
                            for row in csv_reader:
                                if self.verify_bounds(float(row[0]), float(row[1]), float(row[2]), float(row[3])):
                                    # move the mapper to position
                                    self.moveXYZR(float(row[0]), float(row[1]), float(row[2]), float(row[3]), Units.LENGTH_MILLIMETRES, Units.ANGLE_DEGREES)
                                    self.check_warnings()
                                    # Wait for oscillation to damp out
                                    sleep(self.probe_stop_time)
                                    # Write data into new csv file
                                    self.log_data(self.csv_writer, float(row[0]), float(row[1]), float(row[2]), float(row[3]))
                                else:
                                    self.log_data(self.csv_writer, float(row[0]), float(row[1]), float(row[2]), float(row[3]), in_bounds=False)

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



    




