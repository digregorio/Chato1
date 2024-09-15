import streamlit as st
import os
from openai import OpenAI

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
      if user_input:
          # Adiciona a mensagem do usuário ao histórico
          st.session_state['messages'].append({"role": "user", "content": user_input})

          # Processar o arquivo enviado, se houver
          if uploaded_file is not None:
              file_content = uploaded_file.read()
              file_text = file_content.decode("utf-8") if uploaded_file.type in ["text/plain", "application/pdf"] else "Arquivo recebido."
              st.session_state['messages'].append({"role": "user", "content": f"Arquivo enviado: {uploaded_file.name}"})
              st.session_state['messages'].append({"role": "user", "content": file_text})

          # Chama a API da AIML
          response = client.chat.completions.create(
              model="o1-preview",
              messages=st.session_state['messages'],
          )

          assistant_message = response.choices[0].message.content

          # Adiciona a resposta do assistente ao histórico
          st.session_state['messages'].append({"role": "assistant", "content": assistant_message})

          # Atualiza a interface
          display_messages()