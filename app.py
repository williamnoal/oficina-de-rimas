# Arquivo: app.py

import streamlit as st
import re
from theme_generator import generate_themes, generate_progression_ideas
from rhyme_engine import get_ai_rhymes
from spell_checker import find_errors
from pdf_generator import create_poem_pdf, generate_pdf_style
from collections import defaultdict

st.set_page_config(layout="wide", page_title="Oficina de Rimas")

# --- ESTILOS MODERNOS E ADAPTATIVOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    body { font-family: 'Roboto', sans-serif; }
    .stApp { background-color: transparent; }
    .stButton>button { border-radius: 20px; }
    .card {
        background-color: var(--background-color, #ffffff);
        border-radius: 10px; padding: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    h1, h2, h3 { color: var(--text-color, #31333F); }
    [data-testid="stTooltipContent"] { font-size: 1.1em !important; }
    .rhyme-list { font-size: 1.1em !important; columns: 2; -webkit-columns: 2; -moz-columns: 2; }
    .correction-list { font-size: 1.1em; }
    .correction-verse { border-bottom: 1px solid var(--text-color, #D3D3D3); margin-bottom: 15px; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO E FUNÇÕES DE CALLBACK ---
if 'app_stage' not in st.session_state:
    st.session_state.app_stage = 'getting_interest'
    st.session_state.interest_text = ""
    st.session_state.generated_themes = []
    st.session_state.chosen_theme = ""
    st.session_state.poem_text = ""
    st.session_state.rhymes = None
    st.session_state.rhyme_word = ""
    st.session_state.spell_errors = []
    st.session_state.theme_suggestions = []
    st.session_state.pdf_data = None
    st.session_state.pdf_filename = ""

def get_poem_stats(text):
    verses = [line for line in text.split('\n') if line.strip()]
    stanzas = [stanza for stanza in text.split('\n\n') if stanza.strip()]
    return len(verses), len(stanzas)

def apply_correction(original, suggestion):
    """Substitui uma palavra errada pela sugestão escolhida."""
    def replace_word(match):
        word = match.group(0)
        if word.isupper():
            return suggestion.upper()
        elif word.istitle():
            return suggestion.title()
        else:
            return suggestion.lower()
    
    st.session_state.poem_text = re.sub(r'\b' + re.escape(original) + r'\b', replace_word, st.session_state.poem_text, count=1, flags=re.IGNORECASE)
    st.session_state.spell_errors = find_errors(st.session_state.poem_text)

# --- ROTEAMENTO DA APLICAÇÃO ---

# ETAPA 1: Coleta de Interesses
if st.session_state.app_stage == 'getting_interest':
    st.title("Vamos Criar um Poema Incrível! 🚀")
    with st.container(border=True):
        st.header("Agora você vai escrever um poema. Escreva no espaço abaixo algo que você goste muito e eu vou apresentar ideias para você.")
        interest = st.text_area("Escreva aqui sobre o que você gosta...", key="interest_input", height=150)
        if st.button("Gerar Ideias de Temas →", type="primary"):
            if interest:
                st.session_state.interest_text = interest
                with st.spinner("O Assistente está criando temas com a sua cara..."):
                    st.session_state.generated_themes = generate_themes(st.session_state.interest_text)
                st.session_state.app_stage = 'choosing_theme'
                st.rerun()
            else:
                st.warning("Escreva algo que você gosta para a gente começar!")

# ETAPA 2: Escolha do Tema
elif st.session_state.app_stage == 'choosing_theme':
    st.title("Ótimas Ideias! ✨")
    st.subheader("Pensei em alguns temas que podem ter a ver com você. Escolha um para começar:")
    if "Erro:" in st.session_state.generated_themes[0]:
        st.error(st.session_state.generated_themes[0])
    else:
        for theme in st.session_state.generated_themes:
            if st.button(theme, use_container_width=True):
                st.session_state.chosen_theme = theme
                with st.spinner("Preparando sua oficina de escrita..."):
                    st.session_state.theme_suggestions = generate_progression_ideas(theme)
                st.session_state.app_stage = 'writing_poem'
                st.rerun()

# ETAPA 3: Oficina de Escrita
elif st.session_state.app_stage == 'writing_poem':
    st.title(f"✍️ Oficina de Escrita: {st.session_state.chosen_theme}")
    
    col_editor, col_sidebar = st.columns([2, 1])

    with col_editor:
        with st.container(border=True):
            st.subheader("Escreva seu poema aqui")
            st.session_state.poem_text = st.text_area("Seu Poema", value=st.session_state.poem_text, height=450, key="poem_editor", label_visibility="collapsed")
        
        if st.button("Revisar Ortografia ✍️", use_container_width=True):
            with st.spinner("O Assistente está revisando seu poema..."):
                st.session_state.spell_errors = find_errors(st.session_state.poem_text)
                if not st.session_state.spell_errors:
                    st.toast("Nenhum problema encontrado!", icon="🎉")
        
        if st.session_state.spell_errors:
            with st.container(border=True):
                st.subheader("🕵️‍♀️ Dicas do Assistente Criativo")
                st.info("Encontrei algumas sugestões para melhorar seu poema!")
                errors_by_verse = defaultdict(list)
                for error in st.session_state.spell_errors:
                    errors_by_verse[error['verse_number']].append(error)

                st.markdown("<div class='correction-list'>", unsafe_allow_html=True)
                for verse_num, errors in sorted(errors_by_verse.items()):
                    st.markdown(f"<div class='correction-verse'>", unsafe_allow_html=True)
                    st.markdown(f"**No Verso {verse_num}:**")
                    for error in errors:
                        st.write(f"Problema: **`{error['original']}`**")
                        cols = st.columns(len(error['suggestions']))
                        for i, suggestion in enumerate(error['suggestions']):
                            cols[i].button(
                                suggestion, 
                                key=f"corr_{verse_num}_{error['original']}_{suggestion}",
                                on_click=apply_correction,
                                args=(error['original'], suggestion)
                            )
                        st.caption(f"Motivo: {error['reason']}")
                    st.markdown(f"</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    with col_sidebar:
        with st.container(border=True):
            st.subheader("🔎 Caça-Rimas")
            rhyme_word_input = st.text_input("Digite uma palavra para rimar:", key="rhyme_input")
            if st.button("Buscar Rimas"):
                if rhyme_word_input:
                    with st.spinner(f"Buscando rimas para '{rhyme_word_input}'..."):
                        st.session_state.rhymes = get_ai_rhymes(rhyme_word_input, st.session_state.chosen_theme)
                        st.session_state.rhyme_word = rhyme_word_input
                else:
                    st.toast("Digite uma palavra!", icon="❗️")
            
            if st.session_state.rhymes:
                st.markdown(f"**Rimas para '{st.session_state.rhyme_word}':**")
                if "Erro" in st.session_state.rhymes[0]['palavra']:
                    st.warning(st.session_state.rhymes[0]['definicao'])
                else:
                    rhyme_html = "<div class='rhyme-list'>"
                    for rhyme in st.session_state.rhymes:
                        rhyme_html += f"<div><b>{rhyme['palavra']}:</b> <i>{rhyme['definicao']}</i></div>"
                    rhyme_html += "</div>"
                    st.markdown(rhyme_html, unsafe_allow_html=True)

        with st.container(border=True):
            st.subheader("💡 Inspiração Criativa")
            st.caption("Uma lista de ideias para te ajudar a guiar seu poema.")
            if st.session_state.theme_suggestions:
                if "Erro:" in st.session_state.theme_suggestions[0]:
                    st.warning(st.session_state.theme_suggestions[0])
                else:
                    for i, idea in enumerate(st.session_state.theme_suggestions):
                        st.markdown(f"**{i+1}.** {idea}")
        
        with st.container(border=True):
            st.subheader("📊 Estatísticas do Poema")
            verses, stanzas = get_poem_stats(st.session_state.poem_text)
            c1, c2 = st.columns(2)
            c1.metric("Versos", verses)
            c2.metric("Estrofes", stanzas)

    st.markdown("---")
    if st.button("Concluir Poema 🏁", type="primary", use_container_width=True):
        if st.session_state.poem_text.strip():
            st.session_state.app_stage = 'finalizing_poem'
            st.session_state.pdf_data = None
            st.rerun()
        else:
            st.error("Escreva seu poema antes de concluir!")

# ETAPA 4: Finalização e Geração de PDF
elif st.session_state.app_stage == 'finalizing_poem':
    st.title("Quase lá! Vamos dar um Título ao seu Poema 🏆")
    
    with st.form("pdf_form"):
        poem_title = st.text_input("Qual será o título do seu poema?")
        author_name = st.text_input("E qual o nome do(a) poeta? (Seu nome!)")
        st.warning("Você tem certeza que terminou seu poema e fez todas as correções?")
        submitted = st.form_submit_button("Confirmar e Gerar PDF Mágico ✨")
        if submitted:
            if not poem_title or not author_name:
                st.error("Por favor, preencha o título e o seu nome!")
            else:
                with st.spinner("O Assistente está criando um design mágico para o seu poema..."):
                    style = generate_pdf_style(st.session_state.chosen_theme, st.session_state.poem_text)
                    if style:
                        st.session_state.pdf_data = create_poem_pdf(poem_title, author_name, st.session_state.poem_text, style)
                        st.session_state.pdf_filename = f"{re.sub('[^A-Za-z0-9]+', '_', poem_title)}.pdf"
                        st.balloons()
                        st.success("Seu poema está pronto! O botão de download apareceu abaixo.")
                    else:
                        st.error("O Assistente não conseguiu criar o design. Tente novamente.")

    if st.session_state.pdf_data:
        st.download_button(
            label="Baixar meu Poema em PDF 📄",
            data=st.session_state.pdf_data,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf"
        )

    if st.button("Voltar para a Edição"):
        st.session_state.app_stage = 'writing_poem'
        st.session_state.pdf_data = None
        st.rerun()
