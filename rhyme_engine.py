# Arquivo: rhyme_engine.py

import re
import json
from ai_core import configure_ai

def get_ai_rhymes(word, theme):
    """Pede à IA uma lista de rimas com regras fonéticas e definições."""
    model = configure_ai()
    if model is None: return [{"palavra": "Erro", "definicao": "Erro na configuração da IA."}]

    prompt = f"""
    Aja como um linguista computacional especialista em fonética do português brasileiro.
    Sua única tarefa é gerar uma lista de palavras que rimam foneticamente com a palavra '{word}'.
    REGRAS DE RIMA (NÃO PODEM SER QUEBRADAS):
    1.  **SÍLABA TÔNICA:** A correspondência sonora da sílaba tônica é a regra MAIS IMPORTANTE.
    2.  **TIMBRE DA VOGAL:** A vogal da sílaba tônica da rima DEVE ter o mesmo som (aberto ou fechado) que a da palavra-alvo. 'verde' (som ê) NÃO rima com 'ferve' (som é).
    3.  **MONOSSÍLABOS:** Monossílabos tônicos (como 'lá') SÓ rimam com outros monossílabos tônicos ('cá') ou com a sílaba final de oxítonas ('maracujá').
    CONTEXTO (SECUNDÁRIO): Se as regras acima forem cumpridas, tente sugerir palavras do tema '{theme}'.
    Formato da Resposta: Retorne uma lista de objetos JSON com "palavra" e "definicao" (curta e simples para uma criança de 11 anos). Retorne no mínimo 8 sugestões.
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
