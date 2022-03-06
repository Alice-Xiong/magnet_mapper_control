from zaber_motion import Units, Library
from zaber_motion.ascii import Connection
from csv import reader

Library.enable_device_db_store()

maxspeedX = 50.0
maxspeedY = 50.0
maxspeedZ = 50.0

with Connection.open_serial_port("COM8") as connection:
    # establish serial connections
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    # home all devices 
    for device in device_list:
        print("Homing all axes of device with address {}.".format(device.device_address))
        device.all_axes.home()
    
    # initialize structures for devices and axis
    deviceX = device_list[1] # parallel to magnet, horizontal, second stage
    deviceY = device_list[2] # parallel to magnet, vertical, third stage
    deviceZ = device_list[0] # orthogonal to magnet, first stage

    axisX = deviceX.get_axis(1)
    axisY = deviceY.get_axis(1)
    axisZ = deviceZ.get_axis(1)

    # set max velocity in each direction
    deviceX.settings.set('maxspeed', maxspeedX, Units.VELOCITY_MILLIMETRES_PER_SECOND)
    deviceY.settings.set('maxspeed', maxspeedY, Units.VELOCITY_MILLIMETRES_PER_SECOND)
    deviceZ.settings.set('maxspeed', maxspeedZ, Units.VELOCITY_MILLIMETRES_PER_SECOND)

    # Function for moving in XYZ
    def moveXYZ(Xval, Yval, Zval, unit):
        axisX.move_absolute(Xval, unit, wait_until_idle=False)
        axisY.move_absolute(Yval, unit, wait_until_idle=False)
        axisZ.move_absolute(Zval, unit, wait_until_idle=False)

        axisX.wait_until_idle()
        axisY.wait_until_idle()
        axisZ.wait_until_idle()
    
    # Reading from a CSV file and moving the gantry
    with open('path.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        # Check file as empty
        if header != None:
            for row in csv_reader:
                moveXYZ(float(row[0]), float(row[1]), float(row[2]), unit=Units.LENGTH_MILLIMETRES)

print('\n*************** Program finished ***************\n')


