#!/usr/bin/python

__author__ = 'Robert Nelson'

from pyHueISY import app, Director

import logging

#logging.basicConfig(level=logging.DEBUG)

app.director = Director.Director(config_path=app.instance_path)
app.director.start()

app.secret_key = app.director.secret_key

app.run(host='0.0.0.0')
