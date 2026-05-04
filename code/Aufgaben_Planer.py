# Aufgaben_Planer.py
# NEN Dynamics - Aufgabenplanung mit Gemini API + Roboflow Farberkennung
# Verbindet: Roboflow KI (color-classification-w120p/1) + Gemini API + Pfadplanung

# ─────────────────────
# 1. IMPORTS
# ─────────────────────
import google.generativeai as genai
import cv2
import os
import time
import json
import base64
import requests
import numpy as np
from dotenv import load_dotenv

# ─────────────────────
# 2. KONFIGURATION
# ─────────────────────

# API Keys aus .env Datei laden (sicher!)
load_dotenv()
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
ROBOFLOW_API_KEY  = os.getenv("ROBOFLOW_API_KEY")

# Gemini konfigurieren
genai.configure(api_key=GEMINI_API_KEY)

# Roboflow Konfiguration
ROBOFLOW_MODEL_ID  = "color-classification-w120p/1"
ROBOFLOW_API_URL   = "https://serverless.roboflow.com"

# Roboflow Label → interner Farbname
FARBE_MAPPING = {
    "red":    "rot",
    "green":  "gruen",
    "white":  "weiss",
    "blue":   "blau",
    "yellow": "gelb",
    "natur":  "natur",
    # Fallbacks (falls Modell deutschen/anderen Namen zurückgibt)
    "rot":    "rot",
    "gruen":  "gruen",
    "weiss":  "weiss",
    "blau":   "blau",
    "gelb":   "gelb",
}

# ─────────────────────
# 3. ROBOFLOW FARBERKENNUNG
# ─────────────────────

def roboflow_farbe_erkennen(frame):
    """
    Schickt ein Kamerabild an Roboflow und gibt erkannte Farbe + Konfidenz zurück.
    Gibt (farbe_string, konfidenz_float) oder (None, 0.0) bei Fehler zurück.
    """
    try:
        # Bild als JPEG kodieren und Base64 konvertieren
        _, bild_encoded = cv2.imencode(".jpg", frame)
        bild_b64 = base64.b64encode(bild_encoded.tobytes()).decode("utf-8")

        # Roboflow API aufrufen
        url = f"{ROBOFLOW_API_URL}/{ROBOFLOW_MODEL_ID}"
        params = {"api_key": ROBOFLOW_API_KEY}
        antwort = requests.post(url, params=params, data=bild_b64,
                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                timeout=5)
        antwort.raise_for_status()
        daten = antwort.json()

        # Roboflow Klassifikations-Antwort auswerten
        # Format: {"predictions": [{"class": "red", "confidence": 0.95}, ...]}
        vorhersagen = daten.get("predictions", [])
        if not vorhersagen:
            return None, 0.0

        # Beste Vorhersage auswählen
        beste = max(vorhersagen, key=lambda p: p.get("confidence", 0))
        label      = beste.get("class", "").lower()
        konfidenz  = float(beste.get("confidence", 0.0))

        # Label auf internen Farbnamen mappen
        farbe = FARBE_MAPPING.get(label, None)
        return farbe, konfidenz

    except requests.exceptions.Timeout:
        print("  [ROBOFLOW] Timeout – API antwortet nicht")
        return None, 0.0
    except requests.exceptions.RequestException as e:
        print(f"  [ROBOFLOW] Netzwerkfehler: {e}")
        return None, 0.0
    except Exception as e:
        print(f"  [ROBOFLOW] Unbekannter Fehler: {e}")
        return None, 0.0


def roboflow_alle_farben(stream, anzahl_frames=15):
    """
    Scannt mehrere Frames mit Roboflow und gibt eine Liste aller
    erkannten Farben zurück (ohne Duplikate).
    """
    erkannte = []
    print(f"  Scanne {anzahl_frames} Frames mit Roboflow...")

    for i in range(anzahl_frames):
        try:
            ret, frame = stream.get_frame()
            if not ret or frame is None:
                continue

            farbe, konfidenz = roboflow_farbe_erkennen(frame)

            if farbe and konfidenz >= MIN_KONFIDENZ and farbe not in erkannte:
                erkannte.append(farbe)
                print(f"  ✓ Neue Farbe erkannt: {farbe} ({konfidenz:.0%})")

            time.sleep(0.2)  # Kurze Pause zwischen API-Aufrufen

        except Exception as e:
            print(f"  [SCAN] Fehler bei Frame {i}: {e}")
            continue

    return erkannte


# ─────────────────────
# 4. AUFGABEN-PLANUNG (GEMINI)
# ─────────────────────

