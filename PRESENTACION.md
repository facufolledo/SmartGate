# 🚀 INSTRUCCIONES PARA LA PRESENTACIÓN

## 📋 Checklist Pre-Presentación

### ✅ Software Requerido
- [ ] **Python 3.8+** instalado
- [ ] **Node.js 16+** instalado  
- [ ] **MySQL 8.0+** instalado y corriendo
- [ ] **Git** instalado
- [ ] **Visual Studio Code** (ya tienes)

### ✅ Configuración Rápida (5 minutos)

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/smartgate.git
   cd smartgate
   ```

2. **Configuración automática**
   ```bash
   .\setup.bat
   ```

3. **Configurar base de datos**
   - Crear base de datos: `CREATE DATABASE smartgate;`
   - Ejecutar scripts SQL en orden:
     ```bash
     mysql -u root -p smartgate < backend/sql/01_create_tables.sql
     mysql -u root -p smartgate < backend/sql/02_insert_sample_data.sql
     mysql -u root -p smartgate < backend/sql/03_create_default_users.sql
     ```

4. **Configurar variables de entorno**
   - Editar `backend\.env` con tus credenciales de MySQL
   - Configurar cámara (USB: índice 0-3, DroidCam: URL)

### ✅ Ejecutar el Sistema

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Acceder a:**
- Frontend: http://localhost:3000
- API: http://localhost:8000/docs

## 🎯 Demo de la Presentación

### 1. **Login**
- Usuario: `admin`
- Password: `admin123`

### 2. **Funcionalidades a Mostrar**

#### A. **Acceso Automático** (Pantalla principal)
- ✅ Cámara en vivo funcionando
- ✅ Detección automática de patentes
- ✅ Notificaciones emergentes
- ✅ Estados: "Acceso concedido (estado = 1)" / "Acceso denegado (estado = 0)"

#### B. **Gestión de Vehículos**
- ✅ Lista de vehículos registrados
- ✅ Agregar/editar vehículos
- ✅ Cambiar estados de acceso
- ✅ Asociar propietarios

#### C. **Dashboard**
- ✅ Estadísticas en tiempo real
- ✅ Historial de accesos
- ✅ Gráficos de actividad

### 3. **Patentes de Prueba**
```
✅ ACCESO PERMITIDO (estado = 1):
- AB 123 CD (Toyota Corolla)
- EF 456 GH (Honda Civic)
- IJ 789 KL (Ford Focus)

❌ ACCESO DENEGADO (estado = 0):
- UV 678 WX (Nissan Sentra)
- YZ 901 AB (Hyundai Elantra)
```

## 🔧 Solución de Problemas Rápidos

### ❌ "No se pudo abrir la cámara"
```bash
# Probar diferentes índices
CAMERA_INDEX=0  # o 1, 2, 3
```

### ❌ "ModuleNotFoundError"
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### ❌ "Table doesn't exist"
```bash
# Ejecutar scripts SQL en orden
mysql -u root -p smartgate < backend/sql/01_create_tables.sql
```

### ❌ WebSocket no conecta
- Verificar que backend esté corriendo en puerto 8000
- Revisar firewall/antivirus

## 📱 Configuración de Cámara

### **Opción 1: Cámara USB**
```env
CAMERA_INDEX=0  # Probar 0, 1, 2, 3
```

### **Opción 2: DroidCam (Recomendado para demo)**
1. Instalar DroidCam en el celular
2. Conectar por USB o WiFi
3. Configurar en `.env`:
```env
CAMERA_URL=http://192.168.1.100:4747/video
```

## 🎨 Características Destacadas

### **Tecnologías Utilizadas**
- ✅ **YOLOv8** para detección de vehículos y patentes
- ✅ **EasyOCR** para reconocimiento de texto
- ✅ **FastAPI** para API REST
- ✅ **React** con Tailwind CSS para frontend
- ✅ **WebSockets** para comunicación en tiempo real
- ✅ **MySQL** para persistencia de datos

### **Mejoras Implementadas**
- ✅ **Preprocesamiento múltiple** de imágenes para mejor OCR
- ✅ **Validación de formato** de patentes Mercosur
- ✅ **Corrección automática** de caracteres
- ✅ **Notificaciones emergentes** en tiempo real
- ✅ **Sistema robusto** de apertura de cámara
- ✅ **Logging configurable** (silenciar spam)

## 📊 Datos de Prueba Incluidos

- **8 departamentos** (101-402)
- **8 propietarios** con datos completos
- **10 vehículos** con diferentes estados
- **5 registros de acceso** de ejemplo
- **2 usuarios** (admin/ope)

## 🚨 Notas Importantes

1. **Conexión a Internet**: Necesaria para descargar modelos YOLO
2. **Permisos de Cámara**: Permitir acceso en el navegador
3. **Puertos**: 3000 (frontend), 8000 (backend)
4. **Base de Datos**: MySQL debe estar corriendo
5. **Entorno Virtual**: Siempre activar antes de ejecutar backend

## 📞 Soporte de Emergencia

Si algo no funciona durante la presentación:

1. **Reiniciar servicios**:
   ```bash
   # Detener procesos (Ctrl+C)
   # Volver a ejecutar
   ```

2. **Verificar logs**:
   - Backend: consola donde ejecutas uvicorn
   - Frontend: consola del navegador (F12)

3. **Fallback**: Mostrar código y explicar arquitectura

---

## 🎉 ¡LISTO PARA LA PRESENTACIÓN!

**Tiempo estimado de setup**: 5-10 minutos
**Tiempo de demo**: 15-20 minutos
**Backup**: Código fuente y documentación completa

**¡Éxito en la presentación! 🚀**
