# pdf_generator.py
import streamlit as st
import requests
import io
from fpdf import FPDF
import os
from io import BytesIO

def _draw_report_content(pdf, info: dict, product_url: str):
    """
    Função auxiliar que desenha o conteúdo do relatório de UM produto 
    na página atual do objeto PDF fornecido.
    """
    # Define as variáveis de estilo
    font_name = pdf.font_family
    bold_style = 'B' if font_name == 'Arial' else ''
    effective_page_width = pdf.w - 2 * pdf.l_margin

    # Bloco de Informações do Produto
    pdf.set_font(font_name, bold_style, 14)
    pdf.multi_cell(effective_page_width, 8, info.get('product_title', 'Título não encontrado'), align='C')
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
    
    # Bloco de Análise de Inconsistências
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
    
    # Bloco de Imagens do Produto
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

def create_single_pdf_report(info: dict, product_url: str):
    """Cria e retorna um PDF para um único relatório."""
    pdf = FPDF()
    pdf.add_page()
    # Adiciona a fonte (a função de desenho espera que ela já esteja adicionada)
    font_path = 'DejaVuSans.ttf'
    if os.path.exists(font_path):
        try:
            pdf.add_font('DejaVu', '', font_path, uni=True)
        except Exception: pass
    
    # Adiciona o branding
    logo_path = 'globald_logo_512x512_original.jpg'
    if os.path.exists(logo_path):
        logo_width = 40
        logo_x_pos = (pdf.w - logo_width) / 2
        pdf.image(logo_path, x=logo_x_pos, w=logo_width)
        pdf.ln(5)
    pdf.set_font('Arial', '', 10) # Usa uma fonte segura para o tagline
    pdf.cell(0, 10, 'AI Compliance Relatório by www.GlobalD.ai', ln=True, align='C')
    pdf.ln(5)

    # Desenha o conteúdo do relatório
    _draw_report_content(pdf, info, product_url)
    
    return BytesIO(pdf.output())

def create_batch_pdf_report(batch_results: list, urls: list):
    """Cria um PDF consolidado a partir de uma lista de resultados."""
    pdf = FPDF()
    
    # Adiciona a fonte uma vez
    font_path = 'DejaVuSans.ttf'
    if os.path.exists(font_path):
        try:
            pdf.add_font('DejaVu', '', font_path, uni=True)
        except Exception: pass

    for i, result_info in enumerate(batch_results):
        pdf.add_page()
        
        # Adiciona o branding em cada página
        logo_path = 'globald_logo_512x512_original.jpg'
        if os.path.exists(logo_path):
            logo_width = 40
            logo_x_pos = (pdf.w - logo_width) / 2
            pdf.image(logo_path, x=logo_x_pos, w=logo_width)
            pdf.ln(5)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, 'AI Compliance Relatório by www.GlobalD.ai', ln=True, align='C')
        pdf.ln(5)

        # Pega a URL correspondente para este resultado
        product_url = urls[i] if i < len(urls) else "URL não encontrada"
        
        # Desenha o conteúdo do relatório para este produto
        _draw_report_content(pdf, result_info, product_url)

    return BytesIO(pdf.output())