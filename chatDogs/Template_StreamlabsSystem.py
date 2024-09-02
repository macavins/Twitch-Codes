# ---------------------------
#   Import Libraries
# ---------------------------
import os
import sys
import json
import random
import codecs

# sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")


# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "Doggos/Animals too"
Website = "https://www.streamlabs.com"
Description = "Reject Humanity, accept Animal"
Creator = "Mikey"
Version = "3.0.2"

# ---------------------------
#   Define Global Variables
# ---------------------------



# class MySettings(object):
#     def __init__(self, settingsfile=None):
#         try:
#             with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
#                 self.__dict__ = json.load(f)
#         except FileNotFoundError:
#             self.Command = "!dog"
#             self.Permission = "everyone"
#             self.Info = ""
#
#     def Reload(self, jsondata):
#         self.__dict__ = json.loads(jsondata)
#         return
#
#     def Save(self, settingsfile):
#         try:
#             with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
#                 json.dump(self.__dict__, f)
#         except FileNotFoundError:
#             Parent.Log(ScriptName, "Failed to save settings to file.")
#         return




class Settings(object):
    """ Load in saved settings file if available else set default values. """

    command = "!dog"
    animalCommand = "!animal"

    def __init__(self, settingsfile=None):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            return

    def Reload(self, jsondata):
        """ Reload settings from interface by given json data. """
        self.__dict__ = json.loads(jsondata, encoding="utf-8")

    def Save(self, settingsfile):
        """ Save settings to file. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f)
        except FileNotFoundError:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return


global ScriptSettings
SettingsFile = os.path.join(os.path.dirname(__file__), "Settings", "settings.json")
ScriptSettings = Settings(SettingsFile)


# ---------------------------
#   [Required] Initialize Data (Only called on load)
# ---------------------------
def Init():
    global SettingsFile, ScriptSettings
    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    SettingsFile = os.path.join(os.path.dirname(__file__), "Settings", "settings.json")
    ScriptSettings = Settings(SettingsFile)
    return


def read_dogs():
    with open('dogs.txt', 'r') as file:
        return [line.strip() for line in file]


def read_animal():
    with open('animals.txt', 'r') as Afile:
        return[line.strip() for line in Afile]


def pick_rand_dog(dogs):
    return random.choice(dogs)

def pick_rand_animal(animals):
    return random.choice(animals)

def Unload():
    # if 'selected_dog' in ScriptSettings:
    #     del ScriptSettings.selected_dog
    return


# ---------------------------
#   [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):
    if not data.IsFromTwitch() or not data.IsChatMessage() or data.IsWhisper():
        return
    if data.GetParam(0).lower() == ScriptSettings.command.lower():
        if 'selected_dog' not in ScriptSettings.__dict__:
            dogs = read_dogs()
            selected_dog = pick_rand_dog(dogs)
            ScriptSettings.__dict__['selected_dog'] = selected_dog
            Parent.SendStreamMessage("The selected dog this stream for you is: {selected_dog}".format(
            selected_dog=ScriptSettings.__dict__['selected_dog']))
            Parent.SendStreamMessage("Reject humanity, accept being a {selected_dog}".format(selected_dog=ScriptSettings.__dict__['selected_dog']))

        else:
            # If a dog has already been selected, respond with it
            Parent.SendStreamMessage("Reject humanity, accept being a {selected_dog}".format(selected_dog=ScriptSettings.__dict__['selected_dog']))

    if data.GetParam(0).lower() == ScriptSettings.animalCommand.lower():
        if 'selected_animal' not in ScriptSettings.__dict__:
            animals = read_animal()
            selected_animal = pick_rand_animal(animals)
            ScriptSettings.__dict__['selected_animal'] = selected_animal
            Parent.SendStreamMessage("The selected animal this stream for you is: {selected_animal}".format(
            selected_animal=ScriptSettings.__dict__['selected_animal']))
            Parent.SendStreamMessage("Reject humanity, accept {selected_animal}".format(selected_animal=ScriptSettings.__dict__['selected_animal']))
        else:
            # If a dog has already been selected, respond with it
            Parent.SendStreamMessage("Reject humanity, accept {selected_animal}".format(selected_animal=ScriptSettings.__dict__['selected_animal']))

    return



# ---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
# ---------------------------
def Tick():
    return


# ---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
# ---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    if "$myparameter" in parseString:
        return parseString.replace("$myparameter", "I am a cat!")

    return parseString


# ---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
# ---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    ScriptSettings.Reload(jsonData)
    ScriptSettings.Save(SettingsFile)
    return


# ---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
# ---------------------------
def ScriptToggled(state):
    return
