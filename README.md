Zaber Motion Control Code
====================

Installation
------------
### Windows

``` {.bash}
# install the library (only needs to be done once)
py -3 -m pip install --user zaber-motion
py -3 -m pip install pySerial
```


How to Run
----------
Install the [graphical launcher](https://software.zaber.com/zaber-launcher/download#download-section)
to view the serial port and establish connections.

Run main.py as following:

```
# open command terminal in the directory where you loaded these files

# You can also open the 'config.json' file to change configs directly or run the command below to change settings.
py -3 main.py -c {config_filename} -p {profile_name}
```

Make sure to check device manager and change your serial ports to the ones used by Zaber and Arduino.



Code Documentation 
------------------

Site is still under construction. Some classes are not yet documented
https://alice-xiong.github.io/magnet_mapper_control/




Further Reading
----------

Documentation Links:

[Zaber Developer Portal](https://www.zaber.com/software/docs/motion-library/ascii/)


