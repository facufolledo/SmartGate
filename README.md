# Smartgate - Sistema de Control de Acceso Automático

Sistema de control de acceso vehicular con reconocimiento automático de patentes usando YOLOv8 y EasyOCR.

## 🚀 Características

- **Detección automática de patentes** usando YOLOv8
- **Reconocimiento de texto** con EasyOCR
- **Cámara en vivo** con streaming de video
- **Notificaciones emergentes** en tiempo real
- **Base de datos MySQL** para gestión de vehículos y propietarios
- **API REST** con FastAPI
- **Frontend React** con Tailwind CSS
- **WebSockets** para comunicación en tiempo real

## 📋 Requisitos Previos

### Software Necesario
- **Python 3.8+** (recomendado 3.9 o 3.10)
- **Node.js 16+** y npm
- **MySQL 8.0+** o MariaDB
- **Git**

### Hardware Recomendado
- **Cámara USB** o IP (compatible con OpenCV)
- **Mínimo 8GB RAM** (recomendado 16GB para mejor rendimiento)
- **GPU NVIDIA** (opcional, mejora el rendimiento de YOLO)

## 🛠️ Instalación Rápida

### Opción 1: Script Automático (Windows)
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/smartgate.git
cd smartgate

# Ejecutar script de configuración automática
.\setup.bat
```

### Opción 2: Instalación Manual

#### 1. Configurar Backend
```bash
# Crear entorno virtual
cd backend
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tus configuraciones
```

#### 2. Configurar Frontend
```bash
# Instalar dependencias
cd frontend
npm install
```

#### 3. Configurar Base de Datos
```sql
-- Crear base de datos
CREATE DATABASE smartgate;

-- Importar estructura (ejecutar scripts en backend/sql/)
-- Ver sección "Base de Datos" para más detalles
```

## ⚙️ Configuración

### Variables de Entorno (.env)
```env
# Base de datos
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=smartgate

# Cámara
CAMERA_URL=http://192.168.1.100:4747/video  # Para DroidCam o cámaras IP
CAMERA_INDEX=0  # Para cámaras USB locales

# Logging
DETECTIONS_LOG=0  # 1 para mostrar logs de detección, 0 para silenciar

# API
API_HOST=localhost
API_PORT=8000
```

### Configuración de Cámara

#### Cámara USB Local
```env
CAMERA_INDEX=0  # Prueba 0, 1, 2, 3 según tu cámara
```

#### DroidCam (Android/iOS)
1. Instalar DroidCam en tu dispositivo móvil
2. Conectar por USB o WiFi
3. Configurar en .env:
```env
CAMERA_URL=http://192.168.1.100:4747/video  # IP de tu dispositivo
```

#### Cámara IP
```env
CAMERA_URL=http://ip-camara:puerto/video
```

## 🚀 Ejecución

### 1. Iniciar Backend
```bash
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Iniciar Frontend
```bash
cd frontend
npm start
```

### 3. Acceder a la Aplicación
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## 📊 Base de Datos

### Estructura Principal
- **vehiculos**: Información de vehículos y estado de acceso
- **propietarios**: Datos de propietarios
- **departamentos**: Información de departamentos
- **usuarios**: Usuarios del sistema

### Scripts de Base de Datos
Los scripts SQL están en `backend/sql/`:
- `01_create_tables.sql` - Crear tablas
- `02_insert_sample_data.sql` - Datos de prueba
- `03_create_default_users.sql` - Usuarios por defecto

### Datos de Prueba
El sistema incluye datos de prueba para testing:
- Vehículos con diferentes estados
- Propietarios asociados
- Departamentos de ejemplo

## 🔧 Solución de Problemas

### Error: "No se pudo abrir la cámara"
1. Verificar que la cámara esté conectada
2. Probar diferentes índices (0, 1, 2, 3)
3. Para DroidCam, verificar IP y puerto
4. Revisar permisos de cámara

### Error: "ModuleNotFoundError"
1. Asegurarse de que el entorno virtual esté activado
2. Ejecutar `pip install -r requirements.txt`
3. Verificar que estás usando el Python correcto

### Error: "Table doesn't exist"
1. Ejecutar scripts SQL en orden
2. Verificar conexión a base de datos
3. Revisar configuración en .env

### WebSocket no conecta
1. Verificar que el backend esté corriendo
2. Revisar firewall/antivirus
3. Comprobar URL del WebSocket en el frontend

## 📁 Estructura del Proyecto

```
smartgate/
├── backend/
│   ├── camera/
│   │   ├── camera_service.py    # Servicio de cámara
│   │   └── detector.py          # Detector ANPR
│   ├── routers/
│   │   ├── auth.py              # Autenticación
│   │   ├── auto_access.py       # Acceso automático
│   │   ├── cocheras.py          # Gestión de cocheras
│   │   └── general.py           # Rutas generales
│   ├── sql/                     # Scripts de base de datos
│   ├── models/                  # Modelos YOLO
│   ├── main.py                  # Aplicación principal
│   ├── db.py                    # Configuración DB
│   └── requirements.txt         # Dependencias Python
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AutoAccess.js    # Componente principal
│   │   │   ├── Dashboard.js     # Dashboard
│   │   │   ├── Login.js         # Login
│   │   │   └── VehicleAccess.js # Gestión vehicular
│   │   └── App.js               # App principal
│   ├── package.json             # Dependencias Node.js
│   └── tailwind.config.js       # Configuración Tailwind
├── setup.bat                    # Script de configuración automática
├── .env.example                 # Variables de entorno ejemplo
├── .gitignore                   # Archivos a ignorar
└── README.md                    # Este archivo
```

## 🎯 Uso del Sistema

### 1. Login
- Usuario: `admin`
- Password: `admin123`

### 2. Acceso Automático
- La cámara detecta patentes automáticamente
- Se muestran notificaciones emergentes
- El sistema consulta la base de datos para determinar acceso

### 3. Gestión de Vehículos
- Agregar/editar vehículos
- Asociar propietarios
- Configurar estados de acceso

## 📝 Notas de Desarrollo

### Modelos YOLO
- **yolov8n.pt**: Detección de vehículos
- **best.pt**: Detección de patentes (entrenado específicamente)

### Formatos de Patente Soportados
- **Mercosur**: AA NNN AA (ej: AB 123 CD)
- **Tradicional**: AAA NNN (ej: ABC 123)

### Mejoras de Detección
- Preprocesamiento múltiple de imágenes
- Validación de formato de patente
- Corrección automática de caracteres
- Filtrado por confianza mínima

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**¡Listo para la presentación! 🎉**
