import streamlit as st
import requests

# --- Configuração da Página ---
st.set_page_config(
    page_title="Analisador de Produtos Amazon",
    page_icon="🕵️",
    layout="wide"
)

# --- Interface do Usuário ---
st.title("🕵️ Analisador de Inconsistências de Produtos Amazon")
st.markdown("""
Esta ferramenta utiliza agentes de IA para analisar uma página de produto da Amazon. 
Ela compara as informações textuais (descrição, características) com as imagens e vídeos para identificar possíveis inconsistências.
""")

# --- URL da API Backend ---
#BACKEND_URL = "https://globald.onrender.com/analyze"  # Use st.secrets para produção
BACKEND_URL = "http://127.0.0.1:8000/analyze"

# --- Formulário de Entrada ---
with st.form("product_form"):
    amazon_url = st.text_input(
        "🔗 Cole a URL do produto da Amazon aqui",
        placeholder="https://www.amazon.com.br/Seu-Produto-Aqui/dp/ASIN12345"
    )
    submitted = st.form_submit_button("Analisar Produto")

# --- Lógica de Processamento ---
if submitted and amazon_url:
    with st.spinner("Analisando... Este processo pode levar um minuto. 🤖"):
        try:
            payload = {"amazon_url": amazon_url.strip()}
            response = requests.post(BACKEND_URL, json=payload, timeout=120)
            response.raise_for_status()

            data = response.json()
            st.success("Análise concluída com sucesso!")
            st.markdown("---")

            # Exibe o relatório e os detalhes
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📋 Relatório Final")
                st.markdown(data.get('report', 'Nenhum relatório disponível.'))

            with col2:
                st.subheader("📦 Detalhes do Produto")
                st.info(f"**ASIN:** {data.get('asin', 'N/A')}\n\n**País:** {data.get('country', 'N/A')}")
                
                main_image_url = data.get("product_image_url")
                if main_image_url:
                    st.image(main_image_url, caption="Imagem Principal do Produto")
                    # Exibe outras imagens do produto, se houver
                    product_photos = data.get("product_photos", [])
                    if product_photos:
                        st.markdown("**Outras imagens do produto:**")
                        st.image(product_photos, width=200)
                else:
                    st.warning("Imagem principal não disponível.")
                    # Exibe outras imagens, se houver
                    product_photos = data.get("product_photos", [])
                    if product_photos:
                        st.markdown("**Outras imagens do produto:**")
                        st.image(product_photos, width=200)

        except requests.exceptions.HTTPError:
            error_details = response.json().get("detail", "Erro desconhecido.")
            st.error(f"Ocorreu um erro na API: {error_details}")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro de conexão com o backend: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")

elif submitted and not amazon_url:
    st.warning("Por favor, insira uma URL da Amazon para analisar.")
