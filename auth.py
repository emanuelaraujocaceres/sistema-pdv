import streamlit as st
from supabase import create_client
import hashlib

# Configurações do Supabase
@st.cache_resource
def init_supabase():
    """Inicializa a conexão com o Supabase"""
    url = "https://oybrkxtwdwnyjudjpdpv.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im95YnJreHR3ZHdueWp1ZGpwZHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEyOTYwODYsImV4cCI6MjA4Njg3MjA4Nn0.gpoTwrJ8RIODJUW0CwIVqhkrOutLaX1BozoEn2fs_bI"
    return create_client(url, key)

# Inicializar cliente Supabase (uma única vez, em cache)
supabase = init_supabase()

def hash_senha(senha):
    """Cria um hash da senha para armazenamento seguro"""
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_tabela_usuarios():
    """
    Função mantida para compatibilidade.
    As tabelas já foram criadas no Supabase via SQL.
    """
    pass

def get_usuario_id(usuario):
    """
    Retorna o ID do usuário a partir do nome
    """
    try:
        response = supabase.table("usuarios").select("id").eq("usuario", usuario).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
        return None
    except Exception as e:
        st.error(f"Erro ao buscar ID do usuário: {e}")
        return None

def criar_usuario(usuario, senha, nome_completo="", email=""):
    """
    Cria um novo usuário no sistema (no Supabase)
    """
    try:
        # Verificar se usuário já existe
        if usuario_existe(usuario):
            return False, "Nome de usuário já existe!"
        
        senha_hash = hash_senha(senha)
        
        # Inserir no Supabase
        data = supabase.table("usuarios").insert({
            "usuario": usuario,
            "senha_hash": senha_hash,
            "nome_completo": nome_completo,
            "email": email
        }).execute()
        
        return True, "✅ Usuário criado com sucesso!"
        
    except Exception as e:
        return False, f"❌ Erro ao criar usuário: {str(e)}"

def verificar_login(usuario, senha):
    """
    Verifica se o login é válido no Supabase
    """
    try:
        senha_hash = hash_senha(senha)
        
        response = supabase.table("usuarios")\
            .select("*")\
            .eq("usuario", usuario)\
            .eq("senha_hash", senha_hash)\
            .execute()
        
        return len(response.data) > 0
        
    except Exception as e:
        st.error(f"Erro ao verificar login: {e}")
        return False

def usuario_existe(usuario):
    """
    Verifica se um usuário já existe no Supabase
    """
    try:
        response = supabase.table("usuarios")\
            .select("id")\
            .eq("usuario", usuario)\
            .execute()
        
        return len(response.data) > 0
        
    except Exception as e:
        st.error(f"Erro ao verificar usuário: {e}")
        return False

def listar_usuarios():
    """
    Função auxiliar para listar todos os usuários (apenas para admin)
    """
    try:
        response = supabase.table("usuarios")\
            .select("id, usuario, nome_completo, email, data_criacao")\
            .order("data_criacao", desc=True)\
            .execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
        return []