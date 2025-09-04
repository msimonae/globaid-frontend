# app.py
import streamlit as st
import requests
import io
from fpdf import FPDF
import os

# --- FUNÇÃO PARA GERAR O PDF (CORRIGIDA) ---
def create_pdf_report(info: dict):
    """Cria um relatório em PDF com título, texto e imagens do produto."""
    pdf = FPDF()
    pdf.add_page()

    # --- CORREÇÃO: Define o nome da fonte em uma variável para uso consistente ---
    font_name = 'Arial' # Começa com uma fonte padrão segura
    font_path = 'DejaVuSans.ttf'
    if os.path.exists(font_path):
        try:
            pdf.add_font('DejaVu', '', font_path, uni=True)
            font_name = 'DejaVu' # Se a fonte for adicionada com sucesso, usa ela
        except Exception as e:
            st.warning(f"Não foi possível carregar a fonte 'DejaVuSans.ttf': {e}. Usando fonte padrão.")
    else:
        st.warning("Arquivo de fonte 'DejaVuSans.ttf' não encontrado. Acentos no PDF podem não ser exibidos corretamente.")

    pdf.set_font(font_name, 'B', 16) # Usa a variável font_name

    # Título do Produto
    pdf.cell(0, 10, "Relatório de Análise do Produto", ln=True, align='C')
    pdf.set_font(font_name, '', 12)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    pdf.multi_cell(effective_page_width, 10, f"Título: {info.get('product_title', 'N/A')}")
    pdf.multi_cell(effective_page_width, 10, f"ASIN: {info.get('asin', 'N/A')}")
    pdf.ln(10)
    
    # Relatório de Inconsistências
    pdf.set_font(font_name, 'B', 14) # Usa a variável font_name
    pdf.multi_cell(effective_page_width, 10, "Relatório de Inconsistências Gerado por IA")
    pdf.set_font(font_name, '', 11) # Usa a variável font_name
    pdf.multi_cell(effective_page_width, 8, info.get('report', 'Nenhum relatório disponível.'))
    pdf.ln(10)

    # Imagens do Produto
    pdf.set_font(font_name, 'B', 14) # Usa a variável font_name
    pdf.multi_cell(effective_page_width, 10, "Imagens do Produto")
    
    image_urls = info.get('product_photos', [])
    if not image_urls:
        pdf.set_font(font_name, '', 11) # Usa a variável font_name
        pdf.multi_cell(effective_page_width, 10, "Nenhuma imagem adicional encontrada.")

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            pdf.image(io.BytesIO(response.content), w=150)
            pdf.ln(5)
        except Exception as e:
            pdf.set_text_color(255, 0, 0)
            pdf.set_font(font_name, '', 10) # Usa a variável font_name
            pdf.multi_cell(effective_page_width, 10, f"Erro ao carregar imagem {i+1}")
            pdf.set_text_color(0, 0, 0)
            print(f"Erro ao baixar imagem para PDF: {e}")

    return pdf.output(dest='S').encode('latin-1')


# --- CONFIGURAÇÃO DA PÁGINA E INTERFACE ---
st.set_page_config(
    page_title="AI Product Genius para Amazon",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Product Genius para Amazon")
st.markdown("Uma ferramenta de IA para **Analisar Inconsistências** e **Otimizar Listings** de produtos.")

# URLs DA API
BACKEND_BASE_URL = "https://globald.onrender.com"
# BACKEND_BASE_URL = "http://127.0.0.1:8000" # Para teste local
ANALYZE_URL = f"{BACKEND_BASE_URL}/analyze"
OPTIMIZE_URL = f"{BACKEND_BASE_URL}/optimize"

# ESTADO DA SESSÃO
if 'product_info' not in st.session_state: st.session_state.product_info = None
if 'analysis_report' not in st.session_state: st.session_state.analysis_report = None
if 'optimization_report' not in st.session_state: st.session_state.optimization_report = None
if 'url_input' not in st.session_state: st.session_state.url_input = ""

# --- FORMULÁRIO NA BARRA LATERAL ---
with st.sidebar:
    st.header("🔍 Inserir Produto")
    with st.form("product_form"):
        amazon_url = st.text_input("Cole a URL do produto da Amazon", placeholder="https://www.amazon.com.br/dp/ASIN...", key="url_input")
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Buscar", type="primary", use_container_width=True)
        with col2:
            cleared = st.form_submit_button("Limpar", use_container_width=True)

# LÓGICA PRINCIPAL
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

# EXIBIÇÃO DOS RESULTADOS
if st.session_state.product_info:
    info = st.session_state.product_info
    
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        if info.get("product_image_url"):
            st.image(info["product_image_url"], caption="Imagem Principal")
    with col2:
        st.subheader(info.get("product_title", "Título não encontrado"))
        st.info(f"**ASIN:** `{info.get('asin', 'N/A')}` | **Mercado:** `{info.get('country', 'N/A')}`")

    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Análise de Inconsistências", "✨ Otimização de Listing (SEO)"])

    with tab1:
        st.header("Verificação de Consistência entre Texto e Imagens")
        report_text = info.get('report', 'Não foi possível gerar o relatório de análise.')
        with st.expander("Ver Relatório de Análise", expanded=True):
            st.markdown(report_text)
        
        st.divider()
        st.subheader("Download do Relatório")
        
        # A geração do PDF agora é mais segura e não deve mais causar erro
        pdf_bytes = create_pdf_report(info)
        st.download_button(
            label="📄 Baixar Relatório em PDF",
            data=pdf_bytes,
            file_name=f"relatorio_analise_{info.get('asin', 'produto')}.pdf",
            mime="application/pdf"
        )
        
    with tab2:
        st.header("Otimização Completa do Listing para Máxima Performance")
        st.markdown("Gere um listing completo otimizado para os algoritmos da Amazon e para conversão de vendas.")
        
        if st.button("Gerar Listing Otimizado com IA", key="optimize_btn", use_container_width=True):
            with st.spinner("A IA está trabalhando para criar seu listing otimizado... Isso pode levar um minuto. 🧠"):
                try:
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
