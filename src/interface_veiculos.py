"""
Interface para Gestão de Cadastro de Veículos
"""
import tkinter as tk
from tkinter import ttk, messagebox


class JanelaCadastroVeiculos(tk.Toplevel):
    """
    Janela para gerenciar cadastro de veículos
    """
    
    def __init__(self, parent, gerenciador_veiculos):
        super().__init__(parent)
        
        self.gerenciador = gerenciador_veiculos
        
        # Configura janela
        self.title("Cadastro de Veículos")
        self.geometry("1000x600")
        self.resizable(True, True)
        
        # Centraliza janela
        self.transient(parent)
        self.grab_set()
        
        self.criar_interface()
        self.atualizar_tabela()
    
    
    def criar_interface(self):
        """
        Cria interface da janela
        """
        # Frame superior - Botões de ação
        frame_acoes = ttk.Frame(self, padding="10")
        frame_acoes.pack(fill=tk.X)
        
        ttk.Label(
            frame_acoes,
            text="📋 Gestão de Veículos da Frota",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            frame_acoes,
            text="[+] Novo Veículo",
            command=self.novo_veiculo
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_acoes,
            text="[Edit] Editar",
            command=self.editar_veiculo
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_acoes,
            text="[Save] Salvar Tudo",
            command=self.salvar_dados
        ).pack(side=tk.RIGHT, padx=5)
        
        # Frame pesquisa
        frame_pesquisa = ttk.Frame(self, padding="10")
        frame_pesquisa.pack(fill=tk.X)
        
        ttk.Label(frame_pesquisa, text="🔍 Pesquisar:").pack(side=tk.LEFT, padx=(0,5))
        
        self.entrada_pesquisa = ttk.Entry(frame_pesquisa, width=30)
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=5)
        self.entrada_pesquisa.bind('<KeyRelease>', lambda e: self.filtrar_veiculos())
        
        ttk.Button(
            frame_pesquisa,
            text="Limpar",
            command=self.limpar_pesquisa
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame estatísticas
        frame_stats = ttk.Frame(self, padding="10")
        frame_stats.pack(fill=tk.X)
        
        self.label_stats = ttk.Label(frame_stats, text="", font=('Arial', 9))
        self.label_stats.pack()
        
        # Frame tabela
        frame_tabela = ttk.Frame(self, padding="10")
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
        colunas = ['TIPO', 'PLACA', 'DESCRIÇÃO', 'ÚLTIMA KM', 'DATA CADASTRO', 'STATUS']
        
        self.tree['columns'] = colunas
        self.tree.column('#0', width=0, stretch=tk.NO)
        
        larguras = {
            'TIPO': 120,
            'PLACA': 100,
            'DESCRIÇÃO': 250,
            'ÚLTIMA KM': 100,
            'DATA CADASTRO': 120,
            'STATUS': 80
        }
        
        for col in colunas:
            self.tree.column(col, width=larguras.get(col, 100), anchor=tk.W)
            self.tree.heading(col, text=col, anchor=tk.W)
        
        self.tree.bind('<Double-1>', lambda e: self.editar_veiculo())
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Frame inferior - Info
        frame_info = ttk.Frame(self, padding="5")
        frame_info.pack(fill=tk.X)
        
        ttk.Label(
            frame_info,
            text="💡 Dica: Cadastre seus veículos aqui uma única vez. Ao criar manutenção, basta selecionar o veículo e os dados serão preenchidos automaticamente!",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        ).pack()
    
    
    def atualizar_tabela(self):
        """
        Atualiza dados na tabela
        """
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Popula tabela
        df = self.gerenciador.df
        
        if df.empty:
            self.label_stats.config(text="📊 Nenhum veículo cadastrado ainda")
            return
        
        for idx, row in df.iterrows():
            valores = [
                row.get('TIPO_VEICULO', ''),
                row.get('PLACA', ''),
                row.get('DESCRICAO', ''),
                row.get('ULTIMA_KM', '0'),
                row.get('DATA_CADASTRO', ''),
                'ATIVO' if row.get('ATIVO', False) else 'INATIVO'
            ]
            
            # Define cor baseada no status
            tag = 'ativo' if row.get('ATIVO', False) else 'inativo'
            
            self.tree.insert('', tk.END, values=valores, tags=(idx, tag))
        
        # Configura cores
        self.tree.tag_configure('ativo', background='#d1e7dd')
        self.tree.tag_configure('inativo', background='#f8d7da')
        
        # Atualiza estatísticas
        self.atualizar_estatisticas()
    
    
    def atualizar_estatisticas(self):
        """
        Atualiza estatísticas
        """
        stats = self.gerenciador.obter_estatisticas()
        
        texto = f"📊 Total: {stats['total']} | ✅ Ativos: {stats['ativos']} | ❌ Inativos: {stats['inativos']}"
        
        if stats['por_tipo']:
            texto += " | Por Tipo: "
            tipos_texto = [f"{tipo}: {qtd}" for tipo, qtd in stats['por_tipo'].items()]
            texto += ", ".join(tipos_texto)
        
        self.label_stats.config(text=texto)
    
    
    def novo_veiculo(self):
        """
        Abre formulário para novo veículo
        """
        FormularioVeiculo(self, self.gerenciador, callback=self.atualizar_tabela)
    
    
    def editar_veiculo(self):
        """
        Edita veículo selecionado
        """
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um veículo para editar")
            return
        
        item = self.tree.item(selecao[0])
        indice = item['tags'][0] if item['tags'] else None
        
        if indice is not None:
            veiculo = self.gerenciador.df.iloc[indice].to_dict()
            FormularioVeiculo(
                self,
                self.gerenciador,
                veiculo=veiculo,
                indice=indice,
                callback=self.atualizar_tabela
            )
    
    
    def salvar_dados(self):
        """
        Salva cadastro de veículos
        """
        if self.gerenciador.salvar_dados():
            messagebox.showinfo("Sucesso", "Cadastro de veículos salvo com sucesso!")
        else:
            messagebox.showerror("Erro", "Não foi possível salvar o cadastro")
        
    
    def filtrar_veiculos(self):
        """
        Filtra veículos conforme texto digitado na pesquisa
        """
        termo = self.entrada_pesquisa.get().upper().strip()
        
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Se não há termo, mostra todos
        df = self.gerenciador.df
        if not termo:
            self.atualizar_tabela()
            return
        
        # Filtra por placa, tipo ou descrição
        df_filtrado = df[
            df['PLACA'].str.upper().str.contains(termo, na=False) |
            df['TIPO_VEICULO'].str.upper().str.contains(termo, na=False) |
            df['DESCRICAO'].str.upper().str.contains(termo, na=False)
        ]
        
        if df_filtrado.empty:
            self.label_stats.config(text="❌ Nenhum veículo encontrado")
            return
        
        # Popula tabela filtrada
        for idx, row in df_filtrado.iterrows():
            valores = [
                row.get('TIPO_VEICULO', ''),
                row.get('PLACA', ''),
                row.get('DESCRICAO', ''),
                row.get('ULTIMA_KM', '0'),
                row.get('DATA_CADASTRO', ''),
                'ATIVO' if row.get('ATIVO', False) else 'INATIVO'
            ]
            
            tag = 'ativo' if row.get('ATIVO', False) else 'inativo'
            self.tree.insert('', tk.END, values=valores, tags=(idx, tag))
        
        # Atualiza estatísticas
        self.label_stats.config(
            text=f"🔍 {len(df_filtrado)} veículo(s) encontrado(s) de {len(df)} total"
        )
    
    
    def limpar_pesquisa(self):
        """
        Limpa o campo de pesquisa e mostra todos os veículos
        """
        self.entrada_pesquisa.delete(0, tk.END)
        self.atualizar_tabela()
        

class FormularioVeiculo(tk.Toplevel):
    """
    Formulário para adicionar/editar veículo
    """
    
    def __init__(self, parent, gerenciador, veiculo=None, indice=None, callback=None):
        super().__init__(parent)
        
        self.gerenciador = gerenciador
        self.veiculo = veiculo
        self.indice = indice
        self.callback = callback
        
        # Configura janela
        self.title("Novo Veículo" if veiculo is None else "Editar Veículo")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Centraliza janela
        self.transient(parent)
        self.grab_set()
        
        self.criar_formulario()
        
        # Se é edição, preenche dados
        if veiculo is not None:
            self.preencher_dados(veiculo)
    
    
    def criar_formulario(self):
        """
        Cria formulário
        """
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = "Cadastrar Novo Veículo" if self.veiculo is None else "Editar Veículo"
        ttk.Label(
            main_frame,
            text=titulo,
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Tipo de Veículo
        ttk.Label(main_frame, text="Tipo de Veículo:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.combo_tipo = ttk.Combobox(
            main_frame,
            width=38,
            values=['CAVALO', 'CARRETA 1', 'CARRETA 2', 'BUG 1', 'BUG 2', 'LS'],
            state='readonly'
        )
        self.combo_tipo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Placa
        ttk.Label(main_frame, text="Placa:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.entry_placa = ttk.Entry(main_frame, width=40)
        self.entry_placa.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Descrição
        ttk.Label(main_frame, text="Descrição:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.entry_descricao = ttk.Entry(main_frame, width=40)
        self.entry_descricao.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(
            main_frame,
            text="(Ex: Volvo FH 540, Scania R450, etc)",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        ).grid(row=4, column=1, sticky=tk.W, padx=5)
        
        # KM Inicial (só para novo veículo)
        if self.veiculo is None:
            ttk.Label(main_frame, text="KM Inicial:", font=('Arial', 10, 'bold')).grid(
                row=5, column=0, sticky=tk.W, pady=5
            )
            self.entry_km = ttk.Entry(main_frame, width=40)
            self.entry_km.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
            self.entry_km.insert(0, "0")
        
        # Status (só para edição)
        if self.veiculo is not None:
            ttk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(
                row=5, column=0, sticky=tk.W, pady=5
            )
            self.combo_status = ttk.Combobox(
                main_frame,
                width=38,
                values=['ATIVO', 'INATIVO'],
                state='readonly'
            )
            self.combo_status.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            frame_botoes,
            text="[Save] Salvar",
            command=self.salvar,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="[X] Cancelar",
            command=self.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    
    def preencher_dados(self, veiculo):
        """
        Preenche formulário com dados existentes
        """
        self.combo_tipo.set(veiculo.get('TIPO_VEICULO', ''))
        self.entry_placa.insert(0, veiculo.get('PLACA', ''))
        self.entry_descricao.insert(0, veiculo.get('DESCRICAO', ''))
        
        if hasattr(self, 'combo_status'):
            status = 'ATIVO' if veiculo.get('ATIVO', False) else 'INATIVO'
            self.combo_status.set(status)
    
    
    def salvar(self):
        """
        Salva veículo
        """
        # Valida campos
        tipo = self.combo_tipo.get()
        placa = self.entry_placa.get().strip()
        descricao = self.entry_descricao.get().strip()
        
        if not tipo:
            messagebox.showerror("Erro", "Selecione o tipo de veículo")
            return
        
        if not placa:
            messagebox.showerror("Erro", "Informe a placa do veículo")
            return
        
        # Novo veículo
        if self.veiculo is None:
            km_inicial = self.entry_km.get().strip()
            try:
                km_inicial = float(km_inicial) if km_inicial else 0
            except:
                km_inicial = 0
            
            sucesso, mensagem = self.gerenciador.adicionar_veiculo(
                tipo, placa, descricao, km_inicial
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", mensagem)
        
        # Editar veículo
        else:
            ativo = self.combo_status.get() == 'ATIVO'
            
            sucesso, mensagem = self.gerenciador.atualizar_veiculo(
                self.indice, tipo, placa, descricao, ativo
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", mensagem)
