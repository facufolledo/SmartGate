# Sistema de Autenticación - SmartGate

## 📋 Descripción

El sistema de autenticación permite que operadores y administradores accedan al panel de control de SmartGate para gestionar vehículos, consultar historiales y administrar el sistema.

## 🔐 Endpoints de Autenticación

### 1. Login
**POST** `/auth/login`

Autentica un usuario y devuelve un token JWT.

**Body:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user_info": {
        "id": 1,
        "username": "admin",
        "nombre": "Administrador Sistema",
        "rol": "admin",
        "primer_login": true
    }
}
```

### 2. Verificar Token
**GET** `/auth/verify-token`

Verifica si el token es válido.

**Headers:**
```
Authorization: Bearer <token>
```

### 3. Información del Usuario
**GET** `/auth/me`

Obtiene información del usuario actual.

**Headers:**
```
Authorization: Bearer <token>
```

### 4. Registrar Usuario (Solo Administradores)
**POST** `/auth/register`

Registra un nuevo usuario.

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
    "username": "nuevo_operador",
    "password": "password123",
    "nombre": "Nuevo Operador",
    "rol": "ope"
}
```

### 5. Listar Usuarios (Solo Administradores)
**GET** `/auth/users`

Obtiene lista de todos los usuarios.

**Headers:**
```
Authorization: Bearer <token>
```

## 👥 Roles de Usuario

### Administrador (`admin`)
- Acceso completo al sistema
- Puede crear nuevos usuarios
- Puede ver lista de todos los usuarios
- Gestión completa de vehículos y pagos

### Operador (`ope`)
- Acceso limitado al sistema
- Puede consultar vehículos y historiales
- No puede crear usuarios
- Operaciones básicas de gestión

## 🔑 Credenciales de Prueba

### Administrador
- **Username:** `admin`
- **Password:** `admin123`
- **Rol:** `admin`

### Operador 1
- **Username:** `operador`
- **Password:** `operador123`
- **Rol:** `ope`

### Operador 2
- **Username:** `ope1`
- **Password:** `ope123`
- **Rol:** `ope`

## 🛡️ Seguridad

### JWT Tokens
- **Algoritmo:** HS256
- **Duración:** 30 minutos
- **Secret Key:** Configurada en variables de entorno

### Contraseñas
- **Hash:** bcrypt
- **Salt:** Automático
- **Rounds:** 12 (configurable)

## 📊 Estructura de la Base de Datos

```sql
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol ENUM('admin','ope') NOT NULL,
    primer_login TINYINT(1) DEFAULT 1,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP NULL
);
```

## 🚀 Uso en el Frontend

### Ejemplo de Login
```javascript
const login = async (username, password) => {
    const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user_info));
        return data;
    } else {
        throw new Error('Credenciales incorrectas');
    }
};
```

### Ejemplo de Request Autenticado
```javascript
const getVehicles = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('/cocheras/vehicles', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};
```

## ⚠️ Notas Importantes

1. **Cambiar contraseñas en producción:** Las contraseñas de prueba deben ser cambiadas antes de usar en producción.

2. **Secret Key:** Configurar una SECRET_KEY segura en las variables de entorno.

3. **HTTPS:** En producción, usar siempre HTTPS para proteger los tokens.

4. **Logout:** Implementar logout eliminando el token del localStorage.

5. **Refresh Tokens:** Considerar implementar refresh tokens para mayor seguridad.

## 🔧 Configuración

### Variables de Entorno
```env
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=smartgate
```

### Instalación de Dependencias
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```
