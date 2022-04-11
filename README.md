Zaber Motion Control Code
====================

Installation
------------
Install python if you have not already. Additionally, install these libraries.
``` {.bash}
# install the library (only needs to be done once)
py -3 -m pip install --user zaber-motion
py -3 -m pip install pySerial
```

Next, clone this repository into a suitable location.
``` {.bash}
git clone https://github.com/Alice-Xiong/magnet_mapper_control.git {name of folder}
```

How to Run
----------
Install the [graphical launcher](https://software.zaber.com/zaber-launcher/download#download-section)
to view the serial port and establish connections.

Run main.py as following:

* Open command terminal in the directory where you loaded these files
* The following command opens a user menu to change the profile and run the mapper. You can also open the 'config.json' file to change configs directly.

```
py -3 main.py -c {config_filename} -p {profile_name}
```

Make sure to check device manager and change your serial ports to the ones used by Zaber and Arduino.



Code Documentation 
------------------

The following GitHub Pages site contains documentation to all classes in this project.

https://alice-xiong.github.io/magnet_mapper_control/

The project final report is also linked in the documentation webpage.




Further Reading
----------

Documentation Links:

[Zaber Developer Portal](https://www.zaber.com/software/docs/motion-library/ascii/)


