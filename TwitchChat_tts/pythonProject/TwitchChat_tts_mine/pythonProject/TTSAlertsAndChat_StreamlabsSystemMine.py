import os
import codecs
import json
from collections import OrderedDict
import time
import re
import threading
import clr

# clr.AddReference("IronPython.Modules.dll")
# clr.AddReference('System.Speech')
# # clr.AddReferenceToFileAndPath('StreamlabsEventReceiver.dll')
#
# clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "StreamlabsEventReceiver.dll"))
# from System.Speech.Synthesis import SpeechSynthesizer
# from StreamlabsEventReceiver import StreamlabsEventClient

clr.AddReference('System.Speech')
clr.AddReferenceToFileAndPath('IronPython.Modules.dll')
clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "StreamlabsEventReceiver.dll"))

from System.Speech.Synthesis import SpeechSynthesizer
from StreamlabsEventReceiver import StreamlabsEventClient

# Script Information
#---------------------------------------
ScriptName = "TTS Alerts and Chat"
Website = "https://www.twitch.tv/big_kage"
Description = "TTS for Twitch chat"
Creator = "Mikey"
Version = "1.0"

#---------------------------------------
# Socket Receiver
EventReceiver = None

# Setting File Location
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

# UI Config File Location
UIConfigFile = os.path.join(os.path.dirname(__file__), "UI_Config.json")

# banned user and words
bannedUsersFile = os.path.join(os.path.dirname(__file__), "bannedUsers.txt")
bannedWordsFile = os.path.join(os.path.dirname(__file__), "bannedWords.txt")

# TTS Parser
RegTTS = re.compile(r"\$tts\((?P<message>.*?)\)")

SubPlanMap = {
    "Prime": "Prime",
    "1000": "Tier 1",
    "2000": "Tier 2",
    "3000": "Tier 3"
}

