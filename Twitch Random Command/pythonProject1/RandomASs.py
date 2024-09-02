import os
import random
import codecs
import json
from collections import OrderedDict
from playsound import playsound

SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

UIConfigFile = os.path.join(os.path.dirname(__file__), "UI_Config.json")


class Settings(object):
    """ Load in saved settings file if available else set default values. """

    def __init__(self, settingsfile=None):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            self.Volume = 80

    def reload(self, jsondata):
        self.__dict__ = json.loads(jsondata, encoding="utf-8")

    def save(self, settingsfile):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")


class UIConfig(object):
    def __init__(self, UIConfigFile=None):
        try:
            with codecs.open(UIConfigFile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8", object_pairs_hook=OrderedDict)
        except:
            Parent.SendStreamWhisper(Parent.GetChannelName(), "Failed to read UIConfig file: " + str(sys.exc_info()[1]))

    def save(self, UIConfigFile):
        if len(self.__dict__) > 0:
            try:
                with codecs.open(UIConfigFile, encoding="utf-8-sig", mode="w+") as f:
                    json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            except:
                Parent.SendStreamWhisper(Parent.GetChannelName(), "Failed to save ui config to file.")


ScriptName = "Random Noises in My Head"
Website = "https://www.twitch.tv/big_kage"
Description = "Random Noises"
Creator = "Mikey"
Version = "1.0"

# Function to play a random sound from a folder
def play_random_sound():
    sound_folder = "sounds/"
    sound_files = os.listdir(sound_folder)
    rand_sound = random.choice(sound_files)
    playsound(os.path.join(sound_folder, rand_sound))

# Event handler for Twitch chat command
def on_command(channel, user, message, args):
    if message == "!random":
        play_random_sound()

# Register the event handler
def Init():
    # Import the Parent object from the Streamlabs Chatbot environment
    global Parent
    # Register the command event
    Parent.RegisterCommand(ScriptName, "!random", on_command)

# Main entry point
def Execute(data):
    return

# Called when the script is unloaded
def Unload():
    return

# Initialize the script
Init()
