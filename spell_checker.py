# Arquivo: spell_checker.py (Atualizado com Múltiplas Sugestões e Contexto)

import re
import json
from ai_core import configure_ai

def find_errors(text):
    """Pede à IA para revisar um texto e sugerir múltiplas correções contextuais."""
    model = configure_ai()
    if model is None: return []
    
    # PROMPT REFEITO DO ZERO PARA SER UM PROFESSOR CONTEXTUAL E FLEXÍVEL
    prompt = f"""
    Aja como um professor de língua portuguesa experiente e compreensivo, revisando o rascunho de um poema de um aluno de 11 a 13 anos. O aluno pode usar gírias ou cometer erros de digitação comuns (ex: 'torar' querendo dizer 'torrar', 'ten' querendo dizer 'tem').

    Sua tarefa é ler o poema inteiro para entender o contexto e, em seguida, identificar "problemas" de ortografia e de uso de letras maiúsculas.

    **Texto completo do poema (para Contexto):**
    ---
    {text}
    ---

    **Regras de Correção (MUITO IMPORTANTE):**
    1.  **Foco:** Apenas ortografia (palavras escritas erradas) e uso de maiúsculas (início de verso e nomes próprios).
    2.  **Contexto é Rei:** As sugestões devem fazer sentido no contexto da frase.
    3.  **IGNORE A PONTUAÇÃO:** Não sugira correções de pontuação (vírgulas, pontos, etc.). Poemas têm liberdade poética.
    4.  **MÚLTIPLAS SUGESTÕES:** Para cada problema, ofereça uma lista de até 3 possíveis correções, com a mais provável primeiro.
    5.  **Comentários Simples:** Para cada problema, forneça um "motivo" (reason) muito curto e educativo, em uma linguagem que uma criança entenda.

    **Formato OBRIGATÓRIO da Resposta:**
    Retorne uma lista de objetos JSON. Cada objeto deve ter:
    - "original": A palavra com problema.
    - "suggestions": UMA LISTA de strings com as sugestões (ex: ["tem", "tenho"]).
    - "reason": Uma única string com o motivo.
    - "verse_number": O número da linha onde o erro está (começando em 1).
    
    Se não houver erros, retorne uma lista vazia [].
    """
    try:
        # Adiciona as linhas numeradas ao texto para a IA saber o verse_number
        lines = text.split('\n')
        numbered_text = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))
        
        # O prompt agora inclui o texto numerado para referência da IA
        final_prompt = prompt.replace(f"--- \n{text}\n ---", f"---\n{numbered_text}\n---")

        response = model.generate_content(final_prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "").replace("python", "")
        if not json_text or "[]" in json_text: return []
        return json.loads(json_text)
    except Exception:
        return []