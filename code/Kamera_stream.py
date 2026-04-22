# AP15 - Kamera-Stream
# Skript zur Bildaufnahme der Objekte - Threaded Version
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
    Klasse zur Verwaltung des Kamera-Streams in einem separaten Thread.
    Dies verhindert Verzögerungen (Lag) durch den internen Kamera-Buffer.
    """
    def __init__(self, cam_id=0, width=640, height=480):
        self.cam_id = cam_id
        self.width = width
        self.height = height
        
        self.cap = cv2.VideoCapture(self.cam_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        self.ret = False
        self.frame = None
        self.running = False
        
        # FPS Berechnung
        self.fps = 0
        self.prev_time = 0
        
        if not self.cap.isOpened():
            print(f"Fehler: Kamera mit ID {self.cam_id} konnte nicht geöffnet werden.")
        else:
            print(f"Kamera {self.cam_id} initialisiert ({self.width}x{self.height})")

    def start(self):
        """Startet den Capture-Thread."""
        if self.running:
            return self
        self.running = True
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True # Thread beendet sich mit dem Hauptprogramm
        self.thread.start()
        return self

    def _update(self):
        """Interne Methode zum Auslesen der Frames im Hintergrund."""
        while self.running:
            self.ret, self.frame = self.cap.read()
            
            # FPS Berechnung
            current_time = time.time()
            self.fps = 1 / (current_time - self.prev_time) if (current_time - self.prev_time) > 0 else 0
            self.prev_time = current_time

    def get_frame(self):
        """Gibt das aktuelle Bild zurück."""
        return self.ret, self.frame

    def stop(self):
        """Stoppt den Stream und gibt Ressourcen frei."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        self.cap.release()
        print("Kamera-Stream gestoppt.")

    def save_frame(self, frame, folder="assets/captures"):
        """Speichert das übergebene Bild."""
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        dateiname = f"aufnahme_{timestamp}.jpg"
        pfad = os.path.join(folder, dateiname)
        
        cv2.imwrite(pfad, frame)
        print(f"✓ Bild gespeichert: {pfad}")
        return pfad

    def draw_overlay(self, frame):
        """Zeigt Statusinformationen auf dem Bild an."""
        if frame is None:
            return None
        
        overlay = frame.copy()
        
        # Branding (NEN DYNAMICS)
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
    print("  'q' -> Beenden")
    
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

if __name__ == "__main__":
    main()

