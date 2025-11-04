import React, { useState, useEffect, useRef } from 'react';
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
  const apiBase = API_BASE_URL;
  const alertTimeoutRef = useRef(null);

  // Conectar WebSocket al montar el componente
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = (new URL(apiBase)).host || 'localhost:8000';
    const ws = new WebSocket(`${wsProtocol}://${host}/auto-access/ws`);
    
    let pingTimer = null;
    ws.onopen = () => {
      console.log('🔗 WebSocket conectado');
      setIsDetecting(true);
      try { ws.send('hello'); } catch(e) {}
      pingTimer = setInterval(() => { try { ws.send('ping'); } catch(e) {} }, 10000);
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
      if (pingTimer) { clearInterval(pingTimer); pingTimer = null; }
      // Reconectar después de 5 segundos
      setTimeout(connectWebSocket, 5000);
    };
    
    ws.onerror = (error) => {
      console.error('❌ Error en WebSocket:', error);
    };
    
    wsRef.current = ws;
  };

  const handleDetection = (vehicleData) => {
    // Crear nueva detección
    const newDetection = {
      ...vehicleData,
      id: Date.now(),
      timestamp: new Date(vehicleData.timestamp)
    };
    
    // Actualizar detección actual
    setCurrentDetection(newDetection);
    
    // Agregar al historial
    setDetectionHistory(prev => [newDetection, ...prev.slice(0, 9)]);
    
    // Actualizar estadísticas
    setStats(prev => ({
      total: prev.total + 1,
      permitidos: prev.permitidos + (newDetection.acceso ? 1 : 0),
      denegados: prev.denegados + (newDetection.acceso ? 0 : 1)
    }));
    
    // Mostrar alerta emergente
    showDetectionAlert(newDetection);
  };

  const showDetectionAlert = (detection) => {
    setShowAlert(true);
    
    // Limpiar timeout anterior si existe
    if (alertTimeoutRef.current) {
      clearTimeout(alertTimeoutRef.current);
    }
    
    // Ocultar alerta después de 8 segundos
    alertTimeoutRef.current = setTimeout(() => {
      setShowAlert(false);
    }, 8000);
  };

  const closeAlert = () => {
    setShowAlert(false);
    if (alertTimeoutRef.current) {
      clearTimeout(alertTimeoutRef.current);
    }
  };

  return (
    <div className="space-y-8">
      {/* Live Stream */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-4">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Cámara en vivo</h3>
        <img
          src={`${apiBase}/auto-access/video-feed`}
          alt="video"
          className="w-full h-auto rounded-xl border border-gray-200"
        />
      </div>
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Detección Automática</h2>
        <p className="text-gray-600 text-lg">Sistema de reconocimiento automático de patentes en tiempo real</p>
      </div>

      {/* Control Panel */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Control del Sistema</h3>
          <div className="flex space-x-4">
            <button
              onClick={connectWebSocket}
              disabled={isDetecting}
              className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50"
            >
              🔗 Reconectar
            </button>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center space-x-4">
          <div className={`w-4 h-4 rounded-full ${isDetecting ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
          <span className="text-lg font-medium">
            {isDetecting ? '🔴 DETECTANDO EN VIVO' : '⚪ SISTEMA DETENIDO'}
          </span>
        </div>
      </div>

      {/* Alerta Emergente - Ventana flotante */}
      {showAlert && currentDetection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className={`max-w-2xl w-full mx-4 p-6 rounded-2xl border-4 shadow-2xl ${
            currentDetection.acceso 
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300' 
              : 'bg-gradient-to-r from-red-50 to-pink-50 border-red-300'
          }`}>
            <div className="text-center mb-6">
              <h3 className="text-3xl font-bold text-gray-900 mb-2">🚨 DETECCIÓN AUTOMÁTICA</h3>
              <p className="text-gray-600">Patente detectada automáticamente</p>
            </div>

            {/* Patente y Estado */}
            <div className="text-center mb-6">
              <div className="mb-4">
                <span className="text-6xl font-mono font-bold text-gray-900">
                  {currentDetection.matricula}
                </span>
              </div>
              
              <div className="mb-4">
                <span className={`text-3xl font-bold px-6 py-3 rounded-full ${
                  currentDetection.acceso 
                    ? 'bg-green-500 text-white' 
                    : 'bg-red-500 text-white'
                }`}>
                  {currentDetection.acceso 
                    ? `✅ Acceso concedido (estado = ${currentDetection.estado_cuota ?? 1})`
                    : `❌ Acceso denegado (estado = ${currentDetection.estado_cuota ?? 0})`}
                </span>
              </div>

              <div className="text-lg text-gray-600">
                <p>Confianza: {(currentDetection.confianza * 100).toFixed(1)}%</p>
                <p>{currentDetection.timestamp.toLocaleTimeString()}</p>
              </div>
            </div>

            {/* Información del Propietario/Vehículo */}
            <div className="bg-white/80 rounded-xl p-4 mb-4">
              <h4 className="text-xl font-bold text-gray-900 mb-3">Información del Propietario</h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="font-semibold text-gray-700">Nombre:</span>
                  <p className="text-lg">{currentDetection.propietario || 'N/A'}</p>
                </div>
                <div>
                  <span className="font-semibold text-gray-700">Departamento:</span>
                  <p className="text-lg">{currentDetection.departamento || 'N/A'}</p>
                </div>
                <div>
                  <span className="font-semibold text-gray-700">Teléfono:</span>
                  <p className="text-lg">{currentDetection.telefono || 'N/A'}</p>
                </div>
                <div>
                  <span className="font-semibold text-gray-700">Email:</span>
                  <p className="text-lg">{currentDetection.email || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* Botón de cerrar */}
            <div className="text-center">
              <button
                onClick={closeAlert}
                className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-6 rounded-lg transition-all duration-200"
              >
                Cerrar Alerta
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Current Detection - Large Display */}
      {currentDetection && !showAlert && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-8">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">DETECCIÓN ACTUAL</h3>
            <p className="text-gray-600">Última patente detectada</p>
          </div>

          <div className={`p-8 rounded-2xl border-4 ${
            currentDetection.acceso 
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200' 
              : 'bg-gradient-to-r from-red-50 to-pink-50 border-red-200'
          }`}>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Patente y Estado */}
              <div className="text-center">
                <div className="mb-6">
                  <span className="text-6xl font-mono font-bold text-gray-900">
                    {currentDetection.matricula}
                  </span>
                </div>
                
                <div className="mb-6">
                  <span className={`text-4xl font-bold px-6 py-3 rounded-full ${
                    currentDetection.acceso 
                      ? 'bg-green-500 text-white' 
                      : 'bg-red-500 text-white'
                  }`}>
                    {currentDetection.acceso 
                      ? `✅ Acceso concedido (estado = ${currentDetection.estado_cuota ?? 1})`
                      : `❌ Acceso denegado (estado = ${currentDetection.estado_cuota ?? 0})`}
                  </span>
                </div>

                <div className="text-lg text-gray-600">
                  <p>Confianza: {(currentDetection.confianza * 100).toFixed(1)}%</p>
                  <p>{currentDetection.timestamp.toLocaleTimeString()}</p>
                </div>
              </div>

              {/* Información del Propietario */}
              <div className="bg-white/70 rounded-xl p-6">
                <h4 className="text-xl font-bold text-gray-900 mb-4">Información del Propietario</h4>
                <div className="space-y-3">
                  <div>
                    <span className="font-semibold text-gray-700">Nombre:</span>
                    <p className="text-lg">{currentDetection.propietario}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-700">Departamento:</span>
                    <p className="text-lg">{currentDetection.departamento}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-700">Teléfono:</span>
                    <p className="text-lg">{currentDetection.telefono}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-700">Email:</span>
                    <p className="text-lg">{currentDetection.email}</p>
                  </div>
                  
                  {currentDetection.acceso ? (
                    <div className="bg-green-100 p-4 rounded-lg">
                      <span className="font-semibold text-green-800">Estado de Pago:</span>
                      <p className="text-green-800">✅ Al día</p>
                      <p className="text-green-800">Días restantes: {currentDetection.dias_restantes}</p>
                      <p className="text-green-800">Vence: {currentDetection.fecha_vencimiento}</p>
                    </div>
                  ) : (
                    <div className="bg-red-100 p-4 rounded-lg">
                      <span className="font-semibold text-red-800">Motivo de Denegación:</span>
                      <p className="text-red-800">❌ {currentDetection.motivo}</p>
                      {currentDetection.dias_restantes && currentDetection.dias_restantes < 0 && (
                        <p className="text-red-800">Días vencido: {Math.abs(currentDetection.dias_restantes)}</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">{stats.total}</div>
          <div className="text-gray-600">Total Detectadas</div>
        </div>
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">{stats.permitidos}</div>
          <div className="text-gray-600">Accesos Permitidos</div>
        </div>
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 text-center">
          <div className="text-3xl font-bold text-red-600 mb-2">{stats.denegados}</div>
          <div className="text-gray-600">Accesos Denegados</div>
        </div>
      </div>

      {/* Detection History */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Historial de Detecciones</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {detectionHistory.map((detection) => (
            <div key={detection.id} className={`p-4 rounded-xl border-l-4 ${
              detection.acceso 
                ? 'bg-green-50 border-green-400' 
                : 'bg-red-50 border-red-400'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className="text-2xl font-mono font-bold">{detection.matricula}</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                    detection.acceso 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {detection.acceso 
                      ? `PERMITIDO (estado=${detection.estado_cuota ?? 1})`
                      : `DENEGADO (estado=${detection.estado_cuota ?? 0})`}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  {detection.timestamp.toLocaleTimeString()}
                </div>
              </div>
              <div className="mt-2 text-sm text-gray-600">
                {detection.propietario} • Confianza: {(detection.confianza * 100).toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AutoAccess;
