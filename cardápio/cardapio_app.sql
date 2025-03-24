-- Cria o banco de dados
CREATE DATABASE cardapio_app;
USE cardapio_app;



-- Tabela de usuários
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    tipo ENUM('cliente', 'admin') NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP  -- Novo: rastreia quando o usuário foi criado
);

-- Tabela de categorias
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
);

-- Tabela de itens do cardápio
CREATE TABLE itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    preco DECIMAL(10,2) NOT NULL CHECK (preco >= 0),  -- Garante que preço não seja negativo
    imagem VARCHAR(255),
    categoria_id INT,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL  -- Se categoria for deletada, itens ficam sem categoria
);

-- Tabela de pedidos
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,  -- Torna cliente_id obrigatório
    item_id INT NOT NULL,     -- Torna item_id obrigatório
    quantidade INT NOT NULL CHECK (quantidade > 0),  -- Garante quantidade positiva
    mesa INT NOT NULL CHECK (mesa > 0),  -- Garante mesa válida
    forma_pagamento ENUM('Dinheiro', 'Cartão', 'Pix') NOT NULL,  -- Enum pra formas de pagamento
    status ENUM('Pendente', 'Preparando', 'Entregue', 'Cancelado') DEFAULT 'Pendente',  -- Enum pra status
    data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Renomeado pra evitar conflitos e clareza
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id) ON DELETE CASCADE,  -- Remove pedidos se usuário for deletado
    FOREIGN KEY (item_id) REFERENCES itens(id) ON DELETE CASCADE  -- Remove pedidos se item for deletado
);

-- Tabela de configurações
CREATE TABLE configuracoes (
    id INT PRIMARY KEY DEFAULT 1,
    total_mesas INT NOT NULL DEFAULT 20 CHECK (total_mesas > 0),  -- Garante total_mesas válido
    CONSTRAINT check_id CHECK (id = 1)
);

-- Desativa safe updates temporariamente pra ajustes iniciais (opcional, remova se não precisar)
SET SQL_SAFE_UPDATES = 0;

-- Insere usuários iniciais com senhas hasheadas (SHA-256 de '123')
INSERT INTO usuarios (nome, cpf, email, username, password, tipo)
VALUES 
    ('Admin User', '12345678901', 'admin@email.com', 'admin', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'admin'),
    ('Cliente', '98765432109', 'cliente@email.com', 'cliente', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'cliente');

-- Insere categorias iniciais
INSERT INTO categorias (nome)
VALUES ('Bebidas'), ('Pratos Principais'), ('Sobremesas');

-- Insere configuração inicial
INSERT INTO configuracoes (total_mesas) VALUES (20);

-- Reativa safe updates (opcional, ajuste conforme sua preferência)
SET SQL_SAFE_UPDATES = 1;