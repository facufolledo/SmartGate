import os
import cv2
import numpy as np
from ultralytics import YOLO
import urllib.request
from pathlib import Path
import easyocr

# ================== DESCARGA AUTOMÁTICA DE MODELOS ==================

def ensure_weights(models_dir: str, filename: str, fallback_url: str, env_var: str = None):
    """
    Asegura que un archivo de pesos exista.
    Si no existe, lo descarga desde:
    - Variable de entorno (si está definida)
    - URL por defecto fallback_url
    """
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    weight_path = models_dir / filename

    if not weight_path.exists():
        url = os.getenv(env_var) if env_var else None
        if not url:
            url = fallback_url
        
        print(f"⬇️ Descargando {filename} desde {url} ...")
        urllib.request.urlretrieve(url, weight_path)
        print(f"✅ Descargado: {weight_path}")
    
    return str(weight_path)

# ================== VALIDACIÓN Y FORMATO DE PATENTES ==================

def _license_complies_format(text: str) -> bool:
    """Valida formato Mercosur AR: AA NNN AA (2 letras, 3 dígitos, 2 letras)."""
    if len(text) != 7:
        return False

    dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'B': '8', 'S': '5'}
    dict_int_to_char = {'0': 'O', '1': 'I', '3': 'B', '8': 'B', '5': 'S'}

    def ok(index, ch):
        if index in (2,3,4):  # dígitos
            return ch.isdigit() or ch in dict_char_to_int
        return ch.isalpha() or ch in dict_int_to_char

    return all(ok(i, text[i]) for i in range(7))


def _format_license(text: str) -> str:
    dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'B': '8', 'S': '5'}
    dict_int_to_char = {'0': 'O', '1': 'I', '3': 'B', '8': 'B', '5': 'S'}

    res = []
    for i, ch in enumerate(text):
        if i in (2,3,4):
            res.append(dict_char_to_int.get(ch, ch))
        else:
            res.append(dict_int_to_char.get(ch, ch))
    return ''.join(res)

# ================== CLASE PRINCIPAL DEL DETECTOR ==================

class ANPRDetector:
    def __init__(self, models_dir: str):
        """
        models_dir puede no tener pesos locales.
        Si faltan → Se descargan automáticamente.
        """

        # VEHICULOS
        vehicle_weights = ensure_weights(
            models_dir,
            "yolov8n.pt",
            fallback_url="https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt",
            env_var="VEHICLE_WEIGHTS_URL"
        )

        # PATENTES
        plate_weights = ensure_weights(
            models_dir,
            "best.pt",
            fallback_url="https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt",  # fallback si no pones tu modelo
            env_var="PLATE_WEIGHTS_URL"
        )

        self.vehicle_model = YOLO(vehicle_weights)
        self.plate_model = YOLO(plate_weights)
        self.vehicles_classes = {2, 3, 5, 7}  # car, motorcycle, bus, truck
        self.ocr = easyocr.Reader(['en'], gpu=False)
        self.min_crop_h = 80

    def _read_plate(self, img: np.ndarray):
        h, w = img.shape[:2]
        if h < self.min_crop_h:
            scale = self.min_crop_h / float(h)
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        eq = cv2.equalizeHist(gray)
        blur = cv2.GaussianBlur(eq, (3, 3), 0)
        thr_ad = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

        variants = [thr_ad]
        variants.append(cv2.bilateralFilter(eq,7,50,50))
        variants.append(255-thr_ad)

        best_text, best_score = None, 0
        for v in variants:
            detections = self.ocr.readtext(v)
            for _, text, score in detections:
                text = text.upper().replace(" ","")
                if _license_complies_format(text):
                    text = _format_license(text)
                    if score > best_score:
                        best_text, best_score = text, score

        return best_text, (best_score if best_text else None)

    def detect_plate_from_frame(self, frame: np.ndarray):
        vehicle_result = self.vehicle_model(frame, verbose=False)[0]
        vehicle_boxes = [
            [x1, y1, x2, y2, score]
            for x1,y1,x2,y2,score,cls in vehicle_result.boxes.data.tolist()
            if int(cls) in self.vehicles_classes
        ]

        plate_result = self.plate_model(frame, verbose=False)[0]
        best = None

        for x1,y1,x2,y2,p_score,_ in plate_result.boxes.data.tolist():
            crop = frame[int(y1):int(y2), int(x1):int(x2)]
            if crop.size == 0:
                continue

            text, t_score = self._read_plate(crop)
            if text and (best is None or (t_score or 0) > (best['text_score'] or 0)):
                best = {
                    'text': text,
                    'text_score': t_score,
                    'bbox': [int(x1),int(y1),int(x2),int(y2)],
                    'bbox_score': float(p_score)
                }

        if best and best['text_score'] and best['text_score'] >= 0.4:
            return best
        return None




