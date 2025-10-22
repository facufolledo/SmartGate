# Base de Datos - Smartgate

## 📊 Estructura de la Base de Datos

### Tablas Principales

#### 1. `usuarios`
Almacena los usuarios del sistema con sus credenciales y roles.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_usuario` | INT AUTO_INCREMENT | ID único del usuario |
| `username` | VARCHAR(50) | Nombre de usuario único |
| `password_hash` | VARCHAR(255) | Hash de la contraseña (bcrypt) |
| `nombre` | VARCHAR(100) | Nombre completo del usuario |
| `rol` | ENUM('admin', 'ope') | Rol del usuario |
| `activo` | BOOLEAN | Si el usuario está activo |
| `primer_login` | BOOLEAN | Si es el primer login |
| `fecha_creacion` | TIMESTAMP | Fecha de creación |
| `ultimo_login` | TIMESTAMP | Último acceso |

#### 2. `departamentos`
Información de los departamentos del edificio.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_departamento` | INT AUTO_INCREMENT | ID único del departamento |
| `numero` | VARCHAR(10) | Número del departamento |
| `tipo` | ENUM('A', 'B', 'C', 'D') | Tipo de departamento |
| `piso` | INT | Piso del edificio |
| `activo` | BOOLEAN | Si el departamento está activo |

#### 3. `propietarios`
Datos de los propietarios de departamentos.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_propietario` | INT AUTO_INCREMENT | ID único del propietario |
| `nombre` | VARCHAR(100) | Nombre completo |
| `telefono` | VARCHAR(20) | Teléfono de contacto |
| `email` | VARCHAR(100) | Email de contacto |
| `id_departamento` | INT | ID del departamento (FK) |
| `activo` | BOOLEAN | Si el propietario está activo |

#### 4. `vehiculos`
Información de vehículos y estado de acceso.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_vehiculo` | INT AUTO_INCREMENT | ID único del vehículo |
| `matricula` | VARCHAR(20) | Patente del vehículo (única) |
| `marca` | VARCHAR(50) | Marca del vehículo |
| `modelo` | VARCHAR(50) | Modelo del vehículo |
| `color` | VARCHAR(30) | Color del vehículo |
| `id_propietario` | INT | ID del propietario (FK) |
| `estado` | INT | Estado de acceso (1=permitido, 0=denegado) |
| `fecha_registro` | TIMESTAMP | Fecha de registro |
| `fecha_ultimo_acceso` | TIMESTAMP | Último acceso detectado |
| `activo` | BOOLEAN | Si el vehículo está activo |

#### 5. `registros_acceso`
Registro de todos los accesos detectados.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_registro` | INT AUTO_INCREMENT | ID único del registro |
| `matricula` | VARCHAR(20) | Patente detectada |
| `acceso_concedido` | BOOLEAN | Si se concedió el acceso |
| `confianza` | DECIMAL(5,4) | Confianza de la detección (0-1) |
| `timestamp_deteccion` | TIMESTAMP | Momento de la detección |
| `id_usuario` | INT | Usuario que procesó (si aplica) |
| `observaciones` | TEXT | Observaciones adicionales |

## 🔧 Configuración Inicial

### 1. Crear Base de Datos
```sql
CREATE DATABASE smartgate;
USE smartgate;
```

### 2. Ejecutar Scripts en Orden
```bash
# 1. Crear estructura de tablas
mysql -u root -p smartgate < backend/sql/01_create_tables.sql

# 2. Insertar datos de prueba
mysql -u root -p smartgate < backend/sql/02_insert_sample_data.sql

# 3. Crear usuarios por defecto
mysql -u root -p smartgate < backend/sql/03_create_default_users.sql
```

### 3. Generar Hashes de Contraseña
```bash
cd backend
python generate_password_hashes.py
```

## 👥 Usuarios por Defecto

| Usuario | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| `admin` | `admin123` | admin | Administrador del sistema |
| `ope` | `ope123` | ope | Operador del sistema |

## 🚗 Datos de Prueba

### Vehículos con Acceso Permitido (estado = 1)
- `AB 123 CD` - Toyota Corolla - Juan Pérez (Depto 101)
- `EF 456 GH` - Honda Civic - María González (Depto 102)
- `IJ 789 KL` - Ford Focus - Carlos Rodríguez (Depto 201)
- `MN 012 OP` - Chevrolet Cruze - Ana Martínez (Depto 202)
- `QR 345 ST` - Volkswagen Golf - Luis Fernández (Depto 301)

### Vehículos con Acceso Denegado (estado = 0)
- `UV 678 WX` - Nissan Sentra - Sofia López (Depto 302)
- `YZ 901 AB` - Hyundai Elantra - Diego Sánchez (Depto 401)
- `CD 234 EF` - Kia Forte - Laura Torres (Depto 402)

## 🔍 Consultas Útiles

### Verificar Conexión
```sql
SELECT 'Conexión exitosa' as status;
```

### Contar Registros por Tabla
```sql
SELECT 'usuarios' as tabla, COUNT(*) as registros FROM usuarios
UNION ALL
SELECT 'departamentos', COUNT(*) FROM departamentos
UNION ALL
SELECT 'propietarios', COUNT(*) FROM propietarios
UNION ALL
SELECT 'vehiculos', COUNT(*) FROM vehiculos
UNION ALL
SELECT 'registros_acceso', COUNT(*) FROM registros_acceso;
```

### Vehículos con Acceso Permitido
```sql
SELECT v.matricula, v.marca, v.modelo, p.nombre as propietario, d.numero as departamento
FROM vehiculos v
LEFT JOIN propietarios p ON v.id_propietario = p.id_propietario
LEFT JOIN departamentos d ON p.id_departamento = d.id_departamento
WHERE v.estado = 1 AND v.activo = TRUE;
```

### Últimos Accesos Detectados
```sql
SELECT matricula, acceso_concedido, confianza, timestamp_deteccion, observaciones
FROM registros_acceso
ORDER BY timestamp_deteccion DESC
LIMIT 10;
```

## ⚠️ Notas Importantes

1. **Seguridad**: Cambiar las contraseñas por defecto en producción
2. **Backup**: Hacer respaldos regulares de la base de datos
3. **Índices**: Los índices están optimizados para consultas frecuentes
4. **Integridad**: Las claves foráneas mantienen la integridad referencial
5. **Escalabilidad**: La estructura permite agregar más departamentos y vehículos

## 🛠️ Mantenimiento

### Limpiar Registros Antiguos
```sql
-- Eliminar registros de acceso más antiguos que 30 días
DELETE FROM registros_acceso 
WHERE timestamp_deteccion < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### Actualizar Estado de Vehículos
```sql
-- Cambiar estado de acceso de un vehículo
UPDATE vehiculos 
SET estado = 0 
WHERE matricula = 'AB 123 CD';
```

### Agregar Nuevo Vehículo
```sql
INSERT INTO vehiculos (matricula, marca, modelo, color, id_propietario, estado)
VALUES ('XY 999 ZZ', 'Toyota', 'Camry', 'Azul', 1, 1);
```
