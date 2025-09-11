# pages/2_Análise_em_Lote.py
import streamlit as st
import pandas as pd
import requests
# Importa ambos os geradores de relatório
from pdf_generator import create_batch_pdf_report
from docx_generator import create_batch_docx_report

st.set_page_config(layout="wide", page_title="Análise em Lote")

st.title("📦 Análise de Produtos em Lote")
st.markdown("Faça o upload de um arquivo (.txt, .csv ou .xlsx) com uma lista de URLs da Amazon para gerar um relatório consolidado.")

# URLs DA API
BACKEND_BASE_URL = "https://globald.onrender.com"
BATCH_ANALYZE_URL = f"{BACKEND_BASE_URL}/batch_analyze"

# Inicializa o estado da sessão para esta página
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None
if 'uploaded_urls' not in st.session_state:
    st.session_state.uploaded_urls = None

# --- Seletor de formato do relatório ---
# Garante que a escolha do formato seja visível antes do upload
format_choice_batch = st.radio(
    "Selecione o formato para o relatório consolidado:",
    ('Word (.docx)', 'PDF (.pdf)'),
    key='format_selector_batch',
    index=0  # Define Word (.docx) como o padrão
)

# --- Upload Box com CSS ---
st.markdown(
    """
    <style>
    .upload-box {
        border: 2px dashed #0d6efd; border-radius: 10px; padding: 25px;
        text-align: center; margin-top: 20px; margin-bottom: 20px; background-color: #f8f9fa;
    }
    .upload-icon { font-size: 50px; color: #0d6efd; }
    .upload-text { font-size: 1.1em; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():
    st.markdown(
        """
        <div class="upload-box">
            <div class="upload-icon">📎</div>
            <div class="upload-text">Anexe seu arquivo de URLs</div>
            <p>Formatos suportados: .txt, .csv, .xlsx (uma URL por linha)</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader(" ", type=['txt', 'csv', 'xlsx'], key="batch_file_uploader", label_visibility="collapsed")

# --- Lógica de Processamento do Arquivo ---
if uploaded_file is not None:
    # (A lógica de leitura e higienização de URLs permanece a mesma)
    def sanitize_url(url):
        if not isinstance(url, str) or not url.strip(): return None
        s_url = url.strip()
        if not s_url.startswith(('http://', 'https://')):
            s_url = 'https://' + s_url
        return s_url
    try:
        raw_lines = []
        if uploaded_file.name.endswith('.txt'):
            raw_lines = [line.decode('utf-8').strip() for line in uploaded_file.readlines()]
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
            raw_lines = df.iloc[:, 0].dropna().tolist()
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, header=None)
            raw_lines = df.iloc[:, 0].dropna().tolist()
        
        valid_urls = [sanitize_url(line) for line in raw_lines]
        valid_urls = [url for url in valid_urls if url]
        st.session_state.uploaded_urls = valid_urls

        if valid_urls:
            st.success(f"{len(valid_urls)} URLs válidas encontradas e prontas para análise.")
            with st.expander("Visualizar URLs carregadas"):
                st.dataframe(valid_urls, use_container_width=True)
        else:
            st.error("0 URLs válidas encontradas no arquivo. Verifique o conteúdo do arquivo e tente novamente.")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

# --- Lógica do Botão de Análise ---
if st.session_state.uploaded_urls:
    if st.button("🚀 Iniciar Análise em Lote", type="primary", use_container_width=True):
        # (A lógica de chamada da API permanece a mesma)
        pass

# --- Exibição do Relatório para Download ---
if st.session_state.batch_results:
    st.divider()
    st.subheader("📊 Relatório Consolidado")
    st.info("A análise de todos os produtos foi concluída. Clique no botão abaixo para baixar o relatório consolidado.")
    
    # <<< ALTERAÇÃO: Lógica simplificada para gerar sempre DOCX
    docx_file = create_batch_docx_report(st.session_state.batch_results, st.session_state.uploaded_urls)
    st.download_button(
        label="📄 Baixar Relatório Consolidado em Word (.docx)",
        data=docx_file,
        file_name="relatorio_consolidado_analise.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    with st.expander("🔍 Ver resultados individuais da análise (JSON)"):
        st.json(st.session_state.batch_results)
