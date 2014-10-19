__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

import re

import Action
import Scene
from pyHueISY import app
from flask import json, request, redirect, render_template, url_for


@app.route('/config/')
def get_config():
    return json.dumps(app.director.get_config()), 200, {"Content-Type": "application/json"}


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


@app.route('/actions')
def show_actions():
    return render_template('actions.html', triggers=app.director.get_triggers(), actions=app.director.actions)


@app.route('/action/<action_id>', methods=['GET', 'POST'])
def show_action(action_id):
    if request.method == "POST":
        action = parse_action(request.values)
        app.director.update_action(action)
        return redirect(url_for('show_action', action_id=action.name), code=303)
    else:
        if action_id == 'new':
            action = Action.Action()
        else:
            action = app.director.actions[action_id]
        return render_template('action.html', action=action, triggers=app.director.get_triggers(),
                               scenes=app.director.scenes)


@app.route('/action/<action_id>/delete')
def delete_action(action_id):
    name, description = app.director.delete_action(action_id)
    return render_template('action_deleted.html', name=name, description=description)


@app.route('/settings', methods=['GET', 'POST'])
def show_settings():
    return render_template('settings.html', settings=app.director.settings)


@app.route('/scenes')
def show_scenes():
    return render_template('scenes.html', scenes=app.director.scenes)


@app.route('/scene/<scene_id>/delete')
def delete_scene(scene_id):
    name, description = app.director.delete_scene(scene_id)
    return render_template('scene_deleted.html', name=name, description=description)


@app.route('/scene/<scene_id>', methods=['GET', 'POST'])
def show_scene(scene_id):
    if request.method == "POST":
        scene = parse_scene(request.values)
        app.director.update_scene(scene)
        return redirect(url_for('show_scene', scene_id=scene.name), code=303)
    else:
        if scene_id == 'new':
            scene = Scene.Scene()
        else:
            scene = app.director.scenes[scene_id]
        return render_template('scene.html', lights=app.director.get_lights_by_id(), groups=app.director.get_groups(),
                               scene=scene)


def parse_scene(values):
    re_light = re.compile(r'light\[(\d+)\]\[(\w+)\]')
    re_color = re.compile(r'color\[(\d+)\]')
    scene = Scene.Scene()
    if values["name"] != '':
        scene.name = values["name"]

    if values["description"] != '':
        scene.description = values["description"]

    if values["transition-time"] != '':
        scene.transitiontime = values["transition-time"]

    if values["type"] != '':
        scene.type = values["type"]

    if values["interval"] != '':
        scene.interval = int(values["interval"])
    lights = {}
    colors = {}
    for value in values:
        m = re_light.match(value)
        if m is not None and m.lastindex == 2:
            index = int(m.group(1))
            if index not in lights:
                lights[index] = {}
            lights[index][m.group(2)] = values[value]
        else:
            m = re_color.match(value)
            if m is not None and m.lastindex == 1:
                colors[int(m.group(1))] = values[value]

    for key in sorted(lights):
        light = lights[key]
        (light_type, light_id) = light['light'].split('-')
        light['type'] = light_type
        light['id'] = int(light_id)
        del light['light']
        scene.add_member_rgb(light)

    for key in sorted(colors):
        scene.add_color_rgb(colors[key])

    return scene


def parse_action(values):
    re_light = re.compile(r'light\[(\d+)\]\[(\w+)\]')
    re_color = re.compile(r'color\[(\d+)\]')
    scene = Scene.Scene()
    if values["name"] != '':
        scene.name = values["name"]

    if values["description"] != '':
        scene.description = values["description"]

    if values["transition-time"] != '':
        scene.transitiontime = values["transition-time"]

    if values["type"] != '':
        scene.type = values["type"]

    if values["interval"] != '':
        scene.interval = int(values["interval"])
    lights = {}
    colors = {}
    for value in values:
        m = re_light.match(value)
        if m is not None and m.lastindex == 2:
            index = int(m.group(1))
            if index not in lights:
                lights[index] = {}
            lights[index][m.group(2)] = values[value]
        else:
            m = re_color.match(value)
            if m is not None and m.lastindex == 1:
                colors[int(m.group(1))] = values[value]

    for key in sorted(lights):
        light = lights[key]
        (light_type, light_id) = light['light'].split('-')
        light['type'] = light_type
        light['id'] = int(light_id)
        del light['light']
        scene.add_member_rgb(light)

    for key in sorted(colors):
        scene.add_color_rgb(colors[key])

    return scene
