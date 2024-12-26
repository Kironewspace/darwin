CREATE TABLE Clientes (
    id_cliente INT PRIMARY KEY IDENTITY,
    nombre NVARCHAR(100) NOT NULL,
    telefono NVARCHAR(15),
    email NVARCHAR(100)
);

CREATE TABLE Producto (
    id INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(50) NOT NULL,
    modelo NVARCHAR(50) NOT NULL,
    especificaciones NVARCHAR(255),
    categoria NVARCHAR(20) NOT NULL,
    tipo_accesorio NVARCHAR(20),
    stock INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    imagen VARBINARY(MAX)
);