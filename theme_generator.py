# Arquivo: theme_generator.py (VERSÃO FINAL - Correção do Erro de Inspiração)

import re
import json
from ai_core import configure_ai

def generate_themes(interest_text):
    """Gera 10 temas personalizados com base em um texto de interesse."""
    model = configure_ai()
    if model is None: return ["Erro na configuração da IA."]
    
    prompt = f"""
    Aja como um gerador de ideias para um jovem escritor de 11 a 13 anos.
    A tarefa é criar 10 temas para um poema baseados nas palavras que o aluno escreveu.
    Palavras de Inspiração do Aluno:
    "{interest_text}"
    Sua Missão:
    Ofereça dez temas para um poema que se relacionem DIRETAMENTE com o que ele colocou. Os temas devem ser concretos, curtos e estimulantes.
    Formato OBRIGATÓRIO da Resposta:
    Retorne APENAS uma lista Python válida contendo 10 strings.
    """
    try:
        response = model.generate_content(prompt)
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if match:
            list_str = match.group(0)
            themes = eval(list_str)
            if isinstance(themes, list) and len(themes) > 0:
                return themes
        return ["O Assistente não conseguiu criar temas. Tente novamente."]
    except Exception as e:
        return [f"O Assistente teve um problema para criar temas. (Erro: {e})"]

def generate_progression_ideas(theme):
    """Gera uma lista FIXA de 10 ideias de progressão com lirismo básico."""
    model = configure_ai()
    if model is None: return ["Erro na configuração da IA."]
    
    prompt = f"""
    Aja como um professor de escrita criativa experiente, guiando um aluno de 11 a 13 anos que tem pouco contato com poesia.
    O tema do poema é '{theme}'.
    Sua tarefa é criar uma lista fixa de 10 ideias de como progredir na escrita.

    **Diretrizes de Estilo (MUITO IMPORTANTE):**
    1.  **Concretude com Lirismo Básico:** As ideias devem ser fáceis de entender e um pouco mais concretas.
    2.  **Foco nos Sentidos:** Incentive o aluno a pensar em cheiros, sons, cores e sensações relacionadas ao tema.
    3.  **Simplicidade:** Use um vocabulário direto e acessível, mas que desperte a imaginação.
    4.  **Formato de Pergunta ou Comando Criativo:** As ideias devem ser perguntas ou comandos criativos.
    5.  **NÃO ESCREVA VERSOS:** Apenas ideias.

    FORMATO DA RESPOSTA: Retorne APENAS uma lista Python com 10 strings.
    """
    # LÓGICA DE INTERPRETAÇÃO CORRIGIDA E MAIS ROBUSTA
    try:
        response = model.generate_content(prompt)
        # Procura por qualquer coisa que se pareça com uma lista Python na resposta
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if match:
            list_str = match.group(0)
            # A função eval() é mais flexível que json.loads() para listas no estilo Python
            suggestions = eval(list_str)
            if isinstance(suggestions, list) and len(suggestions) > 0:
                return suggestions

        # Se a extração falhar, retorna um erro claro
        return ["O Assistente não conseguiu gerar ideias. Tente novamente!"]
    except Exception as e:
        return [f"O Assistente teve um problema para gerar ideias. (Erro: {e})"]
