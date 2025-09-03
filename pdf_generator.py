# Arquivo: pdf_generator.py (VERSÃO FINAL - Com Decoração de PDF via IA)

from fpdf import FPDF
from datetime import datetime
import json
import random
from ai_core import configure_ai

def generate_pdf_style(theme, poem_text):
    """Gera um estilo de design para o PDF, incluindo um estilo de borda."""
    model = configure_ai()
    if model is None: 
        return {
            "font": "Helvetica", "bg_color_hex": "#F0F8FF", 
            "text_color_hex": "#2F4F4F", "title_color_hex": "#FF6347",
            "border_style": "simples", "border_color_hex": "#4682B4"
        }

    # A IA agora pode escolher entre os estilos de borda que sabemos desenhar
    prompt = f"""
    Aja como um diretor de arte criando um layout para um poema infantil.
    O tema é "{theme}" e o poema é: "{poem_text}".

    Sua tarefa é retornar um objeto JSON com uma paleta de design.

    **Chaves obrigatórias no JSON:**
    - "font": Escolha uma entre "Courier", "Helvetica", "Times".
    - "bg_color_hex": Uma cor de fundo suave em hexadecimal (ex: "#F0F8FF").
    - "text_color_hex": Uma cor de texto que contraste bem com o fundo, em hexadecimal.
    - "title_color_hex": Uma cor de destaque para o título, em hexadecimal.
    - "border_style": Escolha UM dos seguintes estilos de borda, o que mais combinar com o tema: "simples", "dupla", "ondas", "estrelas".
    - "border_color_hex": Uma cor para a borda, em hexadecimal, que combine com o resto da paleta.

    Retorne APENAS o objeto JSON.
    """
    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "").replace("python", "")
        return json.loads(json_text)
    except Exception:
        # Retorna um estilo padrão em caso de falha
        return {
            "font": "Helvetica", "bg_color_hex": "#F0F8FF", 
            "text_color_hex": "#2F4F4F", "title_color_hex": "#FF6347",
            "border_style": "simples", "border_color_hex": "#4682B4"
        }

class PoemPDF(FPDF):
    def __init__(self, style_guide, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = style_guide
        # Converte cores hex para RGB
        self.bg_r, self.bg_g, self.bg_b = tuple(int(self.style['bg_color_hex'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.text_r, self.text_g, self.text_b = tuple(int(self.style['text_color_hex'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.title_r, self.title_g, self.title_b = tuple(int(self.style['title_color_hex'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.border_r, self.border_g, self.border_b = tuple(int(self.style.get('border_color_hex', '#4682B4').lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    def header(self):
        # Fundo da página com a cor sugerida pela IA
        self.set_fill_color(self.bg_r, self.bg_g, self.bg_b)
        self.rect(0, 0, self.w, self.h, 'F')
        # Desenha a borda decorativa
        self.draw_border()

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Gerado pela Oficina de Rimas - {datetime.now().strftime("%d/%m/%Y")}', 0, 0, 'C')

    def draw_border(self):
        """Chama a função de desenho de borda apropriada com base no estilo."""
        style = self.style.get('border_style', 'simples')
        self.set_draw_color(self.border_r, self.border_g, self.border_b)
        
        if style == 'dupla':
            self.set_line_width(1)
            self.rect(5, 5, self.w - 10, self.h - 10)
            self.set_line_width(0.5)
            self.rect(7, 7, self.w - 14, self.h - 14)
        elif style == 'ondas':
            self.draw_waves()
        elif style == 'estrelas':
            self.draw_stars()
        else: # Padrão 'simples'
            self.set_line_width(1)
            self.rect(5, 5, self.w - 10, self.h - 10)

    def draw_waves(self):
        """Desenha uma borda de ondas simples."""
        self.set_line_width(0.5)
        margin = 10
        step = 5
        amplitude = 2
        # Ondas no topo e na base
        for x in range(margin, int(self.w - margin), step):
            self.curve(x, margin, x + step / 2, margin - amplitude, x + step, margin)
            self.curve(x, self.h - margin, x + step / 2, self.h - margin + amplitude, x + step, self.h - margin)
        # Ondas nas laterais
        for y in range(margin, int(self.h - margin), step):
            self.curve(margin, y, margin - amplitude, y + step/2, margin, y + step)
            self.curve(self.w - margin, y, self.w - margin + amplitude, y + step/2, self.w - margin, y + step)

    def draw_stars(self):
        """Desenha estrelas nos quatro cantos da página."""
        self.set_line_width(0.2)
        self.set_fill_color(self.border_r, self.border_g, self.border_b)
        self.draw_star(20, 20)
        self.draw_star(self.w - 20, 20)
        self.draw_star(20, self.h - 20)
        self.draw_star(self.w - 20, self.h - 20)

    def draw_star(self, x, y, size=10):
        """Helper para desenhar uma única estrela."""
        p = []
        for i in range(5):
            angle = i * 2 * 3.14159 / 5 - 3.14159 / 2
            radius = size if i % 2 == 0 else size / 2.5
            p.append((x + radius *_cos(angle), y + radius * _sin(angle)))
        self.polygon(p, 'F')


def create_poem_pdf(title, author, poem_text, style_guide):
    """Cria e retorna o PDF como bytes para download."""
    pdf = PoemPDF(style_guide)
    pdf.add_page()
    
    pdf.set_font(style_guide['font'], 'B', 24)
    pdf.set_text_color(pdf.title_r, pdf.title_g, pdf.title_b)
    pdf.multi_cell(0, 15, title, align='C')
    pdf.ln(20)
    
    pdf.set_font(style_guide['font'], '', 12)
    pdf.set_text_color(pdf.text_r, pdf.text_g, pdf.text_b)
    pdf.multi_cell(0, 10, poem_text)
    pdf.ln(10)
    
    pdf.set_font(style_guide['font'], 'I', 14)
    pdf.multi_cell(0, 10, f'- {author}', align='R')
    
    return bytes(pdf.output())

# Funções matemáticas necessárias para desenhar a estrela
from math import cos as _cos, sin as _sin