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
    inputStr = input('\nSetting now updated. Ready to rewrite path CSV? True (T) for or False (F)? ')
    if inputStr [0] == 'T' or inputStr [0] == 't':
        points_generator = Points_Generator()
        points_generator.run()
    else:
        print('\n*************** Program cancelled by user. ***************\n')
        break

    # Home stages before magnets turn on
    inputStr = input('Ready to home mapper? True (T) for or False (F)? ')
    if inputStr [0] == 'T' or inputStr [0] == 't':
        controller = Controller()
        controller.home()
    else:
        print('\n*************** Program cancelled by user. ***************\n')
        break

    # Run main controller
    inputStr = input('Ready to start mapper? True (T) for or False (F)? ')
    if inputStr [0] == 'T' or inputStr [0] == 't':
        controller.run()
        break
    else:
        print('\n*************** Program cancelled by user. ***************\n')
        break
