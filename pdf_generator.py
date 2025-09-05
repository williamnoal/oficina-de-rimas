# Arquivo: pdf_generator.py (VERSÃO FINAL - Correção do Erro AttributeError)

from fpdf import FPDF
from datetime import datetime
import json
import io
from ai_core import configure_ai
from icon_library import ICONS
from math import cos as _cos, sin as _sin # Importa funções matemáticas

# A lista de ícones que disponibilizamos para a IA escolher
AVAILABLE_ICONS = list(ICONS.keys())

def generate_pdf_style(theme, poem_text):
    """Gera um estilo de design para o PDF, incluindo um ícone temático."""
    model = configure_ai()
    if model is None: 
        return {
            "font": "Helvetica", "bg_color_hex": "#F0F8FF", 
            "text_color_hex": "#2F4F4F", "title_color_hex": "#FF6347",
            "border_style": "simples", "border_color_hex": "#4682B4",
            "icon_name": "estrela"
        }

    # REMOVI A OPÇÃO "ondas" DA LISTA DE ESCOLHAS DA IA PARA EVITAR O ERRO
    prompt = f"""
    Aja como um diretor de arte criando um layout para um poema infantil.
    O tema é "{theme}" e o poema é: "{poem_text}".

    Sua tarefa é retornar um objeto JSON com uma paleta de design.

    **Chaves obrigatórias no JSON:**
    - "font": Escolha uma entre "Courier", "Helvetica", "Times".
    - "bg_color_hex": Uma cor de fundo suave em hexadecimal.
    - "text_color_hex": Uma cor de texto que contraste bem com o fundo.
    - "title_color_hex": Uma cor de destaque para o título.
    - "border_style": Escolha UM dos seguintes estilos de borda: "simples", "dupla", "estrelas".
    - "border_color_hex": Uma cor para a borda, em hexadecimal.
    - "icon_name": Escolha UM dos seguintes nomes de ícone: {json.dumps(AVAILABLE_ICONS)}.

    Retorne APENAS o objeto JSON.
    """
    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "").replace("python", "")
        style = json.loads(json_text)
        if style.get("icon_name") not in AVAILABLE_ICONS:
            style["icon_name"] = "estrela"
        return style
    except Exception:
        return {
            "font": "Helvetica", "bg_color_hex": "#F0F8FF", 
            "text_color_hex": "#2F4F4F", "title_color_hex": "#FF6347",
            "border_style": "simples", "border_color_hex": "#4682B4",
            "icon_name": "estrela"
        }

class PoemPDF(FPDF):
    def __init__(self, style_guide, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = style_guide
        self.bg_r, self.bg_g, self.bg_b = tuple(int(self.style['bg_color_hex'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.text_r, self.text_g, self.text_b = tuple(int(self.style['text_color_hex'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.title_r, self.title_g, self.title_b = tuple(int(self.style['title_color_hex'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.border_r, self.border_g, self.border_b = tuple(int(self.style.get('border_color_hex', '#4682B4').lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    def header(self):
        self.set_fill_color(self.bg_r, self.bg_g, self.bg_b)
        self.rect(0, 0, self.w, self.h, 'F')
        self.draw_watermark_icon()
        self.draw_border()

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Gerado pela Oficina de Rimas - {datetime.now().strftime("%d/%m/%Y")}', 0, 0, 'C')
        
    def draw_watermark_icon(self):
        icon_name = self.style.get('icon_name', 'estrela')
        svg_text = ICONS.get(icon_name)
        if not svg_text:
            return
        try:
            x = (self.w - 100) / 2
            y = (self.h - 100) / 2
            with self.local_context(alpha=0.1):
                self.image(io.StringIO(svg_text), x=x, y=y, w=100, h=100)
        except Exception as e:
            print(f"Erro ao adicionar ícone da biblioteca interna: {e}")

    def draw_border(self):
        """Chama a função de desenho de borda apropriada com base no estilo."""
        style = self.style.get('border_style', 'simples')
        self.set_draw_color(self.border_r, self.border_g, self.border_b)
        
        if style == 'dupla':
            self.set_line_width(1)
            self.rect(5, 5, self.w - 10, self.h - 10)
            self.set_line_width(0.5)
            self.rect(7, 7, self.w - 14, self.h - 14)
        elif style == 'estrelas':
            self.draw_stars()
        else: # Padrão 'simples'
            self.set_line_width(1)
            self.rect(5, 5, self.w - 10, self.h - 10)

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
        outer_radius = size
        inner_radius = size / 2.5
        points = []
        for i in range(10):
            angle = i * 36 - 90
            radius = outer_radius if i % 2 == 0 else inner_radius
            points.append(
                (x + radius * _cos(angle * 3.14159 / 180), 
                 y + radius * _sin(angle * 3.14159 / 180))
            )
        self.polygon(points, 'F')

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
