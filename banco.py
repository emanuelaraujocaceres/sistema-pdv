import sqlite3

def conectar():
    """Conecta ao banco de dados SQLite"""
    return sqlite3.connect('sistema.db')

def criar_tabelas():
    """Cria as tabelas necessárias se não existirem"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            quantidade INTEGER DEFAULT 0,
            categoria TEXT
        )
    ''')
    
    # Tabela de vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL,
            forma_pagamento TEXT
        )
    ''')
    
    # Tabela de itens de venda
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Criar tabelas ao importar o módulo
criar_tabelas()