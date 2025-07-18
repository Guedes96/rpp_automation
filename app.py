import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- Configuração da API e do app ---
st.set_page_config(page_title="Análise de Embalagens com IA", layout="centered")
st.title("📋 Relatório de Primeira Produção")

api_key = st.secrets["GOOGLE_API_KEY"]
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.stop()

# --- Prompts ---
prompt_nao_alimento = """
Você é um assistente de avaliação técnica de **primeira produção**, responsável por avaliar imagens de **embalagens e produtos** com base em critérios técnicos.

Analise visualmente as imagens e extraia, se disponíveis, as seguintes informações diretamente da rotulagem:
- Nome do fornecedor:
- CNPJ do fornecedor:
- Descrição do produto:
- Data de fabricação:
- Data de validade:
- Lote:
- Código EAN:
Se alguma informação não estiver visível ou legível, sinalize como **"Não identificado"**.
"""

prompt_avaliacao_embalagem = """
Você é um assistente de avaliação técnica de **embalagens**, responsável por analisar as imagens de **embalagens** com base em critérios técnicos.

A avaliação deve ser feita com foco nos seguintes critérios:
- Conformidade com exigências normativas da categoria;
- Presença e legibilidade de datação (fabricação e validade), lote e código EAN;
- Presença de informações obrigatórias (uso, composição, fabricante, precauções);
- Ausência de erros ortográficos e gramaticais;
- Condição física da embalagem (sem avarias, vazamentos ou deformações).

**Instruções de resposta**:
- A resposta deve ser em **texto corrido**, com linguagem **técnica e objetiva**;
- **Não use bullet points**;
- Caso encontre falhas, apresente como **ponto de atenção**, com recomendação técnica.

Exemplo de saída esperada:
A embalagem analisada apresenta datação, código EAN e lote de forma legível e de acordo com os requisitos da categoria. As informações obrigatórias estão presentes e redigidas corretamente. A rotulagem apresenta composição, modo de uso, precauções e dados do fabricante conforme exigido. A embalagem não apresenta sinais de avaria ou deformação. Recomenda-se sua aprovação para comercialização.
"""

# --- Upload de Imagens ---
imagens = st.file_uploader("📤 Envie até 5 imagens JPG ou JPEG para análise:", type=["jpg", "jpeg"], accept_multiple_files=True)

# --- Processamento ---
if st.button("🔎 Analisar Imagens"):
    if not imagens:
        st.warning("Envie pelo menos uma imagem.")
        st.stop()

    imagens_pil = []
    for img_file in imagens[:5]:  # Limita a 5
        try:
            img = Image.open(img_file).convert("RGB")
            imagens_pil.append(img)
        except Exception as e:
            st.error(f"Erro ao abrir imagem {img_file.name}: {e}")

    if imagens_pil:
        try:
            # --- Execução da análise 1: extração de dados ---
            st.info("Analisando rotulagem para extração de informações técnicas...")
            resposta_rotulagem = model.generate_content([prompt_nao_alimento] + imagens_pil)
            st.success("✅ Extração de Dados Concluída")
            st.text_area("📋 Resultado da Extração:", resposta_rotulagem.text, height=300)

            # --- Execução da análise 2: avaliação técnica ---
            st.info("Realizando avaliação técnica da embalagem...")
            resposta_avaliacao = model.generate_content([prompt_avaliacao_embalagem] + imagens_pil)
            st.success("✅ Avaliação Técnica Concluída")
            st.text_area("🧪 Resultado da Avaliação Técnica:", resposta_avaliacao.text, height=300)

        except Exception as e:
            st.error(f"Erro durante a análise com IA: {e}")
    else:
        st.warning("Nenhuma imagem válida foi processada.")