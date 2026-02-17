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

# ========== CSS PERSONALIZADO ==========
st.markdown("""
<style>
    /* ===== REMOVER TODOS OS ELEMENTOS DO STREAMLIT ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    header[data-testid="stHeader"] {display: none !important;}
    
    /* Reset de margens e paddings */
    .main > div {padding-top: 0 !important;}
    .block-container {padding-top: 0 !important; max-width: 100% !important;}
    
    /* ===== MENU ROXO SUPERIOR ===== */
    .menu-superior {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem 2rem;
        border-radius: 0 0 15px 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        width: 100%;
    }
    
    .usuario-info {
        background: rgba(255,255,255,0.15);
        color: white;
        padding: 0.4rem 1.5rem;
        border-radius: 40px;
        font-weight: 600;
        font-size: 1rem;
        border: 1px solid rgba(255,255,255,0.3);
        white-space: nowrap;
        backdrop-filter: blur(5px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .menu-botoes {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .botao-menu {
        background: rgba(255,255,255,0.15);
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        padding: 0.4rem 1.2rem;
        border-radius: 40px;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s ease;
        backdrop-filter: blur(5px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: none;
        font-family: inherit;
    }
    
    .botao-menu:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .botao-menu.ativo {
        background: white;
        color: #667eea;
        font-weight: 700;
    }
    
    .botao-menu.sair {
        background: rgba(220, 53, 69, 0.8);
    }
    
    .botao-menu.sair:hover {
        background: rgba(220, 53, 69, 1);
    }
    
    .botao-menu.atualizar {
        background: linear-gradient(135deg, #28a745, #20c997);
        font-weight: 700;
    }
    
    @media (max-width: 768px) {
        .menu-superior {
            flex-direction: column;
            align-items: stretch;
            padding: 1rem;
        }
        .menu-botoes {
            justify-content: center;
        }
        .botao-menu {
            text-align: center;
            flex: 1;
        }
    }
    
    /* Espaço para o conteúdo */
    .conteudo {
        padding: 1rem 0;
    }
</style>

<script>
    function navegar(pagina) {
        // Criar um formulário para enviar a requisição
        const form = document.createElement('form');
        form.method = 'POST';
        form.style.display = 'none';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'navegar';
        input.value = pagina;
        form.appendChild(input);
        
        document.body.appendChild(form);
        form.submit();
    }
    
    function logout() {
        const form = document.createElement('form');
        form.method = 'POST';
        form.style.display = 'none';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'logout';
        input.value = 'true';
        form.appendChild(input);
        
        document.body.appendChild(form);
        form.submit();
    }
    
    function atualizar() {
        const form = document.createElement('form');
        form.method = 'POST';
        form.style.display = 'none';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'atualizar';
        input.value = 'true';
        form.appendChild(input);
        
        document.body.appendChild(form);
        form.submit();
    }
</script>
""", unsafe_allow_html=True)

# ========== PROCESSAR REQUISIÇÕES POST ==========
if st.session_state.autenticado:
    if st.query_params:
        if "navegar" in st.query_params:
            pagina = st.query_params["navegar"]
            if pagina in ["Dashboard", "Estoque", "PDV", "Relatórios", "Configurações"]:
                st.session_state.pagina_atual = pagina
                st.rerun()
        
        if "logout" in st.query_params:
            st.session_state.autenticado = False
            st.session_state.username = ""
            st.session_state.user_id = None
            st.session_state.pagina_atual = "Login"
            st.session_state.carrinho = []
            st.rerun()
        
        if "atualizar" in st.query_params:
            st.rerun()

# ========== MENU SUPERIOR COM JAVASCRIPT ==========
if st.session_state.autenticado:
    usuario_logado = st.session_state.username
    pagina_atual = st.session_state.pagina_atual
    
    # Determinar classes ativas
    dashboard_class = "botao-menu ativo" if pagina_atual == "Dashboard" else "botao-menu"
    estoque_class = "botao-menu ativo" if pagina_atual == "Estoque" else "botao-menu"
    pdv_class = "botao-menu ativo" if pagina_atual == "PDV" else "botao-menu"
    relatorios_class = "botao-menu ativo" if pagina_atual == "Relatórios" else "botao-menu"
    config_class = "botao-menu ativo" if pagina_atual == "Configurações" else "botao-menu"
    
    # HTML do menu com chamadas JavaScript
    menu_html = f"""
    <div class="menu-superior">
        <span class="usuario-info">👤 {usuario_logado}</span>
        <div class="menu-botoes">
            <button onclick="navegar('Dashboard')" class="{dashboard_class}">🏠 Dashboard</button>
            <button onclick="navegar('Estoque')" class="{estoque_class}">📦 Estoque</button>
            <button onclick="navegar('PDV')" class="{pdv_class}">💵 PDV</button>
            <button onclick="navegar('Relatórios')" class="{relatorios_class}">📊 Relatórios</button>
            <button onclick="navegar('Configurações')" class="{config_class}">⚙️ Config</button>
            <button onclick="logout()" class="botao-menu sair">🚪 Sair</button>
            <button onclick="atualizar()" class="botao-menu atualizar">🔄</button>
        </div>
    </div>
    """
    
    st.markdown(menu_html, unsafe_allow_html=True)

