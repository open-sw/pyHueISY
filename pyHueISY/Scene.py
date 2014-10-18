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
        elif value > 254:
            value = 254

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
    def colorsRGB(self):
        colors = []
        for color in self._colors:
            red, green, blue = colorsys.hsv_to_rgb(color['hue'] / 65535.0, color['sat'] / 254.0, color.get('bri', 128) / 255.0)
            colors.append(('%.2X' % int(red * 255)) + ('%.2X' % int(green * 255)) + ('%.2X' % int(blue * 255)))
        return colors

    def add_color(self, color):
        self._colors.append(color)

    def add_colorRGB(self, color):
        rgb = bytearray(color.decode('hex'))
        h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        self._colors.append({'hue': int(h * 65535), 'sat': int(s * 254), 'bri': int(v * 255)})

    def remove_color(self, index):
        self._colors.remove(index)

    @property
    def lights(self):
        return self._lights

    @property
    def lightsRGB(self):
        lights = []
        for light in self._lights:
            if 'color' in light:
                lightRGB = copy.deepcopy(light)
                red, green, blue = colorsys.hsv_to_rgb(light['color']['hue'] / 65535.0, light['color']['sat'] / 254.0, light['color'].get('bri', 128) / 255.0)
                lightRGB['color'] = ('%.2X' % int(red * 255)) + ('%.2X' % int(green * 255)) + ('%.2X' % int(blue * 255))
                lights.append(lightRGB)
            else:
                lights.append(light)
        return lights

    def add_member(self, light):
        self._lights.append(light)

    def add_memberRGB(self, lightRGB):
        light = {}
        if 'color' in lightRGB:
            light = copy.deepcopy(lightRGB)
            rgb = bytearray(lightRGB['color'].decode('hex'))
            h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
            light['color'] = {'hue': int(h * 65535), 'sat': int(s * 254), 'bri': int(v * 255)}
        else:
            light = lightRGB
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
        self._brightness = 254

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


if __name__ == '__main__':
    from phue import phue
    import time

    bridge = phue.Bridge(ip="172.24.0.22", username="isy994user")

    descending_scene_cfg = {
        "type": "descending",
        "interval": 5,
        "colors": [
            {
                "sat": 220,
                "hue": 65000
            },
            {
                "sat": 220,
                "hue": 44000
            },
            {
                "sat": 220,
                "hue": 33000
            },
            {
                "sat": 220,
                "hue": 22000
            },
            {
                "sat": 220,
                "hue": 11000
            }
        ],
        "members": [
            {
                "type": "group",
                "id": 2
            },
            {
                "type": "light",
                "id": 8
            },
            {
                "type": "light",
                "id": 9
            }
        ]
    }

    primary_scene_cfg = {
        "type": "simple",
        "colors": [
            {
                "sat": 254,
                "hue": 0
            },
            {
                "sat": 254,
                "hue": 21845
            },
            {
                "sat": 254,
                "hue": 43690
            }
        ],
        "members": [
            {
                "type": "group",
                "id": 2
            }
        ]
    }

    complex_scene_cfg = {
        "type": "simple",
        "interval": 5,
        "colors": [
            {
                "sat": 254,
                "hue": 0
            },
            {
                "sat": 254,
                "hue": 19296
            },
            {
                "sat": 254,
                "hue": 40959
            },
            {
                "sat": 254,
                "hue": 8191
            },
            {
                "sat": 254,
                "hue": 30218
            },
            {
                "sat": 254,
                "hue": 51699
            }
        ],
        "members": [
            {
                "type": "group",
                "id": 2
            }
        ]
    }

    simple_scene_cfg = {
        "type": "simple",
        "colors": [
            {
                "sat": 255,
                "hue": 10992
            }
        ],
        "members": [
            {
                "type": "group",
                "id": 2
            }
        ]
    }

    simple_scene = Scene(settings=complex_scene_cfg)

    while False:
        sleep_time = simple_scene.on(bridge)
        if sleep_time is None:
            break
        time.sleep(sleep_time)

    #simple_scene.on(bridge)
    #time.sleep(10)
    #simple_scene.brightness(50)
    #simple_scene.on(bridge)

