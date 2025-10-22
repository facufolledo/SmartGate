import React, { useState } from 'react';
import VehicleAccess from './VehicleAccess';
import AutoAccess from './AutoAccess';

const Dashboard = ({ user, onLogout }) => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [drawerOpen, setDrawerOpen] = useState(false);

  const menuItems = [
    { text: 'Dashboard', icon: '📊', action: () => setCurrentView('dashboard') },
    { text: 'Detección Automática', icon: '🤖', action: () => setCurrentView('auto-access') },
    { text: 'Verificar Acceso', icon: '🚗', action: () => setCurrentView('vehicle-access') },
    { text: 'Pagos', icon: '💳', action: () => setCurrentView('payments') },
    ...(user?.rol === 'admin' ? [{ text: 'Usuarios', icon: '👥', action: () => setCurrentView('users') }] : []),
    { text: 'Configuración', icon: '⚙️', action: () => setCurrentView('settings') }
  ];

  const stats = [
    { title: 'Accesos Hoy', value: '156', change: '+12%', icon: '🚗', color: 'blue' },
    { title: 'Pagos Pendientes', value: '23', change: '-5%', icon: '💳', color: 'yellow' },
    { title: 'Usuarios Activos', value: '89', change: '+3%', icon: '👥', color: 'green' },
    { title: 'Ingresos Mensual', value: '$45,230', change: '+18%', icon: '💰', color: 'purple' }
  ];

  const getStatColor = (color) => {
    const colors = {
      blue: 'bg-blue-500',
      yellow: 'bg-yellow-500',
      green: 'bg-green-500',
      purple: 'bg-purple-500'
    };
    return colors[color] || 'bg-gray-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-lg border-b border-gray-200/50 sticky top-0 z-40">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="p-2 rounded-xl hover:bg-gray-100 transition-all duration-200 lg:hidden"
            >
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  SmartGate
                </h1>
                <p className="text-sm text-gray-600">Sistema de Control de Acceso</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium text-gray-900">{user?.nombre}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.rol}</p>
            </div>
            <button
              onClick={onLogout}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-xl transition-all duration-200 text-sm"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white/90 backdrop-blur-sm shadow-xl transform transition-transform duration-300 ease-in-out ${drawerOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:inset-0`}>
          <div className="flex items-center justify-between p-6 border-b border-gray-200/50 lg:hidden">
            <h2 className="text-lg font-semibold text-gray-900">Menú</h2>
            <button
              onClick={() => setDrawerOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <nav className="p-4">
            <ul className="space-y-2">
              {menuItems.map((item) => (
                <li key={item.text}>
                  <button
                    onClick={() => {
                      item.action();
                      setDrawerOpen(false);
                    }}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                      currentView === item.text.toLowerCase().replace(' ', '-')
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg'
                        : 'text-gray-700 hover:bg-gray-100 hover:shadow-md'
                    }`}
                  >
                    <span className="text-lg">{item.icon}</span>
                    <span className="font-medium">{item.text}</span>
                  </button>
                </li>
              ))}
            </ul>
          </nav>
        </aside>

        {/* Overlay para móvil */}
        {drawerOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setDrawerOpen(false)}
          />
        )}

        {/* Contenido principal */}
        <main className="flex-1 p-6">
          {currentView === 'dashboard' && (
            <div className="space-y-8">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h2>
                <p className="text-gray-600">Bienvenido al panel de control de SmartGate</p>
              </div>

              {/* Estadísticas */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                  <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                        <p className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</p>
                        <p className={`text-sm font-medium ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                          {stat.change} vs mes anterior
                        </p>
                      </div>
                      <div className={`w-12 h-12 ${getStatColor(stat.color)} rounded-xl flex items-center justify-center shadow-lg`}>
                        <span className="text-2xl">{stat.icon}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Acciones rápidas */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-6">Acciones Rápidas</h3>
                  <div className="space-y-4">
                    <button
                      onClick={() => setCurrentView('auto-access')}
                      className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                    >
                      <div className="flex items-center justify-center space-x-3">
                        <span className="text-2xl">🤖</span>
                        <span>Detección Automática</span>
                      </div>
                    </button>
                    <button
                      onClick={() => setCurrentView('vehicle-access')}
                      className="w-full bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                    >
                      <div className="flex items-center justify-center space-x-3">
                        <span className="text-2xl">🚗</span>
                        <span>Verificar Acceso de Vehículo</span>
                      </div>
                    </button>
                    <button
                      onClick={() => setCurrentView('payments')}
                      className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                    >
                      <div className="flex items-center justify-center space-x-3">
                        <span className="text-2xl">💳</span>
                        <span>Gestionar Pagos</span>
                      </div>
                    </button>
                  </div>
                </div>

                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-6">Actividad Reciente</h3>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-4 p-4 bg-green-50 rounded-xl border border-green-200">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Acceso autorizado</p>
                        <p className="text-xs text-gray-500">ABC123 - Hace 2 minutos</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 p-4 bg-yellow-50 rounded-xl border border-yellow-200">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Pago pendiente</p>
                        <p className="text-xs text-gray-500">XYZ789 - Hace 15 minutos</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 p-4 bg-blue-50 rounded-xl border border-blue-200">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">Nuevo usuario registrado</p>
                        <p className="text-xs text-gray-500">Usuario123 - Hace 1 hora</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentView === 'auto-access' && <AutoAccess />}
          {currentView === 'vehicle-access' && <VehicleAccess />}
          
          {currentView === 'payments' && (
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Gestión de Pagos</h2>
              <p className="text-gray-600 text-lg">Funcionalidad de pagos en desarrollo...</p>
            </div>
          )}
          
          {currentView === 'users' && user?.rol === 'admin' && (
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Gestión de Usuarios</h2>
              <p className="text-gray-600 text-lg">Panel de administración de usuarios en desarrollo...</p>
            </div>
          )}
          
          {currentView === 'settings' && (
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Configuración</h2>
              <p className="text-gray-600 text-lg">Opciones de configuración del sistema...</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
