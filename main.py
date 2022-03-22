from ast import Continue
import json
from re import T
from mapper_base import Mapper
from mapper_config_setter import Config_Setter
from mapper_points_generator import Points_Generator
from mapper_controller import Controller

mapper = Mapper()
config_setter = Config_Setter()


while True:
    # Ask user to change settings 
    config_setter.run()

    # Run the point generator to convert everything in json to path and write to CSV file
    inputStr = input('\nSetting now updated. Ready to rewrite path CSV? True (T) to start mapper, Quit (Q) to exit the program, and press any key to go back to settings.?')
    if inputStr [0] == 'T' or inputStr [0] == 't':
        points_generator = Points_Generator()
        path_ready = points_generator.run()
        if not path_ready:
           continue
    elif inputStr [0] == 'Q' or inputStr [0] == 'q':
        print('\n*************** Program cancelled by user. ***************\n')
        break
    else:
        continue

    # TODO: check coordinate system is fixed -- DONE
    # TODO: add timing estimate -- DONE
    # TODO: add case to not collect data (no probe) -- DONE
    # TODO: check rotation stage works
    # TODO: add current limit to every stage
    # TODO: add case to explore bounds before running the mapper
    # TODO: write calibration (rectangular coordinates code)
    # TODO: add case to not collect data (no probe)


    # Home stages before magnets turn on
    inputStr = input('\nReady to home mapper? True (T) to start mapper, Quit (Q) to exit the program, and press any key to go back to settings.? ')
    if inputStr [0] == 'T' or inputStr [0] == 't':
        controller = Controller()
        controller.home()
    elif inputStr [0] == 'Q' or inputStr [0] == 'q':
        print('\n*************** Program cancelled by user. ***************\n')
        break
    else:
        continue

    # Run main controller
    inputStr = input('\nReady to start mapper? True (T) to start mapper, Quit (Q) to exit the program, and press any key to go back to settings.')
    if inputStr [0] == 'T' or inputStr [0] == 't':
        controller.run()
    elif inputStr [0] == 'Q' or inputStr [0] == 'q':
        print('\n*************** Program cancelled by user. ***************\n')
        break
    else:
        continue
