// src/pages/AutoAccess.jsx
import React, { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL = 'wss://smartgate-ey9z.onrender.com/auto-access/ws';
const LOCAL_PREVIEW = 'http://127.0.0.1:8090/video'; // lo sirve detector_sender.py

export default function AutoAccess() {
  const [isDetecting, setIsDetecting] = useState(false);
  const [currentDetection, setCurrentDetection] = useState(null);
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const [stats, setStats] = useState({ total: 0, permitidos: 0, denegados: 0 });
  const [camError, setCamError] = useState(false);

  const wsRef = useRef(null);
  const alertTimeoutRef = useRef(null);

  // WebSocket → Render
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setIsDetecting(true);
      // opcional: mantener viva la conexión
      try { ws.send('ping'); } catch {}
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg?.type === 'detection') handleDetection(msg.data);
      } catch {}
    };

    ws.onclose = () => {
      setIsDetecting(false);
      // reintento
      setTimeout(connectWebSocket, 4000);
    };

    ws.onerror = () => {
      // no romper UI si hay error
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => wsRef.current && wsRef.current.close();
  }, [connectWebSocket]);

  // Maneja cada detección entrante
  const handleDetection = (data) => {
    const detection = {
      ...data,
      id: Date.now(),
      timestamp: new Date(),
    };

    setCurrentDetection(detection);
    setDetectionHistory(prev => [detection, ...prev].slice(0, 100));
    setStats(prev => ({
      total: prev.total + 1,
      permitidos: prev.permitidos + (detection.acceso ? 1 : 0),
      denegados: prev.denegados + (!detection.acceso ? 1 : 0),
    }));

    setShowAlert(true);
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
    alertTimeoutRef.current = setTimeout(() => setShowAlert(false), 6000);
  };

  const closeAlert = () => {
    setShowAlert(false);
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
  };

  return (
    <div className="space-y-8">
      {/* Título y descripción */}
      <div>
        <h2 className="text-3xl font-bold mb-1">Detección Automática</h2>
        <p className="text-gray-600">Sistema de reconocimiento automático de patentes en tiempo real</p>
      </div>

      {/* Cámara en vivo (usa el preview local del detector_sender.py) */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xl font-semibold">Cámara en vivo</h3>
          <span className={`inline-flex items-center gap-2 text-sm font-medium px-3 py-1 rounded-full ${isDetecting ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
            <span className={`w-2.5 h-2.5 rounded-full ${isDetecting ? 'bg-green-500' : 'bg-gray-400'}`} />
            {isDetecting ? 'Detectando' : 'Sin señal del detector'}
          </span>
        </div>

        {/* Contenedor 16:9 responsivo */}
        <div className="relative w-full overflow-hidden rounded-xl border border-gray-200" style={{ aspectRatio: '16/9', background: '#000' }}>
          {!camError && (
            <img
              src={LOCAL_PREVIEW}
              alt="video"
              className="absolute inset-0 w-full h-full object-contain"
              onError={() => setCamError(true)}
            />
          )}

          {camError && (
            <div className="absolute inset-0 flex items-center justify-center p-6">
              <div className="max-w-xl text-center text-gray-200">
                <p className="text-lg font-semibold mb-2">No se pudo mostrar la cámara</p>
                <p className="text-sm text-gray-300">
                  Asegurate de tener ejecutándose <code className="px-1 py-0.5 bg-gray-800 rounded">detector_sender.py</code> en esta PC.<br/>
                  El preview se sirve en <code className="px-1 py-0.5 bg-gray-800 rounded">http://127.0.0.1:8090/video</code>.
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  (Si abriste la webcam en otra app, cerrála para liberar el dispositivo)
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Panel estado / reconectar */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-3.5 h-3.5 rounded-full ${isDetecting ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
            <span className="text-lg font-medium">
              {isDetecting ? '🔴 DETECTANDO EN VIVO' : '⚪ SIN SEÑAL DEL DETECTOR'}
            </span>
          </div>
          <button
            onClick={connectWebSocket}
            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition"
          >
            🔗 Reconectar
          </button>
        </div>
      </div>

      {/* Alerta de detección */}
      {showAlert && currentDetection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div
            className={`p-6 rounded-2xl shadow-2xl max-w-xl w-full text-center border-4 ${
              currentDetection.acceso ? 'bg-green-50 border-green-400' : 'bg-red-50 border-red-400'
            }`}
          >
            <h3 className="text-3xl font-bold mb-4">🚨 DETECCIÓN</h3>
            <div className="text-6xl font-mono font-bold mb-4">{currentDetection.matricula}</div>
            <div
              className={`text-2xl font-bold py-3 rounded-lg mb-4 ${
                currentDetection.acceso ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
              }`}
            >
              {currentDetection.acceso ? '✅ ACCESO PERMITIDO' : '❌ ACCESO DENEGADO'}
            </div>
            <button
              onClick={closeAlert}
              className="bg-gray-700 hover:bg-gray-800 text-white font-semibold py-2 px-6 rounded-lg transition"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white/90 rounded-2xl shadow-lg border p-6 text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">{stats.total}</div>
          <div className="text-gray-600">Total Detectadas</div>
        </div>
        <div className="bg-white/90 rounded-2xl shadow-lg border p-6 text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">{stats.permitidos}</div>
          <div className="text-gray-600">Accesos Permitidos</div>
        </div>
        <div className="bg-white/90 rounded-2xl shadow-lg border p-6 text-center">
          <div className="text-3xl font-bold text-red-600 mb-2">{stats.denegados}</div>
          <div className="text-gray-600">Accesos Denegados</div>
        </div>
      </div>

      {/* Historial */}
      <div className="bg-white/90 rounded-2xl shadow-lg border p-6">
        <h3 className="text-xl font-semibold mb-4">Historial de Detecciones</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {detectionHistory.map((d) => (
            <div
              key={d.id}
              className={`p-4 rounded-xl border-l-4 ${
                d.acceso ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-2xl font-mono font-bold">{d.matricula}</span>
                <span className="text-sm text-gray-600">
                  {d.timestamp instanceof Date ? d.timestamp.toLocaleTimeString() : d.timestamp}
                </span>
              </div>
            </div>
          ))}
          {detectionHistory.length === 0 && (
            <div className="text-gray-500 text-sm">Aún no hay detecciones.</div>
          )}
        </div>
      </div>
    </div>
  );
}
