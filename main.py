import sys
import traceback
import os

def android_crash_handler(exctype, value, tb):
    err = ''.join(traceback.format_exception(exctype, value, tb))
    try:
        from jnius import autoclass
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        if context:
            ext_dir = context.getExternalFilesDir(None).getAbsolutePath()
            with open(os.path.join(ext_dir, 'kivy_crash_log.txt'), 'w') as f:
                f.write(err)
    except:
        pass
    try:
        with open('/storage/emulated/0/Download/kivy_crash_log.txt', 'w') as f:
            f.write(err)
    except:
        pass
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = android_crash_handler

import json
from datetime import datetime
from collections import defaultdict

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import platform
from kivy.factory import Factory
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.graphics import Line

# Gráficos (Matplotlib é opcional e NÃO está disponível no Android)
MATPLOTLIB_AVAILABLE = False
if platform != 'android':
    try:
        import matplotlib.pyplot as plt
        MATPLOTLIB_AVAILABLE = True
    except ImportError:
        MATPLOTLIB_AVAILABLE = False

if platform != 'android':
    from kivy.core.window import Window
    Window.size = (450, 800)

class AutoCompleteTextInput(TextInput):
    suggestions = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown = DropDown()
        self.bind(text=self.on_text)
        self.multiline = False
        
    def on_text(self, instance, value):
        if value:
            matches = [s for s in self.suggestions if value.lower() in s.lower()]
            if matches:
                self.dropdown.clear_widgets()
                for match in matches:
                    btn = Button(text=match, size_hint_y=None, height=44)
                    btn.bind(on_release=lambda b, text=match: self.select_match(text))
                    self.dropdown.add_widget(btn)
                
                # Abre o dropdown de forma segura no próximo frame
                Clock.schedule_once(lambda dt: self._open_dropdown(), 0.05)
            else:
                self.dropdown.dismiss()
        else:
            self.dropdown.dismiss()

    def _open_dropdown(self):
        # Só abre se o foco ainda estiver no campo e não houver pai
        if self.focus and not self.dropdown.parent:
            try:
                self.dropdown.open(self)
            except:
                pass

    def select_match(self, text):
        self.text = text
        self.dropdown.dismiss()

def parse_moeda(valor_str):
    if not valor_str: return 0.0
    try:
        return float(valor_str.replace('.', '').replace(',', '.'))
    except ValueError:
        return 0.0

def format_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

