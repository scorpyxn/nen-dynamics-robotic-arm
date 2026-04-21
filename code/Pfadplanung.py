# AP17 - Pfadplanung
# Roboterarm Nen Dynamics - Fahrwege zur Ablage
# Verantwortlicher: Hamidullah Taymuree

import Adafruit_PCA9685
import time

# PCA9685 initialisieren
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)  # 50Hz für Servos

# ─────────────────────────────────────────
# HILFSFUNKTIONEN
# ─────────────────────────────────────────

def ms_zu_pwm(ms):
    """Konvertiert Millisekunden (0.5-2.5) in PWM-Wert (0-4095)"""
    return int((ms / 20.0) * 4096)

def servo_setzen(kanal, ms):
    """Setzt einen einzelnen Servo auf eine Position"""
    pwm.set_pwm(kanal, 0, ms_zu_pwm(ms))

def position_fahren(motor1, motor2, motor3, motor4, motor5, motor6, wartezeit=1.0):
    """
    Fährt alle 6 Motoren gleichzeitig zu den angegebenen Positionen.
    Werte zwischen 0.5 (Minimum) und 2.5 (Maximum)
    motor1 = Drehteller
    motor2 = Unterarm
    motor3 = Oberarm
    motor4 = Unteres Handgelenk
    motor5 = Handgelenk
    motor6 = Kralle (2.5=offen, 0.5=geschlossen)
    """
    servo_setzen(0, motor1)
    servo_setzen(1, motor2)
    servo_setzen(2, motor3)
    servo_setzen(3, motor4)
    servo_setzen(4, motor5)
    servo_setzen(5, motor6)
    time.sleep(wartezeit)

# ─────────────────────────────────────────
# POSITIONEN DEFINIEREN
# ─────────────────────────────────────────

# Startposition (aus der Datenbank: startpos)
START         = (1.5, 0.65, 1.5, 1.9, 0.85, 1.6)

# Sicherheitshöhe (Arm oben, sicher zum Fahren)
SICHERHEIT    = (1.5, 0.65, 2.0, 1.9, 0.85, 1.6)

# Pickup-Position (wo der Block liegt) - ANPASSEN nach Messung!
PICKUP        = (1.2, 1.0, 1.1, 1.9, 0.85, 2.5)
PICKUP_OBEN   = (1.2, 0.65, 1.8, 1.9, 0.85, 2.5)  # über dem Block

# Ablage-Position (wo der Turm gebaut wird) - ANPASSEN nach Messung!
ABLAGE        = (1.8, 1.0, 1.1, 1.9, 0.85, 2.5)
ABLAGE_OBEN   = (1.8, 0.65, 1.8, 1.9, 0.85, 0.5)  # über der Ablage (Kralle geschlossen!)

# Höhe pro Blockebene (jeder Block erhöht die Ablage um diesen Wert)
BLOCK_HOEHE   = 0.12

# ─────────────────────────────────────────
# HAUPTFUNKTIONEN
# ─────────────────────────────────────────

def kralle_oeffnen():
    """Kralle öffnen"""
    servo_setzen(5, 2.5)
    time.sleep(0.5)

def kralle_schliessen():
    """Kralle schließen - Block greifen"""
    servo_setzen(5, 0.5)
    time.sleep(0.5)

def fahre_zur_startposition():
    """Fährt den Arm in die Ausgangsposition"""
    print("→ Fahre zu Startposition")
    position_fahren(*START)

def block_aufnehmen():
    """
    Fahrweg: Arm fährt zum Block und greift ihn
    """
    print("\n[PICKUP] Block aufnehmen")

    print("  1. Kralle öffnen")
    kralle_oeffnen()

    print("  2. Über Block fahren")
    position_fahren(*PICKUP_OBEN)

    print("  3. Arm senken zum Block")
    position_fahren(*PICKUP)

    print("  4. Block greifen")
    kralle_schliessen()

    print("  5. Arm hochheben")
    position_fahren(*PICKUP_OBEN)

    print("  ✓ Block aufgenommen")

def block_ablegen(ebene=0):
    """
    Fahrweg: Arm fährt zur Ablage und legt Block ab.
    ebene=0 → erster Block, ebene=1 → zweiter Block, usw.
    """
    print(f"\n[ABLAGE] Block ablegen (Ebene {ebene + 1})")

    # Ablageposition je nach Stapelhöhe anpassen
    hoehenkorrektur = ebene * BLOCK_HOEHE
    ablage_angepasst = list(ABLAGE)
    ablage_oben_angepasst = list(ABLAGE_OBEN)
    ablage_angepasst[2] += hoehenkorrektur       # Arm höher je mehr Blöcke
    ablage_oben_angepasst[2] += hoehenkorrektur

    print(f"  1. Über Ablage fahren (Höhe +{hoehenkorrektur:.2f})")
    position_fahren(*ablage_oben_angepasst)

    print("  2. Arm senken zur Ablage")
    position_fahren(*ablage_angepasst)

    print("  3. Block loslassen")
    kralle_oeffnen()

    print("  4. Arm hochheben")
    position_fahren(*ablage_oben_angepasst)

    print(f"  ✓ Block {ebene + 1} abgelegt")

def pick_and_place(ebene=0):
    """Kompletter Pick & Place Zyklus für einen Block"""
    block_aufnehmen()
    block_ablegen(ebene=ebene)
    fahre_zur_startposition()

# ─────────────────────────────────────────
# HAUPTPROGRAMM
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 40)
    print("  AP17 - Pfadplanung")
    print("  Nen Dynamics Roboterarm")
    print("=" * 40)

    try:
        fahre_zur_startposition()
        time.sleep(1)

        # 3 Blöcke stapeln (für den 3er-Turm aus AP21)
        anzahl_bloecke = 3
        for i in range(anzahl_bloecke):
            print(f"\n{'='*40}")
            print(f"  Block {i+1} von {anzahl_bloecke}")
            print(f"{'='*40}")
            pick_and_place(ebene=i)
            time.sleep(0.5)

        print("\n✓ Alle Blöcke gestapelt!")
        fahre_zur_startposition()

    except KeyboardInterrupt:
        print("\n⚠ Abgebrochen - fahre zu Startposition")
        fahre_zur_startposition()