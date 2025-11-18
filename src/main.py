"""
Sistema de Gestão de Manutenção de Frota - ALS
Interface Gráfica Principal
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import pandas as pd
import os
import sys
from PIL import Image, ImageTk

# Adiciona o diretório pai ao path (necessário para importações)
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, application_path)

from src.database import DatabaseManager
from src.utils import formatar_data_br, validar_data, validar_numero, limpar_texto, gerar_relatorio_pdf, gerar_relatorio_word
from src.veiculos import GerenciadorVeiculos
from src.interface_veiculos import JanelaCadastroVeiculos
from src.destinos import GerenciadorDestinos


class FormularioRegistro(tk.Toplevel):
    """
    Formulário para adicionar/editar registros
    """
    
    def __init__(self, parent, db, gerenciador_veiculos, gerenciador_destinos, registro=None, callback=None):
        super().__init__(parent)
        
        self.db = db
        self.gerenciador_veiculos = gerenciador_veiculos
        self.gerenciador_destinos = gerenciador_destinos
        self.registro = registro
        self.callback = callback
        self.resultado = None
        
        # Configura janela
        self.title("Novo Registro" if registro is None else "Editar Registro")
        self.geometry("800x700")
        self.resizable(False, False)
        
        # Centraliza janela
        self.transient(parent)
        self.grab_set()
        
        self.criar_formulario()
        
        # Se é edição, preenche dados
        if registro is not None:
            self.preencher_dados(registro)
    
    
    def criar_formulario(self):
        """
        Cria campos do formulário
        """
        # Frame principal com scroll
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = "Novo Registro de Manutenção" if self.registro is None else "Editar Registro"
        ttk.Label(
            main_frame, 
            text=titulo,
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Dicionário para armazenar widgets
        self.campos = {}
        
        # Campo especial de seleção de veículo (no topo)
        row = 1
        
        # Seletor de Veículo Cadastrado
        ttk.Label(
            main_frame,
            text="🚛 Selecionar Veículo:",
            font=('Arial', 10, 'bold')
        ).grid(row=row, column=0, sticky=tk.W, pady=5)
        
        frame_veiculo = ttk.Frame(main_frame)
        frame_veiculo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.combo_veiculo_cadastrado = ttk.Combobox(
            frame_veiculo,
            width=35,
            values=self.gerenciador_veiculos.obter_veiculos_ativos(),
            state='readonly'
        )
        self.combo_veiculo_cadastrado.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_veiculo_cadastrado.bind('<<ComboboxSelected>>', self.ao_selecionar_veiculo)
        
        ttk.Button(
            frame_veiculo,
            text="📋",
            width=3,
            command=self.abrir_cadastro_veiculos
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        row += 1
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )
        row += 1
        
        # Define campos do formulário
        campos_config = [
            ('DATA', 'Data:', 'entry'),
            ('PLACA', 'Placa:', 'entry_readonly'),
            ('KM', 'KM:', 'entry'),
            ('VEÍCULO', 'Tipo:', 'entry_readonly'),
            ('DESTINO PROGRAMADO', 'Destino Programado:', 'combo_com_adicionar'),
            ('SERVIÇO A EXECUTAR', 'Serviço a Executar:', 'text'),
            ('STATUS', 'Status:', 'combo', ['EM SERVIÇO', 'FINALIZADO']),
            ('DATA ENTRADA', 'Data Entrada:', 'entry'),
            ('DATA SAÍDA', 'Data Saída:', 'entry'),
            ('NR° OF', 'NRº OF:', 'entry'),
            ('OBS', 'Observações:', 'text'),
        ]
        
        for campo_config in campos_config:
            campo_nome = campo_config[0]
            campo_label = campo_config[1]
            campo_tipo = campo_config[2]
            
            # Label
            ttk.Label(
                main_frame, 
                text=campo_label,
                font=('Arial', 10, 'bold')
            ).grid(row=row, column=0, sticky=tk.W, pady=5)
            
            # Widget de entrada
            if campo_tipo == 'entry':
                widget = ttk.Entry(main_frame, width=40)
                widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
            
            elif campo_tipo == 'entry_readonly':
                widget = ttk.Entry(main_frame, width=40, state='readonly')
                widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
            
            elif campo_tipo == 'combo_com_adicionar':
                # Frame especial para destino com botão [+]
                frame_destino = ttk.Frame(main_frame)
                frame_destino.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                
                widget = ttk.Combobox(
                    frame_destino,
                    width=35,
                    values=self.gerenciador_destinos.obter_destinos_ativos()
                )
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                ttk.Button(
                    frame_destino,
                    text="[+]",
                    width=4,
                    command=self.adicionar_novo_destino
                ).pack(side=tk.LEFT, padx=(5, 0))
                
            elif campo_tipo == 'combo':
                valores = campo_config[3] if len(campo_config) > 3 else []
                widget = ttk.Combobox(main_frame, width=38, values=valores)
                widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                
            elif campo_tipo == 'text':
                frame_text = ttk.Frame(main_frame)
                frame_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                
                widget = tk.Text(frame_text, height=3, width=40, font=('Arial', 9))
                widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                scroll = ttk.Scrollbar(frame_text, command=widget.yview)
                scroll.pack(side=tk.RIGHT, fill=tk.Y)
                widget.config(yscrollcommand=scroll.set)
            
            self.campos[campo_nome] = widget
            row += 1
        
        # Frame de botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            frame_botoes,
            text="💾  Salvar",
            command=self.salvar,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="❌  Cancelar",
            command=self.cancelar,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Info sobre cálculos automáticos
        ttk.Label(
            main_frame,
            text="ℹ️ Dica: Selecione um veículo cadastrado ou preencha manualmente. Status e Dias em Manutenção são calculados automaticamente.",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        ).grid(row=row+1, column=0, columnspan=2, pady=10)
    
    
    def ao_selecionar_veiculo(self, event=None):
        """
        Quando um veículo cadastrado é selecionado, preenche dados automaticamente
        """
        selecao = self.combo_veiculo_cadastrado.get()
        if not selecao:
            return
        
        # Extrai placa da seleção
        placa = self.gerenciador_veiculos.extrair_placa_da_selecao(selecao)
        
        # Busca dados do veículo
        veiculo = self.gerenciador_veiculos.obter_veiculo_por_placa(placa)
        
        if veiculo:
            # Preenche PLACA (readonly)
            self.campos['PLACA'].config(state='normal')
            self.campos['PLACA'].delete(0, tk.END)
            self.campos['PLACA'].insert(0, veiculo['PLACA'])
            self.campos['PLACA'].config(state='readonly')
            
            # Preenche VEÍCULO/Tipo (readonly)
            self.campos['VEÍCULO'].config(state='normal')
            self.campos['VEÍCULO'].delete(0, tk.END)
            self.campos['VEÍCULO'].insert(0, veiculo['TIPO_VEICULO'])
            self.campos['VEÍCULO'].config(state='readonly')
            
            # Preenche KM com última KM registrada
            self.campos['KM'].delete(0, tk.END)
            ultima_km = veiculo.get('ULTIMA_KM', 0)
            self.campos['KM'].insert(0, str(ultima_km))
            
            # Foca no próximo campo
            self.campos['KM'].focus()
    
    
    def adicionar_novo_destino(self):
        """
        Abre pop-up para adicionar novo destino
        """
        # Cria janela pop-up
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Novo Destino")
        dialog.geometry("400x180")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centraliza
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (200)
        y = (dialog.winfo_screenheight() // 2) - (90)
        dialog.geometry(f"400x180+{x}+{y}")
        
        # Frame principal
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            frame,
            text="📍 Cadastrar Novo Destino",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 15))
        
        # Label e entrada
        ttk.Label(
            frame,
            text="Nome do Destino:",
            font=('Arial', 10)
        ).pack(anchor=tk.W, pady=(0, 5))
        
        entry_destino = ttk.Entry(frame, width=40, font=('Arial', 10))
        entry_destino.pack(fill=tk.X, pady=(0, 15))
        entry_destino.focus()
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack()
        
        def salvar():
            nome = entry_destino.get().strip()
            if not nome:
                messagebox.showwarning("Aviso", "Digite o nome do destino!", parent=dialog)
                return
            
            sucesso, mensagem = self.gerenciador_destinos.adicionar_destino(nome)
            
            if sucesso:
                # Atualiza lista no combobox
                self.campos['DESTINO PROGRAMADO']['values'] = self.gerenciador_destinos.obter_destinos_ativos()
                # Seleciona o novo destino
                self.campos['DESTINO PROGRAMADO'].set(nome.upper())
                messagebox.showinfo("Sucesso", mensagem, parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror("Erro", mensagem, parent=dialog)
        
        def cancelar():
            dialog.destroy()
        
        # Bind Enter para salvar
        entry_destino.bind('<Return>', lambda e: salvar())
        
        ttk.Button(
            frame_botoes,
            text="💾  Salvar",
            command=salvar,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="❌  Cancelar",
            command=cancelar,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    
    def abrir_cadastro_veiculos(self):
        """
        Abre janela de cadastro de veículos
        """
        JanelaCadastroVeiculos(self, self.gerenciador_veiculos)
        
        # Atualiza lista após fechar cadastro
        self.combo_veiculo_cadastrado['values'] = self.gerenciador_veiculos.obter_veiculos_ativos()
    
    
    def preencher_dados(self, registro):
        """
        Preenche formulário com dados existentes
        """
        for campo_nome, widget in self.campos.items():
            valor = registro.get(campo_nome, '')
            
            if isinstance(widget, tk.Text):
                widget.delete('1.0', tk.END)
                widget.insert('1.0', str(valor) if valor else '')
            else:
                widget.delete(0, tk.END)
                
                # Formata datas
                if 'DATA' in campo_nome and valor:
                    valor = formatar_data_br(valor)
                
                widget.insert(0, str(valor) if valor else '')
    
    
    def obter_dados(self):
        """
        Obtém dados do formulário
        """
        dados = {}
        
        for campo_nome, widget in self.campos.items():
            if isinstance(widget, tk.Text):
                valor = widget.get('1.0', tk.END).strip()
            else:
                valor = widget.get().strip()
            
            dados[campo_nome] = valor
        
        return dados
    
    
    def validar_dados(self, dados):
        """
        Valida dados do formulário
        """
        erros = []
        
        # Campos obrigatórios
        if not dados.get('PLACA'):
            erros.append("• Placa é obrigatória")
        
        if not dados.get('DATA ENTRADA'):
            erros.append("• Data de Entrada é obrigatória")
        
        # Valida formato de datas
        for campo in ['DATA', 'DATA ENTRADA', 'DATA SAÍDA']:
            if dados.get(campo):
                if not validar_data(dados[campo]):
                    erros.append(f"• {campo}: formato inválido (use DD/MM/AAAA)")
        
        return erros
    
    
    def salvar(self):
        """
        Salva dados do formulário
        """
        dados = self.obter_dados()
        
        # Valida
        erros = self.validar_dados(dados)
        if erros:
            messagebox.showerror(
                "Erro de Validação",
                "Corrija os seguintes erros:\n\n" + "\n".join(erros)
            )
            return
        
        # Calcula campos automáticos
        from src.utils import calcular_dias_manutencao, calcular_status
        
        dados['TOTAL DE DIAS EM MANUTENÇÃO'] = calcular_dias_manutencao(
            dados.get('DATA ENTRADA'),
            dados.get('DATA SAÍDA')
        )
        
        dados['STATUS'] = calcular_status(
            dados.get('DATA ENTRADA'),
            dados.get('DATA SAÍDA'),
            dados.get('STATUS', '')
        )
        
        # Atualiza KM do veículo no cadastro
        if dados.get('PLACA') and dados.get('KM'):
            try:
                km = float(dados.get('KM', 0))
                self.gerenciador_veiculos.atualizar_km(dados['PLACA'], km)
                self.gerenciador_veiculos.salvar_dados()
            except:
                pass  # Se não conseguir atualizar, continua normalmente
        
        self.resultado = dados
        
        if self.callback:
            self.callback(dados)
        
        self.destroy()
    
    
    def cancelar(self):
        """
        Cancela operação
        """
        self.resultado = None
        self.destroy()


class SistemaManutencao:
    """
    Classe principal da interface gráfica
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Manutenção - ALS")
        self.root.geometry("1400x800")
        
        # Inicializa banco de dados
        try:
            self.db = DatabaseManager()
        except Exception as e:
            messagebox.showerror(
                "Erro ao Inicializar",
                f"Não foi possível carregar o banco de dados:\n{e}\n\nVerifique se a pasta 'data' existe."
            )
            sys.exit(1)
        
        # Inicializa gerenciador de veículos
        try:
            self.gerenciador_veiculos = GerenciadorVeiculos()
        except Exception as e:
            messagebox.showerror(
                "Erro ao Inicializar",
                f"Não foi possível carregar o cadastro de veículos:\n{e}"
            )
            self.gerenciador_veiculos = GerenciadorVeiculos()  # Cria novo vazio
        
        # Inicializa gerenciador de destinos
        try:
            self.gerenciador_destinos = GerenciadorDestinos()
        except Exception as e:
            messagebox.showerror(
                "Erro ao Inicializar",
                f"Não foi possível carregar o cadastro de destinos:\n{e}"
            )
            self.gerenciador_destinos = GerenciadorDestinos()  # Cria novo vazio
        
        # Variável para índice selecionado
        self.indice_selecionado = None
        
        # Controle de ordenação das colunas
        self.ordem_colunas = {}  # Armazena estado de ordenação de cada coluna
        self.df_original = None  # Guarda ordem original dos dados
        
        # Configura estilo
        self.configurar_estilo()
        
        # Cria interface
        self.criar_interface()
        
        # Carrega dados iniciais
        self.atualizar_tabela()
        
        # Atualiza estatísticas
        self.atualizar_estatisticas()
        
        # Configura fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
    
    
    def configurar_estilo(self):
        """
        Configura estilo visual
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        # Aumenta fonte dos botões para emojis ficarem maiores e mais visíveis
        style.configure('TButton', padding=6, font=('Segoe UI Emoji', 11))
        style.configure('TLabel', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Treeview', rowheight=25, font=('Arial', 9))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    
    def criar_interface(self):
        """
        Cria interface completa
        """
        # ==== FRAME TOPO ====
        frame_topo = ttk.Frame(self.root, padding="10")
        frame_topo.pack(fill=tk.X)
        
        # Frame para logo e título
        frame_header = ttk.Frame(frame_topo)
        frame_header.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ALS à esquerda
        try:
            # Determina caminho da logo
            if getattr(sys, 'frozen', False):
                logo_path = os.path.join(sys._MEIPASS, 'img', 'logo ALS.png')
            else:
                logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img', 'logo ALS.png')
            
            # Carrega e redimensiona logo
            logo_original = Image.open(logo_path)
            # Redimensiona mantendo proporção
            altura_nova = 80
            proporcao = altura_nova / logo_original.height
            largura_nova = int(logo_original.width * proporcao)
            logo_redimensionada = logo_original.resize((largura_nova, altura_nova), Image.Resampling.LANCZOS)
            
            self.logo_photo = ImageTk.PhotoImage(logo_redimensionada)
            
            logo_label = ttk.Label(frame_header, image=self.logo_photo)
            logo_label.pack(side=tk.LEFT, padx=(0, 20))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar logo: {e}")
        
        # Título à direita da logo
        titulo_frame = ttk.Frame(frame_header)
        titulo_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        ttk.Label(
            titulo_frame,
            text="SISTEMA DE GESTÃO DE MANUTENÇÃO - ALS",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(25, 0))
        
        # Estatísticas
        self.frame_stats = ttk.Frame(frame_topo)
        self.frame_stats.pack(pady=10)
        
        self.label_stats = ttk.Label(self.frame_stats, text="", font=('Arial', 9))
        self.label_stats.pack()
        
        # ==== FRAME FILTROS ====
        frame_filtros = ttk.LabelFrame(self.root, text="[Filtros de Busca]", padding="10")
        frame_filtros.pack(fill=tk.X, padx=10, pady=5)
        
        filtro_linha = ttk.Frame(frame_filtros)
        filtro_linha.pack(fill=tk.X)
        
        ttk.Label(filtro_linha, text="Placa:").pack(side=tk.LEFT, padx=5)
        self.filtro_placa = ttk.Entry(filtro_linha, width=12)
        self.filtro_placa.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filtro_linha, text="Veículo:").pack(side=tk.LEFT, padx=5)
        self.filtro_veiculo = ttk.Entry(filtro_linha, width=12)
        self.filtro_veiculo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filtro_linha, text="Status:").pack(side=tk.LEFT, padx=5)
        self.filtro_status = ttk.Combobox(
            filtro_linha,
            values=['', 'EM SERVIÇO', 'FINALIZADO'],
            width=12
        )
        self.filtro_status.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filtro_linha, text="🔍  Buscar", command=self.aplicar_filtros).pack(side=tk.LEFT, padx=5)
        ttk.Button(filtro_linha, text="🧹  Limpar", command=self.limpar_filtros).pack(side=tk.LEFT, padx=5)
        
        # ==== FRAME AÇÕES ====
        frame_acoes = ttk.Frame(self.root, padding="10")
        frame_acoes.pack(fill=tk.X)
        
        ttk.Button(frame_acoes, text="➕  Novo Registro", command=self.novo_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="✏️  Editar", command=self.editar_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="🗑️  Excluir", command=self.excluir_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="💾  Salvar", command=self.salvar_dados).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="🔄  Atualizar", command=self.atualizar_tabela).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="🚛  Veículos", command=self.gerenciar_veiculos).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="📊  Relatório", command=self.gerar_relatorio).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="📤  Exportar", command=self.exportar_excel).pack(side=tk.LEFT, padx=5)
        
        # ==== FRAME TABELA ====
        frame_tabela = ttk.Frame(self.root, padding="10")
        frame_tabela.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_tabela, orient=tk.HORIZONTAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            frame_tabela,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode='browse'
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Colunas
        colunas = ['DATA', 'PLACA', 'KM', 'VEÍCULO', 'DESTINO PROGRAMADO',
                   'SERVIÇO A EXECUTAR', 'STATUS', 'DATA ENTRADA', 'DATA SAÍDA',
                   'DIAS', 'NR° OF', 'OBS']
        
        self.tree['columns'] = colunas
        self.tree.column('#0', width=0, stretch=tk.NO)
        
        larguras = {'DATA': 90, 'PLACA': 80, 'KM': 70, 'VEÍCULO': 100,
                    'DESTINO PROGRAMADO': 130, 'SERVIÇO A EXECUTAR': 200,
                    'STATUS': 100, 'DATA ENTRADA': 100, 'DATA SAÍDA': 100,
                    'DIAS': 50, 'NR° OF': 70, 'OBS': 150}
        
        for col in colunas:
            self.tree.column(col, width=larguras.get(col, 100), anchor=tk.W)
            self.tree.heading(
                col, 
                text=col, 
                anchor=tk.W,
                command=lambda c=col: self.ordenar_por_coluna(c)
            )
        
        self.tree.bind('<Double-1>', lambda e: self.editar_registro())
        self.tree.bind('<<TreeviewSelect>>', self.on_selecionar)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # ==== STATUS BAR ====
        self.label_status = ttk.Label(
            self.root,
            text="✅  Sistema pronto",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.label_status.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
    
    
    def on_selecionar(self, event):
        """
        Callback quando linha é selecionada
        """
        selecao = self.tree.selection()
        if selecao:
            item = self.tree.item(selecao[0])
            self.indice_selecionado = item['tags'][0] if item['tags'] else None
    
    
    def ordenar_por_coluna(self, coluna):
        """
        Ordena tabela clicando no cabeçalho da coluna
        Estados: None (original) -> 'asc' (crescente) -> 'desc' (decrescente) -> None (volta ao original)
        """
        # Guarda DataFrame original na primeira ordenação
        if self.df_original is None:
            self.df_original = self.db.df.copy()
        
        # Verifica estado atual da coluna
        estado_atual = self.ordem_colunas.get(coluna, None)
        
        # Mapeia coluna visual para coluna do DataFrame
        mapa_colunas = {
            'DATA': 'DATA',
            'PLACA': 'PLACA',
            'KM': 'KM',
            'VEÍCULO': 'VEÍCULO',
            'DESTINO PROGRAMADO': 'DESTINO PROGRAMADO',
            'SERVIÇO A EXECUTAR': 'SERVIÇO A EXECUTAR',
            'STATUS': 'STATUS',
            'DATA ENTRADA': 'DATA ENTRADA',
            'DATA SAÍDA': 'DATA SAÍDA',
            'DIAS': 'TOTAL DE DIAS EM MANUTENÇÃO',
            'NR° OF': 'NR° OF',
            'OBS': 'OBS'
        }
        
        coluna_df = mapa_colunas.get(coluna, coluna)
        
        # Define próximo estado
        if estado_atual is None:
            # Primeira vez: ordena crescente
            novo_estado = 'asc'
            df_ordenado = self.db.df.copy()
            
            # Tratamento especial para datas
            if coluna in ['DATA', 'DATA ENTRADA', 'DATA SAÍDA']:
                df_ordenado[coluna_df] = pd.to_datetime(df_ordenado[coluna_df], format='%d/%m/%Y', errors='coerce')
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=True, na_position='last')
            # Tratamento especial para números
            elif coluna in ['KM', 'DIAS']:
                df_ordenado[coluna_df] = pd.to_numeric(df_ordenado[coluna_df], errors='coerce')
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=True, na_position='last')
            # Ordenação alfabética para texto
            else:
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=True, na_position='last')
            
            # Atualiza indicador visual no cabeçalho
            self.tree.heading(coluna, text=f"{coluna} ▲")
            
        elif estado_atual == 'asc':
            # Segunda vez: ordena decrescente
            novo_estado = 'desc'
            df_ordenado = self.db.df.copy()
            
            # Tratamento especial para datas
            if coluna in ['DATA', 'DATA ENTRADA', 'DATA SAÍDA']:
                df_ordenado[coluna_df] = pd.to_datetime(df_ordenado[coluna_df], format='%d/%m/%Y', errors='coerce')
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=False, na_position='last')
            # Tratamento especial para números
            elif coluna in ['KM', 'DIAS']:
                df_ordenado[coluna_df] = pd.to_numeric(df_ordenado[coluna_df], errors='coerce')
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=False, na_position='last')
            # Ordenação alfabética para texto
            else:
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=False, na_position='last')
            
            # Atualiza indicador visual no cabeçalho
            self.tree.heading(coluna, text=f"{coluna} ▼")
            
        else:  # estado_atual == 'desc'
            # Terceira vez: volta à ordem original
            novo_estado = None
            df_ordenado = self.df_original.copy()
            
            # Remove indicador visual do cabeçalho
            self.tree.heading(coluna, text=coluna)
        
        # Atualiza estado da coluna
        self.ordem_colunas[coluna] = novo_estado
        
        # Remove indicadores de outras colunas
        colunas_visiveis = ['DATA', 'PLACA', 'KM', 'VEÍCULO', 'DESTINO PROGRAMADO',
                           'SERVIÇO A EXECUTAR', 'STATUS', 'DATA ENTRADA', 'DATA SAÍDA',
                           'DIAS', 'NR° OF', 'OBS']
        for outra_col in colunas_visiveis:
            if outra_col != coluna and self.ordem_colunas.get(outra_col) is not None:
                self.ordem_colunas[outra_col] = None
                self.tree.heading(outra_col, text=outra_col)
        
        # Atualiza a exibição com DataFrame ordenado
        self.db.df = df_ordenado.reset_index(drop=True)
        self.atualizar_tabela()
    
    
    def atualizar_tabela(self, df=None):
        """
        Atualiza dados na tabela
        """
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Usa DataFrame fornecido ou completo
        if df is None:
            df = self.db.obter_dataframe_exibicao()
            # Salva ordem original na primeira vez
            if self.df_original is None:
                self.df_original = self.db.df.copy()
        
        # Popula tabela
        for idx, row in df.iterrows():
            valores = [
                formatar_data_br(row.get('DATA', '')),
                row.get('PLACA', ''),
                row.get('KM', ''),
                row.get('VEÍCULO', ''),
                row.get('DESTINO PROGRAMADO', ''),
                row.get('SERVIÇO A EXECUTAR', ''),
                row.get('STATUS', ''),
                formatar_data_br(row.get('DATA ENTRADA', '')),
                formatar_data_br(row.get('DATA SAÍDA', '')),
                row.get('DIAS', row.get('TOTAL DE DIAS EM MANUTENÇÃO', '0')),
                row.get('NR° OF', ''),
                row.get('OBS', '')
            ]
            
            # Define cor baseada no status
            tag = 'em_servico' if row.get('STATUS', '').upper() == 'EM SERVIÇO' else 'finalizado'
            
            self.tree.insert('', tk.END, values=valores, tags=(idx, tag))
        
        # Configura cores
        self.tree.tag_configure('em_servico', background='#fff3cd')
        self.tree.tag_configure('finalizado', background='#d1e7dd')
        
        self.label_status.config(text=f"📋  {len(df)} registros carregados")
    
    
    def atualizar_estatisticas(self):
        """
        Atualiza estatísticas no topo
        """
        stats = self.db.obter_estatisticas()
        
        texto = f"📊  Total: {stats['total_registros']}  |  "
        texto += f"🔧  Em Serviço: {stats['em_servico']}  |  "
        texto += f"✅  Finalizados: {stats['finalizados']}  |  "
        texto += f"⏱️  Tempo Médio: {stats['tempo_medio']:.1f} dias  |  "
        texto += f"🚗  Placas: {stats['placas_unicas']}"
        
        self.label_stats.config(text=texto)
    
    
    def aplicar_filtros(self):
        """
        Aplica filtros de busca
        """
        filtros = {}
        
        if self.filtro_placa.get():
            filtros['PLACA'] = self.filtro_placa.get()
        
        if self.filtro_veiculo.get():
            filtros['VEÍCULO'] = self.filtro_veiculo.get()
        
        if self.filtro_status.get():
            filtros['STATUS'] = self.filtro_status.get()
        
        df_filtrado = self.db.buscar_registros(filtros)
        self.atualizar_tabela(df_filtrado)
        self.label_status.config(text=f"🔍  {len(df_filtrado)} registros encontrados")
    
    
    def limpar_filtros(self):
        """
        Limpa filtros e mostra todos os registros
        """
        self.filtro_placa.delete(0, tk.END)
        self.filtro_veiculo.delete(0, tk.END)
        self.filtro_status.set('')
        self.atualizar_tabela()
    
    
    def novo_registro(self):
        """
        Abre formulário para novo registro
        """
        def callback(dados):
            if self.db.adicionar_registro(dados):
                self.atualizar_tabela()
                self.atualizar_estatisticas()
                messagebox.showinfo("Sucesso", "Registro adicionado com sucesso!")
        
        FormularioRegistro(self.root, self.db, self.gerenciador_veiculos, self.gerenciador_destinos, callback=callback)
    
    
    def editar_registro(self):
        """
        Edita registro selecionado
        """
        if self.indice_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um registro para editar")
            return
        
        registro = self.db.df.iloc[self.indice_selecionado].to_dict()
        
        def callback(dados):
            if self.db.atualizar_registro(self.indice_selecionado, dados):
                self.atualizar_tabela()
                self.atualizar_estatisticas()
                messagebox.showinfo("Sucesso", "Registro atualizado com sucesso!")
        
        FormularioRegistro(self.root, self.db, self.gerenciador_veiculos, self.gerenciador_destinos, registro=registro, callback=callback)
    
    
    def excluir_registro(self):
        """
        Exclui registro selecionado
        """
        if self.indice_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um registro para excluir")
            return
        
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este registro?"
        )
        
        if resposta:
            if self.db.excluir_registro(self.indice_selecionado):
                self.atualizar_tabela()
                self.atualizar_estatisticas()
                self.indice_selecionado = None
                messagebox.showinfo("Sucesso", "Registro excluído com sucesso!")
    
    
    def salvar_dados(self):
        """
        Salva dados no Excel
        """
        if self.db.salvar_dados():
            self.atualizar_estatisticas()
            messagebox.showinfo("Sucesso", "Dados salvos com sucesso!\n\nBackup criado na pasta 'backup'")
        else:
            messagebox.showerror("Erro", "Não foi possível salvar os dados")
    
    
    def gerenciar_veiculos(self):
        """
        Abre janela de gerenciamento de veículos
        """
        JanelaCadastroVeiculos(self.root, self.gerenciador_veiculos)
    
    
    def gerar_relatorio(self):
        """
        Gera relatório estatístico com opções de formato
        """
        from .utils import gerar_relatorio_pdf, gerar_relatorio_word
        
        # Janela de opções
        dialog = tk.Toplevel(self.root)
        dialog.title("Gerar Relatório")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"400x250+{x}+{y}")
        
        tk.Label(dialog, text="Escolha o formato do relatório:", font=('Arial', 12, 'bold')).pack(pady=20)
        
        def gerar_txt():
            stats = self.db.obter_estatisticas()
            
            relatorio = f"""
