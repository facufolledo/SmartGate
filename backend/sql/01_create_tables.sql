-- ==========================================
-- SMARTGATE - ESTRUCTURA DE BASE DE DATOS
-- ==========================================
-- Script para crear todas las tablas necesarias
-- Ejecutar en PostgreSQL (Neon)

-- Nota: En PostgreSQL, la base de datos debe crearse previamente
-- CREATE DATABASE smartgate;
-- Luego conectar a esa base de datos antes de ejecutar este script

-- ==========================================
-- TABLA: usuarios
-- ==========================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(10) DEFAULT 'ope' CHECK (rol IN ('admin', 'ope')),
    activo BOOLEAN DEFAULT TRUE,
    primer_login BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP NULL
);

-- ==========================================
-- TABLA: departamentos
-- ==========================================
CREATE TABLE IF NOT EXISTS departamentos (
    id_departamento SERIAL PRIMARY KEY,
    numero VARCHAR(10) NOT NULL,
    tipo VARCHAR(1) NOT NULL CHECK (tipo IN ('A', 'B', 'C', 'D')),
    piso INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- TABLA: propietarios
-- ==========================================
CREATE TABLE IF NOT EXISTS propietarios (
    id_propietario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100),
    id_departamento INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
);

-- ==========================================
-- TABLA: vehiculos
-- ==========================================
CREATE TABLE IF NOT EXISTS vehiculos (
    id_vehiculo SERIAL PRIMARY KEY,
    matricula VARCHAR(20) UNIQUE NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    color VARCHAR(30),
    id_propietario INTEGER,
    estado INTEGER DEFAULT 1, -- 1 = acceso permitido, 0 = acceso denegado
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultimo_acceso TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_propietario) REFERENCES propietarios(id_propietario)
);

-- ==========================================
-- TABLA: registros_acceso
-- ==========================================
CREATE TABLE IF NOT EXISTS registros_acceso (
    id_registro SERIAL PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL,
    acceso_concedido BOOLEAN NOT NULL,
    confianza DECIMAL(5,4), -- Confianza de la detección (0.0000 - 1.0000)
    timestamp_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_usuario INTEGER NULL, -- Usuario que procesó manualmente (si aplica)
    observaciones TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- ==========================================
-- ÍNDICES PARA MEJORAR RENDIMIENTO
-- ==========================================
CREATE INDEX idx_vehiculos_matricula ON vehiculos(matricula);
CREATE INDEX idx_vehiculos_estado ON vehiculos(estado);
CREATE INDEX idx_registros_timestamp ON registros_acceso(timestamp_deteccion);
CREATE INDEX idx_registros_matricula ON registros_acceso(matricula);

-- ==========================================
-- COMENTARIOS EN TABLAS (PostgreSQL)
-- ==========================================
COMMENT ON TABLE usuarios IS 'Usuarios del sistema con roles admin/ope';
COMMENT ON TABLE departamentos IS 'Departamentos del edificio';
COMMENT ON TABLE propietarios IS 'Propietarios de departamentos';
COMMENT ON TABLE vehiculos IS 'Vehículos registrados con estado de acceso';
COMMENT ON TABLE registros_acceso IS 'Registro de todos los accesos detectados';

-- ==========================================
-- VERIFICACIÓN DE ESTRUCTURA
-- ==========================================
-- En PostgreSQL, usar:
-- \dt -- para listar tablas
-- \d usuarios -- para describir una tabla
