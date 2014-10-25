__author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2014 Robert Nelson"
__license__ = "BSD"

import re

import Action
import Scene
from pyHueISY import app
from flask import flash, json, request, redirect, render_template, url_for


@app.route('/')
def index():
    if app.director.settings_complete:
        return redirect(url_for('show_actions'), code=302)
    else:
        return redirect(url_for('show_settings'), code=302)


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
    if app.director.hue_bridge is None:
        flash("Hue bridge settings must be saved first", category="error")
        return redirect(url_for('show_settings'), code=302)
    return render_template('actions.html', triggers=app.director.get_triggers(), actions=app.director.actions)


@app.route('/action/<action_id>', methods=['GET', 'POST'])
def show_action(action_id):
    if app.director.hue_bridge is None:
        flash("Hue bridge settings must be saved first", category="error")
        return redirect(url_for('show_settings'), code=302)
    if request.method == "POST":
        action = parse_action(request.values)
        if action_id != action.name and action_id != 'new':    # Rename
            app.director.rename_action(action_id, action.name)
            flash("Action renamed from " + action_id + " to " + action.name + " and updated")
        elif action_id == "new":
            flash("Action " + action.name + " added")
        else:
            flash("Action " + action.name + " updated")
        app.director.update_action(action)
        app.director.save_config()
        return redirect(url_for('show_actions'), code=303)
    else:
        if action_id == 'new':
            action = Action.Action()
        else:
            action = app.director.actions[action_id]
        return render_template('action.html', action=action, triggers=app.director.get_triggers(),
                               scenes=app.director.scenes)


@app.route('/action/<action_id>/delete')
def delete_action(action_id):
    if app.director.hue_bridge is None:
        flash("Hue bridge settings must be saved first", category="error")
        return redirect(url_for('show_settings'), code=302)
    app.director.delete_action(action_id)
    app.director.save_config()
    flash("Action " + action_id + " deleted")
    return redirect(url_for('show_actions'), code=303)


@app.route('/settings', methods=['GET', 'POST'])
def show_settings():
    if request.method == "POST":
        settings = parse_settings(request.values)
        app.director.update_settings(settings)
        if 'HueRegister' in request.values:
            app.director.register_hue()
        flash("Settings updated")
        app.director.save_config()
        return redirect(url_for('show_settings'), code=303)
    else:
        if app.director.hue_bridge is None:
            disable_nav='disabled'
        else:
            disable_nav=''
        return render_template('settings.html', settings=app.director.settings, disable_nav=disable_nav)


@app.route('/scenes')
def show_scenes():
    if app.director.hue_bridge is None:
        flash("Hue bridge settings must be saved first", category="error")
        return redirect(url_for('show_settings'), code=302)
    return render_template('scenes.html', scenes=app.director.scenes)


@app.route('/scene/<scene_id>/delete')
def delete_scene(scene_id):
    if app.director.hue_bridge is None:
        flash("Hue bridge settings must be saved first", category="error")
        return redirect(url_for('show_settings'), code=302)
    actions = app.director.delete_scene(scene_id)
    if len(actions) > 0:
        flash("Can't delete scene " + scene_id + ", it is referenced by these actions: " + ", ".join(actions),
              category="error")
    else:
        app.director.save_config()
        flash("Scene " + scene_id + " deleted")
    return redirect(url_for('show_scenes'), code=303)


@app.route('/scene/<scene_id>', methods=['GET', 'POST'])
def show_scene(scene_id):
    if app.director.hue_bridge is None:
        flash("Hue bridge settings must be saved first", category="error")
        return redirect(url_for('show_settings'), code=302)
    if request.method == "POST":
        scene = parse_scene(request.values)
        if scene_id != scene.name and scene_id != 'new':
            app.director.rename_scene(scene_id, scene.name)
            flash("Scene renamed from " + scene_id + " to " + scene.name + " and updated")
        elif scene_id == "new":
            flash("Scene " + scene.name + " added")
        else:
            flash("Scene " + scene.name + " updated")
        app.director.update_scene(scene)
        app.director.save_config()
        return redirect(url_for('show_scenes'), code=303)
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
    re_trigger = re.compile(r'trigger\[(\d+)\]')
    re_scene = re.compile(r'scene\[(\d+)\]')
    action = Action.Action()
    if values["name"] != '':
        action.name = values["name"]

    if values["description"] != '':
        action.description = values["description"]

    for value in values:
        m = re_trigger.match(value)
        if m is not None and m.lastindex == 1:
            action.add_trigger(values[value])
        else:
            m = re_scene.match(value)
            if m is not None and m.lastindex == 1:
                action.append_scene(values[value])

    return action


def parse_settings(values):
    return {
        'HueIP': values['HueIP'], 'HueUsername': values['HueUsername'],
        'IsyIP': values['IsyIP'], 'IsyUser': values['IsyUser'], 'IsyPass': values['IsyPass']
    }