KV = '''
<Label>:
    color: (0.1, 0.1, 0.2, 1)
    font_size: '14sp'
    text_size: self.size
    shorten: True
    shorten_from: 'right'
    halign: 'center'
    valign: 'middle'

<TextInput>:
    background_normal: ''
    background_color: (0.85, 0.78, 0.69, 1)
    font_size: '18sp'
    foreground_color: (0.1, 0.14, 0.49, 1)
    hint_text_color: (0.1, 0.14, 0.49, 0.6)
    cursor_color: (0.1, 0.14, 0.49, 1)
    padding: [15, 15]
    canvas.after:
        Color:
            rgba: (0.8, 0.8, 0.8, 1)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, 8)
            width: 1

<Button>:
    background_normal: ''
    background_color: (0.1, 0.14, 0.49, 1)
    color: (1, 1, 1, 1)
    bold: True
    font_size: '16sp'
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]

<Spinner>:
    background_normal: ''
    background_color: (0.1, 0.14, 0.49, 1)
    color: (1, 1, 1, 1)
    dropdown_cls: 'DropDown'

<TabbedPanel>:
    background_color: (0, 0, 0, 0)
    border: [0, 0, 0, 0]

<TabbedPanelItem>:
    background_normal: ''
    background_down: ''
    background_color: (0.1, 0.14, 0.49, 1) if self.state == 'down' else (0.1, 0.14, 0.49, 0.6)
    color: (1, 1, 1, 1)
    font_size: '13sp'
    bold: True

<RootLayout>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: (0.96, 0.97, 0.98, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        size_hint_y: None
        height: 80
        padding: [20, 10]
        spacing: 15
        canvas.before:
            Color:
                rgba: (0.1, 0.14, 0.49, 1)
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: (1, 1, 1, 0.1)
            Rectangle:
                pos: self.pos
                size: (self.width, 2)
        
        Image:
            source: 'icon.png'
            size_hint: (None, None)
            size: (60, 60)
            pos_hint: {'center_y': 0.5}
            allow_stretch: True
            keep_ratio: True
        
        Label:
            text: 'GESTOR MARCENARIA'
            bold: True
            font_size: '22sp'
            color: (1, 1, 1, 1)
            halign: 'left'
            valign: 'middle'
            size_hint_x: 1
            text_size: self.size
            
    MainTabs:
        id: main_tabs

<MainTabs>:
    do_default_tab: False
    default_tab: tab_marc
    
    TabbedPanelItem:
        id: tab_marc
        text: 'Marcenaria'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: 15
                spacing: 12
                size_hint_y: None
                height: self.minimum_height
                
                Label:
                    text: 'Despesas de Marcenaria (Estoque)'
                    size_hint_y: None
                    height: 30
                    bold: True
                    
                AutoCompleteTextInput:
                    id: marc_estoque_desc
                    hint_text: 'Descrição (Ex: MDF, Fita)'
                    suggestions: app.sugestoes_marcenaria
                    size_hint_y: None
                    height: 55
                    
                BoxLayout:
                    size_hint_y: None
                    height: 55
                    spacing: 8
                        
                    TextInput:
                        id: marc_estoque_valor
                        hint_text: 'Valor'
                        size_hint_x: 0.6
                        multiline: False
                        
                    Button:
                        text: 'ADD ESTOQUE'
                        size_hint_x: 0.4
                        on_release: app.add_estoque()

                Widget:
                    size_hint_y: None
                    height: 2
                    canvas:
                        Color:
                            rgba: (0.1, 0.1, 0.2, 0.2)
                        Rectangle:
                            pos: self.pos
                            size: self.size

                Label:
                    text: 'Novo Trabalho / Projeto'
                    size_hint_y: None
                    height: 30
                    bold: True
                    
                AutoCompleteTextInput:
                    id: marc_nome
                    hint_text: 'Nome do Projeto / Cliente'
                    suggestions: app.sugestoes_marcenaria
                    size_hint_y: None
                    height: 55
                    
                BoxLayout:
                    size_hint_y: None
                    height: 55
                    spacing: 8
                    TextInput:
                        id: marc_custo
                        hint_text: 'Custo Mat.'
                        multiline: False
                    TextInput:
                        id: marc_venda
                        hint_text: 'Valor Venda'
                        multiline: False
                    
                Button:
                    text: 'SALVAR E CALCULAR'
                    size_hint_y: None
                    height: 50
                    on_release: app.add_marcenaria()
                    
                GridLayout:
                    id: marc_grid
                    cols: 4
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 5
                    padding: 5
                    
                    Label:
                        text: 'Item'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Custo/Venda'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Lucro'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Func. 20%'
                        bold: True
                        height: 35
                        size_hint_y: None

    TabbedPanelItem:
        text: 'Calculadora'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: 15
                spacing: 12
                size_hint_y: None
                height: self.minimum_height
                
                Label:
                    text: 'Calculadora de Precificação (Persikall)'
                    size_hint_y: None
                    height: 30
                    bold: True
                    
                AutoCompleteTextInput:
                    id: calc_nome
                    hint_text: 'Nome do Projeto / Cliente'
                    suggestions: app.sugestoes_marcenaria
                    size_hint_y: None
                    height: 55
                    
                BoxLayout:
                    size_hint_y: None
                    height: 55
                    spacing: 8
                    TextInput:
                        id: calc_custo
                        hint_text: 'Custo Mat.'
                        multiline: False
                    TextInput:
                        id: calc_dias
                        hint_text: 'Dias Trab.'
                        multiline: False
                    
                Button:
                    text: 'CALCULAR E SALVAR'
                    size_hint_y: None
                    height: 50
                    on_release: app.add_calculadora()
                    
                GridLayout:
                    id: calc_grid
                    cols: 5
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 5
                    padding: 5
                    
                    Label:
                        text: 'Projeto'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Custo'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Lucro'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Venda Final'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Func. 20%'
                        bold: True
                        height: 35
                        size_hint_y: None

    TabbedPanelItem:
        text: 'Lucas'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: 15
                spacing: 12
                size_hint_y: None
                height: self.minimum_height
                
                Label:
                    text: 'Resumo de Comissões - Lucas'
                    size_hint_y: None
                    height: 40
                    bold: True
                    font_size: '18sp'
                    
                Label:
                    id: lucas_total
                    text: 'Total: R$ 0,00'
                    size_hint_y: None
                    height: 70
                    bold: True
                    font_size: '18sp'
                    color: (0.1, 0.5, 0.2, 1)
                    halign: 'center'
                    valign: 'middle'
                    text_size: self.size
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12,]
                
                GridLayout:
                    id: lucas_grid
                    cols: 3
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 10
                    padding: 5
                    
                    Label:
                        text: 'Projeto'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Valor'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Status'
                        bold: True
                        height: 35
                        size_hint_y: None

    TabbedPanelItem:
        text: 'Casa'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: 15
                spacing: 12
                size_hint_y: None
                height: self.minimum_height
                
                Label:
                    text: 'Despesas Residenciais'
                    bold: True
                    height: 35
                    size_hint_y: None

                Spinner:
                    id: casa_tipo
                    text: 'Variável'
                    values: ['Fixa', 'Variável']
                    size_hint_y: None
                    height: 55
                    
                AutoCompleteTextInput:
                    id: casa_categoria
                    hint_text: 'Descrição da Despesa'
                    suggestions: app.sugestoes_casa
                    size_hint_y: None
                    height: 55
                    
                BoxLayout:
                    size_hint_y: None
                    height: 55
                    spacing: 8
                    TextInput:
                        id: casa_valor
                        hint_text: 'Valor'
                        size_hint_x: 0.6
                        multiline: False
                    Button:
                        text: 'SALVAR'
                        size_hint_x: 0.4
                        on_release: app.add_casa()
                    
                GridLayout:
                    id: casa_grid
                    cols: 4
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 5
                    
                    Label:
                        text: 'Data'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Tipo'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Categ.'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Valor'
                        bold: True
                        height: 35
                        size_hint_y: None
                            
    TabbedPanelItem:
        text: 'Boletos'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: 15
                spacing: 12
                size_hint_y: None
                height: self.minimum_height
                
                Label:
                    text: 'Vencimentos'
                    bold: True
                    height: 35
                    size_hint_y: None
                
                TextInput:
                    id: bol_desc
                    hint_text: 'Descrição do Boleto'
                    size_hint_y: None
                    height: 55

                BoxLayout:
                    size_hint_y: None
                    height: 55
                    spacing: 8
                    TextInput:
                        id: bol_valor
                        hint_text: 'Valor'
                    TextInput: 
                        id: bol_data
                        hint_text: 'DD/MM/AAAA'
                        on_text: app.validate_date_input(self)

                Button:
                    text: 'ADICIONAR LEMBRETE'
                    size_hint_y: None
                    height: 50
                    on_release: app.add_boleto()
                    
                GridLayout:
                    id: bol_grid
                    cols: 3
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 5
                    
                    Label:
                        text: 'Descrição'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Valor'
                        bold: True
                        height: 35
                        size_hint_y: None
                    Label:
                        text: 'Vencimento'
                        bold: True
                        height: 35
                        size_hint_y: None

    TabbedPanelItem:
        text: 'Resumo'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: 15
                spacing: 12
                size_hint_y: None
                height: self.minimum_height
                
                Label:
                    text: 'Balanço Mensal'
                    bold: True
                    font_size: '18sp'
                    height: 40
                    size_hint_y: None
                    
                GridLayout:
                    id: resumo_grid
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 15

    TabbedPanelItem:
        text: 'Gráficos'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: 15
                spacing: 12
                size_hint_y: None
                height: self.minimum_height
                
                BoxLayout:
                    size_hint_y: None
                    height: 50
                    spacing: 8
                    Button:
                        text: 'Mês'
                        on_release: app.gerar_graficos('mes_atual')
                    Button:
                        text: 'Ev.'
                        on_release: app.gerar_graficos('evolucao')
                    Button:
                        text: 'Comp.'
                        on_release: app.gerar_graficos('comparativo')

                BoxLayout:
                    size_hint_y: None
                    height: 400
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12,]
                    Image:
                        id: graf_imagem
                        source: ''
                        allow_stretch: True
                        keep_ratio: True
       keep_ratio: True
'''

