-- ==========================================
-- SMARTGATE - DATOS DE PRUEBA
-- ==========================================
-- Script para insertar datos de ejemplo
-- Ejecutar después de 01_create_tables.sql
-- Nota: En PostgreSQL, asegúrate de estar conectado a la base de datos correcta

-- ==========================================
-- DATOS DE PRUEBA: DEPARTAMENTOS
-- ==========================================
INSERT INTO departamentos (numero, tipo, piso) VALUES
('101', 'A', 1),
('102', 'A', 1),
('201', 'B', 2),
('202', 'B', 2),
('301', 'C', 3),
('302', 'C', 3),
('401', 'D', 4),
('402', 'D', 4);

-- ==========================================
-- DATOS DE PRUEBA: PROPIETARIOS
-- ==========================================
INSERT INTO propietarios (nombre, telefono, email, id_departamento) VALUES
('Juan Pérez', '+54 11 1234-5678', 'juan.perez@email.com', 1),
('María González', '+54 11 2345-6789', 'maria.gonzalez@email.com', 2),
('Carlos Rodríguez', '+54 11 3456-7890', 'carlos.rodriguez@email.com', 3),
('Ana Martínez', '+54 11 4567-8901', 'ana.martinez@email.com', 4),
('Luis Fernández', '+54 11 5678-9012', 'luis.fernandez@email.com', 5),
('Sofia López', '+54 11 6789-0123', 'sofia.lopez@email.com', 6),
('Diego Sánchez', '+54 11 7890-1234', 'diego.sanchez@email.com', 7),
('Laura Torres', '+54 11 8901-2345', 'laura.torres@email.com', 8);

-- ==========================================
-- DATOS DE PRUEBA: VEHÍCULOS
-- ==========================================
INSERT INTO vehiculos (matricula, marca, modelo, color, id_propietario, estado) VALUES
-- Vehículos con acceso permitido (estado = 1)
('AB 123 CD', 'Toyota', 'Corolla', 'Blanco', 1, 1),
('EF 456 GH', 'Honda', 'Civic', 'Negro', 2, 1),
('IJ 789 KL', 'Ford', 'Focus', 'Azul', 3, 1),
('MN 012 OP', 'Chevrolet', 'Cruze', 'Rojo', 4, 1),
('QR 345 ST', 'Volkswagen', 'Golf', 'Gris', 5, 1),

-- Vehículos con acceso denegado (estado = 0)
('UV 678 WX', 'Nissan', 'Sentra', 'Verde', 6, 0),
('YZ 901 AB', 'Hyundai', 'Elantra', 'Amarillo', 7, 0),
('CD 234 EF', 'Kia', 'Forte', 'Marrón', 8, 0),

-- Vehículos sin propietario asociado (para testing)
('GH 567 IJ', 'BMW', 'Serie 3', 'Plateado', NULL, 1),
('KL 890 MN', 'Mercedes', 'Clase C', 'Dorado', NULL, 0);

-- ==========================================
-- DATOS DE PRUEBA: REGISTROS DE ACCESO
-- ==========================================
INSERT INTO registros_acceso (matricula, acceso_concedido, confianza, timestamp_deteccion, observaciones) VALUES
('AB 123 CD', TRUE, 0.95, NOW() - INTERVAL '2 hours', 'Acceso automático - Detección exitosa'),
('EF 456 GH', TRUE, 0.87, NOW() - INTERVAL '1 hour', 'Acceso automático - Detección exitosa'),
('UV 678 WX', FALSE, 0.92, NOW() - INTERVAL '30 minutes', 'Acceso denegado - Estado inactivo'),
('IJ 789 KL', TRUE, 0.78, NOW() - INTERVAL '15 minutes', 'Acceso automático - Detección exitosa'),
('YZ 901 AB', FALSE, 0.89, NOW() - INTERVAL '5 minutes', 'Acceso denegado - Estado inactivo');

-- ==========================================
-- VERIFICACIÓN DE DATOS INSERTADOS
-- ==========================================
SELECT 'DEPARTAMENTOS' as tabla, COUNT(*) as registros FROM departamentos
UNION ALL
SELECT 'PROPIETARIOS', COUNT(*) FROM propietarios
UNION ALL
SELECT 'VEHICULOS', COUNT(*) FROM vehiculos
UNION ALL
SELECT 'REGISTROS_ACCESO', COUNT(*) FROM registros_acceso;

-- Mostrar algunos datos de ejemplo
SELECT 'Vehículos con acceso permitido:' as info;
SELECT v.matricula, v.marca, v.modelo, p.nombre as propietario, d.numero as departamento
FROM vehiculos v
LEFT JOIN propietarios p ON v.id_propietario = p.id_propietario
LEFT JOIN departamentos d ON p.id_departamento = d.id_departamento
WHERE v.estado = 1
LIMIT 5;

SELECT 'Vehículos con acceso denegado:' as info;
SELECT v.matricula, v.marca, v.modelo, p.nombre as propietario, d.numero as departamento
FROM vehiculos v
LEFT JOIN propietarios p ON v.id_propietario = p.id_propietario
LEFT JOIN departamentos d ON p.id_departamento = d.id_departamento
WHERE v.estado = 0
LIMIT 5;
