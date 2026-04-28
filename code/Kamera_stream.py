# AP15 - Kamera-Stream (Raspberry Pi Camera Module 3)
# Verantwortlicher: Michael / Refactored for NEN Dynamics

# ─────────────────────
# 1. IMPORTS
# ─────────────────────
import cv2
import numpy as np
import time
import os
import threading

# ─────────────────────
# 2. KAMERA KLASSE
# ─────────────────────

class CameraStream:
    """
    Klasse zur Verwaltung eines USB-Webcam Streams.
    Nutzt OpenCV mit einem Hintergrund-Thread für minimalen Lag.
    """
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

        # Kamera initialisieren (0 = erste USB-Webcam)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not self.cap.isOpened():
            print("⚠ FEHLER: USB-Webcam konnte nicht geöffnet werden!")

        self.frame = None
        self.running = False

        # FPS Berechnung
        self.fps = 0
        self.prev_time = 0

        print(f" USB-Webcam initialisiert ({self.width}x{self.height})")

    def start(self):
        if self.running:
            return self
        self.running = True
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def _update(self):
        """Interne Methode: Liest Frames von der Kamera im Hintergrund."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

            current_time = time.time()
            self.fps = 1 / (current_time - self.prev_time) if (current_time - self.prev_time) > 0 else 0
            self.prev_time = current_time

    def get_frame(self):
        """Gibt das aktuelle BGR-Bild zurück."""
        return self.frame is not None, self.frame

    def stop(self):
        """Stoppt den Stream und gibt Ressourcen frei."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        self.cap.release()
        print("Kamera-Stream gestoppt.")

    def save_frame(self, frame, folder="assets/captures"):
        """Speichert das übergebene Bild im captures-Ordner."""
        if not os.path.exists(folder):
            os.makedirs(folder)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        dateiname = f"aufnahme_{timestamp}.jpg"
        pfad = os.path.join(folder, dateiname)

        cv2.imwrite(pfad, frame)
        print(f"✓ Bild gespeichert: {pfad}")
        return pfad

    def draw_overlay(self, frame):
        """Zeichnet Statusinformationen auf das Bild."""
        if frame is None:
            return None

        overlay = frame.copy()

        # Branding
        cv2.putText(overlay, "NEN DYNAMICS - ROBOTIC ARM", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Status / FPS
        status_text = f"LIVE | FPS: {int(self.fps)}"
        cv2.putText(overlay, status_text, (10, self.height - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Zeitstempel
        zeit = time.strftime("%H:%M:%S")
        cv2.putText(overlay, zeit, (self.width - 100, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return overlay

# ─────────────────────
# 3. STANDALONE TEST
# ─────────────────────

def main():
    """Hauptfunktion für den direkten Aufruf des Skripts."""
    stream = CameraStream().start()

    print("\n[LIVE STREAM START]")
    print("  's' -> Bild speichern")
    print("  'q' -> Beenden\n")

    try:
        while True:
            ret, frame = stream.get_frame()

            if not ret or frame is None:
                continue

            # Overlay hinzufügen
            display_frame = stream.draw_overlay(frame)

            # Anzeigen
            cv2.imshow("NEN Dynamics Vision Center", display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                stream.save_frame(frame)

    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        cv2.destroyAllWindows()
        print("\nKamera gestoppt.")

if __name__ == "__main__":
    main()
