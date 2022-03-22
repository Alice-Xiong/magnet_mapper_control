from time import sleep
from zaber_motion import Units, Library
from zaber_motion.ascii import Connection
from zaber_motion import SetDeviceStateExceptionData
from zaber_motion.ascii import SettingConstants
from csv import reader, writer
from mapper_base import Mapper
import serial

class Controller (Mapper):
    def __init__(self): 
        super().__init__
        self.config_dict = Mapper.config_dict
        self.path_filename = self.config_dict['path_filename']
        self.data_filename = self.config_dict['data_filename']
        self.comm_port_zaber = self.config_dict['comm_port_zaber']
        self.comm_port_probe = self.config_dict['comm_port_probe']

        # xyz stage settings
        self.probe_stop_time = self.config_dict['probe_stop_time_sec']
        self.maxspeedX = self.config_dict['x_maxspeed']
        self.maxspeedY = self.config_dict['y_maxspeed']
        self.maxspeedZ = self.config_dict['z_maxspeed']

        # rotation


        # data collection
        if self.config_dict['collect_data'][0] == 'F' or self.config_dict['collect_data'][0] == 'f':
            self.collect_data = False
        else:
            self.collect_data = True
            # configure the serial connections to the probe/Arduino
            self.ser = serial.Serial(
                port=self.comm_port_probe,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
       
        
    # Function for moving in XYZ
    def moveXYZ(self, Xval, Yval, Zval, unit):
        self.axisX.move_absolute(Xval, unit, wait_until_idle=False)
        self.axisY.move_absolute(Yval, unit, wait_until_idle=False)
        self.axisZ.move_absolute(Zval, unit, wait_until_idle=False)

        self.axisX.wait_until_idle()
        self.axisY.wait_until_idle()
        self.axisZ.wait_until_idle()


    def home(self):
        Library.enable_device_db_store()
        with Connection.open_serial_port(self.comm_port_zaber) as connection:
            # establish serial connections
            device_list = connection.detect_devices()
            print("Found {} devices".format(len(device_list)))

            # home all devices 
            for device in device_list:
                print("Homing all axes of device with address {}.".format(device.device_address))
                device.all_axes.home()
            


    def run(self):
        # Reading from a CSV file and moving the gantry
        # Initialize all stages
        Library.enable_device_db_store()

        with Connection.open_serial_port(self.comm_port_zaber) as connection:
            # establish serial connections
            device_list = connection.detect_devices()
            
            # TODO：Add this order to configs
            # initialize structures for devices and axis
            deviceX = device_list[0] # orthogonal to magnet, first stage
            deviceY = device_list[1] # parallel to magnet, horizontal, second stage
            deviceZ = device_list[2] # parallel to magnet, vertical, third stage

            self.axisX = deviceX.get_axis(1)
            self.axisY = deviceY.get_axis(1)
            self.axisZ = deviceZ.get_axis(1)

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
                        csv_writer = writer(write_obj)
                        data = ['X', 'Y', 'Z', 'Rotation', 'Data']
                        csv_writer.writerow(data)

                        # Check file is not empty
                        if header != None:
                            for row in csv_reader:
                                # move the mapper to position
                                self.moveXYZ(float(row[0]), float(row[1]), float(row[2]), unit=Units.LENGTH_MILLIMETRES)
                                # Wait for oscillation to damp out
                                sleep(self.probe_stop_time)
                                # Write data into new csv file
                                self.log_data(csv_writer, float(row[0]), float(row[1]), float(row[2]), 0)
                        
                        # close and save the data
                        write_obj.close()

                # not saving data case
                else:
                    # Check file is not empty
                    if header != None:
                        for row in csv_reader:
                            # move the mapper to position
                            self.moveXYZ(float(row[0]), float(row[1]), float(row[2]), unit=Units.LENGTH_MILLIMETRES)
                            # Wait for oscillation to damp out
                            sleep(self.probe_stop_time)
        


        print('\n*************** Program finished ***************\n')

    
    def log_data(self, csv_writer, x, y, z, rot):
        field = self.ser.readline().strip() # probe reading
        data = [x, y, z, rot, field]
        csv_writer.writerow(data)



