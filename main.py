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
        self.dropdown.clear_widgets()
        if value:
            matches = [s for s in self.suggestions if value.lower() in s.lower()]
            for match in matches:
                btn = Button(text=match, size_hint_y=None, height=44)
                btn.bind(on_release=lambda b, text=match: self.select_match(text))
                self.dropdown.add_widget(btn)
            if matches:
                if not self.dropdown.parent:
                    self.dropdown.open(self)
            else:
                self.dropdown.dismiss()
        else:
            self.dropdown.dismiss()

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
        BoxLayout:
            orientation: 'vertical'
            padding: 15
            spacing: 12
            
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
113: 
114:             Widget:
115:                 size_hint_y: None
116:                 height: 1
117:                 canvas:
118:                     Color:
119:                         rgba: (0.1, 0.1, 0.2, 0.1)
120:                     Rectangle:
121:                         pos: self.pos
122:                         size: self.size
123: 
124:             Label:
125:                 text: 'Novo Trabalho / Projeto'
126:                 size_hint_y: None
127:                 height: 30
128:                 bold: True
129:                 
130:             AutoCompleteTextInput:
131:                 id: marc_nome
132:                 hint_text: 'Nome do Projeto / Cliente'
133:                 suggestions: app.sugestoes_marcenaria
134:                 size_hint_y: None
135:                 height: 55
136:                 
137:             BoxLayout:
138:                 size_hint_y: None
139:                 height: 55
140:                 spacing: 8
141:                 TextInput:
142:                     id: marc_custo
143:                     hint_text: 'Custo Mat.'
144:                     multiline: False
145:                 TextInput:
146:                     id: marc_venda
147:                     hint_text: 'Valor Venda'
148:                     multiline: False
149:                 
150:             Button:
151:                 text: 'SALVAR E CALCULAR'
152:                 size_hint_y: None
153:                 height: 50
154:                 on_release: app.add_marcenaria()
155:                 
156:             ScrollView:
157:                 GridLayout:
158:                     id: marc_grid
159:                     cols: 4
160:                     size_hint_y: None
161:                     height: self.minimum_height
162:                     spacing: 5
163:                     padding: 5
164:                     
165:                     Label:
166:                         text: 'Item'
167:                         bold: True
168:                         height: 35
169:                         size_hint_y: None
170:                     Label:
171:                         text: 'Custo/Venda'
172:                         bold: True
173:                         height: 35
174:                         size_hint_y: None
175:                     Label:
176:                         text: 'Lucro'
177:                         bold: True
178:                         height: 35
179:                         size_hint_y: None
180:                     Label:
181:                         text: 'Func. 20%'
182:                         bold: True
183:                         height: 35
184:                         size_hint_y: None
185: 
186:     TabbedPanelItem:
187:         text: 'Calculadora'
188:         BoxLayout:
189:             orientation: 'vertical'
190:             padding: 15
191:             spacing: 12
192:             
193:             Label:
194:                 text: 'Calculadora de Precificação (Persikall)'
195:                 size_hint_y: None
196:                 height: 30
197:                 bold: True
198:                 
199:             AutoCompleteTextInput:
200:                 id: calc_nome
201:                 hint_text: 'Nome do Projeto / Cliente'
202:                 suggestions: app.sugestoes_marcenaria
203:                 size_hint_y: None
204:                 height: 55
205:                 
206:             BoxLayout:
207:                 size_hint_y: None
208:                 height: 55
209:                 spacing: 8
210:                 TextInput:
211:                     id: calc_custo
212:                     hint_text: 'Custo Mat.'
213:                     multiline: False
214:                 TextInput:
215:                     id: calc_dias
216:                     hint_text: 'Dias Trab.'
217:                     multiline: False
218:                 
219:             Button:
220:                 text: 'CALCULAR E SALVAR'
221:                 size_hint_y: None
222:                 height: 50
223:                 on_release: app.add_calculadora()
224:                 
225:             ScrollView:
226:                 GridLayout:
227:                     id: calc_grid
228:                     cols: 5
229:                     size_hint_y: None
230:                     height: self.minimum_height
231:                     spacing: 5
232:                     padding: 5
233:                     
234:                     Label:
235:                         text: 'Projeto'
236:                         bold: True
237:                         height: 35
238:                         size_hint_y: None
239:                     Label:
240:                         text: 'Custo'
241:                         bold: True
242:                         height: 35
243:                         size_hint_y: None
244:                     Label:
245:                         text: 'Lucro'
246:                         bold: True
247:                         height: 35
248:                         size_hint_y: None
249:                     Label:
250:                         text: 'Venda Final'
251:                         bold: True
252:                         height: 35
253:                         size_hint_y: None
254:                     Label:
255:                         text: 'Func. 20%'
256:                         bold: True
257:                         height: 35
258:                         size_hint_y: None
259: 
260:     TabbedPanelItem:
261:         text: 'Lucas'
262:         BoxLayout:
263:             orientation: 'vertical'
264:             padding: 15
265:             spacing: 12
266:             
267:             Label:
268:                 text: 'Resumo de Comissões - Lucas'
269:                 size_hint_y: None
270:                 height: 40
271:                 bold: True
272:                 font_size: '18sp'
273:                 
274:             Label:
275:                 id: lucas_total
276:                 text: 'Total: R$ 0,00'
277:                 size_hint_y: None
278:                 height: 70
279:                 bold: True
280:                 font_size: '18sp'
281:                 color: (0.1, 0.5, 0.2, 1)
282:                 halign: 'center'
283:                 valign: 'middle'
284:                 text_size: self.size
285:                 canvas.before:
286:                     Color:
287:                         rgba: (1, 1, 1, 1)
288:                     RoundedRectangle:
289:                         pos: self.pos
290:                         size: self.size
291:                         radius: [12,]
292:             
293:             ScrollView:
294:                 GridLayout:
295:                     id: lucas_grid
296:                     cols: 3
297:                     size_hint_y: None
298:                     height: self.minimum_height
299:                     spacing: 10
300:                     padding: 5
301:                     
302:                     Label:
303:                         text: 'Projeto'
304:                         bold: True
305:                         height: 35
306:                         size_hint_y: None
307:                     Label:
308:                         text: 'Valor'
309:                         bold: True
310:                         height: 35
311:                         size_hint_y: None
312:                     Label:
313:                         text: 'Status'
314:                         bold: True
315:                         height: 35
316:                         size_hint_y: None
317: 
318:     TabbedPanelItem:
319:         text: 'Casa'
320:         BoxLayout:
321:             orientation: 'vertical'
322:             padding: 15
323:             spacing: 12
324:             
325:             Label:
326:                 text: 'Despesas Residenciais'
327:                 bold: True
328:                 height: 35
329:                 size_hint_y: None
330: 
331:             Spinner:
332:                 id: casa_tipo
333:                 text: 'Variável'
334:                 values: ['Fixa', 'Variável']
335:                 size_hint_y: None
336:                 height: 55
337:                 
338:             AutoCompleteTextInput:
339:                 id: casa_categoria
340:                 hint_text: 'Descrição da Despesa'
341:                 suggestions: app.sugestoes_casa
342:                 size_hint_y: None
343:                 height: 55
344:                 
345:             BoxLayout:
346:                 size_hint_y: None
347:                 height: 55
348:                 spacing: 8
349:                 TextInput:
350:                     id: casa_valor
351:                     hint_text: 'Valor'
352:                     size_hint_x: 0.6
353:                     multiline: False
354:                 Button:
355:                     text: 'SALVAR'
356:                     size_hint_x: 0.4
357:                     on_release: app.add_casa()
358:                 
359:             ScrollView:
360:                 GridLayout:
361:                     id: casa_grid
362:                     cols: 4
363:                     size_hint_y: None
364:                     height: self.minimum_height
365:                     spacing: 5
366:                     
367:                     Label:
368:                         text: 'Data'
369:                         bold: True
370:                         height: 35
371:                         size_hint_y: None
372:                     Label:
373:                         text: 'Tipo'
374:                         bold: True
375:                         height: 35
376:                         size_hint_y: None
377:                     Label:
378:                         text: 'Categ.'
379:                         bold: True
380:                         height: 35
381:                         size_hint_y: None
382:                     Label:
383:                         text: 'Valor'
384:                         bold: True
385:                         height: 35
386:                         size_hint_y: None
387:                         
388:     TabbedPanelItem:
389:         text: 'Boletos'
390:         BoxLayout:
391:             orientation: 'vertical'
392:             padding: 15
393:             spacing: 12
394:             
395:             Label:
396:                 text: 'Vencimentos'
397:                 bold: True
398:                 height: 35
399:                 size_hint_y: None
400:             
401:             TextInput:
402:                 id: bol_desc
403:                 hint_text: 'Descrição do Boleto'
404:                 size_hint_y: None
405:                 height: 55
406: 
407:             BoxLayout:
408:                 size_hint_y: None
409:                 height: 55
410:                 spacing: 8
411:                 TextInput:
412:                     id: bol_valor
413:                     hint_text: 'Valor'
414:                 TextInput: 
415:                     id: bol_data
416:                     hint_text: 'DD/MM/AAAA'
417:                     on_text: app.validate_date_input(self)
418: 
419:             Button:
420:                 text: 'ADICIONAR LEMBRETE'
421:                 size_hint_y: None
422:                 height: 50
423:                 on_release: app.add_boleto()
424:                 
425:             ScrollView:
426:                 GridLayout:
427:                     id: bol_grid
428:                     cols: 3
429:                     size_hint_y: None
430:                     height: self.minimum_height
431:                     spacing: 5
432:                     
433:                     Label:
434:                         text: 'Descrição'
435:                         bold: True
436:                         height: 35
437:                         size_hint_y: None
438:                     Label:
439:                         text: 'Valor'
440:                         bold: True
441:                         height: 35
442:                         size_hint_y: None
443:                     Label:
444:                         text: 'Vencimento'
445:                         bold: True
446:                         height: 35
447:                         size_hint_y: None
448: 
449:     TabbedPanelItem:
450:         text: 'Resumo'
451:         BoxLayout:
452:             orientation: 'vertical'
453:             padding: 15
454:             spacing: 12
455:             
456:             Label:
457:                 text: 'Balanço Mensal'
458:                 bold: True
459:                 font_size: '18sp'
460:                 height: 40
461:                 size_hint_y: None
462:                 
463:             ScrollView:
464:                 GridLayout:
465:                     id: resumo_grid
466:                     cols: 1
467:                     size_hint_y: None
468:                     height: self.minimum_height
469:                     spacing: 15
470: 
471:     TabbedPanelItem:
472:         text: 'Gráficos'
473:         BoxLayout:
474:             orientation: 'vertical'
475:             padding: 15
476:             spacing: 12
477:             
478:             BoxLayout:
479:                 size_hint_y: None
480:                 height: 50
481:                 spacing: 8
482:                 Button:
483:                     text: 'Mês'
484:                     on_release: app.gerar_graficos('mes_atual')
485:                 Button:
486:                     text: 'Ev.'
487:                     on_release: app.gerar_graficos('evolucao')
488:                 Button:
489:                     text: 'Comp.'
490:                     on_release: app.gerar_graficos('comparativo')
491: 
492:             BoxLayout:
493:                 canvas.before:
494:                     Color:
495:                         rgba: (1, 1, 1, 1)
496:                     RoundedRectangle:
497:                         pos: self.pos
498:                         size: self.size
499:                         radius: [12,]
500:                 Image:
501:                     id: graf_imagem
502:                     source: ''
503:                     allow_stretch: True
504:                     keep_ratio: True
505: '''
506: 
507: class MainTabs(TabbedPanel):
508:     pass
509: 
510: class RootLayout(BoxLayout):
511:     pass
512: 
513: Factory.register('AutoCompleteTextInput', cls=AutoCompleteTextInput)
514: Factory.register('MainTabs', cls=MainTabs)
515: Factory.register('RootLayout', cls=RootLayout)
516: 
517: class GerenciadorApp(App):
518:     sugestoes_marcenaria = ListProperty(['MDF', 'Parafusos', 'Fita de Borda', 'Cola', 'Corrediça', 'Puxador', 'Dobradiça'])
519:     sugestoes_casa = ListProperty(['Mercado', 'Combustível', 'Restaurante', 'Luz', 'Água', 'Internet', 'Consórcio', 'Cartão'])
520:     
521:     def build(self):
522:         self.dados = {
523:             "marcenaria": [],
524:             "calculadora": [],
525:             "casa": [],
526:             "boletos": [],
527:             "sugestoes_marcenaria": self.sugestoes_marcenaria,
528:             "sugestoes_casa": self.sugestoes_casa
529:         }
530:         self.load_dados()
531:         Builder.load_string(KV)
532:         self.root_widget = RootLayout()
533:         self.main_tabs = self.root_widget.ids.main_tabs
534:         Clock.schedule_once(self.populate_grids, 0.5)
535:         return self.root_widget
536:         
537:     @property
538:     def dados_file(self):
539:         return os.path.join(self.user_data_dir, 'dados_gerais.json')
540: 
541:     def load_dados(self):
542:         if os.path.exists(self.dados_file):
543:             try:
544:                 with open(self.dados_file, 'r', encoding='utf-8') as f:
545:                     salvo = json.load(f)
546:                     self.dados.update(salvo)
547:                     self.sugestoes_marcenaria = self.dados.get("sugestoes_marcenaria", self.sugestoes_marcenaria)
548:                     self.sugestoes_casa = self.dados.get("sugestoes_casa", self.sugestoes_casa)
549:             except Exception as e:
550:                 print(f"Erro ao carregar dados: {e}")
551: 
552:     def save_dados(self):
553:         self.dados['sugestoes_marcenaria'] = list(set(self.sugestoes_marcenaria))
554:         self.dados['sugestoes_casa'] = list(set(self.sugestoes_casa))
555:         try:
556:             with open(self.dados_file, 'w', encoding='utf-8') as f:
557:                 json.dump(self.dados, f, ensure_ascii=False, indent=2)
558:             Clock.schedule_once(lambda dt: self.gerar_graficos('mes_atual'), 0.5)
559:         except Exception as e:
560:             print(f"Erro ao salvar dados: {e}")
561: 
562:     def populate_grids(self, dt):
563:         for m in self.dados['marcenaria']:
564:             self.add_row_marcenaria(m)
565:         for cl in self.dados.get('calculadora', []):
566:             self.add_row_calculadora(cl)
567:         for c in self.dados['casa']:
568:             self.add_row_casa(c)
569:         self.refresh_boletos()
570:         self.refresh_lucas()
571:         self.refresh_resumo()
572: 
573:     def add_estoque(self):
574:         root_ids = self.main_tabs.ids
575:         desc = root_ids.marc_estoque_desc.text.strip()
576:         valor = parse_moeda(root_ids.marc_estoque_valor.text)
577:         if not desc or valor == 0: return
578:         data = datetime.now().strftime("%d/%m/%Y")
579:         item = {"data": data, "nome": f"[E] {desc}", "custo": valor, "venda": 0.0, "lucro": -valor, "func": 0.0}
580:         self.dados['marcenaria'].append(item)
581:         if desc not in self.sugestoes_marcenaria: self.sugestoes_marcenaria.append(desc)
582:         self.save_dados()
583:         self.add_row_marcenaria(item)
584:         self.refresh_resumo()
585:         root_ids.marc_estoque_desc.text = ""; root_ids.marc_estoque_valor.text = ""
586: 
587:     def add_marcenaria(self):
588:         root_ids = self.main_tabs.ids
589:         nome = root_ids.marc_nome.text.strip()
590:         custo = parse_moeda(root_ids.marc_custo.text)
591:         venda = parse_moeda(root_ids.marc_venda.text)
592:         if not nome or venda == 0: return
593:         data = datetime.now().strftime("%d/%m/%Y")
594:         lucro = venda - custo; func = lucro * 0.20
595:         item = {"data": data, "nome": nome, "custo": custo, "venda": venda, "lucro": lucro, "func": func}
596:         self.dados['marcenaria'].append(item)
597:         if nome not in self.sugestoes_marcenaria: self.sugestoes_marcenaria.append(nome)
598:         self.save_dados()
599:         self.add_row_marcenaria(item)
600:         self.refresh_lucas(); self.refresh_resumo()
601:         root_ids.marc_nome.text = ""; root_ids.marc_custo.text = ""; root_ids.marc_venda.text = ""
602:         
603:     def add_row_marcenaria(self, item):
604:         grid = self.main_tabs.ids.marc_grid
605:         grid.add_widget(Label(text=item['nome'], size_hint_y=None, height=55))
606:         if item.get('venda', 0.0) == 0.0:
607:             grid.add_widget(Label(text=f"C: {format_moeda(item['custo'])}", size_hint_y=None, height=55))
608:         else:
609:             grid.add_widget(Label(text=f"{format_moeda(item['custo'])}/{format_moeda(item['venda'])}", size_hint_y=None, height=55, font_size='12sp'))
610:         grid.add_widget(Label(text=format_moeda(item['lucro']), size_hint_y=None, height=55))
611:         grid.add_widget(Label(text=format_moeda(item.get('func', 0.0)), color=(0, 0.6, 0.2, 1), bold=True, size_hint_y=None, height=55))
612: 
613:     def add_calculadora(self):
614:         root_ids = self.main_tabs.ids
615:         nome = root_ids.calc_nome.text.strip()
616:         custo = parse_moeda(root_ids.calc_custo.text)
617:         try:
618:             dias_text = root_ids.calc_dias.text.replace(',', '.')
619:             dias = float(dias_text)
620:         except ValueError:
621:             dias = 0.0
622:             
623:         if not nome or dias == 0.0: return
624:         data = datetime.now().strftime("%d/%m/%Y")
625:         
626:         custo_insumos = custo * 1.15
627:         custo_diarias = dias * 595.0
628:         custo_total = custo_insumos + custo_diarias
629:         venda = custo_total * 1.25
630:         lucro = venda - custo_total
631:         func = lucro * 0.20
632:         
633:         item = {"data": data, "nome": nome, "custo": custo_total, "venda": venda, "lucro": lucro, "func": func}
634:         self.dados.setdefault('calculadora', []).append(item)
635:         if nome not in self.sugestoes_marcenaria: self.sugestoes_marcenaria.append(nome)
636:         self.save_dados()
637:         self.add_row_calculadora(item)
638:         self.refresh_lucas()
639:         
640:         root_ids.calc_nome.text = ""
641:         root_ids.calc_custo.text = ""
642:         root_ids.calc_dias.text = ""
643: 
644:     def add_row_calculadora(self, item):
645:         grid = self.main_tabs.ids.calc_grid
646:         grid.add_widget(Label(text=item['nome'], size_hint_y=None, height=55))
647:         grid.add_widget(Label(text=format_moeda(item['custo']), size_hint_y=None, height=55, font_size='12sp'))
648:         grid.add_widget(Label(text=format_moeda(item['lucro']), size_hint_y=None, height=55))
649:         grid.add_widget(Label(text=format_moeda(item['venda']), size_hint_y=None, height=55, font_size='12sp', bold=True, color=(0.1, 0.4, 0.8, 1)))
650:         grid.add_widget(Label(text=format_moeda(item.get('func', 0.0)), color=(0, 0.6, 0.2, 1), bold=True, size_hint_y=None, height=55))
651: 
652:     def refresh_lucas(self):
653:         grid = self.main_tabs.ids.lucas_grid
654:         children = grid.children[:]
655:         for c in children[:-3]: grid.remove_widget(c)
656:         total = 0.0
657:         total_pago = 0.0
658:         items_lucas = self.dados['marcenaria'] + self.dados.get('calculadora', [])
659:         for item in items_lucas:
660:             if item.get('venda', 0.0) > 0.0:
661:                 val = item.get('func', 0.0)
662:                 if val > 0:
663:                     is_pago = item.get('lucas_pago', False)
664:                     grid.add_widget(Label(text=item['nome'], size_hint_y=None, height=35))
665:                     grid.add_widget(Label(text=format_moeda(val), color=(0, 0.6, 0.2, 1), bold=True, size_hint_y=None, height=35))
666:                     
667:                     btn_status = Button(
668:                         text='PAGO' if is_pago else 'PENDENTE',
669:                         size_hint_y=None, height=35,
670:                         background_color=(0, 0.8, 0.4, 1) if is_pago else (0.8, 0.2, 0.2, 1)
671:                     )
672:                     btn_status.bind(on_release=lambda b, it=item: self.toggle_lucas_pago(it))
673:                     grid.add_widget(btn_status)
674:                     
675:                     if not is_pago: total += val
676:                     else: total_pago += val
677: 
678:         self.main_tabs.ids.lucas_total.text = f"Pendente: {format_moeda(total)}"
679: 
680:     def toggle_lucas_pago(self, item):
681:         item['lucas_pago'] = not item.get('lucas_pago', False)
682:         self.save_dados()
683:         self.refresh_lucas()
684: 
685:     def add_casa(self):
686:         root_ids = self.main_tabs.ids
687:         tipo = root_ids.casa_tipo.text
688:         categ = root_ids.casa_categoria.text.strip()
689:         valor = parse_moeda(root_ids.casa_valor.text)
690:         if not categ or valor == 0: return
691:         data = datetime.now().strftime("%d/%m/%Y")
692:         item = {"data": data, "tipo": tipo, "categoria": categ, "valor": valor}
693:         self.dados['casa'].append(item)
694:         if categ not in self.sugestoes_casa: self.sugestoes_casa.append(categ)
695:         self.save_dados()
696:         self.add_row_casa(item)
697:         self.refresh_resumo()
698:         root_ids.casa_categoria.text = ""; root_ids.casa_valor.text = ""
699: 
700:     def add_row_casa(self, item):
701:         grid = self.main_tabs.ids.casa_grid
702:         grid.add_widget(Label(text=item['data'], font_size='11sp', size_hint_y=None, height=45))
703:         grid.add_widget(Label(text=item['tipo'], size_hint_y=None, height=45))
704:         grid.add_widget(Label(text=item['categoria'], size_hint_y=None, height=45))
705:         grid.add_widget(Label(text=format_moeda(item['valor']), color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=45))
706: 
707:     def add_boleto(self):
708:         root_ids = self.main_tabs.ids
709:         desc = root_ids.bol_desc.text.strip()
710:         valor = parse_moeda(root_ids.bol_valor.text)
711:         data = root_ids.bol_data.text.strip()
712:         if not desc or valor == 0 or not data: return
713:         item = {"desc": desc, "valor": valor, "data": data, "pago": False}
714:         self.dados['boletos'].append(item)
715:         self.save_dados()
716:         self.refresh_boletos()
717:         root_ids.bol_desc.text = ""; root_ids.bol_valor.text = ""; root_ids.bol_data.text = ""
718: 
719:     def refresh_boletos(self):
720:         grid = self.main_tabs.ids.bol_grid
721:         children = grid.children[:]
722:         for c in children[:-3]: grid.remove_widget(c)
723:         for b in self.dados['boletos']:
724:             color = (0.5, 0.5, 0.5, 1) if b.get('pago') else (0.8, 0.1, 0.1, 1)
725:             grid.add_widget(Label(text=b['desc'], color=color, size_hint_y=None, height=45))
726:             grid.add_widget(Label(text=format_moeda(b['valor']), color=color, size_hint_y=None, height=45))
727:             btn = Button(text=b['data'], size_hint_y=None, height=45, background_color=color)
728:             btn.bind(on_release=lambda x, it=b: self.toggle_boleto(it))
729:             grid.add_widget(btn)
730: 
731:     def toggle_boleto(self, item):
732:         item['pago'] = not item.get('pago', False)
733:         self.save_dados()
734:         self.refresh_boletos()
735: 
736:     def validate_date_input(self, instance):
737:         t = instance.text.replace('/', '')
738:         if len(t) > 8: t = t[:8]
739:         if len(t) > 4: t = t[:2] + '/' + t[2:4] + '/' + t[4:]
740:         elif len(t) > 2: t = t[:2] + '/' + t[2:]
741:         instance.text = t
742: 
743:     def refresh_resumo(self):
744:         grid = self.main_tabs.ids.resumo_grid
745:         grid.clear_widgets()
746:         
747:         gastos_marc = sum(item['custo'] for item in self.dados['marcenaria'])
748:         vendas_marc = sum(item.get('venda', 0.0) for item in self.dados['marcenaria'])
749:         lucro_marc = sum(item.get('lucro', 0.0) for item in self.dados['marcenaria'])
750:         gastos_casa = sum(item['valor'] for item in self.dados['casa'])
751:         
752:         def add_res_row(label, valor, color=(0.1, 0.1, 0.2, 1)):
753:             bg = BoxLayout(size_hint_y=None, height=60, padding=10, spacing=10)
754:             with bg.canvas.before:
755:                 Color(rgba=(1,1,1,1))
756:                 RoundedRectangle(pos=bg.pos, size=bg.size, radius=[10,])
757:             bg.add_widget(Label(text=label, halign='left', color=(0.3, 0.3, 0.3, 1)))
758:             bg.add_widget(Label(text=format_moeda(valor), bold=True, halign='right', color=color))
759:             grid.add_widget(bg)
760: 
761:         add_res_row("Faturamento Marcenaria", vendas_marc, (0.1, 0.5, 0.2, 1))
762:         add_res_row("Custos Marcenaria", gastos_marc, (0.8, 0.2, 0.2, 1))
763:         add_res_row("Lucro Bruto Marcenaria", lucro_marc, (0.1, 0.4, 0.8, 1))
764:         add_res_row("Despesas Casa", gastos_casa, (0.8, 0.2, 0.2, 1))
765:         add_res_row("SALDO FINAL", lucro_marc - gastos_casa, (0, 0, 0, 1))
766: 
767:     def gerar_graficos(self, tipo):
768:         if not MATPLOTLIB_AVAILABLE: return
769:         plt.figure(figsize=(6, 4))
770:         if tipo == 'mes_atual':
771:             labels = ['Lucro', 'Casa']; values = [sum(i['lucro'] for i in self.dados['marcenaria']), sum(i['valor'] for i in self.dados['casa'])]
772:             plt.pie(values, labels=labels, autopct='%1.1f%%', colors=['#4a90e2', '#e94e77'])
773:         
774:         path = os.path.join(self.user_data_dir, 'grafico_temp.png')
775:         plt.savefig(path, transparent=True)
776:         plt.close()
777:         self.root_widget.ids.main_tabs.ids.graf_imagem.source = path
778:         self.root_widget.ids.main_tabs.ids.graf_imagem.reload()
779: 
780: if __name__ == '__main__':
781:     GerenciadorApp().run()
