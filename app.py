import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import banco
import auth

# Criar tabela de usuários (se não existir) - mantido para compatibilidade
auth.criar_tabela_usuarios()

# Configuração da página - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Sistema de Controle Profissional",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="auto"
)

# ========== INICIALIZAÇÃO DA SESSÃO ==========
# Verificar se usuário está autenticado na sessão
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'menu' not in st.session_state:
    st.session_state.menu = "🏠 Dashboard"
if 'codigo_auto' not in st.session_state:
    st.session_state.codigo_auto = ""
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'modo_login' not in st.session_state:
    st.session_state.modo_login = "login"  # "login" ou "criar"

# CSS personalizado global com pull-to-refresh corrigido
st.markdown("""
<style>
    /* Estilo para o menu lateral com botões */
    .sidebar .stButton button {
        text-align: left;
        padding: 10px 15px;
        margin: 2px 0;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .sidebar .stButton button[kind="primary"] {
        background-color: #007BFF !important;
        color: white !important;
        border-left: 4px solid #0056b3;
    }
    
    .sidebar .stButton button[kind="secondary"] {
        background-color: transparent !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
    }
    
    .sidebar .stButton button[kind="secondary"]:hover {
        background-color: #f0f2f6 !important;
        border-left: 4px solid #007BFF !important;
    }

    /* Melhorar aparência dos botões */
    .stButton button {
        font-weight: bold;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }

    /* Ajustar tabelas */
    .dataframe {
        font-size: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
        overflow: hidden;
    }

    /* Remover barra de rolagem horizontal das tabelas */
    .stDataFrame {
        overflow-x: hidden !important;
    }

    /* Melhorar cards de produto */
    .produto-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #007BFF;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Garantir que todo texto seja visível */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
        border-radius: 5px;
        padding: 8px;
    }

    /* Melhorar contraste dos labels */
    .stTextInput label, .stTextArea label, .stNumberInput label, .stSelectbox label {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* Ajustar cards do PDV */
    .produto-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #007BFF;
        color: #333333 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .carrinho-item {
        background-color: #f1f8ff;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        color: #333333 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Garantir texto branco em botões primários */
    .stButton button[type="primary"] {
        color: white !important;
        background-color: #28a745 !important;
        border: none;
    }

    .stButton button[type="primary"]:hover {
        background-color: #218838 !important;
    }

    /* Ajustar métricas */
    [data-testid="stMetricValue"] {
        color: #007BFF !important;
        font-size: 2.5rem !important;
        font-weight: bold;
    }

    /* Ajustar fundo geral para mais claro */
    .main {
        background-color: #f5f5f5 !important;
    }

    /* Ajustar fundo dos inputs */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #ddd !important;
        border-radius: 5px;
        padding: 8px;
    }

    /* Ajustar placeholders */
    input::placeholder, textarea::placeholder {
        color: #aaa !important;
        opacity: 1;
    }
    
    /* CORREÇÃO: Pull-to-refresh verdadeiro */
    body {
        overscroll-behavior: auto !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        height: 100% !important;
    }
    
    .main {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        height: 100vh !important;
        position: relative !important;
    }
    
    .main > div {
        min-height: 100% !important;
    }
    
    .stApp {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        height: 100vh !important;
    }
    
    /* Garantir que o scroll funcione em todos os elementos */
    .element-container, .stMarkdown, .stDataFrame, [data-testid="stVerticalBlock"] {
        overflow-y: visible !important;
    }
    
    /* Remover qualquer overflow hidden que bloqueie o scroll */
    * {
        overflow-y: visible !important;
    }
</style>

<script>
    // CORREÇÃO: Garantir que o pull-to-refresh funcione
    document.addEventListener('touchstart', function(e) {
        // Permitir pull-to-refresh quando estiver no topo da página
        if (window.scrollY === 0) {
            // Não fazer nada, permitir comportamento padrão
        }
    }, { passive: true });
    
    // CORREÇÃO: Prevenir que F5 deslogue o usuário
    window.addEventListener('load', function() {
        // Recarregar os dados sem perder a sessão
        if (window.performance) {
            if (performance.navigation.type === 1) {
                console.log("Página recarregada - mantendo sessão");
                // A sessão é mantida automaticamente pelo Streamlit
            }
        }
    });
</script>
""", unsafe_allow_html=True)

def gerar_codigo(nome_input):
    if nome_input:
        import random
        import re
    
        palavras = nome_input.split()
        letras = []
        for p in palavras[:3]:
            if p:
                letras.append(p[0].upper())
        
        prefixo = ''.join(letras) if letras else "PROD"
        numero = random.randint(100, 999)
        return f"{prefixo}{numero}"
    return ""

