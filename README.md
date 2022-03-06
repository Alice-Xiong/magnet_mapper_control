Zaber Motion Control Code
====================

How to Run
----------
Install the [graphical launcher](https://software.zaber.com/zaber-launcher/download#download-section)
to view the serial port and establish connections.

Open `main.py` file and change `open_serial_port`
to your serial port with Zaber devices.


### Windows

``` {.bash}
# install the library (only needs to be done once)
py -3 -m pip install --user zaber-motion

# open command terminal in the directory where you loaded these files

# check configuration before starting controller
py -3 config_setter.py

# You can also open the 'config.json' file to change configs directly

# run main controller program
py -3 main.py
```


Further Reading
----------

Documentation Links:

[Zaber Developer Portal](https://www.zaber.com/software/docs/motion-library/ascii/)


