import sqlite3
import pandas as pd

def conectar():
    return sqlite3.connect('sistema.db')

def listar_produtos():
    """Retorna todos os produtos do banco"""
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM produtos ORDER BY nome", conn)
    conn.close()
    return df

def produtos_com_estoque():
    """Retorna apenas produtos com quantidade > 0"""
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome", conn)
    conn.close()
    return df

def atualizar_estoque(produto_id, quantidade_vendida):
    """Reduz a quantidade do produto no estoque"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Verificar estoque atual
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
    estoque_atual = cursor.fetchone()[0]
    
    if estoque_atual >= quantidade_vendida:
        novo_estoque = estoque_atual - quantidade_vendida
        cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", 
                      (novo_estoque, produto_id))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False