class Settings(object):
    """ Load in saved settings file if available else set default values. """

    def __init__(self, settingsfile=None):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            self.VoiceName = ""
            self.Volume = 80
            self.Rate = 0
            self.MaxCharacters = 0
            self.MaxCharacterMessage = "{user}, your message was too long for text-to-speech."
            self.TTSCommand = "!tts"
            self.TTSCommandPermission = "Caster"
            self.TTSCommandPermissionInfo = ""
            self.TTSCommandCost = 500
            self.TTSCommandMessage = "{user} says, {message}"
            self.TTSCommandUsage = "Stream Chat"
            self.TTSCommandUsageReply = False
            self.TTSCommandUsageReplyMessage = "{user} you can only use this command from {usage}!"
            self.TTSUseCD = False
            self.TTSCasterCD = True
            self.TTSCooldown = 0
            self.TTSOnCooldown = "{user} the command is still on cooldown for {cooldown} seconds!"
            self.TTSUserCooldown = 10
            self.TTSOnUserCooldown = "{user} the command is still on user cooldown for {cooldown} seconds!"
            self.TTSAllChat = False
            self.TTSAllChatExcludeCommands = True
            self.TTSAllChatMessage = "{user} says, {message}"
            self.TTSAllChatUsage = "Stream Chat"
            self.TTSAllChatUsageReply = False
            self.TTSAllChatUsageReplyMessage = "{user} you can only use this command from {usage}!"
            self.TTSOverlayExcludeAlerts = True
            self.TTSOverlayMessage = "{user} says, {message}"
            self.TTSOverlayTime = 8
            self.TTSOverlayFontColor = "rgba(255,255,255,1.0)"
            self.TTSOverlayUseFontOutline = False
            self.TTSOverlayFontOutline = "rgba(0,0,0,0)"
            self.TTSOverlayUseFontShadow = True
            self.TTSOverlayFontShadow = "rgba(0,0,0,1.0)"
            self.TTSOverlayFontSize = 32
            self.TTSOverlayFont = ""
            self.TTSOverlayUseBackground = True
            self.TTSOverlayBackgroundColor = "rgba(0,0,0,1.0)"
            self.TTSOverlayUseBorder = True
            self.TTSOverlayBorderColor = "rgba(255,255,255,1.0)"
            self.TTSOverlayHorizontalAlign = "center"
            self.TTSOverlayVerticalAlign = "center"
            self.TTSOverlayAnimateIn = 'fadeIn'
            self.TTSOverlayAnimateOut = 'fadeOut'
            self.MixerOnFollow = False
            self.MixerFollowDelay = 0
            self.MixerFollowMessage = "{name} has followed."
            self.MixerOnHost = False
            self.MixerHostMinimum = 0
            self.MixerHostDelay = 0
            self.MixerHostMessage = "{name} has hosted you with {amount} viewer{isPlural}."
            self.MixerOnSub = False
            self.MixerIncludeSubMessage = True
            self.MixerSubDelay = 0
            self.MixerSubMessage = "{name} has subscribed ({tier})."
            self.MixerResubMessage = "{name} has resubscribed ({tier}) for {months} months."
            self.StreamlabsOnDonation = False
            self.StreamlabsIncludeDonationMessage = True
            self.StreamlabsDonationMinimum = 1
            self.StreamlabsDonationDelay = 0
            self.StreamlabsDonationMessage = "{name} donated {amount}."
            self.TwitchOnCheer = False
            self.TwitchIncludeCheerMessage = True
            self.TwitchCheerMinimum = 100
            self.TwitchCheerDelay = 0
            self.TwitchCheerMessage = "{name} has used {amount} bit{isPlural}."
            self.TwitchOnFollow = False
            self.TwitchFollowDelay = 0
            self.TwitchFollowMessage = "{name} has followed."
            self.TwitchOnHost = False
            self.TwitchHostMinimum = 0
            self.TwitchHostDelay = 0
            self.TwitchHostMessage = "{name} has hosted you with {amount} viewer{isPlural}."
            self.TwitchOnRaid = False
            self.TwitchRaidMinimum = 0
            self.TwitchRaidDelay = 0
            self.TwitchRaidMessage = "{name} has raided you with a party of {amount}."
            self.TwitchOnSub = False
            self.TwitchIncludeSubMessage = True
            self.TwitchSubDelay = 0
            self.TwitchSubMessage = "{name} has subscribed ({tier})."
            self.TwitchResubMessage = "{name} has resubscribed ({tier}) for {months} months."
            self.TwitchGiftMessage = "{gifter} has gifted a sub ({tier}) to {name} ({months} month{isPlural})."
            self.TwitchGiftMassMessage = "{gifter} has gifted {amount} subs to the channel: {recipients}."
            # self.YoutubeOnFollow = False
            # self.YoutubeFollowDelay = 0
            # self.YoutubeFollowMessage = "{name} has followed."
            # self.YoutubeOnSub = False
            # self.YoutubeIncludeSubMessage = True
            # self.YoutubeSubDelay = 0
            # self.YoutubeSubMessage = "{name} has subscribed ({tier})."
            # self.YoutubeResubMessage = "{name} has resubscribed ({tier}) for {months} months."
            # self.YoutubeOnSuperchat = False
            # self.YoutubeIncludeSuperchatMessage = True
            # self.YoutubeSuperchatMinimum = 5
            # self.YoutubeSuperchatDelay = 0
            # self.YoutubeSuperchatMessage = "{name} donated {amount}."
            self.BanUserCommand = "!banuser"
            self.BanUserCommandPermission = "Caster"
            self.BanUserCommandPermissionInfo = ""
            self.BanUserAddResponse = "The user was banned from using TTS."
            self.BanUserResponseResponse = "The user is now able to use TTS."
            self.BanWordCommand = "!banword"
            self.BanWordCommandPermission = "Caster"
            self.BanWordCommandPermissionInfo = ""
            self.BanWordAddResponse = "The word was added to the banned words list."
            self.BanWordRemoveResponse = "The word was removed from the banned words list."
            self.BannedAction = "Skip Messages with Banned Words"
            self.BannedActionBoolean = True
            self.BannedMatchWholeWord = True
            self.BannedReplacement = ""
            self.SocketToken = None

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


def EventReceiverConnected(sender, args):
    Parent.Log(ScriptName, "Connected")
    return

def EventReceiverDisconnected(sender, args):
    Parent.Log(ScriptName, "Disconnected")
    # return

def EventReceiverEvent(sender, args):
	handleEvent(sender,args)