def gemini_plan_erstellen(befehl, verfuegbare_farben):
    """
    Schickt den Benutzerbefehl + erkannte Farben an Gemini.
    Gibt einen Plan als Dictionary zurück: {struktur, reihenfolge, beschreibung}
    """
    try:
        prompt = (
            f"Erkannte verfügbare Farben: {verfuegbare_farben}\n"
            f"Benutzerbefehl: \"{befehl}\""
        )

        antwort = gemini.generate_content(prompt)
        text = antwort.text.strip()

        # Markdown-Codeblöcke entfernen, falls vorhanden
        if "```" in text:
            teile = text.split("```")
            # Mittleres Element enthält den JSON-Code
            text = teile[1].replace("json", "").strip()

        plan = json.loads(text)
        return plan

    except json.JSONDecodeError as e:
        print(f"  [GEMINI] JSON-Fehler: {e}\n  Antwort war: {text}")
        raise
    except Exception as e:
        print(f"  [GEMINI] Fehler: {e}")
        raise


# ─────────────────────
# 5. HAUPTFUNKTION
# ─────────────────────

def aufgabe_starten(befehl, stream):
    """
    Hauptfunktion: Sprachbefehl/Text → Gemini-Plan → Arm führt aus.
    Parameter:
        befehl (str): Natürlichsprachlicher Befehl (z.B. "Baue eine Ampel")
        stream: CameraStream-Instanz
    """
    print(f"\n[AUFGABE] '{befehl}'")
    print("─" * 40)

    # ── Schritt 1: Blöcke scannen ──
    print("📷 Scanne Blöcke mit Roboflow...")
    verfuegbare = roboflow_alle_farben(stream)
    print(f"  Erkannte Blöcke: {verfuegbare}")

    if not verfuegbare:
        print("  ⚠ Keine Blöcke erkannt! Bitte Blöcke vor die Kamera legen.")
        return

    # ── Schritt 2: Gemini plant Reihenfolge ──
    print("🧠 Gemini plant die Reihenfolge...")
    try:
        plan = gemini_plan_erstellen(befehl, verfuegbare)
        print(f"  Plan: {plan['beschreibung']}")
        print(f"  Reihenfolge: {plan['reihenfolge']}")
    except Exception as e:
        print(f"  ✗ Gemini Fehler: {e}")
        return

    # ── Schritt 3: Arm ausführen ──
    import Pfadplanung
    import Koordinaten_Logik

    Pfadplanung.fahre_zur_startposition()

    for i, farbe in enumerate(plan['reihenfolge']):
        print(f"\n[{i+1}/{len(plan['reihenfolge'])}] Suche '{farbe}' Block...")

        gefunden = False
        for versuch in range(30):  # Max. 30 Versuche pro Block
            try:
                ret, frame = stream.get_frame()
                if not ret or frame is None:
                    continue

                # Roboflow: Farbe im aktuellen Frame erkennen
                erkannte_farbe, konfidenz = roboflow_farbe_erkennen(frame)

                if erkannte_farbe == farbe and konfidenz >= MIN_KONFIDENZ:
                    # Position des Blocks im Bild bestimmen
                    cx, cy, _ = Koordinaten_Logik.block_position_erkennen(frame)
                    if cx is not None:
                        servo_x, servo_y = Koordinaten_Logik.pixel_zu_servo(cx, cy)

                        # Servo-Werte auf gültigen Bereich prüfen
                        servo_x = max(0.5, min(2.5, servo_x))
                        servo_y = max(0.5, min(2.5, servo_y))

                        print(f"  ✓ '{farbe}' gefunden! Servo: ({servo_x}, {servo_y})")

                        # Pickup-Koordinaten dynamisch setzen
                        original = Pfadplanung.PICKUP
                        Pfadplanung.PICKUP = (servo_x, servo_y) + original[2:]
                        Pfadplanung.pick_and_place(ebene=i)
                        Pfadplanung.PICKUP = original

                        gefunden = True
                        break

                time.sleep(0.1)

            except Exception as e:
                print(f"  [ARM] Fehler bei Versuch {versuch+1}: {e}")
                continue

        if not gefunden:
            print(f"  ✗ '{farbe}' Block nicht gefunden, überspringe...")

    print("\n✅ Aufgabe abgeschlossen!")
    Pfadplanung.fahre_zur_startposition()


# ─────────────────────
# 6. STANDALONE TEST
# ─────────────────────

if __name__ == "__main__":
    from Kamera_stream import CameraStream

    # Kamera starten
    stream = CameraStream().start()
    time.sleep(1)  # Kamera aufwärmen lassen

    print("\n=== NEN DYNAMICS - AUFGABEN PLANER (Roboflow) ===")
    print("Farben: rot, gruen, blau, gelb, weiss, natur")
    print("-" * 50)
    print("Beispiele:")
    print("  'Baue eine Ampel'          → gruen, gelb, rot")
    print("  'Baue eine Pyramide'       → breit unten, schmal oben")
    print("  'Baue einen Turm'          → alle übereinander")
    print("  'Baue einen Regenbogen'    → rot, natur, gelb, gruen, blau, weiss")
    print("  'Sortiere nach Helligkeit' → dunkel unten, hell oben")
    print("  'q' zum Beenden")
    print("=" * 50)

    try:
        while True:
            befehl = input("\nBefehl > ").strip()
            if befehl.lower() == 'q':
                break
            if befehl:
                aufgabe_starten(befehl, stream)
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        cv2.destroyAllWindows()
        print("\nProgramm beendet.")
