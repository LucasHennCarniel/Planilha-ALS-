import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from src.utils import validar_numero, limpar_texto, formatar_data_br

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
        
        # Seletor de Veículo Cadastrado COM BUSCA
        ttk.Label(
            main_frame,
            text="🚛 Buscar Veículo:",
            font=('Arial', 10, 'bold')
        ).grid(row=row, column=0, sticky=tk.W, pady=5)
        
        frame_veiculo = ttk.Frame(main_frame)
        frame_veiculo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Entry com autocomplete (substitui Combobox readonly)
        self.entry_busca_veiculo = ttk.Entry(frame_veiculo, width=35, font=('Arial', 10))
        self.entry_busca_veiculo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Listbox flutuante para resultados
        self.frame_resultados = tk.Frame(main_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        self.listbox_veiculos = tk.Listbox(
            self.frame_resultados,
            height=6,
            font=('Arial', 9),
            activestyle='dotbox',
            relief=tk.FLAT
        )
        self.listbox_veiculos.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para listbox
        scroll_listbox = ttk.Scrollbar(self.frame_resultados, orient=tk.VERTICAL, command=self.listbox_veiculos.yview)
        scroll_listbox.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_veiculos.config(yscrollcommand=scroll_listbox.set)
        
        # Variável para controlar seleção
        self.veiculo_selecionado = None
        self.lista_veiculos_completa = []
        
        # Binds para autocomplete
        self.entry_busca_veiculo.bind('<KeyRelease>', self.filtrar_veiculos)
        self.entry_busca_veiculo.bind('<FocusIn>', lambda e: self.mostrar_resultados())
        self.entry_busca_veiculo.bind('<FocusOut>', lambda e: self.root.after(200, self.esconder_resultados))
        self.entry_busca_veiculo.bind('<Down>', lambda e: self.listbox_veiculos.focus_set())
        self.listbox_veiculos.bind('<Return>', lambda e: self.selecionar_veiculo_lista())
        self.listbox_veiculos.bind('<Double-Button-1>', lambda e: self.selecionar_veiculo_lista())
        self.listbox_veiculos.bind('<Up>', lambda e: self.navegar_lista('up'))
        self.listbox_veiculos.bind('<Down>', lambda e: self.navegar_lista('down'))
        
        # Carrega lista inicial
        self.atualizar_lista_veiculos()
        
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
            ('STATUS', 'Status:', 'combo', ['EM TRÂNSITO', 'EM SERVIÇO', 'FINALIZADO']),
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
                # Frame especial para destino com botão [+] e [X]
                frame_destino = ttk.Frame(main_frame)
                frame_destino.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                
                widget = ttk.Combobox(
                    frame_destino,
                    width=32,
                    values=self.gerenciador_destinos.obter_destinos_ativos()
                )
                widget.pack(side=tk.LEFT)
                
                ttk.Button(
                    frame_destino,
                    text="[+]",
                    width=3,
                    command=self.adicionar_novo_destino
                ).pack(side=tk.LEFT, padx=(5, 0))
                
                ttk.Button(
                    frame_destino,
                    text="[X]",
                    width=3,
                    command=self.excluir_destino_selecionado
                ).pack(side=tk.LEFT, padx=(2, 0))
                
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
        
        # Adiciona máscara automática para campos de data
        for campo in ['DATA', 'DATA ENTRADA', 'DATA SAÍDA']:
            if campo in self.campos:
                self.campos[campo].bind('<KeyRelease>', self.mascara_data)

    def mascara_data(self, event):
        widget = event.widget
        valor = widget.get().replace('/', '')
        novo = ''
        for i, c in enumerate(valor):
            if i == 2 or i == 4:
                novo += '/'
            novo += c
        # Limita a 10 caracteres (DD/MM/AAAA)
        novo = novo[:10]
        widget.delete(0, tk.END)
        widget.insert(0, novo)
    
    
    def ao_selecionar_veiculo(self, event=None):
        """
        Quando um veículo cadastrado é selecionado, preenche dados automaticamente
        """
        # Para compatibilidade com busca antiga
        if hasattr(self, 'combo_veiculo_cadastrado'):
            selecao = self.combo_veiculo_cadastrado.get()
        else:
            # Nova busca com entry
            if not self.veiculo_selecionado:
                return
            selecao = self.veiculo_selecionado
        
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
    
    
    def atualizar_lista_veiculos(self):
        """Atualiza lista completa de veículos no formato PLACA - TIPO"""
        veiculos = self.gerenciador_veiculos.obter_veiculos_ativos_formatado()
        self.lista_veiculos_completa = veiculos
        self.listbox_veiculos.delete(0, tk.END)
        for veiculo in veiculos:
            self.listbox_veiculos.insert(tk.END, veiculo)
    
    
    def filtrar_veiculos(self, event=None):
        """Filtra veículos conforme digitação"""
        termo_busca = self.entry_busca_veiculo.get().upper()
        
        # Limpa listbox
        self.listbox_veiculos.delete(0, tk.END)
        
        if not termo_busca:
            # Mostra todos
            for veiculo in self.lista_veiculos_completa:
                self.listbox_veiculos.insert(tk.END, veiculo)
        else:
            # Filtra por placa ou tipo
            for veiculo in self.lista_veiculos_completa:
                if termo_busca in veiculo.upper():
                    self.listbox_veiculos.insert(tk.END, veiculo)
        
        # Mostra resultados
        if self.listbox_veiculos.size() > 0:
            self.mostrar_resultados()
    
    
    def mostrar_resultados(self):
        """Mostra listbox de resultados"""
        if self.listbox_veiculos.size() > 0:
            self.frame_resultados.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
    
    
    def esconder_resultados(self):
        """Esconde listbox de resultados"""
        self.frame_resultados.grid_forget()
    
    
    def selecionar_veiculo_lista(self):
        """Seleciona veículo da listbox e preenche campos automaticamente"""
        selecao = self.listbox_veiculos.curselection()
        if selecao:
            veiculo_texto = self.listbox_veiculos.get(selecao[0])
            self.entry_busca_veiculo.delete(0, tk.END)
            self.entry_busca_veiculo.insert(0, veiculo_texto)
            self.veiculo_selecionado = veiculo_texto
            self.esconder_resultados()
            
            # Extrai placa do texto selecionado (formato: PLACA - TIPO - DESCRIÇÃO)
            placa = self.gerenciador_veiculos.extrair_placa_da_selecao(veiculo_texto)
            
            # Busca dados completos do veículo
            veiculo = self.gerenciador_veiculos.obter_veiculo_por_placa(placa)
            
            if veiculo:
                # Preenche PLACA automaticamente
                self.campos['PLACA'].config(state='normal')
                self.campos['PLACA'].delete(0, tk.END)
                self.campos['PLACA'].insert(0, veiculo['PLACA'])
                self.campos['PLACA'].config(state='readonly')
                
                # Preenche TIPO automaticamente
                self.campos['VEÍCULO'].config(state='normal')
                self.campos['VEÍCULO'].delete(0, tk.END)
                self.campos['VEÍCULO'].insert(0, veiculo['TIPO_VEICULO'])
                self.campos['VEÍCULO'].config(state='readonly')
                
                # Preenche KM com última KM registrada
                self.campos['KM'].delete(0, tk.END)
                ultima_km = veiculo.get('ULTIMA_KM', 0)
                self.campos['KM'].insert(0, str(ultima_km))
                
                # Foca no campo DATA para continuar preenchimento
                self.campos['DATA'].focus()
    
    
    def navegar_lista(self, direcao):
        """Navega na listbox com teclado"""
        selecao_atual = self.listbox_veiculos.curselection()
        
        if not selecao_atual:
            self.listbox_veiculos.selection_set(0)
            return
        
        indice = selecao_atual[0]
        
        if direcao == 'up' and indice > 0:
            self.listbox_veiculos.selection_clear(indice)
            self.listbox_veiculos.selection_set(indice - 1)
            self.listbox_veiculos.see(indice - 1)
        elif direcao == 'down' and indice < self.listbox_veiculos.size() - 1:
            self.listbox_veiculos.selection_clear(indice)
            self.listbox_veiculos.selection_set(indice + 1)
            self.listbox_veiculos.see(indice + 1)
    
    
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
    
    
    def gerenciar_destinos(self):
        """
        Abre janela para gerenciar destinos com botão X dinâmico
        """
        from src.views.form_destinos import JanelaGerenciarDestinos
        
        def callback():
            # Atualiza lista de destinos no combobox
            self.campos['DESTINO PROGRAMADO']['values'] = self.gerenciador_destinos.obter_destinos_ativos()
        
        JanelaGerenciarDestinos(self, self.gerenciador_destinos, callback=callback)
    
    
    def excluir_destino_selecionado(self):
        """
        Exclui o destino atualmente selecionado no combo
        """
        combo_destino = self.campos.get('DESTINO PROGRAMADO')
        if not combo_destino:
            return
        
        destino_selecionado = combo_destino.get().strip()
        
        if not destino_selecionado:
            messagebox.showwarning(
                "Aviso",
                "Selecione um destino para excluir!",
                parent=self
            )
            return
        
        # Confirmação
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o destino:\n\n'{destino_selecionado}'?\n\n"
            "Esta ação não pode ser desfeita.",
            parent=self
        )
        
        if not resposta:
            return
        
        # Busca o ID do destino
        todos_destinos = self.gerenciador_destinos.obter_todos()
        destino_alvo = next((d for d in todos_destinos if d['nome_destino'] == destino_selecionado.upper()), None)
        
        if not destino_alvo:
            messagebox.showerror(
                "Erro",
                "Destino não encontrado no cadastro!",
                parent=self
            )
            return
        
        # Exclui o destino
        sucesso, mensagem = self.gerenciador_destinos.excluir_destino(destino_alvo['id'])
        
        if sucesso:
            messagebox.showinfo("Sucesso", "Destino excluído com sucesso!", parent=self)
            
            # Atualiza a lista no combo
            novos_destinos = self.gerenciador_destinos.obter_destinos_ativos()
            combo_destino['values'] = novos_destinos
            combo_destino.set('')  # Limpa seleção
        else:
            messagebox.showerror("Erro", mensagem, parent=self)
    
    
    def abrir_cadastro_veiculos(self):
        """
        Abre janela de cadastro de veículos
        """
        JanelaCadastroVeiculos(self, self.gerenciador_veiculos)
        
        # Atualiza lista após fechar cadastro
        if hasattr(self, 'combo_veiculo_cadastrado'):
            self.combo_veiculo_cadastrado['values'] = self.gerenciador_veiculos.obter_veiculos_ativos_formatado()
        else:
            # Nova busca com entry
            self.atualizar_lista_veiculos()
    
    
    def preencher_dados(self, registro):
        """
        Preenche formulário com dados existentes
        """
        for campo_nome, widget in self.campos.items():
            valor = registro.get(campo_nome, '')
            # Corrige valores NaN do pandas
            if valor is None or (isinstance(valor, float) and pd.isna(valor)):
                valor = ''
            if isinstance(widget, tk.Text):
                widget.delete('1.0', tk.END)
                widget.insert('1.0', str(valor) if valor else '')
            else:
                widget.config(state='normal')
                widget.delete(0, tk.END)
                # Formata datas
                if 'DATA' in campo_nome and valor:
                    valor = formatar_data_br(valor)
                widget.insert(0, str(valor) if valor else '')
                # Restaura readonly se necessário
                if widget.cget('state') == 'readonly' or campo_nome in ['PLACA', 'VEÍCULO']:
                    widget.config(state='readonly')
    
    
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
        
        # KM e N° OF são opcionais apenas quando status = "EM TRÂNSITO"
        status = dados.get('STATUS', '').upper()
        if status != 'EM TRÂNSITO':
            # Para outros status, KM e N° OF podem ser validados se necessário
            pass  # Mantém opcional para todos
        
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
        
        # IMPORTANTE: Pega o status selecionado pelo usuário
        status_selecionado = dados.get('STATUS', '').strip().upper()
        
        # Se o usuário selecionou um status manualmente, USA ELE
        # Só calcula automaticamente se não tiver status selecionado
        if status_selecionado:
            dados['STATUS'] = status_selecionado
        else:
            dados['STATUS'] = calcular_status(
                dados.get('DATA ENTRADA'),
                dados.get('DATA SAÍDA'),
                ''
            )
        
        # Atualiza KM do veículo no cadastro
        if dados.get('PLACA') and dados.get('KM'):
            try:
                km = float(dados.get('KM', 0))
                self.gerenciador_veiculos.atualizar_km(dados['PLACA'], km)
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

