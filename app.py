# app.py
import streamlit as st
import requests
import io
from fpdf import FPDF
import os
from io import BytesIO
import re
from pdf_generator import create_single_pdf_report # <<< Importa a função refatorada

# --- FUNÇÃO PARA GERAR O PDF ---
# (A função create_pdf_report não precisa de alterações)
def create_pdf_report(info: dict, product_url: str):
    """Cria um relatório em PDF com layout aprimorado e formatação de negrito."""
    pdf = FPDF()
    pdf.add_page()
    font_name = 'Arial'
    font_path = 'DejaVuSans.ttf'
    if os.path.exists(font_path):
        try:
            pdf.add_font('DejaVu', '', font_path, uni=True)
            font_name = 'DejaVu'
        except Exception as e:
            st.warning(f"Não foi possível carregar a fonte 'DejaVuSans.ttf': {e}. Usando fonte padrão.")
    else:
        st.warning("Arquivo de fonte 'DejaVuSans.ttf' não encontrado. Acentos no PDF podem não ser exibidos corretamente.")
    bold_style = 'B' if font_name == 'Arial' else ''
    effective_page_width = pdf.w - 2 * pdf.l_margin
    logo_path = 'globald_logo_512x512_original.jpg'
    if os.path.exists(logo_path):
        logo_width = 40
        logo_x_pos = (pdf.w - logo_width) / 2
        pdf.image(logo_path, x=logo_x_pos, w=logo_width)
        pdf.ln(5)
    else:
        st.warning(f"Arquivo do logo '{logo_path}' não encontrado. O PDF será gerado sem o logo.")
    pdf.set_font(font_name, '', 10)
    pdf.cell(0, 10, 'AI Compliance Relatório by www.GlobalD.ai', ln=True, align='C')
    pdf.ln(5)
    pdf.set_font(font_name, bold_style, 14)
    pdf.multi_cell(effective_page_width, 8, info.get('product_title', 'N/A'), align='C')
    pdf.ln(3)
    pdf.set_font(font_name, bold_style, 12)
    pdf.cell(0, 8, f"ASIN: {info.get('asin', 'N/A')}", ln=True, align='L')
    pdf.set_font(font_name, bold_style, 12)
    pdf.cell(0, 8, "Link do Produto:", ln=True, align='L')
    pdf.set_font(font_name, 'U', 11)
    pdf.set_text_color(0, 0, 255)
    pdf.multi_cell(effective_page_width, 6, txt=product_url, link=product_url, align='L')
    pdf.set_font(font_name, '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)
    pdf.set_font(font_name, bold_style, 14)
    pdf.multi_cell(effective_page_width, 10, "Relatório de Inconsistências e Melhorias", align='C', ln=True)
    pdf.set_font(font_name, '', 11)
    report_text = info.get('report', 'Nenhum relatório disponível.')
    for line in report_text.split('\n'):
        parts = line.split('**')
        for i, part in enumerate(parts):
            if not part: continue
            if i % 2 == 1:
                pdf.set_font(font_name, bold_style, 11)
                pdf.write(5, part)
                pdf.set_font(font_name, '', 11)
            else:
                pdf.write(5, part)
        pdf.ln()
    pdf.ln(10)
    pdf.set_font(font_name, bold_style, 14)
    pdf.multi_cell(effective_page_width, 10, "Imagens do Produto", align='C', ln=True)
    image_urls = info.get('product_photos', [])
    if not image_urls:
        pdf.set_font(font_name, '', 11)
        pdf.multi_cell(effective_page_width, 10, "Nenhuma imagem adicional encontrada.")
    image_width = 120
    image_x_pos = (pdf.w - image_width) / 2
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            pdf.image(io.BytesIO(response.content), x=image_x_pos, w=image_width)
            pdf.ln(5)
        except Exception as e:
            pdf.set_text_color(255, 0, 0)
            pdf.set_font(font_name, '', 10)
            pdf.multi_cell(effective_page_width, 10, f"Erro ao carregar imagem {i+1}", align='C')
            pdf.set_text_color(0, 0, 0)
            print(f"Erro ao baixar imagem para PDF: {e}")
    return BytesIO(pdf.output())

# --- CONFIGURAÇÃO DA PÁGINA E INTERFACE ---
st.set_page_config(
    page_title="GlobalD IA Compliance para Amazon",
    page_icon="🚀",
    layout="wide"
)
st.title("🚀 GlobalD IA Compliance para Amazon")
st.markdown("Uma ferramenta de IA para **Analisar Inconsistências** e **Otimizar Listings** de produtos.")

# URLs DA API
BACKEND_BASE_URL = "https://globald.onrender.com"
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
        
        # <<< CORREÇÃO: Garante que st.markdown seja usado para renderizar o negrito
        with st.expander("Ver Relatório de Análise", expanded=True):
            st.markdown(report_text, unsafe_allow_html=True)

        st.divider()
        st.subheader("Imagens do Produto Analisadas")
        
        all_image_urls = info.get('product_photos', [])
        
        if all_image_urls:
            num_columns = 4
            cols = st.columns(num_columns)
            for i, url in enumerate(all_image_urls):
                with cols[i % num_columns]:
                    st.image(url, caption=f"Imagem {i+1}", use_container_width=True)
        else:
            st.info("Nenhuma imagem de produto foi retornada pela API para exibição.")
        
        st.divider()
        st.subheader("Download do Relatório")

        pdf_file = create_single_pdf_report(info, st.session_state.url_input)
        #pdf_file = create_pdf_report(info, st.session_state.url_input)
        st.download_button(
            label="📄 Baixar Relatório em PDF",
            data=pdf_file,
            file_name=f"relatorio_analise_{info.get('asin', 'produto')}.pdf",
            mime="application/pdf"
        )
        
    with tab2:
        st.header("Otimização Completa do Listing para Máxima Performance")
        st.markdown("Gere um listing completo (título, pontos, descrição, etc.) otimizado para os algoritmos da Amazon e para conversão de vendas, com base em reviews de clientes e dados de concorrentes.")
        
        if st.button("Gerar Listing Otimizado com IA", key="optimize_btn", use_container_width=True):
            with st.spinner("A IA está buscando reviews, analisando concorrentes e criando seu listing otimizado... Isso pode levar um minuto. 🧠"):
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
            st.markdown("---")
            st.subheader("📈 Seu Novo Listing Otimizado:")
            st.markdown(st.session_state.optimization_report)










