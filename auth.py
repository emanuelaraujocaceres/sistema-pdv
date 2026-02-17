import sqlite3
import hashlib

def conectar():
    """Conecta ao banco de dados"""
    return sqlite3.connect('sistema.db')

def criar_tabela_usuarios():
    """Cria a tabela de usuários se não existir"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Verificar se a tabela já existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
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

def hash_senha(senha):
    """Cria um hash da senha para armazenamento seguro"""
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_usuario(usuario, senha, nome_completo="", email=""):
    """Cria um novo usuário no sistema"""
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        senha_hash = hash_senha(senha)
        # APENAS UMA linha de inserção (a correta, com hash)
        cursor.execute('''
            INSERT INTO usuarios (usuario, senha, nome_completo, email)
            VALUES (?, ?, ?, ?)
        ''', (usuario, senha_hash, nome_completo, email))
        conn.commit()
        return True, "Usuário criado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Nome de usuário já existe!"
    except Exception as e:
        return False, f"Erro ao criar usuário: {e}"
    finally:
        conn.close()

def verificar_login(usuario, senha):
    """Verifica se o login é válido"""
    conn = conectar()
    cursor = conn.cursor()
    
    senha_hash = hash_senha(senha)
    
    cursor.execute('''
        SELECT * FROM usuarios WHERE usuario = ? AND senha = ?
    ''', (usuario, senha_hash))
    
    usuario_encontrado = cursor.fetchone()
    conn.close()
    
    return usuario_encontrado is not None

def usuario_existe(usuario):
    """Verifica se um usuário já existe"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM usuarios WHERE usuario = ?', (usuario,))
    existe = cursor.fetchone() is not None
    
    conn.close()
    return existe