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
    """Checks the arguments when running main.py.

    Extracts the ``config_name`` from the '-c' argument. If not found, defaults to ``config_file = 'config.json'``

    Extracts the ``profile_name`` from the '-p' argument. If not found, defaults to ``profile = 'test_rectangular'``

    The ``config_name`` and ``profile_name`` are printed to terminal.

    Args:
        argv: list of arguments when starting the program

    Returns:
        (string, string): name of the config JSON file, name of the profile in config JSON file
    """
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
    """This is the main loop and menu of the program. 

    Args:
        argv: list of arguments when starting the program

    On startup, calls ``init()`` and obtains the ``config_file`` and ``profile_name``. This information is then 
    used to instantiate ``Mapper`` object. As well, ``Config_Setter``, ``Points_Generator``, ``Controller`` are 
    all instantiated. These objects may be updated or recreated throughout the main loop.

    The user is then brought to a menu that contains five options:

    0) Change configurations
    1) Generate path for mapping and for edges
    2) Home the mapper
    3) Run mapper along edges of mapping path
    4) Start mapper in full mapping path

    Each of these options bring the user to a different program:

    **Change configurations**

    Creates a new instance of the ``Config_Setter`` class and allows the user 
    to change any configurations with the user interface.
    
    Afterwards, creates a new instance of ``Points_Generator`` and generates both the full mapping path and 
    the edges path.

    The program asks the user whether they want to change more configurations before exiting back to the main menu.

    **Generate path for mapping and for edges**

    Creates a new instance of ``Points_Generator`` and generates both the full mapping path and 
    the edges path. 
    
    Note that this option should be run whenever configurations are directly changed in the 
    JSON file. If using option 0\) of the menu, no need to run this option.

    **Home the mapper**

    Homes the mapper as the name suggests. This will home all axes -- it is recommended to home after a long 
    time of inactivity to avoid drift.

    **Run mapper along edges of mapping path**

    Regenerates the edges path in case it has not been generated already and then moves the mapper along the 
    edges path. 
    """
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



