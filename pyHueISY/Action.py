__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

__all__ = ['Action']

import logging

DIM_INCR = 25
BRIGHT_INCR = 28
BRIGHT_TIME = 5

logger = logging.getLogger(__package__)


class Action(object):
    def __init__(self, **kwargs):
        # logger.debug("Scene ", self.__class__.__name__)

        self.debug = kwargs.get("debug", 0)
        self._shut_down = 0
        self._on = False
        self._current_scene = 0
        self._ignore_status = False
        self._brightness = 128
        self._brighten_factor = 0

        settings = kwargs.get("settings", {})
        self._name = settings.get("name", "default")
        self._triggers = settings.get("triggers", [])
        self._scenes = settings.get("scenes", [])

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if value < 0:
            value = 0
        elif value > 254:
            value = 254

        self._brightness = value

    @property
    def name(self):
        return self._name

    @property
    def triggers(self):
        return self._triggers

    def add_trigger(self, value):
        self._triggers.append(value)

    def remove_trigger(self, index):
        self._triggers.remove(index)

    @property
    def current_scene(self):
        return self._current_scene

    @current_scene.setter
    def current_scene(self, value):
        if value >= len(self._scenes):
            value = 0
        elif value < 0:
            value = len(self._scenes) - 1
        self._current_scene = value

    @property
    def scenes(self):
        return self._scenes

    def add_scene(self, value):
        self._scenes.append(value)

    def remove_scene(self, index):
        self._scenes.remove(index)

    def on(self, director, ignore_status):
        if self._on:
            if len(self._scenes) > 1:
                self.off(director)
                self.current_scene += 1
        self._ignore_status = ignore_status
        scene = director.lookup_scene(self._scenes[self.current_scene])
        self._brightness = scene.brightness
        wait_time = scene.on(director.hue_bridge)
        if wait_time:
            director.add_scene(wait_time, scene)
        self._on = True

    def off(self, director):
        scene = director.lookup_scene(self._scenes[self.current_scene])
        director.remove_scene(scene)
        scene.off(director.hue_bridge)
        self._on = False

    def begin_lightlevel(self, director, brighten=True):
        if brighten:
            self._brighten_factor = BRIGHT_INCR
        else:
            self._brighten_factor = -DIM_INCR

        director.add_dimmer(self)

    def end_lightlevel(self, director):
        director.remove_dimmer(self)
        self._ignore_status = True

    def update_lightlevel(self, director):
        scene = director.lookup_scene(self._scenes[self.current_scene])
        self.brightness += self._brighten_factor

        if self._on and self.brightness > 0:
            scene.update_brightness(director.hue_bridge, self.brightness, BRIGHT_TIME)
        else:
            scene.off(director.hue_bridge)

    def set_lightlevel(self, director, level):
        if not self._ignore_status:
            if level == 255:
                self.on(director, False)
            elif level == 0:
                self.off(director)
        else:
            self._ignore_status = False
