<p align="center">
  <img src="C:\Users\Naice\OneDrive\Imágenes\ChatGPT Image 13. Apr. 2026, 10_53_13.png" alt="NEN DYNAMICS Logo" width="300">
</p>

# NEN DYNAMICS - KI-gesteuerter Roboterarm



# NEN DYNAMICS - KI-gesteuerter Roboterarm 🤖

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green?style=for-the-badge&logo=opencv)
![Status](https://img.shields.io/badge/Status-In_Umsetzung-orange?style=for-the-badge)

Willkommen im Repository von **NEN DYNAMICS**. Dieses Projekt befasst sich mit der Entwicklung und Integration eines KI-gestützten Roboterarms, der autonom Objekte erkennt und zu einem Turm stapelt.

## 📌 Projektübersicht
Im Rahmen unseres Projekts (April - Mai 2026) entwickeln wir eine intelligente Steuerung für einen Roboterarm. Mithilfe einer Kamera und Bildverarbeitung (OpenCV) werden Objekte identifiziert, deren Koordinaten berechnet und präzise gestapelt.

### Kernfeatures:
- **Objekterkennung:** Echtzeit-Identifikation von bis zu 6 Objekttypen.
- **Präzisions-Greifen:** Automatisierte Berechnung der Greifpunkte.
- **Autonomer Turmbau:** Stapeln von 3 Objekten ohne manuellen Eingriff.
- **Sicherheits-Logik:** Integrierter Not-Halt und Fehlererkennung.

## 🛠 Technologien & Tools
- **Hardware:** Roboterarm (Lehrstück), Kamera-Modul.
- **Programmiersprache:** Python.
- **Bibliotheken:** - `OpenCV` für die Bildverarbeitung.
  - `NumPy` für mathematische Berechnungen.
  - `Serial` / `Robot-API` zur Ansteuerung der Motoren.

## 📂 Struktur
```text
├── docs/               # Projekthandbuch & Dokumentation
├── src/                # Quellcode
│   ├── vision/         # KI & Objekterkennung (OpenCV)
│   ├── control/        # Robotersteuerung
│   └── main.py         # Hauptprogramm
├── tests/              # Testprotokolle (gemäß Testplan)
└── README.md           # Diese Datei
