# AP14 - Greif-Justierung
# Feinabstimmung für verschiedene Bauteile
# Verantwortlicher: Hamidullah Taymuree

# ─────────────────────
# 1. IMPORTS
# ─────────────────────
import time
import sys
import Pfadplanung  

# ─────────────────────
# 2. KONFIGURATION
 
# ─────────────────────

def clear_screen():
    print("\n" * 10)

def print_header(title):
    print("=" * 50)
    print(f" {title:^48} ")
    print("=" * 50)

def test_gripper_position(ms):
    """Setzt den Greifer auf einen spezifischen ms-Wert."""
    try:
        val = float(ms)
        if 0.5 <= val <= 2.5:
            Pfadplanung.servo_setzen(GRIPPER_CHANNEL, val)
            print(f"→ Greifer auf {val} ms gesetzt.")
        else:
            print("⚠ Wert muss zwischen 0.5 (zu) und 2.5 (offen) liegen.")
    except ValueError:
        print("⚠ Ungültige Eingabe. Bitte eine Zahl eingeben.")

def gripper_calibration_loop():
    """Interaktive Kalibrierung des Greifers."""
    clear_screen()
    print_header("GREIFER KALIBRIERUNG")
    print("Bewege den Greifer schrittweise, um die optimalen")
    print("Werte für 'Offen' und 'Geschlossen' zu finden.")
    print("\nBefehle:")
    print("  [Wert 0.5-2.5] -> Position anfahren")
    print("  'o'           -> Standard OFFEN (2.5)")
    print("  'c'           -> Standard GESCHLOSSEN (0.5)")
    print("  'q'           -> Zurück zum Hauptmenü")
    
    while True:
        cmd = input("\nGreifer-Wert eingeben > ").lower()
        if cmd == 'q':
            break
        elif cmd == 'o':
            test_gripper_position(2.5)
        elif cmd == 'c':
            test_gripper_position(0.5)
        else:
            test_gripper_position(cmd)

def height_alignment_loop():
    """Richtet den Arm über der Pickup-Position aus zum Testen der Höhe."""
    clear_screen()
    print_header("HÖHEN-AUSRICHTUNG (PICKUP)")
    print("Der Arm fährt zur Pickup-Position.")
    print("Du kannst die Höhe (Motor 2 & 3) feinjustieren.")
    
    # Aktuelle Pickup-Werte laden
    m1, m2, m3, m4, m5, m6 = Pfadplanung.PICKUP
    
    print(f"\nAktuelle Werte: M2={m2}, M3={m3}")
    Pfadplanung.position_fahren(m1, m2, m3, m4, m5, m6)
    
    while True:
        print("\nAnpassung (w/s = M3 Hoch/Tief, i/k = M2 Vor/Zurück, q = Exit):")
        cmd = input("Kommando > ").lower()
        
        if cmd == 'q':
            break
        elif cmd == 'w': m3 += 0.05
        elif cmd == 's': m3 -= 0.05
        elif cmd == 'i': m2 += 0.05
        elif cmd == 'k': m2 -= 0.05
        
        # Grenzwerte einhalten
        m2 = max(0.5, min(2.5, m2))
        m3 = max(0.5, min(2.5, m3))
        
        Pfadplanung.position_fahren(m1, m2, m3, m4, m5, m6, wartezeit=0.2)
        print(f"→ Aktuell: M2={m2:.2f}, M3={m3:.2f}")

def show_summary():
    clear_screen()
    print_header("ZUSAMMENFASSUNG")
    print("Kopiere diese Werte bei Bedarf in Pfadplanung.py:")
    print("-" * 50)
    print(f"PICKUP Motor 2 (Unterarm): {Pfadplanung.PICKUP[1]}")
    print(f"PICKUP Motor 3 (Oberarm):  {Pfadplanung.PICKUP[2]}")
    print(f"Kralle OFFEN:              2.5")
    print(f"Kralle GESCHLOSSEN:        0.5")
    print("-" * 50)
    input("\nDrücke Enter zum Fortfahren...")

# ─────────────────────
# 4. HAUPTMENU
# ─────────────────────

def main():
    try:
        Pfadplanung.fahre_zur_startposition()
        
        while True:
            clear_screen()
            print_header("NEN DYNAMICS - GREIF-JUSTIERUNG")
            print("1. Greifer-Bereich testen (Auf/Zu)")
            print("2. Pickup-Höhe feinjustieren")
            print("3. Werte-Zusammenfassung anzeigen")
            print("q. Beenden")
            
            choice = input("\nAuswahl > ").lower()
            
            if choice == '1':
                gripper_calibration_loop()
            elif choice == '2':
                height_alignment_loop()
            elif choice == '3':
                show_summary()
            elif choice == 'q':
                print("\nFahre in Sicherheitsposition...")
                Pfadplanung.fahre_zur_startposition()
                break
                
    except KeyboardInterrupt:
        print("\n\nAbbruch durch Benutzer.")
    finally:
        print("Programm beendet.")

if __name__ == "__main__":
    main()
