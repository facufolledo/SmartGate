# ===========================================
# GUÍA DE DESPLIEGUE - SmartGate
# ===========================================

## 🚀 Despliegue en Render (Backend)

### 1. Preparación

1. **Crea una cuenta en Render**: https://render.com
2. **Crea un nuevo Web Service** desde tu repositorio de GitHub

### 2. Configuración en Render

#### Configuración del servicio:
- **Name**: `smartgate-backend`
- **Environment**: `Python 3`
- **Python Version**: `3.11` (importante para compatibilidad)
- **Region**: `Oregon` (o la más cercana)
- **Branch**: `main` (o tu rama principal)
- **Root Directory**: `backend`
- **Build Command**: `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Variables de entorno en Render:
```
DATABASE_URL=postgresql://neondb_owner:npg_KcnXpzSMw7H4@ep-cool-lake-acun8p1l-pooler.sa-east-1.aws.neon.tech/smartgate?sslmode=require&channel_binding=require
DB_SCHEMA=public
SECRET_KEY=<genera una clave secreta larga y segura>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CAMERA_INDEX=0
DETECTIONS_LOG=0
MODELS_DIR=models
```

**⚠️ IMPORTANTE**: 
- Genera una nueva `SECRET_KEY` segura para producción
- No uses la misma que en desarrollo
- Puedes generar una con: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 3. Después del despliegue

- Render te dará una URL como: `https://smartgate-backend.onrender.com`
- Guarda esta URL para configurar el frontend

---

## 🌐 Despliegue en Netlify (Frontend)

### 1. Preparación

1. **Crea una cuenta en Netlify**: https://netlify.com
2. **Crea un nuevo sitio** desde tu repositorio de GitHub

### 2. Configuración en Netlify

#### Build settings:
- **Base directory**: `frontend`
- **Build command**: `npm install && npm run build`
- **Publish directory**: `frontend/build`

#### Variables de entorno en Netlify:
```
REACT_APP_API_BASE=https://smartgate-backend.onrender.com
```

**⚠️ IMPORTANTE**: 
- Reemplaza `https://smartgate-backend.onrender.com` con la URL real de tu backend en Render
- Las variables de entorno en Netlify deben empezar con `REACT_APP_` para que React las reconozca

### 3. Configuración adicional

- El archivo `netlify.toml` ya está configurado con las redirecciones necesarias para SPA
- Netlify automáticamente detectará el archivo `netlify.toml` en la raíz del proyecto

---

## 📋 Checklist de Despliegue

### Backend (Render):
- [ ] Repositorio conectado a Render
- [ ] Variables de entorno configuradas
- [ ] `DATABASE_URL` apunta a Neon PostgreSQL
- [ ] `SECRET_KEY` generada y configurada
- [ ] Build y deploy exitosos
- [ ] Verificar que la URL del backend funciona: `https://tu-backend.onrender.com/docs`

### Frontend (Netlify):
- [ ] Repositorio conectado a Netlify
- [ ] Variable `REACT_APP_API_BASE` configurada con la URL de Render
- [ ] Build y deploy exitosos
- [ ] Verificar que la aplicación carga correctamente
- [ ] Probar login desde la aplicación desplegada

---

## 🔧 Verificación Post-Despliegue

1. **Backend**:
   - Ve a `https://tu-backend.onrender.com/docs` - Deberías ver la documentación de la API
   - Prueba `GET /general/test-db` - Debería devolver conexión exitosa

2. **Frontend**:
   - Abre la URL de Netlify
   - Intenta hacer login
   - Verifica que las llamadas a la API funcionen

---

## 🐛 Troubleshooting

### Error de CORS:
- Verifica que la URL del frontend esté en `allowed_origins` del backend
- Asegúrate de que `NETLIFY_URL` esté configurada en Render si es necesario

### Error de conexión a la base de datos:
- Verifica que `DATABASE_URL` sea correcta
- Verifica que Neon permita conexiones desde Render (debería funcionar por defecto)

### Build falla en Netlify:
- Verifica que Node.js esté en la versión correcta (18+)
- Revisa los logs de build en Netlify

### El frontend no puede conectar al backend:
- Verifica que `REACT_APP_API_BASE` esté configurada correctamente
- Verifica que el backend esté corriendo y accesible
- Revisa la consola del navegador para errores de CORS

---

## 📝 Notas Importantes

1. **Render puede suspender servicios gratuitos** después de 15 minutos de inactividad
2. **Netlify** tiene límites en el plan gratuito pero son generosos
3. **Base de datos Neon** tiene un plan gratuito con límites razonables
4. Para producción, considera planes pagos para mejor rendimiento

