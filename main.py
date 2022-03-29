from ast import Continue
import json
from re import T
from mapper_base import Mapper
from mapper_config_setter import Config_Setter
from mapper_points_generator import Points_Generator
from mapper_controller import Controller

# Ask user to input json profile name
inputStr_config = input('Enter your config filename (.json will be automatically appeneded to your filename): ') + ".json"
inputStr_profile = input('Enter your profile name: ')
mapper = Mapper(inputStr_config, inputStr_profile)

# Initialize
config_setter = Config_Setter()
points_generator = Points_Generator()
controller = Controller()

while True:
    # TODO: add case to explore bounds before running the mapper

    # Main menu-ish thing
    print('\n******************** Main Menu ********************\n')
    print('0) Change configurations')
    print('1) Home the mapper')
    print('2) Run mapper along edges of mapping path')
    print('3) Start mapper in full mapping path')
    print('\nPress Q to exit the program')

    # Home stages before magnets turn on
    inputStr = input('\nEnter the number of operation you would like to perform: ')
    if inputStr [0] == '0':
        # Ask user to input json profile name
        config_setter = Config_Setter()

        # Ask user to change settings 
        config_setter.run()

        # Run the point generator to convert everything in json to path and write to CSV file
        inputStr = input('\nSetting now updated. Ready to rewrite path CSV? True (T) to start CSV writing, Quit (Q) to exit the program, and press any key to go back to settings. ')
        if inputStr [0] == 'T' or inputStr [0] == 't':
            points_generator = Points_Generator()
            points_generator.run()
            continue
        elif inputStr [0] == 'Q' or inputStr [0] == 'q':
            print('\n*************** Program cancelled by user. ***************\n')
            break
        else:
            continue

    elif inputStr [0] == '1':
        controller = Controller()
        controller.home()
    elif inputStr [0] == '2':
        points_generator.run()
        points_generator.generate_edges()
        controller = Controller()
        controller.run_edges()
        pass
    elif inputStr [0] == '3':
        controller = Controller()
        controller.run()
    elif inputStr [0] == 'Q' or inputStr [0] == 'q':
        print('\n*************** Program cancelled by user. ***************\n')
        break
    else:
        continue