def handleEvent(sender, args):
    # Just grab the all data in from the event
    eventData = args.Data

    # Check if it contains data and for what streaming service it is
    if eventData and eventData.For == "twitch_account":
        if eventData.Type == "follow" and ScriptSettings.TwitchFollow:
            for message in eventData.Message:
                ttsMessage = ScriptSettings.TwitchFollowMessage.foramt(name=message.Name)
                sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.TwitchFollowDelay)
        elif eventData.Type == "bits" and ScriptSettings.TwitchOnCheer:
            s = ''
            for message in eventData.Message:
                if message.Amount >= ScriptSettings.TwitchCheerMinimum:
                    if message.Amount > 1:
                        s = 's'
                    else:
                        s = ''
                    ttsMessage = ScriptSettings.TwitchCheerMessage.format(name=message.Name, amount=message.Amount, isPlural=s)
                    sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.twitchCheerDelay, ScriptSettings.TwitchIncludeCheerMessage, message.Message, message.Name)
        elif eventData.Type == "host" and ScriptSettings.TwitchOnHost:
            s = ''
            for message in eventData.Message:
                if int(message.Viewers) >= ScriptSettings.TwitchHostMinimum:
                    if message.Viewers > 1:
                        s = 's'
                    else:
                        s = ''
                    ttsMessage = ScriptSettings.TwitchHostMessage.format(name=message.Name, amount=str(message.Viewers), isPlural=s)
                    sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.TwitchHostDelay)
        elif eventData.Type == "raid" and ScriptSettings.TwitchOnRaid:
            for message in eventData.Message:
                if int(message.Raiders) <= ScriptSettings.TwitchRaidMinimum:
                    ttsMessage = ScriptSettings.TwitchMessage.format(name=message.Name, amount=str(message.Raiders))
                    sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.TwitchRaidDelay)

        elif eventData.Type == "subscription" and ScriptSettings.TwitchOnSub:
            try:
                s = ''
                if len(eventData.Message) > 1 and eventData.Message[0].Gifter:
                    names = []
                    for message in eventData.Message:
                        names.append(message.Name)
                    gifters = ', '.join(names)
                    ttsMessage = ScriptSettings.TwitchGiftMassMessage.format(recipients=gifters, gifter=message.Gifter, amount=len(names)) # giftees = gifters
                else:
                    for message in eventData.Message:
                        tier = SubPlanMap[str(message.SubPlan)]
                        ttsMessage = ''
                        if message.Gifter:
                            if message.Months > 1:
                                s = 's'
                            else:
                                s = ''
                            ttsMessage = ScriptSettings.TwitchGiftMassMessage.format(name=message.Name, gifter=message.Gifter, tier=tier, months=message.Months, isPlural=s)
                        else:
                            if message.Months == 1:
                                ttsMessage = ScriptSettings.TwitchSubMessage.format(name=message.Name, tier=tier, months=message.Months)
                            else:
                                ttsMessage = ScriptSettings.TwitchResubMessage.format(name=message.Name, tier=tier, months=message.Months)
                sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.TwitchSubDelay, ScriptSettings.TwitchIncludeSubMessage, message.Message, message.Name)
            except Exception as e:
                Parent.SendStreamWhisper(Parent.GetChannelName(), 'Failed to process sub. Please see logs (i).')
                Parent.Log(ScriptName, str(e.args))

    elif eventData and eventData.For == "mixer_account":
        if eventData.Type == "follow" and ScriptSettings.MixerOnFollow:
            for message in eventData.Message:
                ttsMessage = ScriptSettings.MixerFollowMessage.format(name=message.Name)
                sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.MixerFollowDelay)

        elif eventData.Type == "subscription" and ScriptSettings.MixerOnSub:
            for message in eventData.Message:
                ttsMessage = ''
                if message.Months == 1:
                    ttsMessage = ScriptSettings.MixerSubMessage.format(name=message.Name, tier=tier,
                                                                       months=message.Months)
                else:
                    ttsMessage = ScriptSettings.MixerResubMessage.format(name=message.Name, tier=tier,
                                                                         months=message.Months)

                sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.MixerSubDelay,
                                         ScriptSettings.MixerIncludeSubMessage, message.Message, message.Name)

        elif eventData.Type == "host" and ScriptSettings.MixerOnHost:
            s = ''
            for message in eventData.Message:
                if int(message.Viewers) >= ScriptSettings.MixerHostMinimum:
                    if message.Viewers > 1:
                        s = 's'
                    else:
                        s = ''
                    ttsMessage = ScriptSettings.MixerHostMessage.format(name=message.Name, amount=str(message.Viewers),
                                                                        isPlural=s)
                    sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.MixerHostDelay)

    elif eventData and eventData.For == "streamlabs":
        if eventData.Type == "donation" and ScriptSettings.StreamlabsOnDonation:
            for message in eventData.Message:
                if float(message.Amount) >= ScriptSettings.StreamlabsDonationMinimum:
                    ttsMessage = ScriptSettings.StreamlabsDonationMessage.format(name=message.Name, amount=str(message.FormattedAmount))
                    sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.StreamlabsDonationDelay, ScriptSettings.StreamLabsIncludeDonationMessage, message.Message, message.Name)
    #
    # elif eventData and eventData.For == "youtube_account":
    #     if eventData.Type == "follow" and ScriptSettings.YoutubeOnFollow:
    #         for message in eventData.Message:
    #             ttsMessage = ScriptSettings.YoutubeFollowMessage.format(name=message.Name)
    #             sendTTSMessagesWithDelay(ttsMessage,ScriptSettings.YoutubeFollowDelay)
    #
    #     elif eventData.Type == "subscription" and ScriptSettings.YoutubeOnSub:
    #         for message in eventData.Message:
    #             ttsMessage = ''
    #             if message.Months == 1:
    #                 ttsMessage = ScriptSettings.YoutubeSubMessage.format(name=message.Name, tier=tier, months=message.Months)
    #             else:
    #                 ttsMessage = ScriptSettings.YoutubeResubMessage.foramt(name=message.Name, tier=tier, months=message.Months)
    #
    #             sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.YoutubeSubDelay)
    #
    #     elif eventData.Type == "superchat" and ScriptSettings.YoutubeOnSuperchat:
    #         for message in eventData.Message:
    #             if float(message.Amount) >= ScriptSettings.YoutubeSuperchatMinimum:
    #                 ttsMessage = ScriptSettings.YoutubeSuperchatMessage.format(name=message.Name, amount=str(message.FormattedAmount))
    #                 sendTTSMessagesWithDelay(ttsMessage, ScriptSettings.YoutubeSuperchatDelay, ScriptSettings.YoutubeIncludeSuperchatMessage, message.Message, message.Name)
    #

