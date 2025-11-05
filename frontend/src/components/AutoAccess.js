import React, { useState, useEffect, useRef, useCallback } from 'react';
import API_BASE_URL from '../config/api';

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
  const apiBase = API_BASE_URL;

  // ✅ Memoizamos connectWebSocket para evitar warning
  const connectWebSocket = useCallback(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = (new URL(apiBase)).host || 'localhost:8000';
    const ws = new WebSocket(`${wsProtocol}://${host}/auto-access/ws`);

    let pingTimer = null;

    ws.onopen = () => {
      console.log('🔗 WebSocket conectado');
      setIsDetecting(true);
      try { ws.send('hello'); } catch (e) {}
      pingTimer = setInterval(() => { try { ws.send('ping'); } catch (e) {} }, 10000);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'detection') {
        handleDetection(message.data);
      }
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket desconectado');
      setIsDetecting(false);
      if (pingTimer) clearInterval(pingTimer);
      setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (error) => {
      console.error('❌ Error WebSocket:', error);
    };

    wsRef.current = ws;
  }, [apiBase]);

  // ✅ Efecto corregido
  useEffect(() => {
    connectWebSocket();
    return () => wsRef.current && wsRef.current.close();
  }, [connectWebSocket]);

  const handleDetection = (vehicleData) => {
    const newDetection = {
      ...vehicleData,
      id: Date.now(),
      timestamp: new Date(vehicleData.timestamp)
    };

    setCurrentDetection(newDetection);
    setDetectionHistory(prev => [newDetection, ...prev.slice(0, 9)]);
    setStats(prev => ({
      total: prev.total + 1,
      permitidos: prev.permitidos + (newDetection.acceso ? 1 : 0),
      denegados: prev.denegados + (newDetection.acceso ? 0 : 1)
    }));

    setShowAlert(true);
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
    alertTimeoutRef.current = setTimeout(() => setShowAlert(false), 8000);
  };

  // ✅ ESTA FUNCIÓN ES NECESARIA PARA EVITAR EL WARNING
  const closeAlert = () => {
    setShowAlert(false);
    if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
  };

  return (
    <div className="space-y-8">

      {/* Cámara */}
      <div className="bg-white/80 rounded-2xl shadow-lg border border-gray-200 p-4">
        <h3 className="text-xl font-semibold mb-4">Cámara en vivo</h3>
        <img
          src={`${apiBase}/auto-access/video-feed`}
          alt="video"
          className="w-full h-auto rounded-xl border border-gray-200"
        />
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

      {/* ✅ ALERTA */}
      {showAlert && currentDetection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className={`max-w-2xl w-full mx-4 p-6 rounded-2xl border-4 shadow-2xl ${
            currentDetection.acceso 
              ? 'bg-green-50 border-green-300' 
              : 'bg-red-50 border-red-300'
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

      {/* DETECCIÓN ACTUAL */}
      {currentDetection && !showAlert && (
        <div className="bg-white/80 rounded-2xl shadow-lg border border-gray-200 p-8">
          {/* Tu código original continúa aquí, no se tocó */}
        </div>
      )}

      {/* Estadísticas */}
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
          {detectionHistory.map((detection) => (
            <div key={detection.id} className={`p-4 rounded-xl border-l-4 ${
              detection.acceso ? 'bg-green-50 border-green-400' : 'bg-red-50 border-red-400'
            }`}>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-mono font-bold">{detection.matricula}</span>
                <span className="text-sm text-gray-600">{detection.timestamp.toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default AutoAccess;
