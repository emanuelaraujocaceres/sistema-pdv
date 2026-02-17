import streamlit as st
from supabase import create_client
import hashlib
import pandas as pd

# Configurações do Supabase
@st.cache_resource
def init_supabase():
    url = "https://oybrkxtwdwnyjudjpdpv.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im95YnJreHR3ZHdueWp1ZGpwZHB2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEyOTYwODYsImV4cCI6MjA4Njg3MjA4Nn0.gpoTwrJ8RIODJUW0CwIVqhkrOutLaX1BozoEn2fs_bI"
    return create_client(url, key)

supabase = init_supabase()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ========== USUÁRIOS ==========
def criar_usuario(usuario, senha, nome_completo="", email=""):
    try:
        senha_hash = hash_senha(senha)
        data = supabase.table("usuarios").insert({
            "usuario": usuario,
            "senha_hash": senha_hash,
            "nome_completo": nome_completo,
            "email": email
        }).execute()
        return True, "✅ Usuário criado com sucesso!"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def verificar_login(usuario, senha):
    response = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
    if response.data:
        usuario_data = response.data[0]
        if usuario_data["senha_hash"] == hash_senha(senha):
            return True
    return False

def usuario_existe(usuario):
    response = supabase.table("usuarios").select("id").eq("usuario", usuario).execute()
    return len(response.data) > 0

# ========== PRODUTOS ==========
def listar_produtos():
    response = supabase.table("produtos").select("*").order("nome").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def listar_produtos_com_estoque():
    response = supabase.table("produtos").select("*").gt("quantidade", 0).order("nome").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def criar_produto(codigo, nome, descricao, preco, quantidade, categoria):
    try:
        data = supabase.table("produtos").insert({
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

def atualizar_produto(id, codigo, nome, descricao, preco, quantidade, categoria):
    try:
        data = supabase.table("produtos").update({
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "quantidade": quantidade,
            "categoria": categoria
        }).eq("id", id).execute()
        return True, "✅ Produto atualizado!"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def excluir_produto(id):
    try:
        data = supabase.table("produtos").delete().eq("id", id).execute()
        return True, "✅ Produto excluído!"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def dar_baixa_estoque(produto_id, quantidade_vendida):
    response = supabase.table("produtos").select("quantidade").eq("id", produto_id).execute()
    if response.data:
        estoque_atual = response.data[0]["quantidade"]
        novo_estoque = estoque_atual - quantidade_vendida
        supabase.table("produtos").update({"quantidade": novo_estoque}).eq("id", produto_id).execute()
        return True
    return False

# ========== VENDAS ==========
def criar_venda(total, forma_pagamento, itens):
    try:
        # Criar venda
        venda = supabase.table("vendas").insert({
            "total": total,
            "forma_pagamento": forma_pagamento
        }).execute()
        
        venda_id = venda.data[0]["id"]
        
        # Inserir itens
        for item in itens:
            supabase.table("itens_venda").insert({
                "venda_id": venda_id,
                "produto_id": item['id'],
                "quantidade": item['quantidade'],
                "preco_unitario": item['preco'],
                "subtotal": item['subtotal']
            }).execute()
            
            # Dar baixa no estoque
            dar_baixa_estoque(item['id'], item['quantidade'])
        
        return True, "✅ Venda finalizada!"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def listar_vendas(data_inicio, data_fim):
    response = supabase.table("vendas").select("*")\
        .gte("data_hora", f"{data_inicio}T00:00:00")\
        .lte("data_hora", f"{data_fim}T23:59:59")\
        .order("data_hora", desc=True).execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()