"""Quick diagnostic to test if TTS audio is actually playing through speakers."""
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")

print("Available voices:")
for i, v in enumerate(voices):
    print(f"  [{i}] {v.name}")

print(f"\nVolume: {engine.getProperty('volume')}")
print(f"Rate: {engine.getProperty('rate')}")

# Set female voice, max volume, slower rate
engine.setProperty("voice", voices[1].id)
engine.setProperty("volume", 1.0)
engine.setProperty("rate", 160)

print("\n--- Speaking now. Check your speakers! ---")
engine.say("Hello! Can you hear me? I am Friday, your personal AI assistant. If you can hear this, your audio is working perfectly.")
engine.runAndWait()
print("--- Done speaking. ---")
