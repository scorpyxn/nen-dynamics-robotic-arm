# Aufgaben_Planer.py
# NEN Dynamics - Aufgabenplanung mit Gemini API + Teachable Machine Farberkennung
# Verbindet: Farb-KI (project.tm) + Gemini API + Pfadplanung

# ─────────────────────
# 1. IMPORTS
# ─────────────────────
import google.generativeai as genai
import numpy as np
import cv2
import os
import time
import json
from dotenv import load_dotenv

# Teachable Machine (TFLite)
try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

# ─────────────────────
# 2. KONFIGURATION
# ─────────────────────

# API Key aus .env Datei laden (sicher!)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Pfad zum Teachable Machine Modell
# project.tm ist eine ZIP-Datei → erst entpacken!
MODELL_PFAD = "../project.tm"          # Relativer Pfad zur .tm Datei
MODELL_ORDNER = "../assets/ki_modell"  # Entpackt hierhin

# ── Trainierte Farben ──
# WICHTIG: Exakt die gleichen Namen wie in Teachable Machine!
FARB_KLASSEN = [
    "Grüne Würfel",   # Index 0
    "Gelbe Würfel",   # Index 1
    "Blaue Würfel",   # Index 2
    "Weise Würfel",   # Index 3  (Weiße)
    "Natur Würfel",   # Index 4
    "Rote Würfel",    # Index 5
]

# Mapping: TM-Label → einfacher Name (für Gemini & Terminal-Ausgabe)
FARBE_KURZ = {
    "Grüne Würfel": "gruen",
    "Gelbe Würfel": "gelb",
    "Blaue Würfel": "blau",
    "Weise Würfel": "weiss",
    "Natur Würfel": "natur",
    "Rote Würfel":  "rot",
}

# Gemini Modell
gemini = genai.GenerativeModel("gemini-1.5-flash")

# ─────────────────────
# 3. MODELL LADEN
# ─────────────────────

def modell_entpacken():
    """Entpackt project.tm (ZIP) in den assets/ki_modell Ordner."""
    import zipfile
    if not os.path.exists(MODELL_ORDNER):
        os.makedirs(MODELL_ORDNER)
    with zipfile.ZipFile(MODELL_PFAD, 'r') as zip_ref:
        zip_ref.extractall(MODELL_ORDNER)
    print(f"✓ Modell entpackt nach: {MODELL_ORDNER}")

def modell_laden():
    """Lädt das TFLite-Modell aus dem entpackten Ordner."""
    # Modell entpacken falls noch nicht geschehen
    if not os.path.exists(MODELL_ORDNER):
        modell_entpacken()

    # TFLite Modell Datei suchen
    modell_datei = os.path.join(MODELL_ORDNER, "model.tflite")
    if not os.path.exists(modell_datei):
        modell_entpacken()  # Nochmal versuchen

    interpreter = tflite.Interpreter(model_path=modell_datei)
    interpreter.allocate_tensors()
    print("✓ Teachable Machine Farb-KI geladen")
    return interpreter

# ─────────────────────
# 4. FARBERKENNUNG (Eure trainierte KI)
# ─────────────────────

def farbe_erkennen(interpreter, frame):
    """
    Übergibt ein Kamerabild an das TFLite-Modell.
    Gibt die erkannte Farbe + Konfidenz zurück.
    """
    # Input Details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Bild auf Modell-Größe skalieren (Teachable Machine = 224x224)
    bild = cv2.resize(frame, (224, 224))
    bild = cv2.cvtColor(bild, cv2.COLOR_BGR2RGB)
    bild = np.expand_dims(bild, axis=0).astype(np.float32) / 255.0

    # Vorhersage
    interpreter.set_tensor(input_details[0]['index'], bild)
    interpreter.invoke()
    ausgabe = interpreter.get_tensor(output_details[0]['index'])[0]

    # Beste Klasse
    beste_klasse = int(np.argmax(ausgabe))
    konfidenz = float(ausgabe[beste_klasse])
    tm_label = FARB_KLASSEN[beste_klasse]          # z.B. "Grüne Würfel"
    farbe_kurz = FARBE_KURZ.get(tm_label, tm_label) # z.B. "gruen"

    return farbe_kurz, konfidenz

def alle_sichtbaren_farben(interpreter, stream, min_konfidenz=0.85):
    """
    Scannt mehrere Frames und gibt eine Liste der erkannten Blöcke zurück.
    """
    erkannte = []
    for _ in range(10):  # 10 Frames scannen
        ret, frame = stream.get_frame()
        if not ret or frame is None:
            continue
        farbe, konfidenz = farbe_erkennen(interpreter, frame)
        if konfidenz >= min_konfidenz and farbe not in erkannte:
            erkannte.append(farbe)
        time.sleep(0.1)
    return erkannte

# ─────────────────────
# 5. AUFGABEN-PLANUNG (Gemini API)
# ─────────────────────

