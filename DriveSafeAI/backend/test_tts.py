import pyttsx3
import time

print("Initializing pyttsx3...")
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

print("Speaking test message 1...")
engine.say("Driver appears drowsy. Please open your eyes.")
engine.runAndWait()

time.sleep(1)

print("Speaking test message 2...")
engine.say("Mobile phone detected. Please put it down.")
engine.runAndWait()

print("TTS Test completed successfully!")
