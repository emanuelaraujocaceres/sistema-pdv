import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import banco
import auth

# ========== INICIALIZAÇÃO DA SESSÃO ==========
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = "Login"
if 'codigo_auto' not in st.session_state:
    st.session_state.codigo_auto = ""
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'modo_login' not in st.session_state:
    st.session_state.modo_login = "login"

# Configuração da página
st.set_page_config(
    page_title="Sistema de Controle Profissional",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== FUNÇÕES AUXILIARES ==========
def redirecionar_pagina(pagina):
    st.session_state.pagina_atual = pagina
    st.rerun()

def gerar_codigo(nome_input):
    if nome_input:
        import random
        palavras = nome_input.split()
        letras = []
        for p in palavras[:3]:
            if p:
                letras.append(p[0].upper())
        prefixo = ''.join(letras) if letras else "PROD"
        numero = random.randint(100, 999)
        return f"{prefixo}{numero}"
    return ""

def get_current_user_id():
    if st.session_state.autenticado:
        return auth.get_usuario_id(st.session_state.username)
    return None

def autenticar_usuario(usuario, senha):
    return auth.verificar_login(usuario, senha)

# ========== CSS PERSONALIZADO ==========
st.markdown("""
<style>
    /* ===== REMOVER TODOS OS ELEMENTOS DO STREAMLIT ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    .stApp header .stActionButton,
    .stApp header [data-testid="stActionButton"],
    .stApp header [aria-label="Share"],
    .stApp header [aria-label="Star"],
    .stApp header [aria-label="Edit app"],
    .stApp header [aria-label="Deploy"],
    button[kind="header"],
    button[kind="headerNoPadding"],
    [data-testid="stStatusWidget"],
    [data-testid="stDecoration"],
    .st-emotion-cache-1wrcr25,
    .st-emotion-cache-1miom6v,
    .st-emotion-cache-18ni7ap,
    .st-emotion-cache-1dp5yr8,
    .st-emotion-cache-1qg05tj,
    .st-emotion-cache-15ecur0 {
        display: none !important;
    }
    
    /* ===== MENU SUPERIOR FIXO ===== */
    .menu-superior {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px 30px;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        flex-wrap: wrap;
    }
    
    .menu-links {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        align-items: center;
    }
    
    .menu-link {
        color: white;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
        background-color: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        cursor: pointer;
    }
    
    .menu-link:hover {
        background-color: rgba(255,255,255,0.2);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .menu-link.ativo {
        background-color: white;
        color: #667eea;
        border-color: white;
        font-weight: bold;
    }
    
    .botao-atualizar {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 8px 24px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
    }
    
    .botao-atualizar:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
        background: linear-gradient(135deg, #20c997, #28a745);
    }
    
    .usuario-info {
        color: white;
        font-weight: 500;
        margin-right: 15px;
        padding: 8px 16px;
        background: rgba(255,255,255,0.15);
        border-radius: 8px;
    }
    
    .conteudo {
        margin-top: 90px;
        padding: 30px;
        background-color: #f8f9fa;
        min-height: calc(100vh - 90px);
    }
    
    /* ===== RESPONSIVIDADE ===== */
    @media (max-width: 768px) {
        .menu-superior {
            flex-direction: column;
            padding: 15px;
            gap: 15px;
        }
        
        .menu-links {
            justify-content: center;
            width: 100%;
        }
        
        .conteudo {
            margin-top: 150px;
            padding: 15px;
        }
    }
    
    @media (max-width: 480px) {
        .menu-links {
            flex-direction: column;
            width: 100%;
        }
        
        .menu-link {
            width: 100%;
            text-align: center;
        }
        
        .botao-atualizar {
            width: 100%;
            text-align: center;
        }
        
        .conteudo {
            margin-top: 280px;
        }
    }
    
    /* ===== ESTILOS EXISTENTES ===== */
    .produto-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .carrinho-item {
        background-color: #f1f8ff;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        color: #333333 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    [data-testid="stMetricValue"] {
        color: #667eea !important;
        font-size: 2.5rem !important;
        font-weight: bold;
    }

    .main {
        background-color: #f8f9fa !important;
    }

    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# ========== SISTEMA DE LOGIN ==========
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="color: #667eea;">💰 Sistema de Controle</h1>
            <p style="color: #666; font-size: 1.1rem;">Profissional</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.modo_login == "login":
            st.subheader("🔐 Login no Sistema")
            
            with st.form("login_form"):
                usuario = st.text_input("Usuário", key="login_usuario")
                senha = st.text_input("Senha", type="password", key="login_senha")
                login = st.form_submit_button("Entrar", use_container_width=True, type="primary")
                
                if login:
                    if autenticar_usuario(usuario, senha):
                        st.session_state.autenticado = True
                        st.session_state.username = usuario
                        st.session_state.user_id = auth.get_usuario_id(usuario)
                        st.session_state.pagina_atual = "Dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos. Tente novamente.")
            
            if st.button("📝 Criar Conta", use_container_width=True):
                st.session_state.modo_login = "criar"
                st.rerun()
        
        else:
            st.subheader("📝 Criar Nova Conta")
            
            with st.form("criar_conta_form"):
                novo_usuario = st.text_input("Novo Usuário *")
                nova_senha = st.text_input("Nova Senha *", type="password")
                conf_senha = st.text_input("Confirmar Senha *", type="password")
                nome_completo = st.text_input("Nome Completo (opcional)")
                email = st.text_input("E-mail (opcional)")
                
                st.caption("* Campos obrigatórios")
                
                if st.form_submit_button("✅ Criar Conta", use_container_width=True, type="primary"):
                    if not novo_usuario or not nova_senha:
                        st.error("❌ Usuário e senha são obrigatórios!")
                    elif nova_senha != conf_senha:
                        st.error("❌ As senhas não coincidem!")
                    elif auth.usuario_existe(novo_usuario):
                        st.error("❌ Nome de usuário já existe!")
                    else:
                        sucesso, mensagem = auth.criar_usuario(novo_usuario, nova_senha, nome_completo, email)
                        if sucesso:
                            st.success("✅ Conta criada com sucesso! Faça login.")
                            st.session_state.modo_login = "login"
                            st.rerun()
                        else:
                            st.error(f"❌ {mensagem}")
            
            if st.button("🔙 Voltar para Login", use_container_width=True):
                st.session_state.modo_login = "login"
                st.rerun()
    
    st.stop()

# ========== MENU SUPERIOR FIXO ==========
menu_html = f"""
<div class="menu-superior">
    <div class="menu-links">
        <span class="usuario-info">👤 {st.session_state.username}</span>
        <button class="menu-link {'ativo' if st.session_state.pagina_atual == 'Dashboard' else ''}" 
                onclick="window.location.href='?pagina=Dashboard'">🏠 Dashboard</button>
        <button class="menu-link {'ativo' if st.session_state.pagina_atual == 'Estoque' else ''}" 
                onclick="window.location.href='?pagina=Estoque'">📦 Estoque</button>
        <button class="menu-link {'ativo' if st.session_state.pagina_atual == 'PDV' else ''}" 
                onclick="window.location.href='?pagina=PDV'">💵 PDV</button>
        <button class="menu-link {'ativo' if st.session_state.pagina_atual == 'Relatórios' else ''}" 
                onclick="window.location.href='?pagina=Relatórios'">📊 Relatórios</button>
        <button class="menu-link {'ativo' if st.session_state.pagina_atual == 'Configurações' else ''}" 
                onclick="window.location.href='?pagina=Configurações'">⚙️ Config.</button>
        <button class="menu-link" onclick="window.location.href='?logout=true'">🚪 Sair</button>
    </div>
    <button class="botao-atualizar" onclick="window.location.reload()">🔄 Atualizar</button>
</div>
<div class="conteudo">
"""

st.markdown(menu_html, unsafe_allow_html=True)

# Corrigir comportamento de F5 e pull-to-refresh
query_params = st.experimental_get_query_params()

if "pagina" in query_params:
    pagina = query_params["pagina"][0]
    if pagina in ["Dashboard", "Estoque", "PDV", "Relatórios", "Configurações"]:
        st.session_state.pagina_atual = pagina

if "logout" in query_params:
    st.session_state.autenticado = False
    st.session_state.username = ""
    st.session_state.user_id = None
    st.session_state.pagina_atual = "Login"
    st.session_state.carrinho = []
    st.experimental_set_query_params()
    st.rerun()

# Atualizar a página sem redirecionar para o login
if not st.session_state.autenticado:
    st.session_state.pagina_atual = "Login"
    st.experimental_set_query_params(pagina="Login")
    st.stop()

# Atualizar a URL para refletir a página atual
st.experimental_set_query_params(pagina=st.session_state.pagina_atual)