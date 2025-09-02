# app.py
import streamlit as st
import requests

# --- Configuração da Página e Título ---
st.set_page_config(
    page_title="AI Product Genius para Amazon",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Product Genius para Amazon")
st.markdown("Uma ferramenta de IA para **Analisar Inconsistências** e **Otimizar Listings** de produtos.")

# --- URLs da API Backend (ajuste conforme necessário) ---
BACKEND_BASE_URL = "https://globald.onrender.com" 
# BACKEND_BASE_URL = "http://127.0.0.1:8000" # Para teste local
ANALYZE_URL = f"{BACKEND_BASE_URL}/analyze"
OPTIMIZE_URL = f"{BACKEND_BASE_URL}/optimize"

# --- Inicialização do Estado da Sessão ---
if 'product_info' not in st.session_state:
    st.session_state.product_info = None
if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = None
if 'optimization_report' not in st.session_state:
    st.session_state.optimization_report = None
if 'url_input' not in st.session_state:
    st.session_state.url_input = ""

# --- Formulário de Entrada na Barra Lateral ---
with st.sidebar:
    st.header("🔍 Inserir Produto")
    with st.form("product_form"):
        amazon_url = st.text_input(
            "Cole a URL do produto da Amazon",
            placeholder="https://www.amazon.com.br/dp/ASIN...",
            key="url_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Buscar", type="primary", use_container_width=True)
        with col2:
            cleared = st.form_submit_button("Limpar", use_container_width=True)

# --- Lógica de Processamento Principal ---

if cleared:
    st.session_state.product_info = None
    st.session_state.analysis_report = None
    st.session_state.optimization_report = None
    st.session_state.url_input = ""

if submitted and not amazon_url:
    st.warning("Por favor, insira uma URL da Amazon para começar.")

if submitted and amazon_url:
    st.session_state.product_info = None
    st.session_state.analysis_report = None
    st.session_state.optimization_report = None
    
    with st.spinner("Buscando informações básicas do produto... 🤖"):
        try:
            # Higieniza a URL para garantir que tenha o prefixo https://
            sanitized_url = amazon_url.strip()
            if not sanitized_url.startswith(('http://', 'https://')):
                sanitized_url = 'https://' + sanitized_url

            payload = {"amazon_url": sanitized_url}
            response = requests.post(ANALYZE_URL, json=payload, timeout=120)
            response.raise_for_status()
            
            st.session_state.product_info = response.json()
            st.session_state.analysis_report = st.session_state.product_info.get('report')

        except requests.exceptions.HTTPError as e:
            try:
                error_details = e.response.json().get("detail", "Erro desconhecido do servidor.")
            except requests.exceptions.JSONDecodeError:
                error_details = e.response.text
            st.error(f"Ocorreu um erro na API ao buscar o produto: {error_details}")
            st.session_state.product_info = None
        except requests.exceptions.RequestException as e:
            st.error(f"Erro de conexão com o backend: {e}")
            st.session_state.product_info = None

# --- Exibição dos Resultados ---
if st.session_state.product_info:
    info = st.session_state.product_info
    
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        if info.get("product_image_url"):
            st.image(info["product_image_url"], caption="Imagem Principal")
    with col2:
        # Esta linha agora funcionará corretamente com a API ajustada
        st.subheader(info.get("product_title", "Título não encontrado"))
        st.info(f"**ASIN:** `{info.get('asin', 'N/A')}` | **Mercado:** `{info.get('country', 'N/A')}`")

    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Análise de Inconsistências", "✨ Otimização de Listing (SEO)"])

    with tab1:
        st.header("Verificação de Consistência entre Texto e Imagens")
        st.markdown("Esta análise compara os textos do anúncio com suas imagens para encontrar discrepâncias factuais que possam confundir o cliente.")
        
        if st.session_state.analysis_report:
            with st.expander("Ver Relatório de Análise de Inconsistências", expanded=True):
                st.markdown(st.session_state.analysis_report)
        else:
            st.warning("Não foi possível gerar o relatório de análise.")

    with tab2:
        st.header("Otimização Completa do Listing para Máxima Performance")
        st.markdown("Gere um listing completo (título, pontos, descrição, etc.) otimizado para os algoritmos da Amazon (A9, Rufus) e para conversão de vendas.")
        
        if st.button("Gerar Listing Otimizado com IA", key="optimize_btn", use_container_width=True):
            with st.spinner("A IA está trabalhando para criar seu listing otimizado... Isso pode levar um minuto. 🧠"):
                try:
                    # Higieniza a URL aqui também
                    sanitized_url = st.session_state.url_input.strip()
                    if not sanitized_url.startswith(('http://', 'https://')):
                        sanitized_url = 'https://' + sanitized_url
                        
                    payload = {"amazon_url": sanitized_url}
                    response = requests.post(OPTIMIZE_URL, json=payload, timeout=180)
                    response.raise_for_status()
                    st.session_state.optimization_report = response.json().get('optimized_listing_report')
                except requests.exceptions.HTTPError as e:
                    try:
                        error_details = e.response.json().get("detail", "Erro desconhecido do servidor.")
                    except requests.exceptions.JSONDecodeError:
                        error_details = e.response.text
                    st.error(f"Ocorreu um erro na API durante a otimização: {error_details}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão com o backend: {e}")

        if st.session_state.optimization_report:
            st.markdown("### 📈 Seu Novo Listing Otimizado:")
            st.markdown(st.session_state.optimization_report)
