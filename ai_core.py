# Arquivo: ai_core.py

import google.generativeai as genai
import streamlit as st

def configure_ai():
    """Configura e retorna o modelo de IA."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        return model
    except (KeyError, FileNotFoundError):
        st.error("Chave da API do Google AI não encontrada. Verifique o arquivo secrets.toml.")
        return None
