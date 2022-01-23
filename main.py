from zaber_motion import Units, Library
from zaber_motion.ascii import Connection

Library.enable_device_db_store()

with Connection.open_serial_port("COM3") as connection:
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device = device_list[0]
    axis = device.get_axis(1)
    axis.home()

    # test stuff
    # Move to 10mm
    axis.move_absolute(10, Units.LENGTH_MILLIMETRES)

    # Move an additional 20mm
    axis.move_relative(20, Units.LENGTH_MILLIMETRES)


    # start command stream
    stream = device.get_stream(1)
    stream.setup_live(1, 3)

    #set maximum speed
    stream.set_max_speed(0.5, Units.VELOCITY_CENTIMETRES_PER_SECOND)

    # placeholder, this will come from a separate script
    path_in_mm = [(0.00, 1.00, 0.00), (1.00, 1.00, 0.00), (2.00, 1.00, 0.00), (3.00, 1.00, 0.00), (4.00, 1.00, 0.00)]
    for point in path_in_mm:
        stream.line_absolute(
            Measurement(point[0], Units.LENGTH_MILLIMETRES),
            Measurement(point[1], Units.LENGTH_MILLIMETRES),
            Measurement(point[2], Units.LENGTH_MILLIMETRES)
        )