import React, { useState } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';

const VehicleAccess = () => {
  const [matricula, setMatricula] = useState('');
  const [accessType, setAccessType] = useState('general');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!matricula.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const endpoint = accessType === 'general'
        ? `${API_BASE_URL}/general/verificar-acceso`
        : `${API_BASE_URL}/cocheras/verificar-acceso`;

      const response = await axios.post(endpoint, { matricula: matricula.toUpperCase() });
      setResult(response.data);
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.response?.data?.motivo) {
        setResult(err.response.data);
      } else {
        setError('Error de conexión. Verifica que el servidor esté ejecutándose.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PERMITIDO':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'DENEGADO':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'PENDIENTE':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'PERMITIDO':
        return '✅';
      case 'DENEGADO':
        return '❌';
      case 'PENDIENTE':
        return '⏳';
      default:
        return '❓';
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Verificar Acceso de Vehículo</h2>
        <p className="text-gray-600 text-lg">Ingresa la matrícula del vehículo para verificar su acceso</p>
      </div>

      {/* Formulario */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Tipo de acceso */}
          <div>
            <label className="block text-lg font-semibold text-gray-700 mb-4">
              Tipo de Verificación
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setAccessType('general')}
                className={`p-6 rounded-2xl border-2 transition-all duration-200 ${
                  accessType === 'general'
                    ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg'
                    : 'border-gray-300 bg-white hover:border-gray-400 hover:shadow-md'
                }`}
              >
                <div className="flex items-center justify-center space-x-4">
                  <span className="text-3xl">🚗</span>
                  <div className="text-left">
                    <span className="font-semibold text-lg">Acceso General</span>
                    <p className="text-sm text-gray-600">Verificación básica</p>
                  </div>
                </div>
              </button>
              <button
                type="button"
                onClick={() => setAccessType('cocheras')}
                className={`p-6 rounded-2xl border-2 transition-all duration-200 ${
                  accessType === 'cocheras'
                    ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg'
                    : 'border-gray-300 bg-white hover:border-gray-400 hover:shadow-md'
                }`}
              >
                <div className="flex items-center justify-center space-x-4">
                  <span className="text-3xl">🏢</span>
                  <div className="text-left">
                    <span className="font-semibold text-lg">Acceso Cocheras</span>
                    <p className="text-sm text-gray-600">Verificación completa</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Campo matrícula */}
          <div>
            <label htmlFor="matricula" className="block text-lg font-semibold text-gray-700 mb-4">
              Matrícula del Vehículo
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <input
                type="text"
                id="matricula"
                value={matricula}
                onChange={(e) => setMatricula(e.target.value.toUpperCase())}
                className="w-full px-4 py-4 pl-12 text-xl font-mono border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                placeholder="ABC123"
                required
                maxLength="10"
              />
            </div>
          </div>

          {/* Botón de verificación */}
          <button
            type="submit"
            disabled={loading || !matricula.trim()}
            className="w-full bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white font-semibold py-4 px-8 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none text-lg"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-3">
                <svg className="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Verificando...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-3">
                <span className="text-2xl">🔍</span>
                <span>Verificar Acceso</span>
              </div>
            )}
          </button>
        </form>
      </div>

      {/* Mensaje de error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl">
          <div className="flex items-center space-x-3">
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">{error}</span>
          </div>
        </div>
      )}

      {/* Resultado */}
      {result && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-gray-900">Resultado de la Verificación</h3>
            <span className="text-4xl">{getStatusIcon(result.status)}</span>
          </div>

          <div className={`p-6 rounded-2xl border-2 ${getStatusColor(result.status)}`}>
            <div className="flex items-center justify-between mb-4">
              <span className="text-2xl font-mono font-bold">{result.matricula}</span>
              <span className={`px-4 py-2 rounded-full text-sm font-bold ${
                result.status === 'PERMITIDO' ? 'bg-green-100 text-green-800' :
                result.status === 'DENEGADO' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {result.status}
              </span>
            </div>

            <p className="text-lg mb-4">{result.mensaje}</p>

            {result.motivo && (
              <div className="bg-white/70 p-4 rounded-xl border mb-4">
                <p className="text-sm font-semibold text-gray-700 mb-2">Motivo:</p>
                <p className="text-sm text-gray-600">{result.motivo}</p>
              </div>
            )}

            {result.dias_restantes !== undefined && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
                <p className="text-lg font-semibold text-blue-800 mb-4">Información de Pago:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-white/70 p-4 rounded-lg">
                    <span className="text-blue-600 font-medium">Días restantes:</span>
                    <span className="ml-2 text-xl font-bold text-blue-800">{result.dias_restantes}</span>
                  </div>
                  {result.fecha_vencimiento && (
                    <div className="bg-white/70 p-4 rounded-lg">
                      <span className="text-blue-600 font-medium">Vence:</span>
                      <span className="ml-2 text-xl font-bold text-blue-800">{result.fecha_vencimiento}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default VehicleAccess;

