# AP20 - Koordinaten-Logik
# Autor: Hamidullah Taymuree
# Datum: 21.04.2026

# ─────────────────────
# 1. IMPORTS
# ─────────────────────
import cv2
import numpy as np
import time
import Pfadplanung  # Verbindet dieses Modul mit der Motorsteuerung (AP17)
from Kamera_stream import CameraStream


# Kamera über das neue Modul initialisieren
stream = CameraStream().start()

# ─────────────────────
# 3. KALIBRIERUNG
# ─────────────────────
# Pixel-Grenzen des Arbeitsbereichs
PIXEL_X_MIN, PIXEL_X_MAX = 0, 640
PIXEL_Y_MIN, PIXEL_Y_MAX = 0, 480

# Servo-Grenzen (aus AP17 bekannt) - MÜSSEN GETESTET WERDEN!
# Servo 0 (Drehteller)
SERVO_X_MIN, SERVO_X_MAX = 2.0, 1.0  # z.B. 2.0 ist links im Bild, 1.0 rechts
# Servo 1 (Unterarm / Reichweite)
SERVO_Y_MIN, SERVO_Y_MAX = 1.5, 0.8  # z.B. 1.5 ist weit weg (oben im Bild), 0.8 ist nah

# ─────────────────────
# 4. UMRECHNUNGSFUNKTION
# ─────────────────────
def pixel_zu_servo(pixel_x, pixel_y):
    """Rechnet (X, Y) Pixel- in (Motor1, Motor2) Servowerte um mittels linearer Interpolation."""
    servo_x = np.interp(pixel_x, [PIXEL_X_MIN, PIXEL_X_MAX], [SERVO_X_MIN, SERVO_X_MAX])
    servo_y = np.interp(pixel_y, [PIXEL_Y_MIN, PIXEL_Y_MAX], [SERVO_Y_MIN, SERVO_Y_MAX])
    return round(servo_x, 3), round(servo_y, 3)

# ─────────────────────
# 5. BLOCK ERKENNEN
# ─────────────────────
def block_position_erkennen(bild):
    """Findet einen farbigen Block im Bild und liefert X/Y Pixel."""
    # 1. In HSV Farbraum wandeln (besser für Farberkennung)
    hsv = cv2.cvtColor(bild, cv2.COLOR_BGR2HSV)
    
    # 2. Rote Farbe erkennen (Werte an deine Blöcke anpassen!)
    # Rot hat im HSV-Kreis zwei Bereiche (unten und ganz oben)
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    
    # 3. Maske generieren
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # 4. Bereinigen
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # 5. Konturen suchen
    konturen, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(konturen) > 0:
        # Den größten roten Fleck finden
        groesste_kontur = max(konturen, key=cv2.contourArea)
        
        # Mittelpunkt bestimmen
        M = cv2.moments(groesste_kontur)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy, groesste_kontur
            
    return None, None, None

# ─────────────────────
# 6. HAUPTPROGRAMM
# ─────────────────────
if __name__ == "__main__":
    print("=" * 40)
    print("  AP20 - Vision & Koordinaten Logik")
    print("  Tasten:")
    print("    'q' = Beenden")
    print("    'p' = Erkannten Block greifen")
    print("=" * 40)

    Pfadplanung.fahre_zur_startposition()
    time.sleep(1)

    while True:
        # Kamerabild über den Stream-Thread abrufen
        ret, frame = stream.get_frame()
        if not ret or frame is None:
            continue
            
        # Block im Bild suchen
        cx, cy, kontur = block_position_erkennen(frame)
        servo_x, servo_y = None, None
        
        if cx is not None:
            # Rahmen um den Block zeichnen
            cv2.drawContours(frame, [kontur], -1, (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
            
            # Pixel-Werte anzeigen
            cv2.putText(frame, f"Pixel: {cx}, {cy}", (cx - 50, cy - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Servo-Werte berechnen und anzeigen
            servo_x, servo_y = pixel_zu_servo(cx, cy)
            cv2.putText(frame, f"Servo: X={servo_x}, Y={servo_y}", (cx - 50, cy - 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Overlay aus dem Kamera-Modul hinzufügen (Branding & FPS)
        frame = stream.draw_overlay(frame)
        
        # Videostream anzeigen
        cv2.imshow("Robot Vision Center", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('p') and cx is not None:
            print(f"\n[AKTION] Greife Block bei Pixel ({cx}, {cy}) -> Servo ({servo_x}, {servo_y})")
            
            # 1. Alte Zielkoordinaten merken
            original_pickup = Pfadplanung.PICKUP
            original_pickup_leer = Pfadplanung.PICKUP_OBEN_LEER
            original_pickup_voll = Pfadplanung.PICKUP_OBEN_VOLL
            
            # 2. Dynamische Koordinaten für den Greifvorgang setzen (Motor1 und Motor2 überschreiben)
            Pfadplanung.PICKUP = (servo_x, servo_y) + original_pickup[2:]
            Pfadplanung.PICKUP_OBEN_LEER = (servo_x, servo_y) + original_pickup_leer[2:]
            Pfadplanung.PICKUP_OBEN_VOLL = (servo_x, servo_y) + original_pickup_voll[2:]
            
            # 3. Pfadplanung starten!
            Pfadplanung.pick_and_place(ebene=0)
            
            # 4. Koordinaten wiederherstellen
            Pfadplanung.PICKUP = original_pickup
            Pfadplanung.PICKUP_OBEN_LEER = original_pickup_leer
            Pfadplanung.PICKUP_OBEN_VOLL = original_pickup_voll

    # Aufräumen am Ende
    stream.stop()
    cv2.destroyAllWindows()