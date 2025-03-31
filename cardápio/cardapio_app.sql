DROP DATABASE cardapio_app;
CREATE DATABASE cardapio_app;
USE cardapio_app;




CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    tipo ENUM('cliente', 'admin') NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
);


CREATE TABLE itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    preco DECIMAL(10,2) NOT NULL CHECK (preco >= 0),  
    imagem VARCHAR(255),
    categoria_id INT,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL  
);


CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,  
    item_id INT NOT NULL,    
    quantidade INT NOT NULL CHECK (quantidade > 0), 
    mesa INT NOT NULL CHECK (mesa > 0),  
    forma_pagamento ENUM('Dinheiro', 'Cartão', 'Pix') NOT NULL, 
    status ENUM('Pendente', 'Preparando', 'Entregue', 'Cancelado') DEFAULT 'Pendente', 
    data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,  
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id) ON DELETE CASCADE,  
    FOREIGN KEY (item_id) REFERENCES itens(id) ON DELETE CASCADE 
);


CREATE TABLE configuracoes (
    id INT PRIMARY KEY DEFAULT 1,
    total_mesas INT NOT NULL DEFAULT 20 CHECK (total_mesas > 0), 
    CONSTRAINT check_id CHECK (id = 1)
);


SET SQL_SAFE_UPDATES = 0;


INSERT INTO usuarios (nome, cpf, email, username, password, tipo)
VALUES 
    ('Admin User', '12345678901', 'admin@email.com', 'admin', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'admin'),
    ('Cliente', '98765432109', 'cliente@email.com', 'cliente', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'cliente');


INSERT INTO categorias (nome)
VALUES ('Bebidas'), ('Pratos Principais'), ('Sobremesas');


INSERT INTO configuracoes (total_mesas) VALUES (20);


SET SQL_SAFE_UPDATES = 1;