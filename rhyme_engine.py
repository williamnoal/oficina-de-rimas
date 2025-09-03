# Arquivo: rhyme_engine.py (VERSÃO FINAL - Precisão Fonética Máxima)

import re
import json
from ai_core import configure_ai

def get_ai_rhymes(word, theme):
    """Pede à IA uma lista de rimas com regras fonéticas e definições."""
    model = configure_ai()
    if model is None: return [{"palavra": "Erro", "definicao": "Erro na configuração da IA."}]

    # PROMPT REFEITO DO ZERO PARA MÁXIMA PRECISÃO
    prompt = f"""
    Aja como um linguista computacional e poeta, especialista absoluto em fonética do português brasileiro.

    Sua tarefa é gerar uma lista de palavras que rimam com a palavra '{word}', seguindo duas regras inquebráveis.

    **REGRA 1: PRECISÃO FONÉTICA TOTAL (A MAIS IMPORTANTE)**
    A semelhança fonética a partir da sílaba tônica é obrigatória. Isso inclui:
    - **Sons da Sílaba Tônica:** A vogal tônica e todos os sons que a seguem devem corresponder perfeitamente.
    - **Timbre da Vogal (Aberta vs. Fechada):** A vogal tônica da rima DEVE ter o mesmo som (timbre aberto ou fechado) que a da palavra-alvo. 'esc**ó**la' (som aberto) rima com 'b**ó**la', mas NÃO rima com 'b**ô**la' (de bolo). 'av**ó**' (aberto) NÃO rima com 'av**ô**' (fechado).
    - **Sons Nasais:** Corresponda sons nasais perfeitamente. 'coraç**ão**' rima com 'emoç**ão**'.

    **REGRA 2: RELEVÂNCIA PARA O PÚBLICO**
    - **Idade:** As palavras devem ser adequadas para o vocabulário de uma criança de 11 a 13 anos.
    - **Tema:** Se possível, e apenas se a REGRA 1 for 100% cumprida, dê preferência a palavras que combinem com o tema do poema: '{theme}'.
    - **Proibição:** Palavras arcaicas, muito complexas ou que não fazem parte do universo infantil devem ser evitadas.

    **Formato da Resposta:**
    Retorne uma lista de objetos JSON. Cada objeto deve ter duas chaves:
    1. "palavra": A palavra que rima.
    2. "definicao": Uma definição muito curta e simples da palavra, em uma linguagem que uma criança entenda.
    Retorne no mínimo 8 sugestões, se possível.
    """
    try:
        generation_config = {"temperature": 0.8}
        response = model.generate_content(prompt, generation_config=generation_config)
        json_text = response.text.strip().replace("```json", "").replace("```", "").replace("python", "")
        rhymes = json.loads(json_text)
        rhymes = [r for r in rhymes if r['palavra'].lower() != word.lower()]
        return rhymes if rhymes else [{"palavra": "Puxa!", "definicao": f"O Assistente não encontrou rimas para '{word}'."}]
    except Exception:
        return [{"palavra": "Erro", "definicao": f"O Assistente teve um problema para buscar rimas."}]