# Script Functions
def updateUIConfig():
    voices = []
    for voice in spk.GetInstalledVoices():
        info = voice.VoiceInfo
        voices.append(info.Name)

    UIConfigs = UIConfig(UIConfigFile)
    UIConfigs.VoiceName['items'] = voices

    if ScriptSettings.VoiceName not in voices:
        ScriptSettings.VoiceName = ''
        ScriptSettings.save(SettingsFile)

    UIConfigs.save(UIConfigFile)

def updateBannedSettings():
    global ScriptSettings, reBanned, bannedWords, bannedUsers
    ScriptSettings.BannedActionBoolean = bool(ScriptSettings. annedAction == 'Skip Messages with Banned Words')

    if ScriptSettings.BannedMatchWholeWord:
        reBanned = re.compile(r"\b({0})\b".format('|'.join(bannedWords)), re.IGNORECASE)
    else:
        reBanned = re.compile(r"({0})".format('|'.join(bannedWords)), re.IGNORECASE)


def SendOverlayUpdate(message):
    """ Send updated info to the overlay"""
    message = message.encode('uf8', 'replace')
    payload = {
        'message': message,
        'time': ScriptSettings.TTSOverlayTime,
        'fontColor': ScriptSettings.TTSOverlayFontColor,
        'useOutline': ScriptSettings.TTSOverlayUseFontOutline,
        'fontOutline': ScriptSettings.TTSOverlayFontOutline,
        'useShadow': ScriptSettings.TTSOverlayUseFontShadow,
        'fontShadow': ScriptSettings.TTSOverlayFontShadow,
        'fontSize': ScriptSettings.TTSOverlayFontSize,
        'font': ScriptSettings.TTSOverlayFont,
        'useBackground': ScriptSettings.TTSOverlayUseBackground,
        'background': ScriptSettings.TTSOverlayBackgroundColor,
        'useBorder': ScriptSettings.TTSOverlayUseBorder,
        'border': ScriptSettings.TTSOverlayBorderColor,
        'horizontalAlign': ScriptSettings.TTSOverlayHorizontalAlign,
        'verticalAlign': ScriptSettings.TTSOverlayVerticalAlign,
        'animateIn': ScriptSettings.TTSOverlayAnimateIn,
        'animateOut': ScriptSettings.TTSOverlayAnimateOut,
    }
    Parent.BroadcastWsEvent("EVENT_TTS_AC_OVERLAY", json.dumps(payload))

