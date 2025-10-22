from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse
import cv2
import numpy as np
import json
import asyncio
from typing import List
import os
from camera.camera_service import init_camera_service, get_camera_service
from db import db_config
import threading
import queue

router = APIRouter(prefix="/auto-access", tags=["Auto Access"])

detection_queue = queue.Queue()


active_connections: List[WebSocket] = []


camera_service = None

def init_camera():
    """Inicializa el servicio de cámara"""
    global camera_service
    camera_service = init_camera_service(db_config)
    
    def detection_callback(vehicle_data):
        """Callback cuando se detecta una patente"""
        if os.getenv('DETECTIONS_LOG', '').lower() in ('1', 'true', 'yes', 'on'):
            print(f"🚗 DETECCIÓN: {vehicle_data['matricula']} - {'PERMITIDO' if vehicle_data['acceso'] else 'DENEGADO'}")
        
        # Enviar a la cola para WebSocket
        detection_queue.put(vehicle_data)
    
    camera_service.set_detection_callback(detection_callback)
    camera_service.start_background_capture()

@router.on_event("startup")
async def startup_event():
    """Inicializa la cámara al arrancar el servidor"""
    init_camera()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para alertas en tiempo real"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Mantener la conexión activa
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@router.get("/video-feed")
async def get_video_feed():
    """Stream de video en tiempo real"""
    def generate_frames():
        while True:
            if camera_service and camera_service.get_current_frame() is not None:
                frame = camera_service.get_current_frame().copy()
                # Overlay de última patente detectada (texto y bbox)
                overlay = camera_service.get_last_plate_for_overlay()
                if overlay:
                    try:
                        x1, y1, x2, y2 = overlay.get('bbox') or [0,0,0,0]
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label = overlay.get('text', '')
                        if label:
                            cv2.putText(frame, label, (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                    except Exception:
                        pass
                # Convertir a bytes para streaming
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                # Frame vacío si no hay cámara
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')
    
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.get("/status")
async def get_camera_status():
    """Obtiene el estado de la cámara"""
    if camera_service:
        return {
            "status": "running" if camera_service.is_running else "stopped",
            "camera_id": camera_service.camera_id,
            "last_detection": camera_service.last_detection_time
        }
    return {"status": "not_initialized"}

@router.get("/ui", response_class=HTMLResponse)
async def auto_access_ui():
    """Página simple que muestra el stream y detecciones en vivo"""
    return """
<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Auto Access - Cámara</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }
    header { padding: 12px 16px; background: #111827; border-bottom: 1px solid #1f2937; }
    h1 { margin: 0; font-size: 18px; }
    .container { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; padding: 16px; }
    .card { background: #111827; border: 1px solid #1f2937; border-radius: 8px; overflow: hidden; }
    .card h2 { margin: 0; padding: 12px 16px; font-size: 14px; border-bottom: 1px solid #1f2937; background: #0f172a; }
    .stream { display: block; width: 100%; height: auto; background: #000; }
    .list { max-height: 70vh; overflow: auto; }
    .log { padding: 12px 16px; border-bottom: 1px dashed #1f2937; }
    .ok { color: #22c55e; }
    .bad { color: #ef4444; }
    .meta { opacity: 0.7; font-size: 12px; }
  </style>
  <script>
    let ws;
    function startWS() {
      const url = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/auto-access/ws';
      ws = new WebSocket(url);
      ws.onopen = () => console.log('WS conectado');
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === 'detection') {
            appendDetection(msg.data);
          }
        } catch (_) {}
      };
      ws.onclose = () => setTimeout(startWS, 1500);
      ws.onerror = () => ws.close();
    }
    function appendDetection(d) {
      const el = document.createElement('div');
      el.className = 'log';
      const acceso = d.acceso ? '<span class=\"ok\">PERMITIDO</span>' : '<span class=\"bad\">DENEGADO</span>';
      const motivo = d.motivo ? ` · ${d.motivo}` : '';
      const dias = (d.dias_restantes ?? '') !== '' ? ` · días restantes: ${d.dias_restantes}` : '';
      el.innerHTML = `<div><b>${d.matricula}</b> · ${acceso}${motivo}${dias}</div>
                      <div class=\"meta\">${new Date(d.timestamp).toLocaleString()} · ${d.departamento ?? ''} · ${d.propietario ?? ''}</div>`;
      const list = document.getElementById('list');
      list.prepend(el);
      const nodes = list.querySelectorAll('.log');
      if (nodes.length > 100) nodes[nodes.length - 1].remove();
    }
    window.addEventListener('load', () => startWS());
  </script>
  </head>
  <body>
    <header>
      <h1>Auto Access · Cámara en vivo</h1>
    </header>
    <div class=\"container\">
      <div class=\"card\">
        <h2>Stream</h2>
        <img class=\"stream\" src=\"/auto-access/video-feed\" alt=\"video\" />
      </div>
      <div class=\"card\">
        <h2>Detecciones</h2>
        <div id=\"list\" class=\"list\"></div>
      </div>
    </div>
  </body>
</html>
    """

@router.post("/start")
async def start_camera():
    """Inicia la cámara"""
    if camera_service:
        camera_service.start_background_capture()
        return {"message": "Cámara iniciada"}
    return {"error": "Servicio de cámara no inicializado"}

@router.post("/stop")
async def stop_camera():
    """Detiene la cámara"""
    if camera_service:
        camera_service.stop_capture()
        return {"message": "Cámara detenida"}
    return {"error": "Servicio de cámara no inicializado"}

# Función para enviar alertas a todos los clientes WebSocket
async def broadcast_detection(vehicle_data: dict):
    """Envía la detección a todos los clientes conectados"""
    message = {
        "type": "detection",
        "data": vehicle_data
    }
    
    # Enviar a todas las conexiones activas
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(message))
        except:
            # Remover conexiones cerradas
            active_connections.remove(connection)

# Thread para procesar la cola de detecciones
def process_detection_queue():
    """Procesa la cola de detecciones y envía alertas"""
    while True:
        try:
            vehicle_data = detection_queue.get(timeout=1)
            asyncio.run(broadcast_detection(vehicle_data))
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error procesando detección: {e}")

# Iniciar thread de procesamiento
detection_thread = threading.Thread(target=process_detection_queue, daemon=True)
detection_thread.start()
