__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

__all__ = ['Director', 'Action', 'Scene', 'ConfigApi']

from flask import Flask


class MyFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update({
        'extensions': ['jinja2.ext.do'],
        'trim_blocks': True,
        'lstrip_blocks': True
    })


app = MyFlask(__package__)

import ConfigApi
