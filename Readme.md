# pyHueISY - Philips Hue and Universal Devices ISY 994i Control Software

This software provides a bridge between Insteon devices, Universal Device's ISY 994i controllers and Philips Hue 
Lighting.

## Installation

The best way to install it is using [virtualenv](https://pypi.python.org/pypi/virtualenv).

1. `virtualenv pyHueISY`
2. `pyHueISY/bin/pip install pyHueISY-X.X.X.tar.gz`
3. `pyHueISY/bin/pyHueISYServer`
4. `http://hostname:5000`

## Configuration

Configuration is done using a web interface.  The Settings page will be displayed until the Hue bridge IP address and 
user name are entered.  In most cases the IP addresses of the Hue bridge and ISY controller will be detected 
automatically.

![Scene Configuration](http://robert-nelson.github.io/pyHueISY/images/settings.png)

Once the settings have been completed you can add your first scene.  A scene comprises a set of Philips' Hue Lights and
a palette of colors.  The scene specifies how the colors should be assigned to the lights.  The most basic form has a 
fixed color assigned to each light.  More complex scenes can specify that lights should be assigned in sequence and then
changed after a specified interval.

![Scene Configuration](http://robert-nelson.github.io/pyHueISY/images/scene.png)

Actions associate Insteon controllers with a set of scenes.  Actions respond to on, off, bright and dim commands.  If an
on command is received when the action is already on then the next scene will be selected.

![Action Configuration](http://robert-nelson.github.io/pyHueISY/images/action.png)

## Acknowledgements

The following open source projects were used to create this project and the possibly modified source code is included:

| Name                                          | Licence                           | Web site
| --------------------------------------------- | --------------------------------- | -------------------------------------------
| jscolor                                       | GNU Lesser General Public License | http://jscolor.com
| css-toggle-switch                             | Unlicense                         | https://github.com/ghinda/css-toggle-switch
| free_icons_for_developers_icons_pack_120612   | Free                              | http://www.all-free-download.com/
| phue                                          | WTFPL - http://www.wtfpl.net      | https://github.com/studioimaginaire/phue
| ISYlib-python                                 | BSD style                         | https://github.com/evilpete/ISYlib-python

There is also a dependency on the following open source projects:

| Name                                          | Licence                           | Web site
| --------------------------------------------- | --------------------------------- | -------------------------------------------
| Flask                                         | BSD style                         | http://flask.pocoo.org/
