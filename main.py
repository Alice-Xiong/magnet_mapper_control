import json

# Read configurations from 'config.json'
with open('config.json', 'r') as json_file:
	json_load = json.load(json_file)

profile = 'test'
config_dict = json_load[profile]

# Edits values in a passed in dict, in a generic way, not having to know ahead of time the name and type of each setting
# Assumption is made that lists/tuples contain only strings, ints, or float types, and that all members of any list/tuple are same type

while True:
    # Dumps standard dictionary settings into an ordered dictionary, prints settings to screen in a numbered fashion from the ordered dictionary,
    # making it easy to select a setting to change. 
    print('\n*************** Current Mapper Settings *******************')
    showDict = {} # Dictionary that stores things to display, temporary
    itemDict = {}
    nP = 0
    for key in config_dict:
        value = config_dict.get(key)
        showDict.update({nP:{key: value}})
        nP += 1
    for ii in range(0, nP):
        itemDict.update(showDict [ii])
        kvp = itemDict.popitem()
        print(str(ii + 1) +') ', kvp [0], ' = ', kvp [1])
    print('**********************************\n')

    # Start to update dictionary
    updateDict = {}
    inputStr = input('Enter number of setting to edit, or 0 to exit: ')
    # Ensure an integer is entered
    try:
        inputNum = int(inputStr)
    except ValueError as e:
        print('enter a NUMBER for setting, please: %s\n' % str(e))
        continue

    # Exit editting if 0 is entered
    if inputNum == 0:
        break
    else:
        itemDict = showDict.get(inputNum -1)
        kvp = itemDict.popitem()
        itemKey = kvp [0]
        itemValue = kvp [1]
        # Edit based on type of input
        if type(itemValue) is str:
            inputStr = input('Enter a new text value for %s, currently %s: ' %(itemKey, str(itemValue)))
            updatDict = {itemKey: inputStr}
        elif type(itemValue) is int:
            inputStr = input('Enter a new integer value for %s, currently %s: ' %(itemKey, str(itemValue)))
            updatDict = {itemKey: int(inputStr)}
        elif type(itemValue) is float:
            inputStr = input('Enter a new floating point value for %s, currently %s: ' %(itemKey, str(itemValue)))
            updatDict = {itemKey: float(inputStr)}
        elif type(itemValue) is tuple or itemValue is list:
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
        config_dict.update(updatDict)


# Load the items from config_dict back into json file
with open('config.json', 'w') as fp:
        fp.write(json.dumps(json_load, separators =(', ', ' : '), sort_keys=False, skipkeys = True))
        fp.close()

while True:
    # Run the point generator to convert everything in json to path and write to CSV file
    inputStr = input('\nSetting now updated. Ready to rewrite path CSV? True (T) for or False (F)? ')
    if inputStr [0] == 'T' or inputStr [0] == 't':
        import point_gen
    else:
        print('\n*************** Program cancelled by user. ***************\n')
        break

    # Run main controller
    inputStr = input('Ready to start mapper? True (T) for or False (F)? ')
    if inputStr [0] == 'T' or inputStr [0] == 't':
        import controller
    else:
        print('\n*************** Program cancelled by user. ***************\n')
        break