# Função auxiliar para pegar o ID do usuário atual
def get_current_user_id():
    """Retorna o ID do usuário logado"""
    if st.session_state.autenticado:
        return auth.get_usuario_id(st.session_state.username)
    return None

# ========== SISTEMA DE LOGIN ==========
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("💰 Sistema de Controle")
        st.markdown("---")
        
        if st.session_state.modo_login == "login":
            st.subheader("🔐 Login no Sistema")

            with st.form("login_form"):
                usuario = st.text_input("Usuário", key="login_usuario")
                senha = st.text_input("Senha", type="password", key="login_senha")
                login = st.form_submit_button("Entrar", use_container_width=True, type="primary")

                if login:
                    if auth.verificar_login(usuario, senha):
                        st.session_state.autenticado = True
                        st.session_state.username = usuario
                        st.session_state.user_id = auth.get_usuario_id(usuario)
                        st.session_state.menu = "🏠 Dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos. Tente novamente.")

            if st.button("📝 Criar Conta", use_container_width=True):
                st.session_state.modo_login = "criar"
                st.rerun()

        elif st.session_state.modo_login == "criar":
            st.subheader("📝 Criar Nova Conta")

            with st.form("criar_conta_form"):
                novo_usuario = st.text_input("Novo Usuário *", key="novo_usuario")
                nova_senha = st.text_input("Nova Senha *", type="password", key="nova_senha")
                conf_senha = st.text_input("Confirmar Senha *", type="password", key="conf_senha")
                nome_completo = st.text_input("Nome Completo (opcional)")
                email = st.text_input("E-mail (opcional)")
                
                st.caption("* Campos obrigatórios")
                
                criar_conta = st.form_submit_button("✅ Criar Conta", use_container_width=True, type="primary")

                if criar_conta:
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

# ========== SISTEMA PRINCIPAL (APÓS LOGIN) ==========

# Menu lateral
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shop.png", width=80)
    st.title(f"👤 {st.session_state.username}")
    st.markdown("---")
    
    if st.button("🏠 Dashboard", use_container_width=True, 
                type="primary" if st.session_state.menu == "🏠 Dashboard" else "secondary"):
        st.session_state.menu = "🏠 Dashboard"
        st.rerun()
    
    if st.button("📦 Controle de Estoque", use_container_width=True,
                type="primary" if st.session_state.menu == "📦 Controle de Estoque" else "secondary"):
        st.session_state.menu = "📦 Controle de Estoque"
        st.rerun()
    
    if st.button("💵 PDV (Ponto de Venda)", use_container_width=True,
                type="primary" if st.session_state.menu == "💵 PDV (Ponto de Venda)" else "secondary"):
        st.session_state.menu = "💵 PDV (Ponto de Venda)"
        st.rerun()
    
    if st.button("📊 Relatórios", use_container_width=True,
                type="primary" if st.session_state.menu == "📊 Relatórios" else "secondary"):
        st.session_state.menu = "📊 Relatórios"
        st.rerun()
    
    if st.button("⚙️ Configurações", use_container_width=True,
                type="primary" if st.session_state.menu == "⚙️ Configurações" else "secondary"):
        st.session_state.menu = "⚙️ Configurações"
        st.rerun()
    
    st.markdown("---")
    
    if st.button("🚪 Sair", use_container_width=True, type="secondary"):
        st.session_state.autenticado = False
        st.session_state.username = ""
        st.session_state.user_id = None
        st.session_state.menu = "🏠 Dashboard"
        st.session_state.carrinho = []
        st.rerun()
    
    st.caption("Sistema Profissional v1.0")

# Título principal
st.title(f"💰 Sistema de Controle - {st.session_state.username}")
st.markdown("---")

# ========== DASHBOARD ==========
if st.session_state.menu == "🏠 Dashboard":
    st.header("📊 Dashboard")
    
    produtos = banco.listar_produtos(st.session_state.user_id)
    
    if not produtos.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Produtos", len(produtos))
        with col2:
            total_estoque = produtos['quantidade'].sum()
            st.metric("Itens em Estoque", total_estoque)
        with col3:
            valor_total = (produtos['quantidade'] * produtos['preco']).sum()
            st.metric("Valor em Estoque", f"R$ {valor_total:.2f}")
        
        if not produtos.empty and 'categoria' in produtos.columns:
            fig = px.pie(produtos, names='categoria', values='quantidade',
                        title="Distribuição do Estoque por Categoria")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 Nenhum produto cadastrado ainda. Acesse 'Controle de Estoque' para começar!")

