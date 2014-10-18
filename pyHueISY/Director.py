__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

__all__ = ['Director']

import threading

from flask import json

from phue import phue
import ISY
import time

import Action
import Scene

import logging

logger = logging.getLogger(__package__)

insteon_devices = {
    "0.0": {"name": "Control Linc"},
    "0.16": {"name": "Remote Linc 2 - 4 Scene"},
    "0.18": {"name": "Remote Linc 2 - 8 Scene"},
    # "1.14": {"name": "Lamp Linc BiPhy"},
    "1.32": {"name": "Switch Linc Dimmer"},
    "1.65": {"name": "Keypad Linc Dimmer - 8 Button"},
    "1.66": {"name": "Keypad Linc Dimmer - 5 Button"},
    "2.42": {"name": "Switch Linc Relay Dual Band"},
}


class Director(object):

    def __init__(self, **kwargs):
        # print("Scene ", self.__class__.__name__)

        self.debug = kwargs.get("debug", 0)
        self._shut_down = 0
        self._on = False

        self._config = None
        self._scene_thread = None
        self._scene_event = threading.Event()
        self._scene_lock = threading.Lock()
        self._scene_queue = []
        self._scene_shutdown = False

        self._dimmer_thread = None
        self._dimmer_event = threading.Event()
        self._dimmer_lock = threading.Lock()
        self._dimmer_queue = []
        self._dimmer_shutdown = False

        self._Hue_IP = None
        self._Hue_Username = None
        self._Hue_Bridge = None

        self._Isy_IP = None
        self._Isy_User = None
        self._Isy_Pass = None
        self._Isy = None

        self._actions = {}
        self._scenes = {}

        self._trigger_actions = {}

        self._isy_triggers = None
        self._lights = None

        logging.basicConfig(level=logging.DEBUG)

    @property
    def settings(self):
        return {'HueIP': self._Hue_IP, 'HueUsername': self._Hue_Username, 'IsyIP': self._Isy_IP, 'IsyUser': self._Isy_User, 'IsyPass': self._Isy_Pass}

    @property
    def Isy(self):
        return self._Isy

    @property
    def HueBridge(self):
        return self._Hue_Bridge

    @property
    def scenes(self):
        return self._scenes

    def update_scene(self, scene):
        self._scenes[scene.name] = scene

    @property
    def actions(self):
        return self._actions

    def lookup_scene(self, scene_id):
        return self._scenes[scene_id]

    @property
    def config(self):
        return self._config

    def load_config(self):
        config_fp = open('HueISY.json')
        self._config = config = json.load(config_fp)
        config_fp.close()
        
        self._Hue_IP = config.get("HueIP")
        self._Hue_Username = config.get("HueUsername")

        self._Isy_IP = config.get("IsyIP")
        self._Isy_User = config.get("IsyUser")
        self._Isy_Pass = config.get("IsyPass")

        for action_cfg in config.get("actions", []):
            action = Action.Action(settings=action_cfg)
            self._actions[action.name] = action
            for trigger_id in action.triggers:
                self._trigger_actions[trigger_id] = action

        for scene_cfg in config.get("scenes", []):
            scene = Scene.Scene(settings=scene_cfg)
            self._scenes[scene.name] = scene

    def get_triggers(self):
        if self._isy_triggers is None:
            self._isy_triggers = {}
            for node in self._Isy:
                if node.objtype == "node":
                    category, subcat, version, other = node.type.split('.')
                    node_type_info = insteon_devices.get(category + "." + subcat)
                    if node_type_info is not None:
                        node_info = {
                            'name': node.name, 'type': node.type, 'address': node.address, 'type_desc': node_type_info["name"]
                        }
                        self._isy_triggers[node_info['address']] = node_info
                else:
                    print("skipping node", node)
        return self._isy_triggers

    def get_lights_by_id(self):
        return self._Hue_Bridge.get_light_objects(mode="id")

    def get_lights_by_name(self):
        return self._Hue_Bridge.get_light_objects(mode="name")

    def get_groups(self):
        return self._Hue_Bridge.get_group()

    def handle_event(self, data):
        # control == DOF, DON, ST, BMAN, SMAN
        #   BMAN: action - 0 = dim, 1 = bright
        #   ST: action = level
        #   *: node = id
        # action
        #   0 =
        logger.debug("control="+data['Event']["control"]+", action="+data['Event']["action"]+", node="+data['Event']["node"])
        control = data['Event']['control']
        responder = self._trigger_actions.get(data['Event']['node'])
        if responder:
            if control == 'DON':
                responder.on(self, True)
            elif control == 'DOF':
                responder.off(self)
            elif control == 'ST':
                responder.set_lightlevel(self, int(data['Event']['action']))
            elif control == 'BMAN':
                responder.begin_lightlevel(self, int(data['Event']['action']) == 1)
            elif control == 'SMAN':
                responder.end_lightlevel(self)

    def start(self):
        self.load_config()
        self._Hue_Bridge = phue.Bridge(ip=self._Hue_IP, username=self._Hue_Username)

        self._Isy = ISY.Isy(addr=self._Isy_IP, userl=self._Isy_User, userp=self._Isy_Pass, eventupdates=1)

        for action_id in self._actions:
            for trigger in self._actions[action_id].triggers:
                self._Isy.callback_set(trigger, lambda data: self.handle_event(data))

        self.start_scene_thread()
        self.start_dimmer_thread()

    def start_scene_thread(self):
        if self._scene_thread and isinstance(self._scene_thread, threading.Thread):
            if self._scene_thread.is_alive():
                logger.error("Thread already running ?")
                return
        self._scene_shutdown = False
        self._scene_event.clear()

        self._scene_thread = threading.Thread(target=lambda: self.scene_thread())
        self._scene_thread.daemon = True
        self._scene_thread.start()

    def stop_scene_thread(self):
        if self._scene_thread and isinstance(self._scene_thread, threading.Thread):
            self._scene_shutdown = True
            self._scene_event.set()
            self._scene_thread.join()

    def add_scene(self, wait_time, scene):
        while not self._scene_lock.acquire():
            pass

        self.queue_scene(time.clock() + wait_time, scene)

        self._scene_lock.release()
        self._scene_event.set()

    def remove_scene(self, scene):
        while not self._scene_lock.acquire():
            pass

        for index in range(len(self._scene_queue)):
            if self._scene_queue[index][1] is scene:
                del self._scene_queue[index]
                break

        self._scene_lock.release()
        self._scene_event.set()

    def remove_all_scenes(self):
        while not self._scene_lock.acquire():
            pass

        while len(self._scene_queue) > 0:
            (schedule_time, scene) = self._scene_queue.pop()
            scene.off(self.HueBridge)

        self._scene_lock.release()
        self._scene_event.set()

    def scene_thread(self):
        timeout = None
        while True:
            if self._scene_event.wait(timeout=timeout):
                if self._scene_shutdown:
                    self.remove_all_scenes()
                    break

            while not self._scene_lock.acquire():
                pass

            self._scene_event.clear()

            while len(self._scene_queue) > 0:
                now = time.clock()
                if self._scene_queue[0][0] <= now:
                    next_scene = self._scene_queue.pop(0)[1]
                    new_time = next_scene.on(self.HueBridge)
                    if new_time:
                        self.queue_scene(now + new_time, next_scene)
                else:
                    break

            if len(self._scene_queue) > 0:
                timeout = self._scene_queue[0][0] - time.clock()
            else:
                timeout = None

            self._scene_lock.release()

    def queue_scene(self, future_time, scene):
        inserted = False
        for index in range(len(self._scene_queue) - 1, -1, -1):
            if self._scene_queue[index][0] <= future_time:
                self._scene_queue.insert(index + 1, (future_time, scene))
                inserted = True
                break
        if not inserted:
            self._scene_queue.insert(0, (future_time, scene))

    def start_dimmer_thread(self):
        if self._dimmer_thread and isinstance(self._dimmer_thread, threading.Thread):
            if self._dimmer_thread.is_alive():
                logger.error("Thread already running ?")
                return
        self._dimmer_shutdown = False
        self._dimmer_event.clear()

        self._dimmer_thread = threading.Thread(target=lambda: self.dimmer_thread())
        self._dimmer_thread.daemon = True
        self._dimmer_thread.start()

    def stop_dimmer_thread(self):
        if self._dimmer_thread and isinstance(self._dimmer_thread, threading.Thread):
            self._dimmer_shutdown = True
            self._dimmer_event.set()
            self._dimmer_thread.join()

    def add_dimmer(self, responder):
        while not self._dimmer_lock.acquire():
            pass

        self._dimmer_queue.append(responder)

        self._dimmer_lock.release()
        self._dimmer_event.set()

    def remove_dimmer(self, responder):
        while not self._dimmer_lock.acquire():
            pass

        for index in range(len(self._dimmer_queue)):
            if self._dimmer_queue[index] is responder:
                del self._dimmer_queue[index]
                break

        self._dimmer_lock.release()
        self._dimmer_event.set()

    def remove_all_dimmers(self):
        while not self._dimmer_lock.acquire():
            pass

        while len(self._dimmer_queue) > 0:
            self._dimmer_queue.pop()

        self._dimmer_lock.release()
        self._dimmer_event.set()

    def dimmer_thread(self):
        timeout = None
        while True:
            if self._dimmer_event.wait(timeout=timeout):
                if self._dimmer_shutdown:
                    self.remove_all_dimmers()
                    break

            while not self._dimmer_lock.acquire():
                pass

            self._dimmer_event.clear()

            for responder in self._dimmer_queue:
                responder.update_lightlevel(self)

            if len(self._dimmer_queue) > 0:
                timeout = 0.5
            else:
                timeout = None

            self._dimmer_lock.release()
