# Koordinaten_Logik.py
# NEN Dynamics - Roboflow KI + Pixel zu Servo Koordinaten
# Autor: Hamidullah Taymuree

# ─────────────────────
# 1. IMPORTS
# ─────────────────────
import cv2
import numpy as np
import time
import base64
import requests
import os
from dotenv import load_dotenv
import Pfadplanung
from Kamera_stream import CameraStream

# ─────────────────────
# 2. KONFIGURATION
# ─────────────────────

load_dotenv()
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_MODEL_ID = "color-classification-w120p/1"
ROBOFLOW_API_URL  = "https://serverless.roboflow.com"

# Kamera wird nur im Standalone-Betrieb gestartet (nicht beim Import)
stream = None

# ─────────────────────
# 3. KALIBRIERUNG
# ─────────────────────
# Pixel-Grenzen des Arbeitsbereichs
PIXEL_X_MIN, PIXEL_X_MAX = 0, 640
PIXEL_Y_MIN, PIXEL_Y_MAX = 0, 480

# Servo-Grenzen - MÜSSEN GETESTET WERDEN!
# Servo 0 (Drehteller): 2.0 = links, 1.0 = rechts
SERVO_X_MIN, SERVO_X_MAX = 2.0, 1.0
# Servo 1 (Unterarm): 1.5 = weit weg (oben im Bild), 0.8 = nah
SERVO_Y_MIN, SERVO_Y_MAX = 1.5, 0.8

# ─────────────────────
# 4. UMRECHNUNGSFUNKTION
# ─────────────────────
def pixel_zu_servo(pixel_x, pixel_y):
    """
    Rechnet Pixel-Koordinaten in Servo-Werte um.
    Servo-Werte werden auf gültigen Bereich [0.5, 2.5] begrenzt.
    """
    try:
        servo_x = np.interp(pixel_x, [PIXEL_X_MIN, PIXEL_X_MAX], [SERVO_X_MIN, SERVO_X_MAX])
        servo_y = np.interp(pixel_y, [PIXEL_Y_MIN, PIXEL_Y_MAX], [SERVO_Y_MIN, SERVO_Y_MAX])

        # Servo-Werte auf gültigen Bereich begrenzen
        servo_x = max(0.5, min(2.5, round(servo_x, 3)))
        servo_y = max(0.5, min(2.5, round(servo_y, 3)))

        return servo_x, servo_y
    except Exception as e:
        print(f"  [SERVO] Umrechnungsfehler: {e}")
        return 1.5, 1.5  # Sicherer Standardwert (Mitte)

