import cv2
import json
import requests
from detector import ANPRDetector  # Tu clase de detección

# Cámara local (DroidCam o webcam)
VIDEO_SOURCE = 0   # Webcam local 

# Endpoint que agregamos en el backend
BACKEND_EVENT = "https://smartgate-ey9z.onrender.com/auto-access/event"


def main():
    print("🔍 Cargando modelo ANPR...")
    detector = ANPRDetector("models")

    print("🎥 Abriendo cámara:", VIDEO_SOURCE)
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print("❌ ERROR: No se pudo conectar a la cámara.")
        return

    print("✅ Cámara OK — Detección iniciada")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        result = detector.detect_plate_from_frame(frame)
        if result:
            data = {
                "matricula": result["text"],
                "confianza": float(result["text_score"]),
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            }

            try:
                requests.post(BACKEND_EVENT, json=data, timeout=3)
                print(f"📨 Enviado → {data}")
            except Exception as e:
                print(f"⚠️ No se pudo enviar → {e}")


if __name__ == "__main__":
    main()

