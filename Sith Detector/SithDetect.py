#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#   Import your Settings class
from Settings_Module import MySettings
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Sith Detector"
Website = "https://www.streamlabs.com"
Description = "Sith Dector game"
Creator = "Mikey"
Version = "1.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
# global SettingsFile
SettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
# global ScriptSettings
ScriptSettings = MySettings()

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init(): # called when ran
    Log("Init Called")

    #   Create Settings Directory
    EnsureLocalDirecoryExists("Settings")

    #   Load settings
    ScriptSettings = MySettings(SettingsFile)
    Log("Init Ended")
    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data): # if there's any data that was received
    Log("Execute Called")
    if not data.IsChatMessage() or not data.IsFromTwitch():
        return 
    
    # if "sith" in data.Message.lower():
    if ScriptSettings.Command.lower() in data.Message.lower():
        number = Parent.GetRandom(0, 100)
        if number < MySettings.SithOdds:
            SendMessage(MySettings.SithMessage)
        else:
            SendMessage(MySettings.JediMessage)

    # if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Command and Parent.IsOnUserCooldown(ScriptName,ScriptSettings.Command,data.User):
    #     Parent.SendStreamMessage("Time Remaining " + str(Parent.GetUserCooldownDuration(ScriptName,ScriptSettings.Command,data.User)))

    Log("Execute Ended")
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick(): # Called constently
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message): # 

    
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    ScriptSettings.__dict__ = json.loads(jsonData)
    ScriptSettings.Save(SettingsFile)
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state): # toggle on/off on chatbot
    return

def EnsureLocalDirecoryExists(dirName): # Creates directory if does not exist
    directory = os.path.join(os.path.dirname(__file__), dirName)
    if not os.path.exists(directory):
        os.makedirs(directory)

def Log(message):
    Parent.Log("SithDetect", str(message))
    return

def SendMessage(message):
    Parent.SendStreamMessage(message)
    return