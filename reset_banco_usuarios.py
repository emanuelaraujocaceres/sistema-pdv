import sqlite3
import os

# Conectar ao banco
conn = sqlite3.connect('sistema.db')
cursor = conn.cursor()

# Drop da tabela antiga se existir
cursor.execute("DROP TABLE IF EXISTS usuarios")

# Criar tabela nova com a estrutura correta
cursor.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nome_completo TEXT,
        email TEXT,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()
print("✅ Tabela de usuários recriada com sucesso!")