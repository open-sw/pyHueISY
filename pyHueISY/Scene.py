__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

__all__ = ['Scene']

import copy
import logging
import colorsys

Hue_Red = 0
Hue_Yellow = 8191       # 10921
Hue_Green = 19296       # 21843
Hue_Cyan = 30218        # 32768
Hue_Blue = 40959        # 43689
Hue_Magenta = 51699     # 54611

logger = logging.getLogger(__package__)


class Scene(object):
    def __init__(self, **kwargs):
        self.debug = kwargs.get("debug", 0)
        self._shut_down = 0
        self._first_color = 0
        self._brightness = 0
        self._base_brightness = 0
        self._max_brightness = 0

        settings = kwargs.get("settings", {})
        self._name = settings.get("name", "default")
        self._description = settings.get("description", "")
        self._type = settings.get("type", "simple")
        self._interval = settings.get("interval")
        self._transitiontime = settings.get("transitiontime")
        self._colors = settings.get("colors", [])
        self._lights = settings.get("lights", [])
        self.calc_brightness()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if value < 0:
            value = 0
        elif value > self._max_brightness:
            value = self._max_brightness
        self._brightness = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value

    @property
    def transitiontime(self):
        return self._transitiontime

    @transitiontime.setter
    def transitiontime(self, value):
        self._transitiontime = value

    @property
    def colors(self):
        return self._colors

    @property
    def colors_rgb(self):
        colors = []
        for color in self._colors:
            red, green, blue = colorsys.hsv_to_rgb(color['hue'] / 65535.0,
                                                   color['sat'] / 255.0,
                                                   color.get('bri', 128) / 255.0)
            colors.append('%.2X%.2X%.2X' % (int(red * 255), int(green * 255), int(blue * 255)))
        return colors

    def add_color(self, color):
        self._colors.append(color)
        self.calc_brightness()

    def add_color_rgb(self, color):
        rgb = bytearray(color.decode('hex'))
        h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        self._colors.append({'hue': int(h * 65535), 'sat': int(s * 255), 'bri': int(v * 255)})
        self.calc_brightness()

    def remove_color(self, index):
        self._colors.remove(index)
        self.calc_brightness()

    @property
    def lights(self):
        return self._lights

    @property
    def lights_rgb(self):
        lights = []
        for light in self._lights:
            if 'color' in light:
                light_rgb = copy.deepcopy(light)
                red, green, blue = colorsys.hsv_to_rgb(light['color']['hue'] / 65535.0,
                                                       light['color']['sat'] / 255.0,
                                                       light['color'].get('bri', 128) / 255.0)
                light_rgb['color'] = '%.2X%.2X%.2X' % (int(red * 255), int(green * 255), int(blue * 255))
                lights.append(light_rgb)
            else:
                lights.append(light)
        return lights

    def serialize(self):
        action = {'name': self._name, 'description': self._description, 'type': self._type}
        if self._interval is not None:
            action['interval'] = self._interval
        if self._transitiontime is not None:
            action['transitiontime'] = self._transitiontime
        if len(self._colors) > 0:
            action['colors'] = self._colors
        if len(self._lights) > 0:
            action['lights'] = copy.deepcopy(self._lights)
            for light in action['lights']:
                if 'current_brightness' in light:
                    del light['current_brightness']
        return action

    def add_member(self, light):
        self._lights.append(light)
        self.calc_brightness()

    def add_member_rgb(self, light_rgb):
        if 'color' in light_rgb:
            light = copy.deepcopy(light_rgb)
            rgb = bytearray(light_rgb['color'].decode('hex'))
            h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
            light['color'] = {'hue': int(h * 65535), 'sat': int(s * 255), 'bri': int(v * 255)}
        else:
            light = light_rgb
        self._lights.append(light)
        self.calc_brightness()

    def remove_member(self, index):
        self._lights.remove(index)
        self.calc_brightness()

    def off(self, hue_bridge):
        action = {u"on": False}
        if self._transitiontime is not None:
            action[u"transitiontime"] = self._transitiontime
        for light in self._lights:
            if light["type"] == "group":
                hue_bridge.set_group(light["id"], action)
            elif light["type"] == "light":
                hue_bridge.set_light(light["id"], action)
        self._first_color = 0
        self._brightness = self._base_brightness
        return None

    def on(self, hue_bridge):
        color_index = self._first_color
        for light in self._lights:
            if light["mode"] == "auto":
                brightness = self._colors[color_index].get("bri", 128)
                light["current_brightness"] = brightness
                action = self._colors[color_index].copy()
                action[u"bri"] = self._brightness - self._base_brightness + brightness
                action[u"on"] = True
                if self._transitiontime is not None:
                    action[u"transitiontime"] = self._transitiontime
                if light["type"] == "group":
                    hue_bridge.set_group(light["id"], action)
                    #time.sleep(1)
                elif light["type"] == "light":
                    hue_bridge.set_light(light["id"], action)
                color_index += 1
                if color_index >= len(self._colors):
                    color_index = 0
            elif light["mode"] == "manual":
                action = light["color"].copy()
                action[u"bri"] = self._brightness - self._base_brightness + light["color"].get("bri", 128)
                action[u"on"] = True
                if self._transitiontime is not None:
                    action[u"transitiontime"] = self._transitiontime
                if light["type"] == "group":
                    hue_bridge.set_group(light["id"], action)
                elif light["type"] == "light":
                    hue_bridge.set_light(light["id"], action)
            else:
                action = {u"on": False}
                if self._transitiontime is not None:
                    action[u"transitiontime"] = self._transitiontime
                hue_bridge.set_light(light["id"], action)

        if self._type == "simple":
            self._first_color = color_index
        elif self._type == "ascending":
            self._first_color += 1
            if self._first_color >= len(self._colors):
                self._first_color = 0
        elif self._type == "descending":
            self._first_color -= 1
            if self._first_color <= 0:
                self._first_color = len(self._colors) - 1
        return self._interval

    def update_brightness(self, hue_bridge, brightness, transition_time=None):
        self.brightness = brightness
        if transition_time is not None:
            action = {u"transitiontime": transition_time}
        else:
            action = {}
        for light in self._lights:
            if light["mode"] == "auto":
                action[u"bri"] = self._brightness - self._base_brightness + light["current_brightness"]
                action[u"on"] = True
                if light["type"] == "group":
                    hue_bridge.set_group(light["id"], action)
                    #time.sleep(1)
                elif light["type"] == "light":
                    hue_bridge.set_light(light["id"], action)
            elif light["mode"] == "manual":
                action[u"bri"] = self._brightness - self._base_brightness + light["color"].get("bri", 128)
                action[u"on"] = True
                if self._transitiontime is not None:
                    action[u"transitiontime"] = self._transitiontime
                if light["type"] == "group":
                    hue_bridge.set_group(light["id"], action)
                elif light["type"] == "light":
                    hue_bridge.set_light(light["id"], action)


    def calc_brightness(self):
        min_level = 255
        max_level = 0

        for color in self._colors:
            bri = color.get('bri', 128)
            if bri < min_level:
                min_level = bri
            if bri > max_level:
                max_level = bri

        for light in self._lights:
            if light['mode'] == 'manual':
                bri = light['color'].get('bri', 128)
                if bri < min_level:
                    min_level = bri
                if bri > max_level:
                    max_level = bri

        self._max_brightness = 255 - (max_level - min_level)
        self._base_brightness = min_level
        self._brightness = min_level