def gemini_plan_erstellen(befehl, verfuegbare_farben):
    """
    Schickt den Benutzerbefehl + verfügbare Farben an Gemini.
    Gemini gibt die optimale Reihenfolge zurück.
    """
    prompt = f"""
Du steuerst einen Roboterarm mit 6 farbigen Blöcken.
Veifügbare Farben des Systems: gruen, blau, gelb, rot, weiss, natur (Holz).
Diese Blöcke wurden gerade vor der Kamera erkannt: {verfuegbare_farben}

Benutzerbefehl: "{befehl}"

Regeln:
- Verwende NUR Farben aus der erkannten Liste: {verfuegbare_farben}
- Antworte NUR mit einem JSON-Objekt, ohne Erklärung
- "reihenfolge": Farben in Platzier-Reihenfolge (zuerst = unten/hinten/basis)
- "struktur": Name der Struktur (pyramide/turm/ampel/reihe/stapel)
- "beschreibung": Kurze Erklärung was gebaut wird

Beispiel Ampel (rot oben, gelb mitte, gruen unten):
{{"struktur": "ampel", "reihenfolge": ["gruen", "gelb", "rot"], "beschreibung": "Ampel: gruen unten, gelb mitte, rot oben"}}

Beispiel Pyramide (breite Basis unten, Spitze oben):
{{"struktur": "pyramide", "reihenfolge": ["rot", "weiss", "natur", "blau", "gelb", "gruen"], "beschreibung": "Pyramide: 3 unten, 2 mitte, 1 oben"}}

Beispiel Turm (alle übereinander):
{{"struktur": "turm", "reihenfolge": ["natur", "rot", "weiss", "gruen", "blau", "gelb"], "beschreibung": "Turm aus allen verfügbaren Blöcken"}}
"""

    antwort = gemini.generate_content(prompt)
    text = antwort.text.strip()

    # JSON aus Antwort extrahieren (falls Gemini Markdown-Blöcke nutzt)
    if "```" in text:
        text = text.split("```")[1].replace("json", "").strip()

    plan = json.loads(text)
    return plan

# ─────────────────────
# 6. HAUPTFUNKTION
# ─────────────────────

def aufgabe_starten(befehl, stream, interpreter):
    """
    Hauptfunktion: Befehl → Plan → Arm bewegt sich.
    """
    print(f"\n[AUFGABE] '{befehl}'")
    print("─" * 40)

    # Schritt 1: Verfügbare Farben erkennen
    print("📷 Scanne Blöcke...")
    verfuegbare = alle_sichtbaren_farben(interpreter, stream)
    print(f"✓ Erkannte Blöcke: {verfuegbare}")

    if not verfuegbare:
        print("⚠ Keine Blöcke erkannt! Bitte Blöcke vor die Kamera legen.")
        return

    # Schritt 2: Gemini erstellt den Plan
    print("🧠 Gemini plant die Reihenfolge...")
    try:
        plan = gemini_plan_erstellen(befehl, verfuegbare)
        print(f"✓ Plan: {plan['beschreibung']}")
        print(f"  Reihenfolge: {plan['reihenfolge']}")
    except Exception as e:
        print(f"⚠ Gemini Fehler: {e}")
        return

    # Schritt 3: Arm ausführen
    import Pfadplanung
    import Koordinaten_Logik

    Pfadplanung.fahre_zur_startposition()

    for i, farbe in enumerate(plan['reihenfolge']):
        print(f"\n[{i+1}/{len(plan['reihenfolge'])}] Suche {farbe} Block...")

        # Farbe im Live-Bild suchen
        gefunden = False
        for versuch in range(30):  # Max 3 Sekunden suchen
            ret, frame = stream.get_frame()
            if not ret or frame is None:
                continue

            erkannte_farbe, konfidenz = farbe_erkennen(interpreter, frame)

            if erkannte_farbe == farbe and konfidenz >= 0.85:
                # Koordinaten bestimmen
                cx, cy, _ = Koordinaten_Logik.block_position_erkennen(frame)
                if cx is not None:
                    servo_x, servo_y = Koordinaten_Logik.pixel_zu_servo(cx, cy)
                    print(f"✓ {farbe} gefunden! Servo: ({servo_x}, {servo_y})")

                    # Arm greift Block
                    original = Pfadplanung.PICKUP
                    Pfadplanung.PICKUP = (servo_x, servo_y) + original[2:]
                    Pfadplanung.pick_and_place(ebene=i)
                    Pfadplanung.PICKUP = original

                    gefunden = True
                    break
            time.sleep(0.1)

        if not gefunden:
            print(f"⚠ {farbe} Block nicht gefunden, überspringe...")

    print("\n✅ Aufgabe abgeschlossen!")
    Pfadplanung.fahre_zur_startposition()


# ─────────────────────
# 7. STANDALONE TEST
# ─────────────────────

if __name__ == "__main__":
    from Kamera_stream import CameraStream

    stream = CameraStream().start()
    interpreter = modell_laden()

    print("\n=== NEN DYNAMICS - AUFGABEN PLANER ===")
    print("Farben: gruen, blau, gelb, rot, weiss, natur")
    print("-" * 40)
    print("Beispiele:")
    print("  'Baue eine Ampel'                    (rot, gelb, gruen)")
    print("  'Baue eine Pyramide'                 (3 unten, 2 mitte, 1 oben)")
    print("  'Baue einen Turm'                    (alle übereinander)")
    print("  'Baue eine Reihe mit rot weiss natur'")
    print("  'Sortiere nach Farbe'")
    print("  'q' zum Beenden")
    print("=" * 40)

    try:
        while True:
            befehl = input("\nBefehl > ").strip()
            if befehl.lower() == 'q':
                break
            if befehl:
                aufgabe_starten(befehl, stream, interpreter)
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        cv2.destroyAllWindows()
        print("\nProgramm beendet.")
