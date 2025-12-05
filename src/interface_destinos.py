"""
Interface para Gestão de Destinos com botão X dinâmico
"""
import tkinter as tk
from tkinter import ttk, messagebox


class JanelaGerenciarDestinos(tk.Toplevel):
    """
    Janela para gerenciar destinos com botão X ao passar mouse
    """
    
    def __init__(self, parent, gerenciador_destinos, callback=None):
        super().__init__(parent)
        
        self.gerenciador = gerenciador_destinos
        self.callback = callback
        self.item_hover = None
        self.botao_x = None
        
        # Configura janela
        self.title("Gerenciar Destinos")
        self.geometry("600x500")
        self.resizable(True, True)
        
        # Centraliza janela
        self.transient(parent)
        self.grab_set()
        
        self.criar_interface()
        self.atualizar_lista()
    
    
    def criar_interface(self):
        """Cria interface da janela"""
        # Frame superior
        frame_acoes = ttk.Frame(self, padding="10")
        frame_acoes.pack(fill=tk.X)
        
        ttk.Label(
            frame_acoes,
            text="📍 Gestão de Destinos",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            frame_acoes,
            text="[+] Novo Destino",
            command=self.novo_destino
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_acoes,
            text="[Fechar]",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Frame lista com Canvas para botão X dinâmico
        frame_lista = ttk.Frame(self, padding="10")
        frame_lista.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame_lista,
            text="💡 Passe o mouse sobre um destino para ver o botão [X] de exclusão",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        ).pack(pady=(0, 10))
        
        # Canvas e Scrollbar
        self.canvas = tk.Canvas(frame_lista, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.canvas.yview)
        
        self.frame_destinos = ttk.Frame(self.canvas)
        self.frame_destinos.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.frame_destinos, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind scroll com mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    
    def _on_mousewheel(self, event):
        """Handler para scroll do mouse"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    
    def atualizar_lista(self):
        """Atualiza lista de destinos"""
        # Limpa frame
        for widget in self.frame_destinos.winfo_children():
            widget.destroy()
        
        df = self.gerenciador.df
        
        if df.empty:
            ttk.Label(
                self.frame_destinos,
                text="Nenhum destino cadastrado",
                font=('Arial', 10)
            ).pack(pady=20)
            return
        
        # Cria item para cada destino
        for idx, row in df.iterrows():
            self.criar_item_destino(idx, row)
    
    
    def criar_item_destino(self, indice, dados):
        """Cria item de destino com botão X dinâmico"""
        nome = dados.get('NOME_DESTINO', '')
        ativo = dados.get('ATIVO', True)
        
        # Frame do item
        frame_item = tk.Frame(
            self.frame_destinos,
            bg='#f8f9fa' if ativo else '#f8d7da',
            relief=tk.RAISED,
            borderwidth=1,
            height=50
        )
        frame_item.pack(fill=tk.X, padx=5, pady=2)
        frame_item.pack_propagate(False)
        
        # Label do destino
        label_destino = tk.Label(
            frame_item,
            text=f"📍 {nome}",
            font=('Arial', 11, 'bold' if ativo else 'normal'),
            bg='#f8f9fa' if ativo else '#f8d7da',
            anchor='w'
        )
        label_destino.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Status
        status_texto = "✅ ATIVO" if ativo else "❌ INATIVO"
        label_status = tk.Label(
            frame_item,
            text=status_texto,
            font=('Arial', 9),
            bg='#f8f9fa' if ativo else '#f8d7da',
            fg='green' if ativo else 'red'
        )
        label_status.pack(side=tk.RIGHT, padx=10)
        
        # Botão X (inicialmente escondido)
        btn_excluir = tk.Button(
            frame_item,
            text="❌",
            font=('Arial', 12),
            bg='#dc3545',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: self.excluir_destino(indice, nome)
        )
        
        # Binds para mostrar/esconder botão X
        def mostrar_x(event):
            btn_excluir.pack(side=tk.RIGHT, padx=5)
            frame_item.config(bg='#fff3cd')
            label_destino.config(bg='#fff3cd')
            label_status.config(bg='#fff3cd')
        
        def esconder_x(event):
            btn_excluir.pack_forget()
            cor = '#f8f9fa' if ativo else '#f8d7da'
            frame_item.config(bg=cor)
            label_destino.config(bg=cor)
            label_status.config(bg=cor)
        
        # Aplica binds em todos os widgets do frame
        for widget in [frame_item, label_destino, label_status]:
            widget.bind('<Enter>', mostrar_x)
            widget.bind('<Leave>', esconder_x)
    
    
    def novo_destino(self):
        """Adiciona novo destino"""
        dialog = tk.Toplevel(self)
        dialog.title("Novo Destino")
        dialog.geometry("400x180")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centraliza
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 90
        dialog.geometry(f"400x180+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text="📍 Novo Destino",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 15))
        
        ttk.Label(
            frame,
            text="Nome do Destino:",
            font=('Arial', 10)
        ).pack(anchor=tk.W, pady=(0, 5))
        
        entry_nome = ttk.Entry(frame, width=40, font=('Arial', 10))
        entry_nome.pack(fill=tk.X, pady=(0, 15))
        entry_nome.focus()
        
        def salvar():
            nome = entry_nome.get().strip()
            if not nome:
                messagebox.showwarning("Aviso", "Digite o nome do destino!", parent=dialog)
                return
            
            sucesso, mensagem = self.gerenciador.adicionar_destino(nome)
            
            if sucesso:
                self.atualizar_lista()
                if self.callback:
                    self.callback()
                messagebox.showinfo("Sucesso", mensagem, parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror("Erro", mensagem, parent=dialog)
        
        entry_nome.bind('<Return>', lambda e: salvar())
        
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack()
        
        ttk.Button(
            frame_botoes,
            text="💾 Salvar",
            command=salvar,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="❌ Cancelar",
            command=dialog.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    
    def excluir_destino(self, indice, nome):
        """Exclui destino após confirmação"""
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o destino:\n\n'{nome}'?\n\nEsta ação não pode ser desfeita.",
            parent=self
        )
        
        if resposta:
            sucesso, mensagem = self.gerenciador.excluir_destino(indice)
            
            if sucesso:
                self.atualizar_lista()
                if self.callback:
                    self.callback()
                messagebox.showinfo("Sucesso", "Destino excluído com sucesso!", parent=self)
            else:
                messagebox.showerror("Erro", mensagem, parent=self)
    
    
    def destroy(self):
        """Sobrescreve destroy para limpar binds"""
        self.canvas.unbind_all("<MouseWheel>")
        super().destroy()
