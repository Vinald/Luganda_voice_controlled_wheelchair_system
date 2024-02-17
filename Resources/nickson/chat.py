from pathlib import Path
from openai import OpenAI
import sounddevice as sd
import wavio
import pygame



API_KEY = "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"
client = OpenAI(api_key=API_KEY)

def record_audio(duration=7, fs=44100):
    print("Recording...")
    play_audio("beep.mp3")
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

# user_input = input("Enter your input: ")
conversation = [{"role": "system", "content": "Provide brief answers to the asked questions."}]
def gpt_reponse(user_input):
    conversation.append({"role": "user", "content": user_input})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        temperature=0.5,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    response_str = completion.choices[0].message.content.replace("\n", "")
    return response_str
# print(response_str)

def speech_generation(response_str):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model = "tts-1",
        voice = "echo",
        input = response_str,
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path

def play_audio(speech_file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(speech_file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    pygame.mixer.music.stop()
    pygame.mixer.quit() 

while True:
    user_input = record_audio()
    user_input = recognize_speech(user_input)
    gpt_reponse_result = gpt_reponse(user_input)
    audio_generated = speech_generation(gpt_reponse_result)
    play_audio(audio_generated)

    #ask the user if they there is anything else they would like to ask
    #if yes, then loop again
    #if no, then end the program
    #if invalid input, then ask again
    #if no input, then end the program
    another_question = input("Is there anything else you would like to ask? (y/n): ")
    if another_question.lower() != "y":
        break