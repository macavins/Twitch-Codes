#!/usr/bin/python
# -*- coding: utf-8 -*-

""" RPS-LS

	Classic Rock Paper Scissors mini game and LS extension

	1.0.0
		Initial release

	Upcoming features
		latin to ascii comparisons (Lézard == Lezard) should be True
		Add multiple way to write a choice (ex. French: Pierre, Roche)

"""

# --------------------------------------
# Script Import Libraries
# --------------------------------------
import clr
import os
import json
import codecs
import re

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")


# --------------------------------------
# Script Information
# --------------------------------------
ScriptName = "RPS-masta2"
Website = "https://github.com/macavins"
Description = "Rock Paper Scissors"
Creator = "Mikey"
Version = "2.0.1"


# --------------------------------------
# Script Variables
# --------------------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
cooldown_command = "!rps"
local = {}

winningTable = [
	# 0: rock, 1: paper, 2: scissors, 3: lizard, 4: Spock
	[2, 1, 5],   # cuts
	[1, 0, 6],   # covers
	[0, 2, 7]   # crushes
	# [0, 3, 8],   # crushes
	# [3, 4, 9],   # poisons
	# [4, 2, 10],  # smashes
	# [2, 3, 11],  # decapitates
	# [3, 1, 12],  # eats
	# [1, 4, 13],  # disproves
	# [4, 0, 14]   # vaporizes
]


# --------------------------------------
# Script Classes
# --------------------------------------
class Settings(object):
	""" Load in saved settings file if available else set default values. """

	classic_command = "!rps"
	# lizardspock_command = "!rpsls"
	wordFile = "words.txt"
	reward = 100
	user_cooldown = 60

	def __init__(self, settingsfile=None):
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
				self.__dict__ = json.load(f, encoding="utf-8")
		except:
			return

	def Reload(self, jsondata):
		""" Reload settings from interface by given json data. """
		self.__dict__ = json.loads(jsondata, encoding="utf-8")


# --------------------------------------
# Script Functions
# --------------------------------------
# Utilities
def Log(message):
	Parent.Log(ScriptName, str(message))


def Message(message):
	Parent.SendStreamMessage(str(message))


# def Whisper(target, message):
# 	Parent.SendStreamWhisper(str(target), str(message))


# Functions
def Localization():

	global local

	try:
		# Parse localisation file
		file_name = os.path.join(os.path.dirname(__file__), ScriptSettings.wordFile)
		_file = codecs.open(file_name, encoding="utf-8-sig", mode="r")

		# get all lines, strip \n and remove any comments commencing with #
		lines = [re.sub('#.*', '', line.rstrip('\r\n')) for line in _file]
		# discard all empty and comment line
		local = list(filter(lambda x: x, lines))

	except Exception as e:
		Log("ERROR : Unable to parse localisation file." + str(e))


def add_user_cooldown(data):
	if ScriptSettings.user_cooldown > 0:
		Parent.AddUserCooldown(ScriptName, cooldown_command, data.User, ScriptSettings.user_cooldown)


def giveReward(data):
	if ScriptSettings.reward > 0:
		Parent.AddPoints(data.User, data.UserName, ScriptSettings.reward)


def result(data, user, comp, winner):

	if user != comp:
		if user == winner[0]:
			# win
			giveReward(data)
			res = local[15]
		else:
			# loose
			res = local[16]

		res = res.replace('{phrase}', local[winner[0]] + ' ' + local[winner[2]] + ' ' + local[winner[1]])
	else:
		# tie
		res = local[17]

	res = res.replace('{user}', data.UserName)
	# result = result.replace('{bot}', ... Bot name ? )
	res = res.replace('{user_pick}', local[user])
	res = res.replace('{bot_pick}', local[comp])

	Message(res)


# limit 3 : classic rock, paper, scissors
# limit 5 : rock, paper, scissors, lizard, Spock
def play(data, limit=3):

	if ScriptSettings.user_cooldown > 0:
		duration = Parent.GetUserCooldownDuration(ScriptName, cooldown_command, data.User)
		if duration > 0:
			# Message(data.UserName + ' can\'t use this command for another ' + str(duration) + ' seconds.')
			return

	# parse parameter 1 and try to find its index 1-3 in classic or 1-5 in LS mode
	user_choice_str = data.GetParam(1).lower()

	user_choice = -1
	for c in local:
		user_choice += 1
		if user_choice > limit:
			user_choice = -1
			break
		elif c.lower() == user_choice_str:
			break

	# user_choice -1 : the user gives and invalid option
	if user_choice != -1:

		add_user_cooldown(data)

		# random computer choice
		computer_choice = Parent.GetRandom(0, limit)  # Limit is excluded

		if user_choice == computer_choice:
			# Equality
			result(data, user_choice, computer_choice, None)
		else:
			# Find the choice combination
			for win in winningTable:
				if user_choice in win and computer_choice in win:
					result(data, user_choice, computer_choice, win)
					break


# --------------------------------------
# Chatbot Initialize Function
# --------------------------------------
def Init():

	global ScriptSettings

	# Load settings from settings file
	ScriptSettings = Settings(SettingsFile)

	Localization()


# --------------------------------------
# Chatbot Save Settings Function
# --------------------------------------
def ReloadSettings(jsondata):

	# Reload newly saved settings and verify
	ScriptSettings.Reload(jsondata)
	Localization()


# --------------------------------------
# Chatbot Execute Function
# --------------------------------------
def Execute(data):
	# Twitch chat message only for now
	if not data.IsFromTwitch() or not data.IsChatMessage() or data.IsWhisper():
		return
	command = data.GetParam(0).lower()
	# if len(ScriptSettings.lizardspock_command) > 0 and command == ScriptSettings.lizardspock_command.lower():
	# 	play(data, 5)
	if len(ScriptSettings.classic_command) > 0 and command == ScriptSettings.classic_command.lower():
		play(data, 3)
	return


# --------------------------------------
# Chatbot Script Unload Function
# --------------------------------------
def Unload():
	return


# --------------------------------------
# Chatbot Tick Function
# --------------------------------------
def Tick():
	return