# ─────────────────────
# 5. ROBOFLOW POSITION ERKENNEN
# ─────────────────────
def roboflow_bloecke_erkennen(frame):
    """
    Schickt ein Bild an Roboflow und gibt alle erkannten Blöcke zurück.
    Gibt eine Liste zurück: [(label, konfidenz, cx, cy), ...]
    """
    try:
        # Bild als JPEG kodieren und Base64 konvertieren
        _, bild_encoded = cv2.imencode(".jpg", frame)
        bild_b64 = base64.b64encode(bild_encoded.tobytes()).decode("utf-8")

        url = f"{ROBOFLOW_API_URL}/{ROBOFLOW_MODEL_ID}"
        params = {"api_key": ROBOFLOW_API_KEY}
        antwort = requests.post(url, params=params, data=bild_b64,
                                headers={"Content-Type": "application/x-www-form-urlencoded"},
                                timeout=5)
        antwort.raise_for_status()
        daten = antwort.json()

        vorhersagen = daten.get("predictions", [])
        ergebnisse = []
        
        for p in vorhersagen:
            label = p.get("class", "").lower()
            konfidenz = float(p.get("confidence", 0.0))
            cx = int(p.get("x", frame.shape[1] // 2))
            cy = int(p.get("y", frame.shape[0] // 2))
            ergebnisse.append((label, konfidenz, cx, cy))

        return ergebnisse

    except requests.exceptions.Timeout:
        print("  [ROBOFLOW] Timeout")
        return []
    except Exception as e:
        print(f"  [ROBOFLOW] Fehler: {e}")
        return []


# ─────────────────────
# 6. FALLBACK: HSV POSITION (OpenCV)
# ─────────────────────
def block_position_erkennen(bild):
    """
    Fallback: Findet einen farbigen Block per HSV-Farberkennung.
    Wird genutzt wenn Roboflow keine Bounding Box liefert.
    Gibt (cx, cy, kontur) oder (None, None, None) zurück.
    """
    try:
        hsv = cv2.cvtColor(bild, cv2.COLOR_BGR2HSV)

        # Alle 6 Farben kombiniert erkennen (breite HSV-Maske)
        # Rot (zwei Bereiche im HSV-Kreis)
        mask_rot1 = cv2.inRange(hsv, np.array([0, 100, 70]),   np.array([10, 255, 255]))
        mask_rot2 = cv2.inRange(hsv, np.array([160, 100, 70]), np.array([180, 255, 255]))
        # Grün
        mask_gruen = cv2.inRange(hsv, np.array([35, 80, 50]),  np.array([90, 255, 255]))
        # Blau
        mask_blau  = cv2.inRange(hsv, np.array([90, 80, 50]),  np.array([135, 255, 255]))
        # Gelb
        mask_gelb  = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([35, 255, 255]))
        # Weiß
        mask_weiss = cv2.inRange(hsv, np.array([0, 0, 180]),   np.array([180, 30, 255]))
        # Natur/Holz (beige/braun)
        mask_natur = cv2.inRange(hsv, np.array([10, 30, 100]), np.array([25, 150, 220]))

        # Alle Masken kombinieren
        mask = (mask_rot1 | mask_rot2 | mask_gruen | mask_blau |
                mask_gelb | mask_weiss | mask_natur)

        # Rauschen entfernen
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Konturen suchen
        konturen, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if konturen:
            groesste = max(konturen, key=cv2.contourArea)
            # Nur Konturen ab 500 Pixel² als Block werten
            if cv2.contourArea(groesste) > 500:
                M = cv2.moments(groesste)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return cx, cy, groesste

        return None, None, None

    except Exception as e:
        print(f"  [HSV] Fehler: {e}")
        return None, None, None


# ─────────────────────
# 7. HAUPTPROGRAMM (TEST)
# ─────────────────────
if __name__ == "__main__":
    print("=" * 40)
    print("  NEN Dynamics - Koordinaten Logik")
    print("  Roboflow KI + Pixel zu Servo")
    print("  Tasten:")
    print("    'q' = Beenden")
    print("    'p' = Erkannten Block greifen")
    print("=" * 40)

    # Kamera und Pfadplanung nur im Standalone-Betrieb starten
    stream = CameraStream().start()
    time.sleep(1)

    Pfadplanung.fahre_zur_startposition()
    time.sleep(1)

    while True:
        try:
            ret, frame = stream.get_frame()
            if not ret or frame is None:
                continue

            # Roboflow: Farben + Positionen erkennen
            ergebnisse = roboflow_bloecke_erkennen(frame)
            servo_x, servo_y = None, None
            beste_vorhersage = None

            for (label, konfidenz, cx_rf, cy_rf) in ergebnisse:
                if konfidenz >= 0.70 and cx_rf is not None:
                    # Roboflow-Position verwenden
                    cx, cy = cx_rf, cy_rf
                    s_x, s_y = pixel_zu_servo(cx, cy)

                    # Anzeige im Bild
                    cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)
                    cv2.putText(frame, f"RF: {label} ({konfidenz:.0%})",
                                (cx - 60, cy - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(frame, f"Pixel: {cx}, {cy}",
                                (cx - 60, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.putText(frame, f"Servo: {s_x}, {s_y}",
                                (cx - 60, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    
                    if beste_vorhersage is None or konfidenz > beste_vorhersage[1]:
                        beste_vorhersage = (label, konfidenz, cx, cy)
                        servo_x, servo_y = s_x, s_y

            if beste_vorhersage is None:
                # Fallback: HSV-Erkennung für Position
                cx, cy, kontur = block_position_erkennen(frame)
                if cx is not None:
                    servo_x, servo_y = pixel_zu_servo(cx, cy)
                    cv2.drawContours(frame, [kontur], -1, (0, 165, 255), 2)
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                    cv2.putText(frame, f"HSV Fallback: {cx}, {cy}",
                                (cx - 60, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)
                    cv2.putText(frame, f"Servo: {servo_x}, {servo_y}",
                                (cx - 60, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Overlay hinzufügen und Bild anzeigen
            frame = stream.draw_overlay(frame)
            cv2.imshow("NEN Dynamics - Vision", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('p') and servo_x is not None:
                print(f"\n[AKTION] Greife Block → Servo ({servo_x}, {servo_y})")

                original_pickup      = Pfadplanung.PICKUP
                original_pickup_leer = Pfadplanung.PICKUP_OBEN_LEER
                original_pickup_voll = Pfadplanung.PICKUP_OBEN_VOLL

                Pfadplanung.PICKUP           = (servo_x, servo_y) + original_pickup[2:]
                Pfadplanung.PICKUP_OBEN_LEER = (servo_x, servo_y) + original_pickup_leer[2:]
                Pfadplanung.PICKUP_OBEN_VOLL = (servo_x, servo_y) + original_pickup_voll[2:]

                Pfadplanung.pick_and_place(ebene=0)

                Pfadplanung.PICKUP           = original_pickup
                Pfadplanung.PICKUP_OBEN_LEER = original_pickup_leer
                Pfadplanung.PICKUP_OBEN_VOLL = original_pickup_voll

        except Exception as e:
            print(f"[MAIN] Fehler: {e}")
            continue

    # Aufräumen
    stream.stop()
    cv2.destroyAllWindows()