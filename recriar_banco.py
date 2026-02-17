import sqlite3
import os

# Remover banco antigo se existir
if os.path.exists('sistema.db'):
    os.remove('sistema.db')

# Criar novo banco
conn = sqlite3.connect('sistema.db')
cursor = conn.cursor()

# Tabela de produtos (com as novas categorias)
cursor.execute('''
    CREATE TABLE produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL,
        quantidade INTEGER DEFAULT 0,
        categoria TEXT
    )
''')

# Tabela de vendas
cursor.execute('''
    CREATE TABLE vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        total REAL NOT NULL,
        forma_pagamento TEXT
    )
''')

# Tabela de itens da venda
cursor.execute('''
    CREATE TABLE itens_venda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL,
        subtotal REAL,
        FOREIGN KEY (venda_id) REFERENCES vendas (id),
        FOREIGN KEY (produto_id) REFERENCES produtos (id)
    )
''')

conn.commit()
conn.close()
print("✅ Banco de dados recriado com sucesso!")