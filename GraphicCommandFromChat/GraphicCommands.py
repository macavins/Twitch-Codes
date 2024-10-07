"""
TODO:
We need command, graphics
command: $command(<graphic>, <time/delay>)


fetch obs,
fetch twitch chat
"""
from xml.sax import parseString, parse

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

import os
import json
import re
import time
import threading

# Script info
ScriptName = "Graphic Command"
Website = "https://macavins.github.io/My-Website/"
Description = "Have graphic play from chat command"
Creator: "Mikey"
Version = "1.0.0"

# Global Variables
RegOBSScene = None
RegOBSSource = None
RegOBSTmdSrc = None
RegOBSTmdScn = None

# Functions we will use

# Logs callback errors
def CallbackLogger(response):
    parseResponse = json.loads(response)
    if parseResponse["status"] == "error":
        Parent.Log("SLOBS", parseResponse["error"])
    return

# Swap to scene, option: after given amount of secs
def ChangeToScene(scene, delay=None):
    # Swap to scene, option: after given amount of sec
    if delay:
        time.sleep(delay)
    Parent.SetOBSCurrentScene(scene, CallbackLogger)
    return

# Set target source visibility optionally in a scene
def SetSourceVisibility(source, enabled, scene=None):
    Parent.SetOBSSourceRender(source, enabled, scene, CallbackLogger)
    return

# Swap to one scene then to another scene after a set delay
def ChangeScenesTimed(scene_one, scene_two, delay):
    Parent.SetOBSCurrentScene(scene_one, CallbackLogger)
    if delay:
        time.sleep(delay)
    Parent.SetOBSCurrentScene(scene_two, CallbackLogger)
    return

# Disables a given source in optional scene after given amount of secs
def VisibilitySourceTimed(source, mode, delay, scene):
    # off - delay - off
    if mode == "offon":
        Parent.SetOBSSourceRender(source, False, scene, CallbackLogger)
        if delay:
            time.sleep(delay)
        Parent.SetOBSSourceRender(source, True, scene, CallbackLogger)
    # on - delay - off
    else:
        Parent.SetOBSSourceRender(source, True, scene, CallbackLogger)
        if delay:
            time.sleep(delay)
        Parent.SetOBSSourceRender(source, False, scene, CallbackLogger)
    return

# Initialize data
def Init():
    global RegOBSScene
    global RegOBSTmdScn
    global RegOBSTmdSrc
    global RegOBSSource

    # Compile regexes in init
    RegObsScene = re.compile(r"(?:\$OBSscene\([\ ]*[\"\'](?P<scene>[^\"\']+)[\"\'][\ ]*(?:\,[\ ]*[\"\'](?P<delay>\d*)[\"\'][\ ]*)?\))", re.U)
    RegObsSource = re.compile(r"(?P<full>\$OBSsource\([\ ]*[\"\'](?P<source>[^\"\']+)[\"\'][\ ]*\,[\ ]*[\"\'](?P<enabled>[^\"\']*)[\"\'][\ ]*(?:\,[\ ]*[\"\'](?P<scene>[^\"\']*)[\"\'][\ ]*)?\))", re.U)
    RegObsTmdScn = re.compile(r"(?P<full>\$OBStimedScene\([\ ]*[\"\'](?P<s1>[^\"\']+)[\"\'][\ ]*\,[\ ]*[\"\'](?P<s2>[^\"\']+)[\"\'][\ ]*\,[\ ]*[\"\'](?P<delay>\d+)[\"\'][\ ]*\))", re.U)
    RegObsTmdSrc = re.compile(r"(?P<full>\$OBStimedSource\([\ ]*[\"\'](?P<source>[^\"\']+)[\"\'][\ ]*\,[\ ]*[\"\'](?P<mode>onoff|offon)[\"\'][\ ]*\,[\ ]*[\"\'](?P<delay>\d+)[\"\'][\ ]*(?:\,[\ ]*[\"\'](?P<scene>[^\"\']*)[\"\'][\ ]*)?\))", re.U)

    # End of Init
    return

# Parse Parameteres
def Parse(ParseString, user, target, message):
    # $SLOBSscene("scene") parameter
    # $SLOBSscene("scene", "delay") parameter
    if "$SLOBSscene" in parseString:
        result = RegOBSScene.search(parseString)
        if result:
            fullParameterMatch = result.group(0)
            scene = result.group("scene")
            delay = int(result.group("delay")) if result.group("delay") else None

            # Change to another scene using threading
            threading.Thread(target=ChangeToScene, args=(scene, delay)).start()

            # Replace the whole parameter with an empty string
            return parseString.replace(fullParameterMatch, "")

    # $SLOBSscene("scene", "enabled")
    # $SLOBSscene("scene", "enabled", "scene")
    if "$SLOBSsource" in parseString:
        # Apply regex to verify correct parameter use
        result = RegOBSSource.search(parseString)
        if result:
            fullParameterMatch = result.group(0)
            source = result.group("source")
            enabled = False if result.group("enabled").lower() == "false" else True
            scene = result.group("scene") if result.group("scene") else None

            # Thread
            threading.Thread(target=SetSourceVisibility, args=(source, enabled, scene)).start()

            # Replace the whole parameter with an empty string
            return parseString.replace(fullParameterMatch, "")

    # $SLOBStimedScene("scene_one","scene_two","delay")
    if "$SLOBStimedScene" in parseString:
        result = RegOBSTmdScn.search(parseString)
        if result:
            fullParameterMatch = result.group(0)
            scene1 = result.group("s1")
            scene2 = result.group("s2")
            delay = int(result.group("delay")) if result.group("delay") else None

            # Change to scene one then to two after set delay using threading
            threading.Thread(target=ChangeScenesTimed, args=(scene1, scene2, delay)).start()

            # Replace the whole parameter with an empty string
            return parseString.replace(fullParameterMatch, "")

    # $SLOBStimedSource("source", "mode", "delay")
    # $SLOBStimedSource("source", "mode", "delay", "scene")
    if "$SLOBStimedSource" in parseString:
        result = RegOBSTmdSrc.search(parseString)
        if result:
            fullParameterMatch = result.group(0)
            source = result.group("source")
            mode = result.group("mode")
            delay = int(result.group("delay")) if result.group("delay") else None
            scene = result.group("scene") if result.group("scene") else None

            # Start a new thread to disable the source again after amount of given seconds
            threading.Thread(target=VisibilitySourceTimed, args=(source, mode, delay, scene)).start()

            return parseString.replace(fullParameterMatch, "")

    # Stop
    if "$SLOBSstop" in parseString:
        Parent.StopOBSStreaming(CallbackLogger)
        return parseString.replace("$SLOBSstop", "")

    # Return unaltered parseString
    return parseString