def sendTTSMessage(voice, message, isAlert, user = '', text = '', displayName = ''):
    if user and user in bannedUsers:
        return

    if user and not text:
        text = message

    if not isAlert and user and ScriptSettings.MaxCharacters != 0 and len(message) > ScriptSettings.MaxCharacters:
        Parent.SendStreamMessage(ScriptSettings.MaxCharacterMessage.format(user=displayName))
        return

    if ScriptSettings.BannedActionBoolean:
        if bool(reBanned.search(message)):
            return
    else:
        message = reBanned.sub(ScriptSettings.BannedReplacement, message)
        text = reBanned.sub(ScriptSettings.BannedReplacement, text)
        displayName = reBanned.sub(ScriptSettings.BannedReplacement, displayName)

    try:
        if (isAlert and not ScriptSettings.TTSOverlayExcludeAlerts) or (not isAlert and not user):
            SendOverlayUpdate(message)
        elif not isAlert:
            SendOverlayUpdate(ScriptSettings.TTSOverlayMessage.format(user=displayName, message=text))
        voice.Speak(message)
    except Exception as e:
        Parent.SendStreamWhisper(Parent.GetChannelName(), 'TTS Failed... Fuck')
        Parent.Log(ScriptName, str(e.args))

def sendTTSMessagesWithDelay(message, delay, includeExtra = False, extraMessage = '', user =''):
    if delay > 0:
        time.sleep(delay)

    global spk
    sendTTSMessage(spk, message, True)
    if includeExtra:
        sendTTSMessage(spk, extraMessage, False, user)

# Read/Write files
def readFileArray(fileToRead):
    lines = []
    with open(fileToRead) as ft:
        lines = ft.readlines()
    lines = [x.strip().decode("utf-8", "replace") for x in lines]
    return lines

def writeArrayToFile(arrayToWrite, fileToWrite):
    with open(fileToWrite, 'w') as ft:
        ft.write('\n'.join(arrayToWrite).encode('utf8', 'replace'))

# -------------------

# Ban
def handleBanUser(data, user):
    global bannedUsers
    if user in bannedUsers:
        bannedUsers.remove(user)
        Parent.SendStreamMessage(ScriptSettings.BanUserRemoveResponse.format(user=data.UserName, banned=user))
    else:
        bannedUsers.append(user)
        Parent.SendSrteamMessage(ScriptSettings.BanUserAddResponse.forma(user=data.UserName, banned=user))
    writeArrayToFile(bannedUsers, bannedUsersFile)

# ------------------


# Chatbot Initialize func

def Init():
    global ScriptSettings
    ScriptSettings = Settings(SettingsFile)

    global spk
    spk = SpeechSynthesizer()
    spk.Rate = ScriptSettings.Rate
    spk.Volume = ScriptSettings.Volume

    updateUIConfig()

    global bannedWords, bannedUsers
    bannedWords = readFileArray(bannedWordsFile)
    bannedUsers = readFileArray(bannedUsersFile)
    updateBannedSettings()

    if ScriptSettings.VoiceName != '':
        spk.SelectVoice(ScriptSettings.VoiceName)

    # Init the Streamlabs Event Receiver
    global EventReceiver
    EventReceiver = StreamlabsEventClient()
    EventReceiver.StreamlabsSocketConnected += EventReceiverConnected
    EventReceiver.streamlabsSocketDisconneced += EventReceiverDisconnected
    EventReceiver.StreamlabsSocketEvent += EventReceiver

    # Auto connect if key already in settings
    if ScriptSettings.SocketToken:
        EventReceiver.Connect(ScriptSettings.SocketToken)
    return

# ------------------------------


# Chatbot Save Settings Func

def ReloadSettings(jsondata):
    # Reload new save settings and verify
    ScriptSettings.reload(jsondata)

    updateBannedSettings()

    if ScriptSettings.VoiceName != '':
        global spk
        spk.SelectVoice(ScriptSettings.VoiceName)
    spk.Rate = ScriptSettings.Rate
    spk.Volume = ScriptSettings.Volume

    global EventReceiver
    if not EventReceiver.IsConnected and ScriptSettings.SocketToken:
        EventReceiver.Connect(ScriptSettings.SocketToken)
    elif EventReceiver.IsConnected and not ScriptSettings.SocketToken:
        EventReceiver.Disconnect()

    # End of ReloadSettings
    return
