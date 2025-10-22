import os
import cv2
import numpy as np
from ultralytics import YOLO

# OCR utilidades inline para evitar dependencias de ruta externa
import string
import easyocr


def _license_complies_format(text: str) -> bool:
	"""Valida formato Mercosur AR: AA NNN AA (2 letras, 3 dígitos, 2 letras)."""
	if len(text) != 7:
		return False
	dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'B': '8', 'S': '5'}
	dict_int_to_char = {'0': 'O', '1': 'I', '3': 'B', '8': 'B', '5': 'S'}

	def ok(index: int, ch: str) -> bool:
		# Dígitos en posiciones 2,3,4
		if index in (2, 3, 4):
			return ch.isdigit() or ch in dict_char_to_int
		# Letras en posiciones 0,1,5,6
		return ch.isalpha() or ch in dict_int_to_char

	return all(ok(i, text[i]) for i in range(7))


def _format_license(text: str) -> str:
	"""Corrige confusiones típicas para cumplir AA NNN AA."""
	dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'B': '8', 'S': '5'}
	dict_int_to_char = {'0': 'O', '1': 'I', '3': 'B', '8': 'B', '5': 'S'}
	result = []
	for i, ch in enumerate(text):
		if i in (2, 3, 4):  # deben ser dígitos
			result.append(dict_char_to_int.get(ch, ch))
		else:  # deben ser letras
			result.append(dict_int_to_char.get(ch, ch))
	return ''.join(result)


class ANPRDetector:
	def __init__(self, models_dir: str):
		"""models_dir debe contener 'yolov8n.pt' y 'best.pt'"""
		vehicle_weights = os.path.join(models_dir, 'yolov8n.pt')
		plate_weights = os.path.join(models_dir, 'best.pt')
		self.vehicle_model = YOLO(vehicle_weights)
		self.plate_model = YOLO(plate_weights)
		self.vehicles_classes = {2, 3, 5, 7}  # car, motorcycle, bus, truck (COCO)
		self.ocr = easyocr.Reader(['en'], gpu=False)
		self.min_crop_h = 80  # asegurar tamaño mínimo para OCR

	def _read_plate(self, img: np.ndarray):
		"""Prueba múltiples preprocesados y devuelve el mejor resultado."""
		# asegurar tamaño mínimo
		h, w = img.shape[:2]
		if h < self.min_crop_h:
			scale = self.min_crop_h / float(h)
			img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

		variants = []
		# 1) Gris + EQ + Gauss + Adaptive
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		eq = cv2.equalizeHist(gray)
		blur = cv2.GaussianBlur(eq, (3, 3), 0)
		thr_ad = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
		variants.append(thr_ad)
		# 2) CLAHE + Bilateral + Otsu
		clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
		bil = cv2.bilateralFilter(clahe, 7, 50, 50)
		_, otsu = cv2.threshold(bil, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		variants.append(otsu)
		# 3) Invertida
		variants.append(255 - thr_ad)

		best_text, best_score = None, 0.0
		for v in variants:
			detections = self.ocr.readtext(v)
			for _, text, score in detections:
				text = text.upper().replace(' ', '')
				if _license_complies_format(text):
					text = _format_license(text)
					if float(score) > best_score:
						best_text, best_score = text, float(score)
		return best_text, (best_score if best_text else None)

	def detect_plate_from_frame(self, frame: np.ndarray):
		# Detectar vehículos
		vehicle_result = self.vehicle_model(frame, verbose=False)[0]
		vehicle_boxes = []
		for x1, y1, x2, y2, score, cls in vehicle_result.boxes.data.tolist():
			if int(cls) in self.vehicles_classes:
				vehicle_boxes.append([x1, y1, x2, y2, score])

		# Detectar patentes
		plate_result = self.plate_model(frame, verbose=False)[0]
		best = None
		for x1, y1, x2, y2, pscore, _ in plate_result.boxes.data.tolist():
			crop = frame[int(y1):int(y2), int(x1):int(x2), :]
			if crop.size == 0:
				continue
			# padding leve para no cortar caracteres
			pad = 4
			y1p = max(0, int(y1) - pad); x1p = max(0, int(x1) - pad)
			y2p = min(frame.shape[0], int(y2) + pad); x2p = min(frame.shape[1], int(x2) + pad)
			crop = frame[y1p:y2p, x1p:x2p, :]

			# exigir inclusión dentro de vehículo si hay detecciones de vehículos
			inside_vehicle = False
			for vx1, vy1, vx2, vy2, _ in vehicle_boxes:
				if x1 >= vx1 and y1 >= vy1 and x2 <= vx2 and y2 <= vy2:
					inside_vehicle = True
					break
			if not inside_vehicle and len(vehicle_boxes) > 0:
				continue

			text, tscore = self._read_plate(crop)
			if text and (best is None or (tscore or 0) > (best['text_score'] or 0)):
				best = {
					'text': text,
					'text_score': tscore,
					'bbox': [int(x1), int(y1), int(x2), int(y2)],
					'bbox_score': float(pscore)
				}
		# Filtro mínimo de score OCR
		if best and (best['text_score'] is not None) and best['text_score'] >= 0.4:
			return best
		return None