╔══════════════════════════════════════════╗
║       RELATÓRIO DE MANUTENÇÃO - ALS      ║
╚══════════════════════════════════════════╝

 ESTATÍSTICAS GERAIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total de Registros: {stats['total_registros']}
Veículos em Serviço: {stats['em_servico']}
Manutenções Finalizadas: {stats['finalizados']}
Tempo Médio de Manutenção: {stats['tempo_medio']:.1f} dias
Placas Únicas: {stats['placas_unicas']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            """
            
            arquivo = f"output/Relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(relatorio)
            
            dialog.destroy()
            messagebox.showinfo("Relatório Gerado", f"Relatório salvo em:\n{arquivo}")
        
        def gerar_pdf_relatorio():
            stats = self.db.obter_estatisticas()
            dados = self.db.df.copy()
            arquivo = f"output/Relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            estatisticas = {
                'total': stats['total_registros'],
                'em_servico': stats['em_servico'],
                'finalizados': stats['finalizados'],
                'tempo_medio': stats['tempo_medio'],
                'placas_unicas': stats['placas_unicas']
            }
            
            sucesso, resultado = gerar_relatorio_pdf(dados, estatisticas, arquivo)
            dialog.destroy()
            
            if sucesso:
                messagebox.showinfo("Relatório PDF", f"Relatório PDF salvo em:\n{resultado}")
            else:
                messagebox.showerror("Erro", resultado)
        
        def gerar_word_relatorio():
            stats = self.db.obter_estatisticas()
            dados = self.db.df.copy()
            arquivo = f"output/Relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            
            estatisticas = {
                'total': stats['total_registros'],
                'em_servico': stats['em_servico'],
                'finalizados': stats['finalizados'],
                'tempo_medio': stats['tempo_medio'],
                'placas_unicas': stats['placas_unicas']
            }
            
            sucesso, resultado = gerar_relatorio_word(dados, estatisticas, arquivo)
            dialog.destroy()
            
            if sucesso:
                messagebox.showinfo("Relatório Word", f"Relatório Word salvo em:\n{resultado}")
            else:
                messagebox.showerror("Erro", resultado)
        
        # Botões
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="📄 Texto (.txt)", command=gerar_txt, 
                 width=20, height=2, bg='#95a5a6', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        
        tk.Button(btn_frame, text="📕 PDF (.pdf)", command=gerar_pdf_relatorio, 
                 width=20, height=2, bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        
        tk.Button(btn_frame, text="📘 Word (.docx)", command=gerar_word_relatorio, 
                 width=20, height=2, bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
    
    
    def exportar_excel(self):
        """
        Exporta dados para Excel
        """
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"Exportacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if arquivo:
            try:
                self.db.df.to_excel(arquivo, index=False, sheet_name='Manutenções')
                messagebox.showinfo("Sucesso", f"Dados exportados para:\n{arquivo}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível exportar:\n{e}")
    
    
    def fechar_aplicacao(self):
        """
        Fecha aplicação com confirmação
        """
        resposta = messagebox.askyesnocancel(
            "Fechar Sistema",
            "Deseja salvar os dados antes de sair?"
        )
        
        if resposta is None:  # Cancelar
            return
        elif resposta:  # Sim
            self.db.salvar_dados()
        
        self.root.destroy()


def main():
    """
    Função principal
    """
    root = tk.Tk()
    app = SistemaManutencao(root)
    root.mainloop()


if __name__ == "__main__":
    main()
