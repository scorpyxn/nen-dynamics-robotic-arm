#!/bin/bash
# NEN Dynamics - Roboterarm starten
# Ausführen mit: bash start.sh

echo "======================================"
echo "  NEN DYNAMICS - ROBOTIC ARM SYSTEM"
echo "======================================"

# In den Code-Ordner wechseln
cd "$(dirname "$0")"

# Prüfen ob .env existiert
if [ ! -f ".env" ]; then
    echo " FEHLER: .env Datei nicht gefunden!"
    echo "  Erstelle .env mit deinem Gemini API Key."
    exit 1
fi

# Prüfen ob project.tm existiert
if [ ! -f "project.tm" ]; then
    echo " FEHLER: project.tm (KI-Modell) nicht gefunden!"
    exit 1
fi

echo ""
echo "Welches Modul starten?"
echo "  1) Aufgaben-Planer  (Gemini + KI + Arm) [EMPFOHLEN]"
echo "  2) Kamera-Stream    (nur Kamera-Test)"
echo "  3) Koordinaten-Logik (Kamera + Arm manuell)"
echo "  4) Sprachsteuerung   (Sprachbefehl -> Arm)"
echo ""
read -p "Auswahl [1/2/3/4]: " auswahl

case $auswahl in
    1)
        echo ""
        echo " Starte Aufgaben-Planer..."
        python3 code/Aufgaben_Planer.py
        ;;
    2)
        echo ""
        echo " Starte Kamera-Stream..."
        python3 code/Kamera_stream.py
        ;;
    3)
        echo ""
        echo " Starte Koordinaten-Logik..."
        python3 code/Koordinaten_Logik.py
        ;;
    4)
        echo ""
        echo " Starte Sprachsteuerung..."
        python3 code/Voice_Steuerung.py
        ;;
    *)
        echo "⚠ Ungültige Auswahl."
        exit 1
        ;;
esac