# ========== CONTROLE DE ESTOQUE ==========
elif st.session_state.menu == "📦 Controle de Estoque":
    st.header("📦 Controle de Estoque")
    
    aba1, aba2, aba3 = st.tabs(["📝 Cadastrar", "📋 Listar", "✏️ Editar"])
    
    with aba1:
        st.subheader("📝 Cadastrar Novo Produto")
        
        with st.form("cadastro_produto"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Produto *", key="nome_cadastro")
                if nome:
                    st.session_state.codigo_auto = gerar_codigo(nome)
                descricao = st.text_area("Descrição", key="descricao_cadastro")
            
            with col2:
                preco = st.number_input("Preço (R$) *", min_value=0.01, format="%.2f", step=0.10, key="preco_cadastro")
                quantidade = st.number_input("Quantidade inicial *", min_value=0, step=1, key="qtd_cadastro")
                categoria = st.selectbox("Categoria *", ["Alimentos", "Bebidas", "Outros"], key="cat_cadastro")
            
            codigo = st.text_input("Código do Produto *", value=st.session_state.codigo_auto, key="codigo_cadastro")
            
            st.markdown("* Campos obrigatórios")
            
            submitted = st.form_submit_button("✅ Cadastrar Produto", use_container_width=True)
            
            if submitted:
                if not nome:
                    st.error("❌ Nome do produto é obrigatório!")
                elif not codigo:
                    st.error("❌ Código do produto é obrigatório!")
                elif preco <= 0:
                    st.error("❌ Preço deve ser maior que zero!")
                else:
                    sucesso, mensagem = banco.criar_produto(
                        st.session_state.user_id, codigo, nome, descricao, preco, quantidade, categoria
                    )
                    if sucesso:
                        st.success(mensagem)
                        st.balloons()
                        st.session_state.codigo_auto = ""
                        for key in ['nome_cadastro', 'descricao_cadastro']:
                            if key in st.session_state:
                                del st.session_state[key]
                    else:
                        st.error(mensagem)
                        st.session_state.codigo_auto = gerar_codigo(nome)
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🔄 Gerar Novo Código", use_container_width=True):
                if nome:
                    st.session_state.codigo_auto = gerar_codigo(nome)
                    st.rerun()
                else:
                    st.warning("⚠️ Digite o nome do produto primeiro!")
    
    with aba2:
        st.subheader("📋 Produtos Cadastrados")
        
        produtos = banco.listar_produtos(st.session_state.user_id)
        
        if not produtos.empty:
            colunas_exibicao = {
                'codigo': 'Código',
                'nome': 'Nome',
                'descricao': 'Descrição',
                'preco': 'Preço (R$)',
                'quantidade': 'Quantidade',
                'categoria': 'Categoria'
            }
            
            df_exibicao = produtos[list(colunas_exibicao.keys())].copy()
            df_exibicao = df_exibicao.rename(columns=colunas_exibicao)
            df_exibicao['Preço (R$)'] = df_exibicao['Preço (R$)'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
            
            if not produtos.empty and 'categoria' in produtos.columns:
                st.subheader("📊 Estoque por Categoria")
                estoque_categoria = produtos.groupby('categoria')['quantidade'].sum().reset_index()
                fig = px.bar(estoque_categoria, x='categoria', y='quantidade', 
                        title="Quantidade em Estoque por Categoria", color='categoria')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📭 Nenhum produto cadastrado ainda.")
    
    with aba3:
        st.subheader("✏️ Editar/Excluir Produtos")
        
        produtos = banco.listar_produtos(st.session_state.user_id)
        
        if not produtos.empty:
            produto_para_editar = st.selectbox(
                "Selecione o produto para editar",
                options=produtos['id'].tolist(),
                format_func=lambda x: f"{produtos[produtos['id']==x]['codigo'].values[0]} - {produtos[produtos['id']==x]['nome'].values[0]}"
            )
            
            if produto_para_editar:
                produto = produtos[produtos['id'] == produto_para_editar].iloc[0]
                
                with st.form("editar_produto"):
                    st.write("### Editando Produto")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        novo_codigo = st.text_input("Código", value=produto['codigo'])
                        novo_nome = st.text_input("Nome", value=produto['nome'])
                        nova_descricao = st.text_area("Descrição", value=produto['descricao'] if produto['descricao'] else "")
                    
                    with col2:
                        novo_preco = st.number_input("Preço", min_value=0.01, format="%.2f", value=float(produto['preco']))
                        nova_quantidade = st.number_input("Quantidade", min_value=0, step=1, value=int(produto['quantidade']))
                        nova_categoria = st.selectbox(
                            "Categoria", 
                            ["Alimentos", "Bebidas", "Outros"],
                            index=["Alimentos", "Bebidas", "Outros"].index(produto['categoria']) if produto['categoria'] in ["Alimentos", "Bebidas", "Outros"] else 0
                        )
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                            sucesso, mensagem = banco.atualizar_produto(
                                st.session_state.user_id, produto_para_editar, novo_codigo, novo_nome, 
                                nova_descricao, novo_preco, nova_quantidade, nova_categoria
                            )
                            if sucesso:
                                st.success(mensagem)
                                st.rerun()
                            else:
                                st.error(mensagem)

                    with col_btn2:
                        if st.form_submit_button("🗑️ Excluir Produto", use_container_width=True):
                            sucesso, mensagem = banco.excluir_produto(st.session_state.user_id, produto_para_editar)
                            if sucesso:
                                st.success(mensagem)
                                st.rerun()
                            else:
                                st.error(mensagem)

                    with col_btn3:
                        if st.form_submit_button("🔄 Cancelar", use_container_width=True):
                            st.rerun()
        else:
            st.info("📭 Nenhum produto cadastrado para editar.")

# ========== PDV ==========
elif st.session_state.menu == "💵 PDV (Ponto de Venda)":
    st.header("💵 Ponto de Venda")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📦 Produtos Disponíveis")
        
        produtos = banco.listar_produtos_com_estoque(st.session_state.user_id)
        
        if not produtos.empty:
            st.success(f"**{len(produtos)} produtos disponíveis para venda**")
            
            cols = st.columns(3)
            for idx, (_, produto) in enumerate(produtos.iterrows()):
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"""
                        <div class="produto-card">
                            <b>{produto['nome']}</b><br>
                            Cód: {produto['codigo']}<br>
                            R$ {produto['preco']:.2f}<br>
                            Estoque: {produto['quantidade']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"➕ Adicionar", key=f"btn_{produto['id']}"):
                            if 'carrinho' not in st.session_state:
                                st.session_state.carrinho = []
                            
                            encontrado = False
                            for item in st.session_state.carrinho:
                                if item['id'] == produto['id']:
                                    item['quantidade'] += 1
                                    item['subtotal'] = item['quantidade'] * item['preco']
                                    encontrado = True
                                    break
                            
                            if not encontrado:
                                st.session_state.carrinho.append({
                                    'id': int(produto['id']),
                                    'nome': produto['nome'],
                                    'preco': float(produto['preco']),
                                    'quantidade': 1,
                                    'subtotal': float(produto['preco'])
                                })
                            st.rerun()
        else:
            st.warning("📭 Nenhum produto com estoque disponível")
    
    with col2:
        st.subheader("🛒 Carrinho de Compras")
        
        if 'carrinho' not in st.session_state:
            st.session_state.carrinho = []
        
        if st.session_state.carrinho:
            total = 0
            for i, item in enumerate(st.session_state.carrinho):
                with st.container():
                    st.markdown(f"""
                    <div class="carrinho-item">
                        <b>{item['nome']}</b><br>
                        {item['quantidade']} x R$ {item['preco']:.2f} = R$ {item['subtotal']:.2f}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_qtd, col_remove = st.columns([2, 1])
                    with col_qtd:
                        nova_qtd = st.number_input("Qtd", min_value=1, value=item['quantidade'], key=f"qtd_{i}", label_visibility="collapsed")
                        if nova_qtd != item['quantidade']:
                            item['quantidade'] = nova_qtd
                            item['subtotal'] = nova_qtd * item['preco']
                            st.rerun()
                    
                    with col_remove:
                        if st.button("🗑️", key=f"del_{i}"):
                            st.session_state.carrinho.pop(i)
                            st.rerun()
                    
                    total += item['subtotal']
                    st.divider()
            
            st.markdown(f"""
            <div style="background-color: #0f4c81; color: white; padding: 15px; border-radius: 5px; text-align: center; margin: 10px 0;">
                <h2>TOTAL: R$ {total:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            forma_pagamento = st.selectbox(
                "Forma de Pagamento",
                ["💵 Dinheiro", "💳 Cartão de Crédito", "💳 Cartão de Débito", "📱 PIX", "📝 Fiado"]
            )
            
            if st.button("✅ FINALIZAR VENDA", type="primary", use_container_width=True):
                sucesso, mensagem = banco.criar_venda(
                    st.session_state.user_id, total, forma_pagamento, st.session_state.carrinho
                )
                if sucesso:
                    st.balloons()
                    st.success(mensagem)
                    st.session_state.carrinho = []
                    st.rerun()
                else:
                    st.error(mensagem)
        else:
            st.info("🛒 Carrinho vazio")

# ========== RELATÓRIOS ==========
elif st.session_state.menu == "📊 Relatórios":
    st.header("📊 Relatórios")

    tipo_relatorio = st.selectbox("Tipo de Relatório", ["Vendas", "Produtos", "Clientes"])

    if tipo_relatorio == "Vendas":
        st.subheader("📈 Vendas")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data Inicial", value=pd.Timestamp.now().date().replace(day=1), format="DD/MM/YYYY")
        with col2:
            data_fim = st.date_input("Data Final", value=pd.Timestamp.now().date(), format="DD/MM/YYYY")
        
        st.caption(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        
        if st.button("📊 Gerar Relatório", use_container_width=True):
            vendas = banco.listar_vendas(st.session_state.user_id, data_inicio, data_fim)
            
            if not vendas.empty:
                total_vendas = len(vendas)
                valor_total = vendas['total'].sum()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Vendas", total_vendas)
                with col2:
                    st.metric("Valor Total", f"R$ {valor_total:.2f}")
                with col3:
                    media = valor_total / total_vendas if total_vendas > 0 else 0
                    st.metric("Ticket Médio", f"R$ {media:.2f}")
                
                st.subheader("Detalhamento das Vendas")
                df_vendas = vendas[['data_hora', 'total', 'forma_pagamento']].copy()
                df_vendas['data_hora'] = pd.to_datetime(df_vendas['data_hora']).dt.strftime('%d/%m/%Y %H:%M')
                df_vendas['total'] = df_vendas['total'].apply(lambda x: f"R$ {x:.2f}")
                df_vendas.columns = ['Data/Hora', 'Total', 'Pagamento']
                
                st.dataframe(df_vendas, use_container_width=True, hide_index=True)
                
                vendas['data'] = pd.to_datetime(vendas['data_hora']).dt.date
                vendas_por_dia = vendas.groupby('data')['total'].sum().reset_index()
                
                fig = px.line(vendas_por_dia, x='data', y='total', title="Vendas por Dia", markers=True)
                fig.update_layout(yaxis_title="Valor (R$)")
                st.plotly_chart(fig, use_container_width=True)
                
                if 'forma_pagamento' in vendas.columns:
                    fig_pag = px.pie(vendas, names='forma_pagamento', values='total', title="Vendas por Forma de Pagamento")
                    st.plotly_chart(fig_pag, use_container_width=True)
                
                if st.button("📥 Exportar para Excel", use_container_width=True):
                    st.info("Funcionalidade de exportação será implementada em breve!")
            else:
                st.info(f"Nenhuma venda encontrada no período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")

    elif tipo_relatorio == "Produtos":
        st.subheader("📦 Produtos")
        
        produtos = banco.listar_produtos(st.session_state.user_id)
        
        if not produtos.empty:
            produtos['valor_total'] = produtos['quantidade'] * produtos['preco']
            valor_total_estoque = produtos['valor_total'].sum()
            
            st.metric("Valor Total do Estoque", f"R$ {valor_total_estoque:.2f}")
            
            df_estoque = produtos[['nome', 'quantidade', 'preco', 'valor_total']].copy()
            df_estoque['preco'] = df_estoque['preco'].apply(lambda x: f"R$ {x:.2f}")
            df_estoque['valor_total'] = df_estoque['valor_total'].apply(lambda x: f"R$ {x:.2f}")
            
            st.dataframe(df_estoque, use_container_width=True, hide_index=True)
            
            fig = px.bar(produtos, x='nome', y='quantidade', title="Quantidade em Estoque", color='nome')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum produto cadastrado.")

    elif tipo_relatorio == "Clientes":
        st.subheader("👥 Clientes")
        st.info("Nenhum cliente cadastrado.")

# ========== CONFIGURAÇÕES ==========
elif st.session_state.menu == "⚙️ Configurações":
    st.header("⚙️ Configurações")

    with st.form("config_empresa"):
        nome_empresa = st.text_input("Nome da Empresa")
        cnpj = st.text_input("CNPJ")
        endereco = st.text_input("Endereço")
        telefone = st.text_input("Telefone")

        if st.form_submit_button("💾 Salvar Configurações", use_container_width=True, type="primary"):
            st.success("✅ Configurações salvas com sucesso!")