# ----------------------------

# Chatbot Scrip unload Func
def unload():
    global EventReceiver
    if EventReceiver.IsConnected:
        EventReceiver.Disconnect()
    EventReceiver = None

# ---------------------------

# [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
def ScriptToggled(state):
    global EventReceiver
    if not state and EventReceiver.IsConnected:
        EventReceiver.Disconnect()
    elif state and not EventReceiver.IsConnected and ScriptSettings.SocketToken:
        EventReceiver.Connect(ScriptSettings.SocketToken)
    return

# ---------------------------

# Chatbot Execute func
def Execute(data):
    if data.IsChatMessage():
        command = data.GetParam(0)

        if command == ScriptSettings.TTSCommand and IsFromValidSource(data, ScriptSettings.TTSCommandUsage, ScriptSettings.TTSCommandUsageReply. ScriptSettings.TTSCommandUsageReplyMessage):
            if HasPermission(data, ScriptSettings.TTSCommandPermission, ScriptSettings.TTSCommandPermissionInfo):
                if not IsOnCoolDown(data, ScriptSettings.TTSCommand, ScriptSettings.TTSCasterCD, ScriptSettings.TTSUseCD, ScriptSettings.TTSOnCooldown, ScriptSettings.TTSOnUserCooldown):
                    if HasCurrency(data, ScriptSettings.TTSCommandCost):
                        commandOffset = len(ScriptSettings.TTSCommand) + 1
                        text = data.Message[commandOffset:]
                        message = ScriptSettings.TTSCommandMessage.format(user=data.UserName, message=text)
                        messageThread = threading.Thread(target=sendTTSMessage, args=(spk, message, False, data.UserName.lower(), text, data.UserName))
                        messageThread.daemon = True
                        messageThread.start()

                        Parent.AddUserCooldown(ScriptName, ScriptSettings.TTSCommand, data.User, ScriptSettings.TTSUserCooldown)
                    Parent.AddCooldown(ScriptName, ScriptSettings.TTSCommand, ScriptSettings.TTSCooldown)
        elif command == ScriptSettings.BanWordCommand and HasPermission(data, ScriptSettings.BanWordCommandPermission, ScriptSettings.BanWordCommandPermissionInfo) and data.GetParamCoount() > 1:
            message = data.GetParam(1)
            i = 2
            while i < data.GetParamCount():
                message = message + ' ' + data.GetParam(i)
                i += 1

            if message:
                global bannedWords
                isPhrase = (' ' in message)
                if message in bannedWords:
                    bannedWords.remove(message)
                    if isPhrase:
                        Parent.SendStreamMessage(ScriptSettings.BanWordRemoveResponse.format(user=data.UserName, word=message))
                    else:
                        Parent.SendStreamMessage(ScriptSettings.BanWordRemoveResponse.format(user=data.UserName, word=message))
                else:
                    bannedWords.append(message)
                    if isPhrase:
                        Parent.SendStreamMessage(ScriptSettings.BanWordAddResponse.format(user=data.UserName, word=message))
                    else:
                        Parent.SendStreamMessage(ScriptSettings.BanWordAddResponse.format(user=data.UserName, word=message))
                writeArrayToFile(bannedWords, bannedWordsFile)
                updateBannedSettings()

        elif command == ScriptSettings.BanUserCommand and HasPermission(data, ScriptSettings.BanUserCommandPermission, ScriptSettings.BanUserCommandPermissionInfo) and data.GetParamCount() > 1:
            user = data.GetParam(1).lower()

            if user:
                handleBanUser(data, user)
                if data.GetParamCount() > 2:
                    time = data.GetParam(2)
                    if time.isdigit():
                        banThread = threading.Timer(int(time), handleBanUser, args=(data, user))
                        banThread.daemon = True
                        banThread.start()

        if ScriptSettings.TTSAllChat and IsFromValidSource(data, ScriptSettings.TTSAllChatUsage, ScriptSettings.TTSAllChatUsageReply, ScriptSettings.TTSAllChatUsageReplyMessage):
            if not ScriptSettings.TTSAllChatExcludeCommands or command[0] != '!':
                message = ScriptSettings.TTSAllChatMessage.format(user=data.UserName, message=data.Message)
                messageThread = threading.Thread(target=sendTTSMessage, args=(spk, message, False, data.UserName.lower(), data.Message, data.UserName))
                messageThread.daemon = True
                messageThread.start()
                
    # End of Execute
    return











