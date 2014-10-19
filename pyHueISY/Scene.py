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
        # logger.debug("Scene ", self.__class__.__name__)

        self.debug = kwargs.get("debug", 0)
        self._shut_down = 0
        self._first_color = 0

        settings = kwargs.get("settings", {})
        self._name = settings.get("name", "default")
        self._description = settings.get("description", "")
        self._type = settings.get("type", "simple")
        self._brightness = settings.get("brightness", 128)
        self._interval = settings.get("interval")
        self._transitiontime = settings.get("transitiontime")
        self._colors = settings.get("colors", [])
        self._lights = settings.get("lights", [])

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
        elif value > 255:
            value = 255

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

    def add_color_rgb(self, color):
        rgb = bytearray(color.decode('hex'))
        h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        self._colors.append({'hue': int(h * 65535), 'sat': int(s * 255), 'bri': int(v * 255)})

    def remove_color(self, index):
        self._colors.remove(index)

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

    def add_member(self, light):
        self._lights.append(light)

    def add_member_rgb(self, light_rgb):
        if 'color' in light_rgb:
            light = copy.deepcopy(light_rgb)
            rgb = bytearray(light_rgb['color'].decode('hex'))
            h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
            light['color'] = {'hue': int(h * 65535), 'sat': int(s * 255), 'bri': int(v * 255)}
        else:
            light = light_rgb
        self._lights.append(light)

    def remove_member(self, index):
        self._lights.remove(index)

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
        self._brightness = 255

        return None

    def on(self, hue_bridge):
        color_index = self._first_color
        for light in self._lights:
            if light["mode"] == "auto":
                action = self._colors[color_index].copy()
                action[u"bri"] = self._brightness
                action[u"on"] = True
                if self._transitiontime is not None:
                    action[u"transitiontime"] = self._transitiontime
                light_ids = []
                if light["type"] == "group":
                    if len(self._colors) == 1:
                        hue_bridge.set_group(light["id"], action)
                        #time.sleep(1)
                    else:
                        light_ids = []
                        for light_id in hue_bridge.get_group(light["id"], "lights"):
                            light_ids.append(int(light_id))
                elif light["type"] == "light":
                    light_ids = [light["id"]]
                light_count = 0
                for light_id in light_ids:
                    light_count += 1
                    if (light_count > 5) and ((light_count % 5) == 1):
                        #time.sleep(1)
                        pass
                    hue_bridge.set_light(light_id, action)
                    color_index += 1
                    if color_index >= len(self._colors):
                        color_index = 0
                    action = self._colors[color_index].copy()
                    action[u"bri"] = self._brightness
                    action[u"on"] = True
                    if self._transitiontime is not None:
                        action[u"transitiontime"] = self._transitiontime
            elif light["mode"] == "manual":
                action = light["color"].copy()
                action[u"bri"] = light.get("bri", 128)
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
        action = {u"bri": brightness}
        if transition_time is not None:
            action[u"transitiontime"] = transition_time
        for light in self._lights:
            if light["type"] == "group":
                hue_bridge.set_group(light["id"], action)
            elif light["type"] == "light":
                hue_bridge.set_light(light["id"], action)
