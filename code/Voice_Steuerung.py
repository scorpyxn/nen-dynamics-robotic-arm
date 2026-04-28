# Voice_Steuerung.py
# NEN Dynamics - Sprachsteuerung für den Roboterarm
# Konvertiert Sprachbefehle in Text und steuert den Aufgaben_Planer

import speech_recognition as sr
import time
import os
import sys

# Pfad zum 'code' Ordner sicherstellen, falls von außerhalb aufgerufen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import Aufgaben_Planer
from Kamera_stream import CameraStream

def hoere_befehl():
    """
    Nimmt Audio vom Mikrofon auf und wandelt es in Text um.
    """
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n Höre zu... (Bitte sprechen)")
        # Umgebungsgeräusche anpassen
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        print(" Verarbeite Sprache...")
        # Google Speech Recognition
        text = recognizer.recognize_google(audio, language="de-DE")
        print(f" Erkannt: '{text}'")
        return text
    except sr.UnknownValueError:
        print(" Konnte nichts verstehen. Bitte deutlicher sprechen.")
        return None
    except sr.RequestError as e:
        print(f" Fehler beim Sprachdienst: {e}")
        return None

def main():
    print("\n=== NEN DYNAMICS - VOICE CONTROL ===")
    print("Initialisiere Systeme...")
    
    # Kamera und KI-Modell laden
    stream = CameraStream().start()
    interpreter = Aufgaben_Planer.modell_laden()
    
    print("-" * 40)
    print("Bereit! Sag einen Befehl (z.B. 'Baue eine Ampel')")
    print("Drücke STRG+C zum Beenden.")
    print("-" * 40)

    try:
        while True:
            befehl = hoere_befehl()
            
            if befehl:
                # Befehl an den Aufgaben-Planer übergeben
                Aufgaben_Planer.aufgabe_starten(befehl, stream, interpreter)
                
            print("\nBereit für den nächsten Befehl...")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nBeende Sprachsteuerung...")
    finally:
        stream.stop()
        print("Programm beendet.")

if __name__ == "__main__":
    main()