# Chatbot Execute helper funcs
def IsFromValidSource(data, usage, sendResponse, usageResponse):
    """Boolean, message sent from source"""
    usedDiscord = data.IsFromDiscord()
    usedWhisper = data.IsWhisper()
    if not usedDiscord:
        l = ["stream Chat", "Chat Both", "All", "Stream Both"]
        if not usedWhisper and (usage in l):
            return True

        l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
        if usedWhisper and (usage in l):
            return True

    if usedDiscord:
        l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
        if not usedWhisper and (usage in l):
            return True

        l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
        if usedWhisper and (usage in l):
            return True

    if sendResponse:
        message = usageResponse.format(user=data.UserName, usage=usage)
        SendResp(data, message)

    return False

def SendResp(data, Message):
    """Sends message to Stream or discord chat depending on settings"""
    if not data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendStreamMessage(Message)

    if not data.IsFromDiscord() and data.IsWhisper():
        Parent.SendStreamWhisper(data.User, Message)

    if data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendStreamMessage(Message)

    if data.IsFromDiscord() and data.IsWhisper():
        Parent.SendDiscordDM(data.User, Message)

def HasPermission(data, permission, permissionInfo):
    """Returns true if user has permission and false if user doesn't"""
    if not Parent.HasPermission(data.User, permission, permissionInfo):
        return False
    else:
        return True

def IsOnCoolDown(data, command, casterCoolDown, useCoolDown, coolDownMessage, userCoolDownMessage):
    """Return true if command is on cooldown and send cooldown message if enabled"""
    cooldown = Parent.IsOnCoolDown(ScriptName, command)
    userCoolDown = Parent.IsOnUserCooldown(ScriptName, command, data.User)
    caster = (Parent.HasPermission(data.User, "Caster", "") and casterCoolDown)

    # Check if command is on cooldown
    if (cooldown or userCoolDown) and caster is False:
        # Check if cooldown message is enabled
        if useCoolDown:

            # Set variables for cooldown
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, command, data.User)

            # Check for the longest CD
            if cooldownDuration > userCDD:
                m_cooldownRemaining = cooldownDuration
                message = coolDownMessage.format(user=data.UserName, cooldown=m_cooldownRemaining)
                SendResp(data, message)
            else:
                m_cooldownRemaining = userCDD
                message = userCoolDownMessage.format(user=data.UserName, cooldown=m_cooldownRemaining)
                SendResp(data, message)
        return True
    return False

def HasCurrency(data, cost):
    if (cost == 0) or (Parent.RemovePoints(data.User, data.UserName, cost)):
        return True
    return False

# Chatbot tick func
def Tick():

    # End of Tick
    return

# Chatbot Parameter Parser
def Parse(parseString, user, target, message):
    res = RegTTS.search(parseString)
    if res:
        paramMessage = res.group(0)
        ttsMessage = res.group("message")
        parseString = parseString.replace(paramMessage, "")

        messageThread = threading.Thread(target=sendTTSMessage, args=(spk, ttsMessage, False))
        messageThread.daemon = True
        messageThread.start()

    # Return unaltered parseString
    return parseString

# Chatbot Button Func
def OpenOverlayFolder():
    os.startfile(os.path.join(os.path.dirname(__file__), "overlay"))

def OpenReadMe():
    os.startfile(os.path.join(os.path.dirname(__file__), "README.txt"))

def OpenBannedWordFile():
    os.startfile(bannedWordsFile)

def OpenBannedUserFile():
    os.startfile(bannedUsersFile)

def OpenAnimateDemo():
    """Open Animation Demo Website"""
    OpenLink("https://daneden.github.io/animate.css/")

def OpenSocketToken():
    """Open Streamlabs API Settings"""
    OpenLink("https://streamlabs.com/dashboard#/settings/api-settings")

def OpenGithubRepository():
    """Open the GitHub Repository for this script"""
    OpenLink("https://github.com")

def OpenTwitter():
    """Open the Twitter of the author"""
    OpenLink("https://twitter.com")

def OpenLink(link):
    """Open links through buttons in UI"""
    os.system("explorer " + link)
