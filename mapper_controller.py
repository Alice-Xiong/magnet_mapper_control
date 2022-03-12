from time import sleep
from zaber_motion import Units, Library
from zaber_motion.ascii import Connection
from csv import reader, writer
from mapper_base import Mapper

class Controller (Mapper):
    def __init__(self): 
        super().__init__
        self.config_dict = Mapper.config_dict
        self.path_filename = self.config_dict['path_filename']
        self.data_filename = self.config_dict['data_filename']
        self.comm_port_zaber = self.config_dict['comm_port_zaber']
        self.comm_port_probe = self.config_dict['comm_port_probe']

        self.probe_stop_time = self.config_dict['probe_stop_time_sec']
        self.maxspeedX = self.config_dict['x_maxspeed']
        self.maxspeedY = self.config_dict['y_maxspeed']
        self.maxspeedZ = self.config_dict['z_maxspeed']
       
        
    # Function for moving in XYZ
    def moveXYZ(self, Xval, Yval, Zval, unit):
        self.axisX.move_absolute(Xval, unit, wait_until_idle=False)
        self.axisY.move_absolute(Yval, unit, wait_until_idle=False)
        self.axisZ.move_absolute(Zval, unit, wait_until_idle=False)

        self.axisX.wait_until_idle()
        self.axisY.wait_until_idle()
        self.axisZ.wait_until_idle()
            

    def run(self):
        # Reading from a CSV file and moving the gantry
        # Initialize all stages
        Library.enable_device_db_store()

        with Connection.open_serial_port(self.comm_port_zaber) as connection:
            # establish serial connections
            device_list = connection.detect_devices()
            print("Found {} devices".format(len(device_list)))

            # home all devices 
            for device in device_list:
                print("Homing all axes of device with address {}.".format(device.device_address))
                device.all_axes.home()
            
           # TODO：Add this order to configs
            # initialize structures for devices and axis
            deviceX = device_list[1] # parallel to magnet, horizontal, second stage
            deviceY = device_list[2] # parallel to magnet, vertical, third stage
            deviceZ = device_list[0] # orthogonal to magnet, first stage

            self.axisX = deviceX.get_axis(1)
            self.axisY = deviceY.get_axis(1)
            self.axisZ = deviceZ.get_axis(1)

            # set max velocity in each direction
            deviceX.settings.set('maxspeed', self.maxspeedX, Units.VELOCITY_MILLIMETRES_PER_SECOND)
            deviceY.settings.set('maxspeed', self.maxspeedY, Units.VELOCITY_MILLIMETRES_PER_SECOND)
            deviceZ.settings.set('maxspeed', self.maxspeedZ, Units.VELOCITY_MILLIMETRES_PER_SECOND)

            # open the data csv and write the header
            with open(self.data_filename, 'w') as write_obj:
                csv_writer = writer(write_obj)
                data = ['X', 'Y', 'Z', 'Rotation', 'Data']
                csv_writer.writerow(data)

                # actually run the stages
                with open(self.path_filename, 'r') as read_obj:
                    csv_reader = reader(read_obj)
                    header = next(csv_reader)

                    # Check file is not empty
                    if header != None:
                        for row in csv_reader:
                            self.moveXYZ(float(row[0]), float(row[1]), float(row[2]), unit=Units.LENGTH_MILLIMETRES)
                            # Wait for oscillation to damp out
                            sleep(self.probe_stop_time)
                            # Write data into new csv file
                            self.log_data(csv_writer, float(row[0]), float(row[1]), float(row[2]), 0)
            
            # close and save the data
            write_obj.close()

        print('\n*************** Program finished ***************\n')

    
    def log_data(self, csv_writer, x, y, z, rot):
        field = "0.1G" # change this to real time probe reading
        data = [x, y, z, rot, field]
        csv_writer.writerow(data)



