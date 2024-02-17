
import wavio
import sounddevice as sd
from openai import OpenAI
from pathlib import Path
import pygame


API_KEY = "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"
client = OpenAI(api_key=API_KEY)

def record_audio(duration=5, fs=44100):
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    print("Finished recording.")
    wav_filename = "file.wav"
    wavio.write(wav_filename, recording, fs, sampwidth=2)
    return wav_filename

def recognize_speech(wav_filename):
    try:
        audio_file = open(wav_filename, "rb")
        transcript = client.audio.transcriptions.create(
            model = "whisper-1",
            file = audio_file,
            language = "en",
            response_format = "text",
        )
        user_input = transcript
        # print(user_input)
        return user_input
    except:
        return "Sorry, I didn't catch that. Please try again."

audio = record_audio()
user_input = recognize_speech(audio)
print(user_input)