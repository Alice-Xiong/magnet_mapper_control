import serial
from csv import writer
import re

class Datalogger():
    """The Datalogger class interfaces with the Arduino and reads serial data from the Teslameter. This class 
    will likely need to be changed if the RS232 interface is used instead. This class is mainly called by functions 
    in mapper_controller.Controller (ie the functions that run the stages) to make measurements at each step.
    """
    def __init__(self, data_filename, comm_port):
        """Initializes the Datalogger class with save filename and Arduino comm port.

        Args:
            data_filename (string): path and name to save the data to, e.g. 'data/data_date_time.csv'
            comm_port (string): name of COMM port that the Arduino is connected to, e.g. 'COM3'
        """
        self.data_filename = data_filename
        self.comm_port = comm_port
        pass

    # Collect data from serial port and write one line into the Excel sheet
    def log_data(self, x, y, z, rot, in_bounds = True):
        """Log one line of data into the specified CSV file.

        Each line of the data will look like:

        [X   Y   Z   Rotation   Field   Value   Unit]

        The reading from the COMM port is separated into the signed value ('0.16') and the unit ('G'), stored in two different cells.

        To reduce chance of corrupted data:

        * Regular expression '-*[0-9]{1,2}\.[0-9]{2,4}' is used to check that the probe data reading contains 1-2 digits followed by a decimal point, followed by 2-4 digits.
        
        * The first two readings after opening the COMM port is dropped. The third one (at the same location) is recorded.


        Args:
            x (float): position of the linear stage in X direction, in mm
            y (float): position of the linear stage in Y direction, in mm
            z (float): position of the linear stage in Z direction, in mm
            rot (float): position of the rotational stage, in degrees, between 0 - 180 degress.
            in_bounds (bool, optional): set to False if motion system decides the point is out of bounds and skips this data point. Defaults to True.
        """
        if not in_bounds:
            data = [x, y, z, rot, 'out of motion bounds']
            print(data)
            csv_writer.writerow(data)
            return

        # configure the serial connections to the probe/Arduino
        with serial.Serial(self.comm_port, 9600, timeout=None) as ser:
            while (True):
                try:
                    ser.readline() # do not keep the first or second probe reading
                    ser.readline()
                    field = ser.readline().decode('ascii').strip() # probe reading
                    # use regular expression to check the field satisfies a certain value
                    field_val = re.findall('-*[0-9]{1,5}\.[0-9]{1,4}', field)[0]
                    field_unit = field[-1]
                    data = [x, y, z, rot, field_val, field_unit]
                    # print data to screen
                    print(data)
                    
                    # if data seems correct, place it in csv file
                    with open(self.data_filename, 'a', newline='') as write_obj:
                        csv_writer = writer(write_obj)
                        csv_writer.writerow(data)

                    ser.flush()
                    break

                except Exception as e:
                    pass