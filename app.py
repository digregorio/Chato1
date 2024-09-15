import streamlit as st
import os
from openai import OpenAI
from PyPDF2 import PdfReader
import tempfile

# Configuração da chave da API
API_KEY = os.getenv("API_KEY")

# Verifica se a chave da API está definida
if not API_KEY:
  st.error("Por favor, defina a variável de ambiente 'API_KEY' com sua chave da API da AIML.")
else:
  # Configuração do cliente OpenAI
  client = OpenAI(
      api_key=API_KEY,
      base_url="https://api.aimlapi.com",
  )

  st.title("Chat AI - Semelhante ao ChatGPT")
  st.sidebar.header("Configurações")

  # Inicialização das mensagens
  if 'messages' not in st.session_state:
      st.session_state['messages'] = []

  # Função para exibir mensagens
  def display_messages():
      for message in st.session_state['messages']:
          if message['role'] == 'user':
              st.markdown(f"**Você:** {message['content']}")
          elif message['role'] == 'assistant':
              st.markdown(f"**Assistente:** {message['content']}")

  # Exibir mensagens
  display_messages()

  # Caixa de entrada de texto
  user_input = st.text_input("Digite sua mensagem:", "")

  # Upload de arquivos
  uploaded_file = st.file_uploader("Faça upload de um arquivo", type=["txt", "pdf", "docx", "png", "jpg", "jpeg"])

  if st.button("Enviar"):
      if user_input or uploaded_file:
          if user_input:
              # Adiciona a mensagem do usuário ao histórico
              st.session_state['messages'].append({"role": "user", "content": user_input})

          if uploaded_file:
              # Processar o arquivo enviado
              if uploaded_file.type == "text/plain":
                  try:
                      file_text = uploaded_file.read().decode("utf-8")
                      st.session_state['messages'].append({"role": "user", "content": f"Arquivo de texto enviado: {uploaded_file.name}"})
                      st.session_state['messages'].append({"role": "user", "content": file_text})
                  except UnicodeDecodeError:
                      st.warning("Não foi possível decodificar o arquivo de texto. Certifique-se de que está em UTF-8.")
              elif uploaded_file.type == "application/pdf":
                  try:
                      with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                          tmp_file.write(uploaded_file.read())
                          tmp_file_path = tmp_file.name

                      reader = PdfReader(tmp_file_path)
                      pdf_text = ""
                      for page in reader.pages:
                          text = page.extract_text()
                          if text:
                              pdf_text += text + "\n"

                      st.session_state['messages'].append({"role": "user", "content": f"Arquivo PDF enviado: {uploaded_file.name}"})
                      st.session_state['messages'].append({"role": "user", "content": pdf_text if pdf_text else "Não foi possível extrair texto do PDF."})
                  except Exception as e:
                      st.warning(f"Erro ao processar o PDF: {e}")
              elif uploaded_file.type in ["image/png", "image/jpg", "image/jpeg"]:
                  image = uploaded_file.read()
                  st.session_state['messages'].append({"role": "user", "content": f"Imagem enviada: {uploaded_file.name}. Atualmente, o processamento de imagens não está implementado."})
                  st.image(image, caption=uploaded_file.name, use_column_width=True)
              else:
                  st.warning("Tipo de arquivo não suportado.")

          # Chama a API da AIML
          try:
              response = client.chat.completions.create(
                  model="o1-preview",
                  messages=st.session_state['messages'],
              )

              assistant_message = response.choices[0].message.content

              # Adiciona a resposta do assistente ao histórico
              st.session_state['messages'].append({"role": "assistant", "content": assistant_message})

              # Atualiza a interface
              display_messages()
          except Exception as e:
              st.error(f"Erro ao chamar a API: {e}")
