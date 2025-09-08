# pages/2_Análise_em_Lote.py
import streamlit as st
import pandas as pd
import requests
# <<< NOVO: Importa a função específica para gerar o PDF em lote
from pdf_generator import create_batch_pdf_report

st.set_page_config(layout="wide", page_title="Análise em Lote")

st.title("🚀 Análise de Produtos em Lote")
st.markdown("Faça o upload de um arquivo (.txt, .csv ou .xlsx) com uma lista de URLs da Amazon para análise consolidada.")

# URLs DA API
BACKEND_BASE_URL = "https://globald.onrender.com"
BATCH_ANALYZE_URL = f"{BACKEND_BASE_URL}/batch_analyze"

# Inicializa o estado da sessão para esta página
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None
if 'uploaded_urls' not in st.session_state:
    st.session_state.uploaded_urls = None

uploaded_file = st.file_uploader(
    "Escolha um arquivo (uma URL por linha)",
    type=['txt', 'csv', 'xlsx']
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
            with st.expander("Visualizar URLs"):
                st.dataframe(urls)

            if st.button("Iniciar Análise em Lote", type="primary", use_container_width=True):
                with st.spinner(f"Analisando {len(urls)} produtos... Isso pode levar vários minutos. 🤖"):
                    try:
                        payload = {"amazon_urls": urls}
                        response = requests.post(BATCH_ANALYZE_URL, json=payload, timeout=900) # Timeout de 15 minutos
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
    st.subheader("Relatório Consolidado")
    
    pdf_file = create_batch_pdf_report(st.session_state.batch_results, st.session_state.uploaded_urls)
    st.download_button(
        label="📄 Baixar Relatório Consolidado em PDF",
        data=pdf_file,
        file_name="relatorio_consolidado_analise.pdf",
        mime="application/pdf"
    )

    with st.expander("Ver resultados individuais da análise (JSON)"):
        st.json(st.session_state.batch_results)