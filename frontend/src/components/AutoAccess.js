import React, { useState, useEffect, useRef, useCallback } from 'react';

const STREAM_URL = 'http://127.0.0.1:8090/video'; // servido por detector_sender.py
const WS_URL = 'wss://smartgate-ey9z.onrender.com/auto-access/ws';

const AutoAccess = () => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [currentDetection, setCurrentDetection] = useState(null);
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const [inlineBlocked, setInlineBlocked] = useState(false); // mixed-content bloqueado
  const alertTimeoutRef = useRef(null);
  const wsRef = useRef(null);

  // WebSocket para eventos de detección
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setIsDetecting(true);
      // opcional: pings suaves
      try { ws.send('hello'); } catch {}
    };

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === 'detection') {
          handleDetection(msg.data);
        }
      } catch {}
    };

    ws.onclose = () => {
      setIsDetecting(false);
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = () => {
      // silenciamos para reintentar
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => wsRef.current && wsRef.current.close();
  }, [connectWebSocket]);

  const handleDetection = (data) => {
    const d = {
      ...data,
      id: Date.now(),
      timestamp: new Date(),
    };
    setCurrentDetection(d);
    setDetectionHistory((prev) => [d, ...prev.slice(0, 50)]);
    setShowAlert(true);
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
    alertTimeoutRef.current = setTimeout(() => setShowAlert(false), 6000);
  };

  // Handler para cuando el <img> del stream falla (p.ej. por HTTPS→HTTP bloqueado)
  const onStreamError = () => {
    setInlineBlocked(true);
  };

  return (
    <div className="space-y-8">
      {/* Cámara / Stream */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-5">
        <h3 className="text-xl font-semibold mb-4">Cámara en vivo</h3>

        {/* Si estás navegando la app por HTTP, el <img> carga normalmente.
            Si estás en HTTPS, Chrome/Edge/Brave bloquean HTTP local → mostramos aviso y botón. */}
        {window.location.protocol === 'https:' ? (
          inlineBlocked ? (
            <div className="p-6 rounded-xl border border-amber-300 bg-amber-50 text-amber-900">
              <p className="mb-3 font-medium">
                No se pudo incrustar el stream por <b>contenido mixto (HTTPS→HTTP)</b>.
              </p>
              <div className="space-x-2">
                <a
                  className="inline-block px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
                  href={STREAM_URL}
                  target="_blank"
                  rel="noreferrer"
                >
                  Abrir vista local
                </a>
                <button
                  className="inline-block px-4 py-2 rounded-lg border"
                  onClick={() => setInlineBlocked(false)}
                >
                  Reintentar incrustar
                </button>
              </div>
              <ul className="mt-3 text-sm list-disc pl-5">
                <li>
                  Opcional: permití “Contenido inseguro” para este dominio (Candado → Configuración del sitio →
                  Contenido inseguro → <b>Permitir</b>) y recargá.
                </li>
              </ul>
            </div>
          ) : (
            <img
              src={STREAM_URL}
              alt="video"
              onError={onStreamError}
              className="w-full max-w-3xl mx-auto block rounded-xl border border-gray-300 shadow"
            />
          )
        ) : (
          <img
            src={STREAM_URL}
            alt="video"
            onError={onStreamError}
            className="w-full max-w-3xl mx-auto block rounded-xl border border-gray-300 shadow"
          />
        )}
      </div>

      {/* Estado del sistema */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3">
          <span
            className={`inline-block w-3.5 h-3.5 rounded-full ${
              isDetecting ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
            }`}
          />
          <span className="text-lg font-medium">
            {isDetecting ? '🔴 DETECTANDO EN VIVO' : '⚪ SIN SEÑAL DEL DETECTOR'}
          </span>
        </div>
        <p className="text-sm text-gray-500 mt-2">
          Requiere <code>detector_sender.py</code> corriendo en esta PC
          (sirve el stream en <code>http://127.0.0.1:8090/video</code> y envía detecciones por WebSocket).
        </p>
      </div>

      {/* Alerta de detección */}
      {showAlert && currentDetection && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div
            className={`p-6 rounded-2xl shadow-2xl max-w-xl w-full text-center border-4 ${
              currentDetection.acceso ? 'bg-green-50 border-green-400' : 'bg-red-50 border-red-400'
            }`}
          >
            <h2 className="text-3xl font-bold mb-4">🚨 DETECCIÓN</h2>
            <p className="text-6xl font-mono font-bold mb-4">{currentDetection.matricula}</p>
            <div
              className={`text-2xl font-bold py-3 rounded-lg ${
                currentDetection.acceso ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
              }`}
            >
              {currentDetection.acceso ? '✅ ACCESO PERMITIDO' : '❌ ACCESO DENEGADO'}
            </div>
          </div>
        </div>
      )}

      {/* Historial */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-6">
        <h3 className="text-xl font-semibold mb-4">Historial</h3>
        <div className="max-h-80 overflow-y-auto space-y-2">
          {detectionHistory.map((d) => (
            <div
              key={d.id}
              className={`p-3 rounded-lg border-l-4 ${
                d.acceso ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-2xl">{d.matricula}</span>
                <span className="text-xs text-gray-500">{d.timestamp.toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AutoAccess;
