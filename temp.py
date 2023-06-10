from ctypes import *
from contextlib import contextmanager
import pyaudio
import openai
import speech_recognition as sr
import pyttsx3
import time

# From alsa-lib Git 3fd4ab9be0db7c7430ebd258f2717a976381715d
# $ grep -rn snd_lib_error_handler_t
# include/error.h:59:typedef void (*snd_lib_error_handler_t)(const char *file, int line, const char *function, int err, const char *fmt, ...) /* __attribute__ ((format (printf, 5, 6))) */;
# Define our error handler type

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

# Initialize OpenAI API

openai.api_key = "ciao a tutti"

# Initialize the text to speech engine 

engine=pyttsx3.init()

def transcribe_audio_to_test(filename):

    recogizer=sr.Recognizer()

    with sr.AudioFile(filename)as source:

        audio=recogizer.record(source) 

    try:

        return recogizer.recognize_google(audio)

    except:

        print("skipping unkown error")


def generate_response(prompt):

    response= openai.Completion.create(

        engine="text-davinci-003",

        prompt=prompt,

        max_tokens=4000,

        n=1,

        stop=None,

        temperature=0.5,

    )

    return response ["Choices"][0]["text"]

def speak_text(text):

    engine.say(text)

    engine.runAndWait()



def main():

    while True:

        #Waith for user say "genius"

        print("Say 'Genius' to start recording your question")

        with sr.Microphone() as source:

            recognizer=sr.Recognizer()

            audio=recognizer.listen(source)

            try:

                transcription = recognizer.recognize_google(audio)

                if transcription.lower()=="genius":

                    #record audio

                    filename ="input.wav"

                    print("Say your question")

                    with sr.Microphone() as source:

                        recognizer=sr.Recognizer()

                        source.pause_threshold=1

                        audio=recognizer.listen(source,phrase_time_limit=None,timeout=None)

                        with open(filename,"wb")as f:

                            f.write(audio.get_wav_data())

              

                    #transcript audio to test 

                    text=transcribe_audio_to_test(filename)

                    if text:

                        print(f"yuo said {text}")

                        

                        #Generate the response

                        response = generate_response(text)

                        print(f"chat gpt 3 say {response}")

                            

                        #read resopnse using GPT3

                        speak_text(response)

            except Exception as e:

                

                print("An error ocurred : {}".format(e))

if __name__=="__main__":

    main()