# ========== CONTEÚDO DAS PÁGINAS ==========
st.markdown('<div class="conteudo">', unsafe_allow_html=True)

# ===== DASHBOARD =====
if st.session_state.pagina_atual == "Dashboard":
    st.header("📊 Dashboard")
    
    produtos = banco.listar_produtos(st.session_state.user_id)
    
    if not produtos.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Produtos", len(produtos))
        with col2:
            total_estoque = int(produtos['quantidade'].sum())
            st.metric("Itens em Estoque", total_estoque)
        with col3:
            valor_total = (produtos['quantidade'] * produtos['preco']).sum()
            st.metric("Valor em Estoque", f"R$ {valor_total:.2f}")
        
        if 'categoria' in produtos.columns:
            fig = px.pie(produtos, names='categoria', values='quantidade',
                        title="Distribuição do Estoque por Categoria",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 Nenhum produto cadastrado ainda. Acesse 'Estoque' para começar!")

# ===== ESTOQUE =====
elif st.session_state.pagina_atual == "Estoque":
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
            
            if st.form_submit_button("✅ Cadastrar Produto", use_container_width=True):
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
            df_exibicao['Preço (R$)'] = df_exibicao['Preço (R$)'].apply(lambda x: f"R$ {x:.2f}")
            
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
            
            if 'categoria' in produtos.columns:
                st.subheader("📊 Estoque por Categoria")
                estoque_categoria = produtos.groupby('categoria')['quantidade'].sum().reset_index()
                fig = px.bar(estoque_categoria, x='categoria', y='quantidade', 
                           title="Quantidade em Estoque por Categoria", 
                           color='categoria',
                           color_discrete_sequence=px.colors.qualitative.Set3)
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

# ===== PDV =====
elif st.session_state.pagina_atual == "PDV":
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
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 10px; text-align: center; margin: 15px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="margin:0;">TOTAL: R$ {total:.2f}</h3>
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

# ===== RELATÓRIOS =====
elif st.session_state.pagina_atual == "Relatórios":
    st.header("📊 Relatórios")

    tipo_relatorio = st.selectbox("Tipo de Relatório", ["Vendas", "Produtos"])

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
                
                fig = px.line(vendas_por_dia, x='data', y='total', title="Vendas por Dia", 
                             markers=True, color_discrete_sequence=['#667eea'])
                fig.update_layout(yaxis_title="Valor (R$)")
                st.plotly_chart(fig, use_container_width=True)
                
                if 'forma_pagamento' in vendas.columns:
                    fig_pag = px.pie(vendas, names='forma_pagamento', values='total', 
                                   title="Vendas por Forma de Pagamento",
                                   color_discrete_sequence=px.colors.qualitative.Set3)
                    st.plotly_chart(fig_pag, use_container_width=True)
            else:
                st.info("Nenhuma venda encontrada no período selecionado.")

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
            
            fig = px.bar(produtos, x='nome', y='quantidade', title="Quantidade em Estoque", 
                        color='nome', color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum produto cadastrado.")

# ===== CONFIGURAÇÕES =====
elif st.session_state.pagina_atual == "Configurações":
    st.header("⚙️ Configurações")

    with st.form("config_empresa"):
        st.subheader("Dados da Empresa")
        col1, col2 = st.columns(2)
        with col1:
            nome_empresa = st.text_input("Nome da Empresa")
            cnpj = st.text_input("CNPJ")
        with col2:
            endereco = st.text_input("Endereço")
            telefone = st.text_input("Telefone")

        if st.form_submit_button("💾 Salvar Configurações", use_container_width=True, type="primary"):
            st.success("✅ Configurações salvas com sucesso!")

st.markdown("</div>", unsafe_allow_html=True)