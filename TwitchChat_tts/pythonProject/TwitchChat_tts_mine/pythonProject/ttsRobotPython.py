import requests
import json
from twitchio.ext import commands
from google.cloud import texttospeech

# Set up Streamlabs API credentials
STREAMLABS_SOCKET_TOKEN = "YOUR_STREAMLABS_SOCKET_TOKEN"

# Twitch Bot setup
bot = commands.Bot(
    # Set up the bot
    irc_token='YOUR_TWITCH_OAUTH_TOKEN_HERE',
    nick='YOUR_TWITCH_BOT_USERNAME_HERE',
    prefix='!',
    initial_channels=['#your_channel_here']
)

def convert_to_audio(text):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

    return "output.mp3"

@bot.event
async def event_message(ctx):
    # Convert the message to audio using a TTS service
    tts_audio = convert_to_audio(ctx.content)

    # Use the Streamlabs Socket API to play the audio on your stream
    requests.post(
        'https://sockets.streamlabs.com/alert',
        data=json.dumps({
            'token': STREAMLABS_SOCKET_TOKEN,
            'type': 'tts',
            'message': tts_audio,
        }),
        headers={'Content-Type': 'application/json'}
    )

    # Read the message in the chat
    await ctx.channel.send(ctx.content)

    await bot.handle_commands(ctx)

if __name__ == "__main__":
    bot.run()
