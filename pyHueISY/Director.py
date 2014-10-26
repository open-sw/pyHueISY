__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

__all__ = ['Director']

import base64
import os
import threading
import time

from flask import json

from phue import phue
import ISY

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

        self.debug = kwargs.get("debug", False)
        self._config_path = kwargs.get("config_path", ".")
        self._shut_down = 0
        self._on = False

        self._secret_key = None

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

        self._Hue_IP = ""
        self._Hue_Username = ""
        self._Hue_Bridge = None

        self._Isy_IP = ""
        self._Isy_User = ""
        self._Isy_Pass = ""
        self._isy_controller = None

        self._actions = {}
        self._scenes = {}

        self._trigger_actions = {}

        self._isy_triggers = None
        self._lights = None

    @property
    def settings(self):
        return {'HueIP': self._Hue_IP, 'HueUsername': self._Hue_Username,
                'IsyIP': self._Isy_IP, 'IsyUser': self._Isy_User, 'IsyPass': self._Isy_Pass,
                'SecretKey': self._secret_key}

    def update_settings(self, settings):
        if settings['HueIP'] != self._Hue_IP or settings['HueUsername'] != self._Hue_Username:
            self._Hue_IP = settings['HueIP']
            self._Hue_Username = settings['HueUsername']
            if len(self._Hue_IP) > 0 and len(self._Hue_Username) > 0:
                self._Hue_Bridge = phue.Bridge(ip=self._Hue_IP, username=self._Hue_Username)
            else:
                self._Hue_Bridge = None
        if (settings['IsyIP'] != self._Isy_IP or settings['IsyUser'] != self._Isy_User or
                settings['IsyPass'] != self._Isy_Pass):
            self._Isy_IP = settings['IsyIP']
            self._Isy_User = settings['IsyUser']
            self._Isy_Pass = settings['IsyPass']
            if len(self._Isy_IP) > 0 and len(self._Isy_User) > 0 and len(self._Isy_Pass) > 0:
                self._isy_controller = ISY.Isy(addr=self._Isy_IP, userl=self._Isy_User, userp=self._Isy_Pass,
                                               eventupdates=1)
                for action_id in self._actions:
                    for trigger in self._actions[action_id].triggers:
                        self._isy_controller.callback_set(trigger, lambda data: self.handle_event(data))
            else:
                self._isy_controller = None

    @property
    def settings_complete(self):
        return (len(self._Hue_IP) > 0 and len(self._Hue_Username) > 0 and
                len(self._Isy_IP) > 0 and len(self._Isy_User) > 0 and len(self._Isy_Pass) > 0)

    @property
    def secret_key(self):
        if self._secret_key is None:
            self._secret_key = os.urandom(32)
            self.save_config()
        return self._secret_key

    @property
    def isy_controller(self):
        return self._isy_controller

    @property
    def hue_bridge(self):
        return self._Hue_Bridge

    @property
    def scenes(self):
        return self._scenes

    def rename_scene(self, old, new):
        while not self._scene_lock.acquire():
            pass

        scene = self._scenes[old]
        scene.name = new
        del self._scenes[old]
        self._scenes[scene.name] = scene

        for action_id in self._actions:
            for index, scene_id in enumerate(self._actions[action_id].scenes):
                if scene_id == old:
                    self._actions[action_id].remove_scene(index)
                    self._actions[action_id].insert_scene(index, new)
                    break

        self._scene_lock.release()

    def delete_scene(self, scene_id):
        while not self._scene_lock.acquire():
            pass

        actions = []
        for action_id in sorted(self._actions):
            if scene_id in self._actions[action_id].scenes:
                actions.append(self._actions[action_id].name)

        if len(actions) == 0:
            del self._scenes[scene_id]

        self._scene_lock.release()

        return actions

    def update_scene(self, scene):
        self._scenes[scene.name] = scene

    def lookup_scene(self, scene_id):
        return self._scenes[scene_id]

    @property
    def actions(self):
        return self._actions

    def rename_action(self, old, new):
        for action_id, action in self._actions:
            if action_id == old:
                action.name = new
                del self._actions[action_id]
                self._actions[new] = action

    def update_action(self, action):
        if action.name in self._actions:
            old_action = self._actions[action.name]
            for trigger in old_action.triggers:
                self._isy_controller.callback_del(trigger)
        self._actions[action.name] = action
        for trigger in action.triggers:
            self._trigger_actions[trigger] = action
            self._isy_controller.callback_set(trigger, lambda data: self.handle_event(data))

    def delete_action(self, action_id):
        action = self._actions[action_id]
        action.off(self)
        for trigger in action.triggers:
            self._isy_controller.callback_del(trigger)
            del self._trigger_actions[trigger]
        self.remove_dimmer(action)
        del self._actions[action_id]

    def load_config(self):
        try:
            config_fp = open(os.path.join(self._config_path, 'HueISY.json'))
            config = json.load(config_fp)
            config_fp.close()
        except IOError:
            config = {}

        secret_key = config.get("SecretKey")

        if secret_key is not None:
            self._secret_key = base64.b64decode(secret_key)
        else:
            self._secret_key = None

        self._Hue_IP = config.get("HueIP", "")
        if self._Hue_IP == "":
            self._Hue_IP = phue.Bridge.get_ip_address()
        self._Hue_Username = config.get("HueUsername", "")

        self._Isy_IP = config.get("IsyIP", "")
        if self._Isy_IP == "":
            from ISY.IsyDiscover import isy_discover
            result = isy_discover(timeout=30, count=1)
            if len(result) == 1:
                import urlparse
                self._Isy_IP = urlparse.urlparse(result.values()[0]['URLBase']).netloc

        self._Isy_User = config.get("IsyUser", "")
        self._Isy_Pass = config.get("IsyPass", "")

        for action_cfg in config.get("actions", {}):
            action = Action.Action(settings=action_cfg)
            self._actions[action.name] = action
            for trigger_id in action.triggers:
                self._trigger_actions[trigger_id] = action

        for scene_cfg in config.get("scenes", {}):
            scene = Scene.Scene(settings=scene_cfg)
            self._scenes[scene.name] = scene

    def save_config(self):
        config = self.settings.copy()
        config['SecretKey'] = base64.b64encode(self._secret_key)
        if len(self._actions) > 0:
            config['actions'] = []
            for action_id in sorted(self._actions):
                config['actions'].append(self._actions[action_id].serialize())
        if len(self._scenes) > 0:
            config['scenes'] = []
            for scene_id in sorted(self._scenes):
                config['scenes'].append(self._scenes[scene_id].serialize())
        config_fp = open(os.path.join(self._config_path, 'HueISY.json'), 'w')
        json.dump(config, config_fp, indent=4, separators=(',', ': '), sort_keys=True)
        config_fp.write("\n")
        config_fp.close()

    def register_hue(self):
        self._Hue_Bridge = phue.Bridge(ip=self._Hue_IP)
        self._Hue_Username = self._Hue_Bridge.username

    def get_triggers(self):
        if self._isy_triggers is None:
            self._isy_triggers = {}
            for node in self._isy_controller:
                if node.objtype == "node":
                    category, subcat, version, other = node.type.split('.')
                    node_type_info = insteon_devices.get(category + "." + subcat)
                    if node_type_info is not None:
                        node_info = {
                            'name': node.name,
                            'type': node.type,
                            'address': node.address,
                            'type_desc': node_type_info["name"]
                        }
                        self._isy_triggers[node_info['address']] = node_info
                else:
                    logger.debug("skipping node", node)
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
        logger.debug("control="+data['Event']["control"] +
                     ", action="+data['Event']["action"] +
                     ", node="+data['Event']["node"])
        control = data['Event']['control']
        action = self._trigger_actions.get(data['Event']['node'])
        if action:
            if control == 'DON':
                action.on(self, True)
            elif control == 'DOF':
                action.off(self)
            elif control == 'ST':
                action.set_lightlevel(self, int(data['Event']['action']))
            elif control == 'BMAN':
                action.begin_lightlevel(self, int(data['Event']['action']) == 1)
            elif control == 'SMAN':
                action.end_lightlevel(self)

    def start(self):
        self.load_config()
        if len(self._Hue_IP) > 0 and len(self._Hue_Username) > 0:
            self._Hue_Bridge = phue.Bridge(ip=self._Hue_IP, username=self._Hue_Username)

        if len(self._Isy_IP) > 0 and len(self._Isy_User) > 0 and len(self._Isy_Pass) > 0:
            self._isy_controller = ISY.Isy(addr=self._Isy_IP, userl=self._Isy_User, userp=self._Isy_Pass, eventupdates=1)

            for action_id in self._actions:
                for trigger in self._actions[action_id].triggers:
                    self._isy_controller.callback_set(trigger, lambda data: self.handle_event(data))

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

    def queue_scene(self, wait_time, scene):
        while not self._scene_lock.acquire():
            pass

        self._insert_scene(time.clock() + wait_time, scene)

        self._scene_lock.release()
        self._scene_event.set()

    def dequeue_scene(self, scene):
        while not self._scene_lock.acquire():
            pass

        for index in range(len(self._scene_queue)):
            if self._scene_queue[index][1] is scene:
                del self._scene_queue[index]
                break

        self._scene_lock.release()
        self._scene_event.set()

    def dequeue_all_scenes(self):
        while not self._scene_lock.acquire():
            pass

        while len(self._scene_queue) > 0:
            (schedule_time, scene) = self._scene_queue.pop()
            scene.off(self.hue_bridge)

        self._scene_lock.release()
        self._scene_event.set()

    def scene_thread(self):
        timeout = None
        while True:
            if self._scene_event.wait(timeout=timeout):
                if self._scene_shutdown:
                    self.dequeue_all_scenes()
                    break

            while not self._scene_lock.acquire():
                pass

            self._scene_event.clear()

            while len(self._scene_queue) > 0:
                now = time.clock()
                if self._scene_queue[0][0] <= now:
                    next_scene = self._scene_queue.pop(0)[1]
                    new_time = next_scene.on(self.hue_bridge)
                    if new_time:
                        self._insert_scene(now + new_time, next_scene)
                else:
                    break

            if len(self._scene_queue) > 0:
                timeout = self._scene_queue[0][0] - time.clock()
            else:
                timeout = None

            self._scene_lock.release()

    def _insert_scene(self, future_time, scene):
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

    def add_dimmer(self, action):
        while not self._dimmer_lock.acquire():
            pass

        if action not in self._dimmer_queue:
            self._dimmer_queue.append(action)

        self._dimmer_lock.release()
        self._dimmer_event.set()

    def remove_dimmer(self, action):
        while not self._dimmer_lock.acquire():
            pass

        for index, queue_action in enumerate(self._dimmer_queue):
            if queue_action is action:
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

            for action in self._dimmer_queue:
                action.update_lightlevel(self)

            if len(self._dimmer_queue) > 0:
                timeout = 0.5
            else:
                timeout = None

            self._dimmer_lock.release()
