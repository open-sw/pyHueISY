#!/usr/bin/python

__author__ = 'Robert Nelson'

from pyHueISY import app, Director

import logging
logging.basicConfig(level=logging.DEBUG)

app.director = Director.Director()
app.director.start()

app.run(debug=True)
