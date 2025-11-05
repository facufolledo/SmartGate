import React, { useState, useEffect, useRef, useCallback } from 'react';

const AutoAccess = () => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [currentDetection, setCurrentDetection] = useState(null);
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    permitidos: 0,
    denegados: 0
  });

  const wsRef = useRef(null);
  const alertTimeoutRef = useRef(null);

  // ✅ Conectar al WebSocket (Render)
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket("wss://smartgate-ey9z.onrender.com/auto-access/ws");

    ws.onopen = () => {
      console.log("🔗 WebSocket conectado");
      setIsDetecting(true);
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "detection") handleDetection(msg.data);
    };

    ws.onclose = () => {
      console.log("⚠️ WS cerrado — reconectando...");
      setIsDetecting(false);
      setTimeout(connectWebSocket, 4000);
    };

    ws.onerror = (err) => console.log("❌ WS Error:", err);

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => wsRef.current && wsRef.current.close();
  }, [connectWebSocket]);


  // ✅ Mostrar cámara local solo en esta página
  useEffect(() => {
    const video = document.getElementById("localCamera");
    if (!video) return;

    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => { video.srcObject = stream; })
      .catch(() => {
        console.log("🚫 No hay cámara disponible en este dispositivo.");
      });
  }, []);


  // ✅ Manejo detección entrante
  const handleDetection = (data) => {
    const detection = {
      ...data,
      timestamp: new Date(),
      id: Date.now()
    };

    setCurrentDetection(detection);
    setDetectionHistory(prev => [detection, ...prev.slice(0, 50)]);
    setStats(prev => ({
      total: prev.total + 1,
      permitidos: prev.permitidos + (detection.acceso ? 1 : 0),
      denegados: prev.denegados + (!detection.acceso ? 1 : 0)
    }));

    setShowAlert(true);
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
    alertTimeoutRef.current = setTimeout(() => setShowAlert(false), 6000);
  };

  return (
    <div className="space-y-8">

      {/* ✅ Esta cámara solo aparece aquí */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-4">
        <h3 className="text-xl font-semibold mb-3">Cámara en Vivo</h3>

        <video
          id="localCamera"
          autoPlay
          playsInline
          className="w-full h-auto rounded-xl border border-gray-300 shadow"
        />
      </div>

      {/* Estado del sistema */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-4">
          <div className={`w-4 h-4 rounded-full ${isDetecting ? "bg-green-500 animate-pulse" : "bg-gray-400"}`}></div>
          <span className="text-lg font-medium">
            {isDetecting ? "🔴 DETECTANDO EN VIVO" : "⚪ SIN SEÑAL DEL DETECTOR"}
          </span>
        </div>
      </div>

      {/* ALERTA */}
      {showAlert && currentDetection && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className={`p-6 rounded-2xl shadow-2xl max-w-xl w-full text-center border-4 ${currentDetection.acceso ? "bg-green-50 border-green-400" : "bg-red-50 border-red-400"}`}>
            <h2 className="text-3xl font-bold mb-4">🚨 DETECCIÓN</h2>
            <p className="text-6xl font-mono font-bold mb-4">{currentDetection.matricula}</p>
            <div className={`text-2xl font-bold py-3 rounded-lg ${currentDetection.acceso ? "bg-green-600 text-white" : "bg-red-600 text-white"}`}>
              {currentDetection.acceso ? "✅ ACCESO PERMITIDO" : "❌ ACCESO DENEGADO"}
            </div>
          </div>
        </div>
      )}

      {/* Historial */}
      <div className="bg-white/90 rounded-2xl shadow-lg border border-gray-200 p-6">
        <h3 className="text-xl font-semibold mb-4">Historial</h3>
        <div className="max-h-80 overflow-y-auto space-y-2">
          {detectionHistory.map(d => (
            <div key={d.id} className={`p-3 rounded-lg border-l-4 ${d.acceso ? "bg-green-50 border-green-500" : "bg-red-50 border-red-500"}`}>
              <span className="font-mono text-2xl">{d.matricula}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default AutoAccess;
