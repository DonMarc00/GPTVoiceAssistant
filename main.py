from ctypes import *
from contextlib import contextmanager
import openai
import pyttsx3
import speech_recognition as sr
import time
import pyaudio

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

with noalsaerr():
    p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=1)


openai.api_key = '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'
engine = pyttsx3.init()

def audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        print('Skipping unknown error')

def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response['choices'][0]['text']

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def main():
    while True:

        print('Say Boss')
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio)
                if transcription.lower() == 'genius':
                    filename = 'input.wav'
                    print('say your thing...')
                    with sr.Microphone() as source:
                        recognizer = sr.Recognizer()
                        source.pause_threshold = 1
                        audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                        with open(filename, 'wb') as f:
                            f.write(audio.get_wav_data())

                    text = audio_to_text(filename)
                    if text:
                        print(f'You: {text}')

                        repsonse = generate_response(text)

                        speak_text(repsonse)
            
            except Exception as e:
                print('An error occured: {}'.format(e))

if __name__ == "__main__":
    main()