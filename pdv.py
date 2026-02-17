import sqlite3
from datetime import datetime

def conectar():
    return sqlite3.connect('sistema.db')

def criar_venda(total, forma_pagamento):
    """Registra uma nova venda"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO vendas (data_hora, total, forma_pagamento)
        VALUES (?, ?, ?)
    ''', (datetime.now(), total, forma_pagamento))
    
    venda_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return venda_id

def adicionar_item(venda_id, produto_id, quantidade, preco_unitario):
    """Adiciona um item à venda"""
    conn = conectar()
    cursor = conn.cursor()
    
    subtotal = quantidade * preco_unitario
    
    cursor.execute('''
        INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
        VALUES (?, ?, ?, ?, ?)
    ''', (venda_id, produto_id, quantidade, preco_unitario, subtotal))
    
    conn.commit()
    conn.close()