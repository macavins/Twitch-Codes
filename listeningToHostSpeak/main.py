from playsound import playsound
import speech_recognition as sr
# from googletrans import Translator
from translate import Translator
# from gtts import gTTS
import os
# import concurrent.futures
# import random
# import time
import keyboard
# import pydirectinput
import pyautogui
from keyCodes import *

recognizer = sr.Recognizer()
translator = Translator(to_lang='en')


def mic():  # Take in mic input
    with sr.Microphone() as source:
        print("Listening on God")
        audio = recognizer.listen(source)
        print("Audio captured")
    return audio


def words_english_text(text):  # idk if we need this
    words = Translator(to_lang="en")
    return words


if __name__ == "__main__":
    while True:
        audio = mic()
        try:
            english_text = recognizer.recognize_google(audio)
            print(f"You said: {english_text}")
            words = english_text.split()
            # translated_text = translator.translate(english_text) # I do not think we need this line lol
            # if english_text.lower() == "up" or "up" in words:
            if "a" in words:
                print("A is pressed")
                HoldAndReleaseKey(A, 2)
            if "hello" in words:
                print("s is pressed")
                HoldAndReleaseKey(S, 2)
            if "up" in words:
                print("w was pressed")
                HoldAndReleaseKey(W, 2)

        except sr.UnknownValueError:
            print("Can not understand you")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")