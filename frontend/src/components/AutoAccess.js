import React, { useState, useEffect, useRef, useCallback } from 'react';

const AutoAccess = () => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [currentDetection, setCurrentDetection] = useState(null);
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const [stats, setStats] = useState({ total: 0, permitidos: 0, denegados: 0 });

  // Cámara local (navegador del usuario)
  const [camReady, setCamReady] = useState(false);
  const [camMsg, setCamMsg] = useState("");

  const wsRef = useRef(null);
  const alertTimeoutRef = useRef(null);

  // ---- WebSocket (Render) ----
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket("wss://smartgate-ey9z.onrender.com/auto-access/ws");

    let pingTimer = null;
    ws.onopen = () => {
      setIsDetecting(true);
      try { ws.send('hello'); } catch {}
      pingTimer = setInterval(() => { try { ws.send('ping'); } catch {} }, 10000);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'detection') {
          handleDetection(message.data);
        }
      } catch {}
    };

    ws.onclose = () => {
      setIsDetecting(false);
      if (pingTimer) clearInterval(pingTimer);
      setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = () => {
      // solo dejamos que reconecte
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => wsRef.current && wsRef.current.close();
  }, [connectWebSocket]);

  // ---- Cámara local (se activa con botón) ----
  const startCamera = async () => {
    setCamMsg("");
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setCamMsg("Este navegador no soporta acceso a cámara.");
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      const video = document.getElementById("localCamera");
      if (video) {
        video.srcObject = stream;
        video.muted = true;
        await video.play().catch(() => {});
      }
      setCamReady(true);
      setCamMsg("Cámara activa ✅");
    } catch (err) {
      if (err?.name === "NotAllowedError") {
        setCamMsg("Permiso de cámara denegado. Habilitalo en el candado 🔒 de la barra de direcciones.");
      } else if (err?.name === "NotFoundError") {
        setCamMsg("No se encontró una cámara disponible.");
      } else if (err?.name === "NotReadableError") {
        setCamMsg("La cámara está en uso por otra app (Zoom/Meet/OBS). Cerrala y reintenta.");
      } else {
        setCamMsg("No se pudo acceder a la cámara. Revisá permisos del navegador/SO.");
      }
    }
  };

  // ---- Detecciones ----
  const handleDetection = (vehicleData) => {
    const newDetection = {
      ...vehicleData,
      id: Date.now(),
      timestamp: new Date(vehicleData.timestamp),
    };

    setCurrentDetection(newDetection);
    setDetectionHistory(prev => [newDetection, ...prev.slice(0, 9)]);
    setStats(prev => ({
      total: prev.total + 1,
      permitidos: prev.permitidos + (newDetection.acceso ? 1 : 0),
      denegados: prev.denegados + (newDetection.acceso ? 0 : 1),
    }));

    setShowAlert(true);
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
    alertTimeoutRef.current = setTimeout(() => setShowAlert(false), 8000);
  };

  const closeAlert = () => {
    setShowAlert(false);
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
  };

  return (
    <div className="space-y-8">

      {/* Cámara local */}
      <div className="bg-white/80 rounded-2xl shadow-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">Cámara en vivo</h3>
          <button
            onClick={startCamera}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg"
          >
            {camReady ? "Reiniciar cámara" : "Activar cámara"}
          </button>
        </div>

        <video
          id="localCamera"
          autoPlay
          playsInline
          className="w-full h-auto rounded-xl border border-gray-200"
        />

        {camMsg && <p className="mt-3 text-sm text-gray-600">{camMsg}</p>}

        <ul className="mt-2 text-xs text-gray-500 list-disc pl-5">
          <li>Si no aparece el prompt, tocá el candado 🔒 en la barra de direcciones y permití “Cámara”.</li>
          <li>En Brave/Chrome, el botón “Activar cámara” evita bloqueos de autoplay.</li>
          <li>Cerrá apps que usen la cámara (Zoom/Meet/OBS).</li>
          <li>Abrí el sitio por <b>HTTPS</b> (Netlify ya lo hace).</li>
        </ul>
      </div>

      <div>
        <h2 className="text-3xl font-bold mb-2">Detección Automática</h2>
        <p className="text-gray-600 text-lg">Sistema de reconocimiento automático de patentes en tiempo real</p>
      </div>

      {/* Panel */}
      <div className="bg-white/80 rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold">Control del Sistema</h3>
          <button
            onClick={connectWebSocket}
            disabled={isDetecting}
            className="bg-green-500 text-white font-semibold py-3 px-6 rounded-xl shadow transition disabled:opacity-50"
          >
            🔗 Reconectar
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <div className={`w-4 h-4 rounded-full ${isDetecting ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
          <span className="text-lg font-medium">
            {isDetecting ? '🔴 DETECTANDO EN VIVO' : '⚪ SISTEMA DETENIDO'}
          </span>
        </div>
      </div>

      {/* Alerta */}
      {showAlert && currentDetection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className={`max-w-2xl w-full mx-4 p-6 rounded-2xl border-4 shadow-2xl ${
            currentDetection.acceso ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'
          }`}>
            <div className="text-center mb-6">
              <h3 className="text-3xl font-bold mb-2">🚨 DETECCIÓN AUTOMÁTICA</h3>
              <p className="text-gray-600">Patente detectada automáticamente</p>
            </div>

            <div className="text-center mb-6">
              <span className="text-6xl font-mono font-bold text-gray-900">
                {currentDetection.matricula}
              </span>
            </div>

            <div className="text-center mb-6">
              <span className={`text-3xl font-bold px-6 py-3 rounded-full ${
                currentDetection.acceso ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
              }`}>
                {currentDetection.acceso ? '✅ Acceso concedido' : '❌ Acceso denegado'}
              </span>
            </div>

            <div className="text-center">
              <button
                onClick={closeAlert}
                className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-6 rounded-lg transition-all duration-200"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Detección actual (placeholder) */}
      {currentDetection && !showAlert && (
        <div className="bg-white/80 rounded-2xl shadow-lg border border-gray-200 p-8">
          {/* acá podés volver a poner tu bloque detallado si querés */}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white/80 rounded-2xl shadow-lg border p-6 text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">{stats.total}</div>
          <div className="text-gray-600">Total Detectadas</div>
        </div>
        <div className="bg-white/80 rounded-2xl shadow-lg border p-6 text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">{stats.permitidos}</div>
          <div className="text-gray-600">Accesos Permitidos</div>
        </div>
        <div className="bg-white/80 rounded-2xl shadow-lg border p-6 text-center">
          <div className="text-3xl font-bold text-red-600 mb-2">{stats.denegados}</div>
          <div className="text-gray-600">Accesos Denegados</div>
        </div>
      </div>

      {/* Historial */}
      <div className="bg-white/80 rounded-2xl shadow-lg border p-6">
        <h3 className="text-xl font-semibold mb-6">Historial de Detecciones</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {detectionHistory.map((d) => (
            <div key={d.id} className={`p-4 rounded-xl border-l-4 ${
              d.acceso ? 'bg-green-50 border-green-400' : 'bg-red-50 border-red-400'
            }`}>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-mono font-bold">{d.matricula}</span>
                <span className="text-sm text-gray-600">{d.timestamp.toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default AutoAccess;
