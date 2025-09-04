# app.py
import streamlit as st
import requests
import io
from fpdf import FPDF
import os
from io import BytesIO
import re # Importa a biblioteca de expressões regulares

# ... (Função create_pdf_report sem alterações) ...

# --- CONFIGURAÇÃO DA PÁGINA E INTERFACE ---
st.set_page_config(
    page_title="GlobalD IA Compliance para Amazon",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 GlobalD IA Compliance para Amazon")
st.markdown("Uma ferramenta de IA para **Analisar Inconsistências** e **Otimizar Listings** de produtos.")

# ... (URLs da API e Estado da Sessão sem alterações) ...

# --- LÓGICA PRINCIPAL e EXIBIÇÃO DOS RESULTADOS ---

# ... (Código do formulário e da lógica de busca sem alterações) ...

# EXIBIÇÃO DOS RESULTADOS
if st.session_state.product_info:
    info = st.session_state.product_info
    
    # ... (Exibição do cabeçalho do produto sem alterações) ...

    tab1, tab2 = st.tabs(["📊 Análise de Inconsistências", "✨ Otimização de Listing (SEO)"])

    with tab1:
        st.header("Verificação de Consistência entre Texto e Imagens")
        report_text = info.get('report', 'Não foi possível gerar o relatório de análise.')
        with st.expander("Ver Relatório de Análise", expanded=True):
            st.markdown(report_text)

        st.divider()
        st.subheader("Imagens Relevantes à Análise")
        
        # <<< CORREÇÃO: Lógica para extrair e mostrar apenas imagens citadas
        all_image_urls = info.get('product_photos', [])
        
        # Usa expressão regular para encontrar todas as menções a "Imagem X" no relatório
        # re.IGNORECASE faz com que não diferencie maiúsculas/minúsculas
        try:
            cited_numbers = re.findall(r'Imagem (\d+)', report_text, re.IGNORECASE)
            # Converte os números encontrados para inteiros e remove duplicatas
            cited_indices = {int(num) - 1 for num in cited_numbers}
            
            # Filtra a lista de URLs para pegar apenas as imagens nos índices citados
            relevant_images = [all_image_urls[i] for i in sorted(list(cited_indices)) if i < len(all_image_urls)]
        except Exception as e:
            print(f"Erro ao processar o relatório para extrair imagens: {e}")
            relevant_images = []


        if relevant_images:
            num_columns = 4
            cols = st.columns(num_columns)
            for i, url in enumerate(relevant_images):
                with cols[i % num_columns]:
                    # Corrigido use_column_width para use_container_width
                    st.image(url, caption=f"Imagem Relevante {i+1}", use_container_width=True)
        else:
            st.info("A análise da IA não apontou uma imagem específica para a inconsistência descrita, ou não houve inconsistência.")
        
        st.divider()
        st.subheader("Download do Relatório")
        
        # ... (Botão de download do PDF sem alterações) ...
        
    with tab2:
        # ... (Código da aba de otimização sem alterações) ...
        pass
