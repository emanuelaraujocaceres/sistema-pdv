import streamlit as st
from supabase import create_client
import pandas as pd

# Configurações do Supabase
@st.cache_resource
def init_supabase():
    url = "https://oybrkxtwdwnyjudjpdpv.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im95YnJreHR3ZHdueWp1ZGpwZHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEyOTYwODYsImV4cCI6MjA4Njg3MjA4Nn0.gpoTwrJ8RIODJUW0CwIVqhkrOutLaX1BozoEn2fs_bI"
    return create_client(url, key)

# Inicializar cliente Supabase
supabase = init_supabase()

def conectar():
    """Retorna o cliente Supabase (para compatibilidade)"""
    return supabase

def get_usuario_id(usuario):
    """Busca ID do usuário no Supabase"""
    try:
        response = supabase.table("usuarios").select("id").eq("usuario", usuario).execute()
        if response.data:
            return response.data[0]["id"]
        return None
    except Exception as e:
        st.error(f"Erro ao buscar usuário: {e}")
        return None

# ========== FUNÇÕES DE PRODUTO ==========
def listar_produtos(user_id):
    """Lista produtos do usuário"""
    try:
        response = supabase.table("produtos").select("*").eq("user_id", user_id).order("nome").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return pd.DataFrame()

def listar_produtos_com_estoque(user_id):
    """Lista produtos com estoque > 0"""
    try:
        response = supabase.table("produtos").select("*").eq("user_id", user_id).gt("quantidade", 0).order("nome").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return pd.DataFrame()

def criar_produto(user_id, codigo, nome, descricao, preco, quantidade, categoria):
    """Cria um novo produto"""
    try:
        # Verificar se código já existe para este usuário
        existe = supabase.table("produtos").select("id").eq("user_id", user_id).eq("codigo", codigo).execute()
        if existe.data:
            return False, f"Código '{codigo}' já existe para sua conta!"
        
        data = supabase.table("produtos").insert({
            "user_id": user_id,
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "quantidade": quantidade,
            "categoria": categoria
        }).execute()
        return True, "✅ Produto criado com sucesso!"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def atualizar_produto(user_id, id, codigo, nome, descricao, preco, quantidade, categoria):
    """Atualiza um produto existente"""
    try:
        data = supabase.table("produtos").update({
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "quantidade": quantidade,
            "categoria": categoria
        }).eq("id", id).eq("user_id", user_id).execute()
        return True, "✅ Produto atualizado!"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def excluir_produto(user_id, id):
    """Exclui um produto"""
    try:
        data = supabase.table("produtos").delete().eq("id", id).eq("user_id", user_id).execute()
        return True, "✅ Produto excluído!"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def dar_baixa_estoque(user_id, produto_id, quantidade_vendida):
    """Dá baixa no estoque após uma venda"""
    try:
        # Buscar produto
        response = supabase.table("produtos").select("quantidade").eq("id", produto_id).eq("user_id", user_id).execute()
        if response.data:
            estoque_atual = response.data[0]["quantidade"]
            if estoque_atual >= quantidade_vendida:
                novo_estoque = estoque_atual - quantidade_vendida
                supabase.table("produtos").update({"quantidade": novo_estoque}).eq("id", produto_id).eq("user_id", user_id).execute()
                return True
        return False
    except Exception as e:
        st.error(f"Erro ao dar baixa no estoque: {e}")
        return False

# ========== FUNÇÕES DE VENDA ==========
def criar_venda(user_id, total, forma_pagamento, itens):
    """Cria uma nova venda"""
    try:
        # Criar venda
        venda = supabase.table("vendas").insert({
            "user_id": user_id,
            "total": total,
            "forma_pagamento": forma_pagamento
        }).execute()
        
        venda_id = venda.data[0]["id"]
        
        # Inserir itens e dar baixa no estoque
        for item in itens:
            supabase.table("itens_venda").insert({
                "user_id": user_id,
                "venda_id": venda_id,
                "produto_id": item['id'],
                "quantidade": item['quantidade'],
                "preco_unitario": item['preco'],
                "subtotal": item['subtotal']
            }).execute()
            
            # Dar baixa no estoque
            dar_baixa_estoque(user_id, item['id'], item['quantidade'])
        
        return True, "✅ Venda finalizada com sucesso!"
    except Exception as e:
        return False, f"❌ Erro ao finalizar venda: {str(e)}"

def listar_vendas(user_id, data_inicio, data_fim):
    """Lista vendas do usuário em um período"""
    try:
        response = supabase.table("vendas").select("*")\
            .eq("user_id", user_id)\
            .gte("data_hora", f"{data_inicio}T00:00:00")\
            .lte("data_hora", f"{data_fim}T23:59:59")\
            .order("data_hora", desc=True).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao listar vendas: {e}")
        return pd.DataFrame()