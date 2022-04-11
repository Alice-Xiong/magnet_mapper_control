File Structure 
==============

===============   ===========================    ===========================================================
Folder            File                           Description
===============   ===========================    ===========================================================
.vscode/          launch.json                    VSCode Debug file
arduino_probe/    arduino_probe.ino              Arduino code to interface with the Teslameter
docs/                                            Generated documentation
data/                                            User generated data                          
path/                                            User generated path
./                .gitignore                     Used to ignore some folders when commiting to GitHub
./                config_default.json            JSON file with default settings for every shape
./                config.json                    JSON file for user to store configuration
./                main.py                        Main python script to start the mapper controller software
./                mapper_base.py                 Contains the ``Mapper`` class
./                mapper_config_setter.py        Contains the ``Config_Setter`` class
./                mapper_datalogger.py           Contains the ``Datalogger`` class
./                mapper_points_generator.py     Contains the ``Points_Generator`` class
===============   ===========================    ===========================================================
