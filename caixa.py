import sqlite3
import pandas as pd
from datetime import datetime, date

def conectar():
    return sqlite3.connect('sistema.db')

def vendas_do_dia(data=None):
    """Retorna as vendas de um dia específico"""
    if data is None:
        data = date.today()
    
    conn = conectar()
    query = '''
        SELECT * FROM vendas 
        WHERE DATE(data_hora) = DATE(?)
        ORDER BY data_hora DESC
    '''
    df = pd.read_sql_query(query, conn, params=(data,))
    conn.close()
    return df

def total_vendas_periodo(data_inicio, data_fim):
    """Calcula total de vendas em um período"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(total) FROM vendas 
        WHERE DATE(data_hora) BETWEEN DATE(?) AND DATE(?)
    ''', (data_inicio, data_fim))
    
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0