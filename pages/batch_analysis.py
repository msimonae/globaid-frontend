# pages/batch_analysis.py
import streamlit as st
import pandas as pd
import requests
from pdf_generator import create_batch_pdf_report # Importa a função de PDF em lote

st.set_page_config(layout="wide", page_title="Análise em Lote")

st.title("📦 Análise de Produtos em Lote")
st.markdown("Faça o upload de um arquivo (.txt, .csv ou .xlsx) com uma lista de URLs da Amazon para análise consolidada.")

# URLs DA API (ajuste conforme necessário)
BACKEND_BASE_URL = "https://globald.onrender.com" # Ou o URL do seu servidor backend
BATCH_ANALYZE_URL = f"{BACKEND_BASE_URL}/batch_analyze"

# Inicializa o estado da sessão para esta página
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None
if 'uploaded_urls' not in st.session_state:
    st.session_state.uploaded_urls = None

# <<< NOVO: Layout visual com ícone de clips e texto descritivo
st.markdown(
    """
    <style>
    .upload-box {
        border: 2px dashed #007bff;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        background-color: #f0f2f6;
    }
    .upload-icon {
        font-size: 50px;
        color: #007bff;
        margin-bottom: 10px;
    }
    .upload-text {
        font-size: 18px;
        font-weight: bold;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="upload-box">
        <div class="upload-icon">📎</div>
        <div class="upload-text">Arraste e solte seu arquivo aqui ou clique para fazer upload</div>
        <p style="font-size: 14px; color: #666;">(Formatos suportados: .txt, .csv, .xlsx)</p>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    " ", # Rótulo vazio para não duplicar o texto
    type=['txt', 'csv', 'xlsx'],
    key="batch_file_uploader",
    label_visibility="collapsed" # Esconde o rótulo padrão do Streamlit
)

if uploaded_file is not None:
    urls = []
    try:
        if uploaded_file.name.endswith('.txt'):
            urls = [line.decode('utf-8').strip() for line in uploaded_file.readlines()]
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
            urls = df.iloc[:, 0].dropna().tolist()
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, header=None)
            urls = df.iloc[:, 0].dropna().tolist()
        
        urls = [url for url in urls if isinstance(url, str) and url.strip().startswith('http')]
        st.session_state.uploaded_urls = urls

        st.success(f"{len(urls)} URLs válidas encontradas no arquivo.")
        if urls:
            with st.expander("Visualizar URLs carregadas"):
                st.dataframe(urls)

            if st.button("🚀 Iniciar Análise em Lote", type="primary", use_container_width=True):
                with st.spinner(f"Analisando {len(urls)} produtos... Isso pode levar vários minutos. 🤖"):
                    try:
                        payload = {"amazon_urls": urls}
                        # Aumente o timeout da requisição se estiver lidando com muitos itens
                        response = requests.post(BATCH_ANALYZE_URL, json=payload, timeout=900) 
                        response.raise_for_status()
                        
                        st.session_state.batch_results = response.json().get('results', [])
                        st.success("Análise em lote concluída!")

                    except requests.exceptions.HTTPError as e:
                        st.error(f"Erro na API durante a análise em lote: {e.response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Erro de conexão com o backend: {e}")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

if st.session_state.batch_results:
    st.divider()
    st.subheader("📊 Relatório Consolidado de Inconsistências")
    
    # Certifique-se de passar as URLs para o gerador de PDF
    pdf_file = create_batch_pdf_report(st.session_state.batch_results, st.session_state.uploaded_urls)
    st.download_button(
        label="📄 Baixar Relatório Consolidado em PDF",
        data=pdf_file,
        file_name="relatorio_consolidado_analise.pdf",
        mime="application/pdf"
    )

    with st.expander("🔍 Ver resultados individuais da análise (JSON)"):
        st.json(st.session_state.batch_results)