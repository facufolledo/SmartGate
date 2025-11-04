import cv2
import numpy as np
import threading
import time
import asyncio
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Callable
import json
import os
from .detector import ANPRDetector

# Schema de la base de datos (public es el default en PostgreSQL)
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")

# Silenciar logs verbosos de OpenCV
try:
	import cv2 as _cv2
	_cv2.utils.logging.setLogLevel(_cv2.utils.logging.LOG_LEVEL_SILENT)
except Exception:
	pass

class CameraService:
    def __init__(self, camera_id=0, db_config=None, models_dir=None):
        self.camera_id = camera_id
        self.db_config = db_config
        self.is_running = False
        self.current_frame = None
        self.detection_callback = None
        self.last_detection_time = None
        self.detection_cooldown = 3  # Segundos entre detecciones de la misma patente
        self.detector = ANPRDetector(models_dir=models_dir) if models_dir else None
        self.last_plate_overlay = None  # {'text':str, 'bbox':[x1,y1,x2,y2], 'ts':float}
        
    def set_detection_callback(self, callback: Callable):
        """Establece el callback para cuando se detecte una patente"""
        self.detection_callback = callback
    
    def start_background_capture(self):
        """Inicia la captura en segundo plano"""
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        print("🎥 Cámara iniciada en segundo plano")
    
    def stop_capture(self):
        """Detiene la captura"""
        self.is_running = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join()
        print("🎥 Cámara detenida")
    
    def _capture_loop(self):
        """Loop principal de captura"""
        cap = self._open_capture()
        
        if cap is None or not cap.isOpened():
            print(f"❌ Error: No se pudo abrir la cámara {self.camera_id}")
            return
        
        print(f"✅ Cámara conectada exitosamente")
        
        while self.is_running:
            ret, frame = cap.read()
            if ret:
                self.current_frame = frame
                # Aquí se procesará con YOLO
                self._process_frame(frame)
            else:
                print("⚠️ Error leyendo frame de la cámara")
                time.sleep(1)
        
        cap.release()
    
    def _open_capture(self):
        """Intenta abrir la cámara usando URL o varios backends/índices en Windows"""
        try:
            camera_url = os.getenv('CAMERA_URL')
            if camera_url:
                cap = cv2.VideoCapture(camera_url)
                if cap.isOpened():
                    print(f"🔗 Cámara abierta por URL: {camera_url}")
                    return cap
                else:
                    cap.release()
        except Exception as e:
            print(f"⚠️ No se pudo abrir URL de cámara: {e}")
        
        # Probar varios índices y backends en Windows
        try_indices = []
        if isinstance(self.camera_id, int):
            try_indices = [self.camera_id]
        else:
            try:
                try_indices = [int(self.camera_id)]
            except:
                try_indices = []
        # agregar fallback 0..3 si no está incluido
        for i in range(0, 4):
            if i not in try_indices:
                try_indices.append(i)
        
        backends = []
        if hasattr(cv2, 'CAP_DSHOW'):
            backends.append(cv2.CAP_DSHOW)
        if hasattr(cv2, 'CAP_MSMF'):
            backends.append(cv2.CAP_MSMF)
        backends.append(None)  # CAP_ANY por defecto
        
        for idx in try_indices:
            for backend in backends:
                try:
                    cap = cv2.VideoCapture(idx) if backend is None else cv2.VideoCapture(idx, backend)
                    if cap.isOpened():
                        be_name = 'default' if backend is None else ('CAP_DSHOW' if backend == getattr(cv2, 'CAP_DSHOW', -1) else ('CAP_MSMF' if backend == getattr(cv2, 'CAP_MSMF', -1) else str(backend)))
                        print(f"📷 Cámara abierta en índice {idx} con backend {be_name}")
                        return cap
                    else:
                        cap.release()
                except Exception:
                    continue
        return None
    
    def _process_frame(self, frame):
        """Procesa el frame con YOLO y OCR"""
        if not self.detector:
            return
        # respetar cooldown
        if (time.time() - (self.last_detection_time or 0)) < self.detection_cooldown:
            return
        try:
            result = self.detector.detect_plate_from_frame(frame)
            if result and result.get('text'):
                plate = result['text']
                # Guardar info para overlay visual por unos segundos
                self.last_plate_overlay = {
                    'text': plate,
                    'bbox': result.get('bbox'),
                    'ts': time.time()
                }
                vehicle_data = self._get_vehicle_data(plate)
                if vehicle_data and self.detection_callback:
                    self.last_detection_time = time.time()
                    self.detection_callback(vehicle_data)
        except Exception as e:
            print(f"❌ Error en procesamiento de frame: {e}")
    
    def _simulate_detection(self):
        """Simula una detección para pruebas"""
        mock_plates = ['ABC123', 'XYZ789', 'DEF456', 'GHI789', 'JKL012']
        detected_plate = np.random.choice(mock_plates)
        
        # Buscar en base de datos
        vehicle_data = self._get_vehicle_data(detected_plate)
        
        if vehicle_data and self.detection_callback:
            self.last_detection_time = time.time()
            self.detection_callback(vehicle_data)
    
    def _get_vehicle_data(self, plate: str) -> Optional[dict]:
        """Busca datos mínimos del vehículo por matrícula en `vehiculos`.
        Acceso basado en `vehiculos.estado` (0 permitido, 1 denegado)."""
        try:
            # Usar la función de conexión de db.py
            from db import get_connection
            conn = get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            from db import table_name
            cursor.execute(f"""
                SELECT *
                FROM {table_name('vehiculos')}
                WHERE matricula = %s
                LIMIT 1
            """, (plate,))

            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                result = dict(result)

            if not result:
                return None

            estado = result.get('estado', 0)
            acceso = (estado == 1)

            return {
                'matricula': plate,
                'timestamp': datetime.now(),
                'confianza': 0.95,
                'propietario': result.get('propietario') or result.get('nombre') or None,
                'telefono': result.get('telefono'),
                'email': result.get('email'),
                'departamento': result.get('id_departamento'),
                'dias_restantes': None,
                'fecha_vencimiento': None,
                'estado_cuota': estado,
                'acceso': acceso,
                'motivo': None if acceso else 'Estado del vehículo denegado'
            }

        except Exception as e:
            print(f"❌ Error consultando base de datos: {e}")
            return None
    
    def get_current_frame(self):
        """Retorna el frame actual para streaming"""
        return self.current_frame

    def get_last_plate_for_overlay(self, max_age_seconds=3):
        """Devuelve la última detección para overlay si no es muy antigua"""
        if not self.last_plate_overlay:
            return None
        if time.time() - self.last_plate_overlay.get('ts', 0) <= max_age_seconds:
            return self.last_plate_overlay
        return None

# Instancia global del servicio de cámara
camera_service = None

def init_camera_service(db_config):
    """Inicializa el servicio de cámara global"""
    global camera_service
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    models_dir = os.path.abspath(models_dir)

    # Verificar existencia de pesos locales; si faltan, usar carpeta externa provista
    vehicle_weights = os.path.join(models_dir, 'yolov8n.pt')
    plate_weights = os.path.join(models_dir, 'best.pt')
    if not (os.path.exists(vehicle_weights) and os.path.exists(plate_weights)):
        external_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'automatic-number-plate-recognition-python-yolov8-main'))
        # pesos en carpeta externa: yolov8n.pt y models/best.pt
        if os.path.exists(os.path.join(external_root, 'yolov8n.pt')) and os.path.exists(os.path.join(external_root, 'models', 'best.pt')):
            models_dir = os.path.join(external_root, 'models')
        else:
            print("⚠️ Pesos de modelos no encontrados ni en backend/models ni en carpeta externa. Asegúrate de colocar 'yolov8n.pt' y 'best.pt'.")

    camera_service = CameraService(camera_id=0, db_config=db_config, models_dir=models_dir)
    return camera_service

def get_camera_service():
    """Retorna la instancia global del servicio de cámara"""
    return camera_service
