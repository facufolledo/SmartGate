import React, { useState, useEffect, useRef, useCallback } from 'react';

/**
 * AutoAccess
 * - La cámara en vivo se sirve desde el detector_sender.py en http://127.0.0.1:8090/video (HTTP).
 * - Si tu app está en HTTPS (Netlify), el navegador puede bloquear el embed (mixed content).
 *   En ese caso mostramos un botón para abrir la vista local en una pestaña aparte.
 * - Las detecciones llegan por WebSocket desde tu backend en Render y disparan alertas/historial.
 */

const WS_URL = 'wss://smartgate-ey9z.onrender.com/auto-access/ws';
const LOCAL_PREVIEW = 'http://127.0.0.1:8090/video';

const AutoAccess = () => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [currentDetection, setCurrentDetection] = useState(null);
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const [camError, setCamError] = useState(false);
  const [stats, setStats] = useState({ total: 0, permitidos: 0, denegados: 0 });

  const wsRef = useRef(null);
  const alertTimeoutRef = useRef(null);

  // Conectar WebSocket (Render)
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setIsDetecting(true);
      try { ws.send('ping'); } catch (_) {}
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg?.type === 'detection') handleDetection(msg.data);
      } catch {}
    };

    ws.onclose = () => {
      setIsDetecting(false);
      setTimeout(connectWebSocket, 4000); // reconectar
    };

    ws.onerror = () => {
      // Silencioso, onclose reintenta
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
    };
  }, [connectWebSocket]);

  // Manejar detección entrante
  const handleDetection = (data) => {
    const detection = {
      ...data,
      id: Date.now(),
      timestamp: new Date(),
    };

    setCurrentDetection(detection);
    setDetectionHistory(prev => [detection, ...prev.slice(0, 50)]);
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
      {/* Cámara en vivo (preview local) */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xl font-semibold">Cámara en vivo</h3>
          <span
            className={`inline-flex items-center gap-2 text-sm font-medium px-3 py-1 rounded-full ${
              isDetecting ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
            }`}
          >
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                isDetecting ? 'bg-green-500' : 'bg-gray-400'
              }`}
            />
            {isDetecting ? 'Detectando' : 'Sin señal del detector'}
          </span>
        </div>

        <div
          className="relative w-full overflow-hidden rounded-xl border border-gray-200"
          style={{ aspectRatio: '16/9', background: '#000' }}
        >
          {!camError ? (
            <img
              src={LOCAL_PREVIEW}
              alt="video"
              className="absolute inset-0 w-full h-full object-contain"
              onError={() => setCamError(true)}
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center p-6 text-center text-gray-700">
              <div>
                <p className="font-semibold mb-2">
                  No se pudo mostrar la cámara aquí (contenido mixto HTTP/HTTPS).
                </p>
                <p className="text-sm mb-4">
                  Asegurate de tener ejecutándose{' '}
                  <code className="px-1 py-0.5 bg-gray-100 rounded">detector_sender.py</code> en esta PC.
                  El preview está en{' '}
                  <code className="px-1 py-0.5 bg-gray-100 rounded">
                    {LOCAL_PREVIEW}
                  </code>
                  .
                </p>
                <div className="flex items-center justify-center gap-3">
                  <button
                    onClick={() => window.open(LOCAL_PREVIEW, '_blank')}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg"
                  >
                    Abrir vista local
                  </button>
                  <button
                    onClick={() => setCamError(false)}
                    className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold px-4 py-2 rounded-lg"
                  >
                    Reintentar
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-3">
                  Si otra app usa la webcam (Zoom/Meet/OBS), cerrala y reintentá.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Encabezado */}
      <div>
        <h2 className="text-3xl font-bold mb-2">Detección Automática</h2>
        <p className="text-gray-600 text-lg">
          Sistema de reconocimiento automático de patentes en tiempo real
        </p>
      </div>

      {/* Estado del sistema */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-4">
          <div
            className={`w-4 h-4 rounded-full ${
              isDetecting ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
            }`}
          />
          <span className="text-lg font-medium">
            {isDetecting ? '🔴 DETECTANDO EN VIVO' : '⚪ SIN SEÑAL DEL DETECTOR'}
          </span>
        </div>
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
            <button
              onClick={closeAlert}
              className="mt-5 bg-gray-700 hover:bg-gray-800 text-white font-semibold px-5 py-2 rounded-lg"
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
                <span className="text-sm text-gray-600">
                  {d.timestamp.toLocaleTimeString()}
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
};

export default AutoAccess;
