#!/usr/bin/env python3
from ast import Continue
import json
from re import T
from mapper_base import Mapper
from mapper_config_setter import Config_Setter
from mapper_points_generator import Points_Generator
from mapper_controller import Controller
import sys, getopt



def init(argv):
    config_file = 'config.json'
    profile_name = 'test_rectangular'

    # get the config_file and profile_name from arguments when opening the file
    try:
        opts, args = getopt.getopt(argv,"hc:p:",["config_filename=","profile_name="])
    except getopt.GetoptError:
        print('main.py -c <config_filename> -p <profile_name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -c <config_filename> -p <profile_name>')
            sys.exit()
        elif opt in ("-c"):
            config_file = arg
        elif opt in ("-p"):
            profile_name = arg
    print('Config file is ', config_file)
    print('Profile name is ', profile_name)

    return config_file, profile_name

    

def main(argv):
    # Get filenames
    config_file, profile_name = init(argv)

    # Initialize mapper object
    Mapper(config_file, profile_name)

    # Initialize
    config_setter = Config_Setter()
    points_generator = Points_Generator()
    controller = Controller()

    while True:
        # Main menu-ish thing
        print('\n******************** Main Menu ********************\n')
        print('0) Change configurations')
        print('1) Generate path for mapping and for edges')
        print('2) Home the mapper')
        print('3) Run mapper along edges of mapping path')
        print('4) Start mapper in full mapping path')
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
                points_generator.generate_edges()
                continue
            elif inputStr [0] == 'Q' or inputStr [0] == 'q':
                print('\n*************** Program cancelled by user. ***************\n')
                break
            else:
                continue
        elif inputStr [0] == '1':
            points_generator = Points_Generator()
            points_generator.run()
            points_generator.generate_edges()
        elif inputStr [0] == '2':
            controller = Controller()
            controller.home()
        elif inputStr [0] == '3':
            points_generator.generate_edges()
            controller = Controller()
            controller.run_edges()
            pass
        elif inputStr [0] == '4':
            controller = Controller()
            controller.run()
            print('\n*************** Program finished ***************\n')
        elif inputStr [0] == 'Q' or inputStr [0] == 'q':
            print('\n*************** Program cancelled by user. ***************\n')
            break
        else:
            continue



if __name__ == "__main__":
   main(sys.argv[1:])



