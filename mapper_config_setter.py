#!/usr/bin/env python3
import json
from mapper_base import Mapper

class Config_Setter(Mapper):

    def __init__(self):
        self.config_filename = Mapper.config_filename
        self.config_dict = Mapper.config_dict
        self.profile = Mapper.profile

        # Read configurations from json file
        with open(self.config_filename, 'r') as json_file:
            self.json_load = json.load(json_file)

        self.config_dict = self.json_load[self.profile]
        Mapper.config_dict = self.config_dict

    
    def update_json(self, filename):
        # Load the items from config_dict back into json file
        with open(filename, 'w') as fp:
            fp.write(json.dumps(self.json_load, separators =(', \n', ' : '), sort_keys=False, skipkeys = True))
            fp.close()


    # Edits values in a passed in dict, in a generic way, not having to know ahead of time the name and type of each setting
    # Assumption is made that lists/tuples contain only strings, ints, or float types, and that all members of any list/tuple are same type
    def run(self):
        while True:
            # Dumps standard dictionary settings into an ordered dictionary, prints settings to screen in a numbered fashion from the ordered dictionary,
            # making it easy to select a setting to change. 
            print('\n*************** Current Mapper Settings *******************')
            showDict = {} # Dictionary that stores things to display, temporary
            itemDict = {}
            nP = 0
            for key in self.config_dict:
                value = self.config_dict.get(key)
                showDict.update({nP:{key: value}})
                nP += 1
            for ii in range(0, nP):
                itemDict.update(showDict [ii])
                kvp = itemDict.popitem()
                print(str(ii + 1) +') ', kvp [0], ' = ', kvp [1])
            print('**********************************\n')

            # Start to update dictionary
            inputStr = input('Enter number of setting to edit, or 0 to exit: ')
            # Ensure an integer is entered
            try:
                inputNum = int(inputStr)
            except ValueError as e:
                print('enter a NUMBER for setting, please: %s\n' % str(e))
                continue

            # Exit editting if 0 is entered
            if inputNum == 0:
                # Check whether we are collecting data
                if self.config_dict['collect_data'][0] == 'F' or self.config_dict['collect_data'][0] == 'f':
                    inputStr = input('\nWarning! You are currently not collecting data. Are you sure you want to continue? True (T) or False (F). ')
                    if inputStr [0] == 'T' or inputStr [0] == 't':
                        self.update_json(self.config_filename)
                    else:
                        continue
                break
            else:
                # Set that json file is updated
                self.config_changed = True

                # Display list of settings in json
                itemDict = showDict.get(inputNum -1)
                kvp = itemDict.popitem()
                itemKey = kvp [0]
                itemValue = kvp [1]
                # Edit based on type of input
                if type(itemValue) is str:
                    inputStr = input('Enter a new text value for %s, currently %s: ' %(itemKey, str(itemValue)))
                    updatDict = {itemKey: str(inputStr)}
                elif type(itemValue) is int:
                    inputStr = input('Enter a new integer value for %s, currently %s: ' %(itemKey, str(itemValue)))
                    updatDict = {itemKey: int(inputStr)}
                elif type(itemValue) is float:
                    inputStr = input('Enter a new floating point value for %s, currently %s: ' %(itemKey, str(itemValue)))
                    updatDict = {itemKey: float(inputStr)}
                elif type(itemValue) is list:
                    outputList = []
                    if type(itemValue [0]) is str:
                        inputStr = input('Enter a new comma separated list of strings for %s, currently %s: ' %(itemKey, str(itemValue)))
                        outputList = list(inputStr.split(','))
                    elif type(itemValue [0]) is int:
                        inputStr = input('Enter a new comma separated list of integer values for %s, currently %s: ' %(itemKey, str(itemValue)))
                        for string in inputStr.split(','):
                            try:
                                outputList.append(int(string))
                            except ValueError:
                                continue
                    elif type(itemValue [0]) is float:
                        inputStr = input('Enter a new comma separated list of floating point values for %s, currently %s:' %(itemKey, str(itemValue)))
                        for string in inputStr.split(','):
                            try:
                                outputList.append(float(string))
                            except ValueError:
                                continue
                    if type(itemValue) is tuple:
                        updatDict = {itemKey: tuple(outputList)}
                    else:
                        updatDict = {itemKey: outputList}
                elif type(itemValue) is bool:
                    inputStr = input('%s, True for or False?, currently %s:' %(itemKey, str(itemValue)))
                    if inputStr [0] == 'T' or inputStr [0] == 't':
                        updatDict = {itemKey: True}
                    else:
                        updatDict = {itemKey: False}
                self.config_dict.update(updatDict)

        # Check if values are within bounds
        if self.config_dict['shape'] == 'rectangular':
            if self.config_dict['x_offset'] + int(self.config_dict['x_range'])/2 > 500 or self.config_dict['x_offset'] - int(self.config_dict['x_range'])/2 < 0:
                print("X stage out of range!")
            elif self.config_dict['y_offset'] + int(self.config_dict['y_range'])/2 > 500 or self.config_dict['y_offset'] - int(self.config_dict['y_range'])/2 < 0:
                print("Y stage out of range!")
            elif self.config_dict['z_offset'] + int(self.config_dict['z_range'])/2 > 1000 or self.config_dict['z_offset'] - int(self.config_dict['z_range'])/2 < 0:
                print("Z stage out of range!")
            else:
                print("All stages within bounds of travel. ")
        elif self.config_dict['shape'] == 'cylinder':
            if self.config_dict['x_offset'] + int(self.config_dict['radius'])/2 > 500 or self.config_dict['x_offset'] - int(self.config_dict['radius'])/2 < 0:
                print("X stage out of range!")
            elif self.config_dict['y_offset'] + int(self.config_dict['radius'])/2 > 500 or self.config_dict['y_offset'] - int(self.config_dict['radius'])/2 < 0:
                print("Y stage out of range!")
            elif self.config_dict['z_offset'] + int(self.config_dict['z_range'])/2 > 1000 or self.config_dict['z_offset'] - int(self.config_dict['z_range'])/2 < 0:
                print("Z stage out of range!")
            else:
                print("All stages within bounds of travel. ")

        # Out of while true loop, ask user to save configuration to json file
        inputStr = input('\nDo you want to save these settings? T to save to original file, N to save to a new file, any other key to save nothing. ')
        if inputStr [0] == 'T' or inputStr [0] == 't':
            self.update_json(self.config_filename)

        elif inputStr [0] == 'N' or inputStr [0] == 'n':
            inputStr = input('\nEnter the new filename. (.json will be automatically appended to your filename.) ')
            # update the new filename as active filename across all modules
            self.config_filename = inputStr + '.json'
            Mapper.config_filename = self.config_filename
            # write into new json file
            self.update_json(self.config_filename)
            
        else:
            print('\nConfigurations NOT saved.\n')

