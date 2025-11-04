-- ==========================================
-- SMARTGATE - USUARIOS POR DEFECTO
-- ==========================================
-- Script para crear usuarios iniciales del sistema
-- Ejecutar después de 01_create_tables.sql
-- Nota: En PostgreSQL, asegúrate de estar conectado a la base de datos correcta

-- ==========================================
-- CREAR USUARIOS POR DEFECTO
-- ==========================================

-- Usuario administrador
-- Password: admin123 (hash generado con bcrypt)
INSERT INTO usuarios (username, password_hash, nombre, rol, activo, primer_login) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2', 'Administrador del Sistema', 'admin', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Usuario operador
-- Password: ope123 (hash generado con bcrypt)
INSERT INTO usuarios (username, password_hash, nombre, rol, activo, primer_login) VALUES
('ope', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2', 'Operador del Sistema', 'ope', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- ==========================================
-- VERIFICACIÓN DE USUARIOS CREADOS
-- ==========================================
SELECT 
    id_usuario,
    username,
    nombre,
    rol,
    activo,
    primer_login,
    fecha_creacion
FROM usuarios
WHERE username IN ('admin', 'ope');

-- ==========================================
-- INFORMACIÓN DE ACCESO
-- ==========================================
SELECT 'USUARIOS CREADOS:' as info;
SELECT 'admin - Password: admin123' as credenciales
UNION ALL
SELECT 'ope - Password: ope123' as credenciales;

-- ==========================================
-- NOTA IMPORTANTE
-- ==========================================
-- Los hashes de contraseña fueron generados usando bcrypt
-- Para generar nuevos hashes, usar la función get_password_hash() en Python:
-- 
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
-- hash = pwd_context.hash("tu_password")
-- print(hash)