class MainTabs(TabbedPanel):
    pass

class RootLayout(BoxLayout):
    pass

Factory.register('AutoCompleteTextInput', cls=AutoCompleteTextInput)
Factory.register('MainTabs', cls=MainTabs)
Factory.register('RootLayout', cls=RootLayout)

class GerenciadorApp(App):
    sugestoes_marcenaria = ListProperty(['MDF', 'Parafusos', 'Fita de Borda', 'Cola', 'Corrediça', 'Puxador', 'Dobradiça'])
    sugestoes_casa = ListProperty(['Mercado', 'Combustível', 'Restaurante', 'Luz', 'Água', 'Internet', 'Consórcio', 'Cartão'])
    
    def build(self):
        self.dados = {
            "marcenaria": [],
            "calculadora": [],
            "casa": [],
            "boletos": [],
            "sugestoes_marcenaria": self.sugestoes_marcenaria,
            "sugestoes_casa": self.sugestoes_casa
        }
        self.load_dados()
        Builder.load_string(KV)
        self.root_widget = RootLayout()
        self.main_tabs = self.root_widget.ids.main_tabs
        Clock.schedule_once(self.populate_grids, 0.5)
        return self.root_widget
        
    @property
    def dados_file(self):
        return os.path.join(self.user_data_dir, 'dados_gerais.json')

    def load_dados(self):
        if os.path.exists(self.dados_file):
            try:
                with open(self.dados_file, 'r', encoding='utf-8') as f:
                    salvo = json.load(f)
                    self.dados.update(salvo)
                    self.sugestoes_marcenaria = self.dados.get("sugestoes_marcenaria", self.sugestoes_marcenaria)
                    self.sugestoes_casa = self.dados.get("sugestoes_casa", self.sugestoes_casa)
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")

    def save_dados(self):
        self.dados['sugestoes_marcenaria'] = list(set(self.sugestoes_marcenaria))
        self.dados['sugestoes_casa'] = list(set(self.sugestoes_casa))
        try:
            with open(self.dados_file, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, ensure_ascii=False, indent=2)
            Clock.schedule_once(lambda dt: self.gerar_graficos('mes_atual'), 0.5)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

    def populate_grids(self, dt):
        for m in self.dados['marcenaria']:
            self.add_row_marcenaria(m)
        for cl in self.dados.get('calculadora', []):
            self.add_row_calculadora(cl)
        for c in self.dados['casa']:
            self.add_row_casa(c)
        self.refresh_boletos()
        self.refresh_lucas()
        self.refresh_resumo()

    def add_estoque(self):
        root_ids = self.main_tabs.ids
        desc = root_ids.marc_estoque_desc.text.strip()
        valor = parse_moeda(root_ids.marc_estoque_valor.text)
        if not desc or valor == 0: return
        data = datetime.now().strftime("%d/%m/%Y")
        item = {"data": data, "nome": f"[E] {desc}", "custo": valor, "venda": 0.0, "lucro": -valor, "func": 0.0}
        self.dados['marcenaria'].append(item)
        if desc not in self.sugestoes_marcenaria: self.sugestoes_marcenaria.append(desc)
        self.save_dados()
        self.add_row_marcenaria(item)
        self.refresh_resumo()
        root_ids.marc_estoque_desc.text = ""; root_ids.marc_estoque_valor.text = ""

    def add_marcenaria(self):
        root_ids = self.main_tabs.ids
        nome = root_ids.marc_nome.text.strip()
        custo = parse_moeda(root_ids.marc_custo.text)
        venda = parse_moeda(root_ids.marc_venda.text)
        if not nome or venda == 0: return
        data = datetime.now().strftime("%d/%m/%Y")
        lucro = venda - custo; func = lucro * 0.20
        item = {"data": data, "nome": nome, "custo": custo, "venda": venda, "lucro": lucro, "func": func}
        self.dados['marcenaria'].append(item)
        if nome not in self.sugestoes_marcenaria: self.sugestoes_marcenaria.append(nome)
        self.save_dados()
        self.add_row_marcenaria(item)
        self.refresh_lucas(); self.refresh_resumo()
        root_ids.marc_nome.text = ""; root_ids.marc_custo.text = ""; root_ids.marc_venda.text = ""
        
    def add_row_marcenaria(self, item):
        grid = self.main_tabs.ids.marc_grid
        grid.add_widget(Label(text=item['nome'], size_hint_y=None, height=55))
        if item.get('venda', 0.0) == 0.0:
            grid.add_widget(Label(text=f"C: {format_moeda(item['custo'])}", size_hint_y=None, height=55))
        else:
            grid.add_widget(Label(text=f"{format_moeda(item['custo'])}/{format_moeda(item['venda'])}", size_hint_y=None, height=55, font_size='12sp'))
        grid.add_widget(Label(text=format_moeda(item['lucro']), size_hint_y=None, height=55))
        grid.add_widget(Label(text=format_moeda(item.get('func', 0.0)), color=(0, 0.6, 0.2, 1), bold=True, size_hint_y=None, height=55))

    def add_calculadora(self):
        root_ids = self.main_tabs.ids
        nome = root_ids.calc_nome.text.strip()
        custo = parse_moeda(root_ids.calc_custo.text)
        try:
            dias_text = root_ids.calc_dias.text.replace(',', '.')
            dias = float(dias_text)
        except ValueError:
            dias = 0.0
            
        if not nome or dias == 0.0: return
        data = datetime.now().strftime("%d/%m/%Y")
        
        custo_insumos = custo * 1.15
        custo_diarias = dias * 595.0
        custo_total = custo_insumos + custo_diarias
        venda = custo_total * 1.25
        lucro = venda - custo_total
        func = lucro * 0.20
        
        item = {"data": data, "nome": nome, "custo": custo_total, "venda": venda, "lucro": lucro, "func": func}
        self.dados.setdefault('calculadora', []).append(item)
        if nome not in self.sugestoes_marcenaria: self.sugestoes_marcenaria.append(nome)
        self.save_dados()
        self.add_row_calculadora(item)
        self.refresh_lucas()
        
        root_ids.calc_nome.text = ""
        root_ids.calc_custo.text = ""
        root_ids.calc_dias.text = ""

    def add_row_calculadora(self, item):
        grid = self.main_tabs.ids.calc_grid
        grid.add_widget(Label(text=item['nome'], size_hint_y=None, height=55))
        grid.add_widget(Label(text=format_moeda(item['custo']), size_hint_y=None, height=55, font_size='12sp'))
        grid.add_widget(Label(text=format_moeda(item['lucro']), size_hint_y=None, height=55))
        grid.add_widget(Label(text=format_moeda(item['venda']), size_hint_y=None, height=55, font_size='12sp', bold=True, color=(0.1, 0.4, 0.8, 1)))
        grid.add_widget(Label(text=format_moeda(item.get('func', 0.0)), color=(0, 0.6, 0.2, 1), bold=True, size_hint_y=None, height=55))

    def refresh_lucas(self):
        grid = self.main_tabs.ids.lucas_grid
        children = grid.children[:]
        for c in children[:-3]: grid.remove_widget(c)
        total = 0.0
        total_pago = 0.0
        items_lucas = self.dados['marcenaria'] + self.dados.get('calculadora', [])
        for item in items_lucas:
            if item.get('venda', 0.0) > 0.0:
                val = item.get('func', 0.0)
                if val > 0:
                    is_pago = item.get('lucas_pago', False)
                    grid.add_widget(Label(text=item['nome'], size_hint_y=None, height=35))
                    grid.add_widget(Label(text=format_moeda(val), color=(0, 0.6, 0.2, 1), bold=True, size_hint_y=None, height=35))
                    
                    btn_status = Button(
                        text='✔ PAGO' if is_pago else 'A PAGAR',
                        background_color=(0.1, 0.6, 0.1, 1) if is_pago else (0.8, 0.2, 0.2, 1),
                        size_hint_y=None, height=35,
                        font_size='13sp'
                    )
                    btn_status.bind(on_release=lambda instance, i=item: self.toggle_lucas_status(i))
                    grid.add_widget(btn_status)
                    
                    total += val
                    if is_pago:
                        total_pago += val
        self.main_tabs.ids.lucas_total.text = f"Total: {format_moeda(total)}\nPago: {format_moeda(total_pago)}  |  A Pagar: {format_moeda(total - total_pago)}"

    def toggle_lucas_status(self, item):
        item['lucas_pago'] = not item.get('lucas_pago', False)
        self.save_dados()
        self.refresh_lucas()

    def add_casa(self):
        root_ids = self.main_tabs.ids
        tipo = root_ids.casa_tipo.text; categoria = root_ids.casa_categoria.text.strip()
        valor = parse_moeda(root_ids.casa_valor.text)
        if not categoria or valor == 0: return
        data = datetime.now().strftime("%d/%m/%Y")
        item = {"data": data, "tipo": tipo, "categoria": categoria, "valor": valor}
        self.dados['casa'].append(item)
        if categoria not in self.sugestoes_casa: self.sugestoes_casa.append(categoria)
        self.save_dados(); self.add_row_casa(item); self.refresh_resumo()
        root_ids.casa_categoria.text = ""; root_ids.casa_valor.text = ""

    def add_row_casa(self, item):
        grid = self.main_tabs.ids.casa_grid
        grid.add_widget(Label(text=item['data'], size_hint_y=None, height=30))
        c_color = (0.8, 0.2, 0.2, 1) if item['tipo'] == 'Fixa' else (0.8, 0.6, 0.2, 1)
        grid.add_widget(Label(text=item['tipo'], color=c_color, size_hint_y=None, height=30))
        grid.add_widget(Label(text=item['categoria'], size_hint_y=None, height=30))
        grid.add_widget(Label(text=format_moeda(item['valor']), size_hint_y=None, height=30))

    def add_boleto(self):
        root_ids = self.main_tabs.ids
        desc = root_ids.bol_desc.text.strip(); valor = parse_moeda(root_ids.bol_valor.text)
        data_venc = root_ids.bol_data.text.strip()
        if not desc or not data_venc: return
        
        # Validação extra de data para evitar quebras no resumo
        try:
            datetime.strptime(data_venc, "%d/%m/%Y")
        except ValueError:
            return # Não adiciona se a data for inválida
            
        item = {"desc": desc, "valor": valor, "vencimento": data_venc}
        self.dados['boletos'].append(item); self.save_dados()
        root_ids.bol_desc.text = ""; root_ids.bol_valor.text = ""; root_ids.bol_data.text = ""
        self.refresh_boletos(); self.refresh_resumo()

    def refresh_boletos(self):
        grid = self.main_tabs.ids.bol_grid
        children = grid.children[:]
        for c in children[:-3]: grid.remove_widget(c)
        hoje = datetime.now()
        for item in self.dados['boletos']:
            grid.add_widget(Label(text=item['desc'], size_hint_y=None, height=35))
            grid.add_widget(Label(text=format_moeda(item['valor']), size_hint_y=None, height=35))
            txt = item['vencimento']; cor = (0.1, 0.1, 0.2, 1)
            try:
                dv = datetime.strptime(item['vencimento'], "%d/%m/%Y")
                diff = (dv - hoje).days
                if diff < 0: cor = (0.8, 0, 0, 1); txt += " (V!)"
                elif diff <= 3: cor = (0.8, 0.4, 0, 1); txt += f" ({diff}d)"
            except: pass
            grid.add_widget(Label(text=txt, color=cor, bold=True, size_hint_y=None, height=35))

    def validate_date_input(self, instance):
        txt = instance.text
        if len(txt) == 10:
            try:
                datetime.strptime(txt, "%d/%m/%Y")
                instance.background_color = (0.9, 1, 0.9, 1)
            except: instance.background_color = (1, 0.9, 0.9, 1)
        else: instance.background_color = (1, 1, 1, 1)

    def refresh_resumo(self):
        grid = self.main_tabs.ids.resumo_grid
        grid.clear_widgets()
        resumo = defaultdict(lambda: {"venda": 0.0, "custo": 0.0, "lucro": 0.0, "lucas": 0.0, "casa": 0.0, "boletos": 0.0})
        for m in self.dados['marcenaria']:
            mes = m['data'][3:]; resumo[mes]['venda'] += m.get('venda', 0.0)
            resumo[mes]['custo'] += m.get('custo', 0.0); resumo[mes]['lucro'] += m.get('lucro', 0.0)
            resumo[mes]['lucas'] += m.get('func', 0.0)
        for c in self.dados['casa']: resumo[c['data'][3:]]['casa'] += c['valor']
        for b in self.dados['boletos']:
            try: resumo[b['vencimento'][3:]]['boletos'] += b['valor']
            except: pass
        sorted_m = sorted(resumo.keys(), key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])), reverse=True)
        for mes in sorted_m:
            d = resumo[mes]; box = BoxLayout(orientation='vertical', size_hint_y=None, height=220, padding=12, spacing=2)
            with box.canvas.before:
                Color(rgba=(1, 1, 1, 1))
                bg_rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[15,])
            box.bind(pos=lambda obj, val, r=bg_rect: setattr(r, 'pos', val),
                     size=lambda obj, val, r=bg_rect: setattr(r, 'size', val))
            box.add_widget(Label(text=f"MÊS: {mes}", bold=True, height=30, size_hint_y=None))
            box.add_widget(Label(text=f"Faturamento: {format_moeda(d['venda'])}", height=22, size_hint_y=None))
            box.add_widget(Label(text=f"Lucro Bruto: {format_moeda(d['lucro'])}", color=(0.1, 0.5, 0.1, 1), height=22, size_hint_y=None))
            box.add_widget(Label(text=f"Lucas (20%): {format_moeda(d['lucas'])}", color=(0.5, 0.4, 0, 1), height=22, size_hint_y=None))
            box.add_widget(Label(text=f"Desp. Casa/Bol: {format_moeda(d['casa']+d['boletos'])}", color=(0.8, 0, 0, 1), height=22, size_hint_y=None))
            saldo = d['lucro'] - d['casa'] - d['boletos']
            box.add_widget(Label(text=f"SALDO: {format_moeda(saldo)}", bold=True, color=((0,0.6,0,1) if saldo>0 else (0.8,0,0,1)), font_size='18sp', height=40, size_hint_y=None))
            grid.add_widget(box)

    def gerar_graficos(self, tipo):
        if not MATPLOTLIB_AVAILABLE: return
        img_path = os.path.join(self.user_data_dir, 'grafico_temp.png')
        bege = '#F9FAFB'; azul = '#1E1B4B'
        plt.clf(); plt.rcParams['figure.facecolor'] = bege; plt.rcParams['axes.facecolor'] = bege
        mes_atual = datetime.now().strftime("%m/%Y")
        if tipo == 'mes_atual':
            d_l = defaultdict(float); d_c = defaultdict(float)
            for m in self.dados['marcenaria']:
                if m['data'][3:] == mes_atual: d_l[m['data'][:2]] += m['lucro']
            for c in self.dados['casa']:
                if c['data'][3:] == mes_atual: d_c[c['data'][:2]] += c['valor']
            dias = sorted(list(set(list(d_l.keys()) + list(d_c.keys()))))
            if not dias: dias = ["01"]
            plt.figure(figsize=(7, 5)); plt.plot(dias, [d_l[d] for d in dias], label='Lucro', color='green', marker='o')
            plt.plot(dias, [d_c[d] for d in dias], label='Gasto', color='red', marker='x')
        elif tipo == 'evolucao':
            h = defaultdict(float)
            for m in self.dados['marcenaria']: h[m['data'][3:]] += m['lucro']
            meses = sorted(h.keys(), key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))
            plt.figure(figsize=(7, 5)); plt.plot(meses, [h[m] for m in meses], marker='o', color='#1f77b4', linewidth=3)
        plt.tight_layout(); plt.savefig(img_path); plt.close()
        self.main_tabs.ids.graf_imagem.source = ''; self.main_tabs.ids.graf_imagem.source = img_path
        self.main_tabs.ids.graf_imagem.reload()

if __name__ == '__main__':
    GerenciadorApp().run()
