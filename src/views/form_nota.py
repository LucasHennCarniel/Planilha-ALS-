import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry


class FormularioNota(tk.Toplevel):
    """Formulário para adicionar/editar notas"""
    
    def __init__(self, parent, db, gerenciador_veiculos, nota=None, callback=None):
        super().__init__(parent)
        
        self.db = db
        self.gerenciador_veiculos = gerenciador_veiculos
        self.nota = nota
        self.callback = callback
        
        self.title("Nova Nota" if nota is None else "Editar Nota")
        self.geometry("600x400")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.criar_formulario()
        
        if nota is not None:
            self.preencher_dados(nota)
    
    
    def criar_formulario(self):
        """Cria campos do formulário"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text="Nova Nota" if self.nota is None else "Editar Nota",
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        self.campos = {}
        
        # Data Programada
        ttk.Label(main_frame, text="📅 Data Programada:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.campos['data_programada'] = ttk.Entry(main_frame, width=30)
        self.campos['data_programada'].grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.campos['data_programada'].insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        # Placa
        ttk.Label(main_frame, text="🚛 Placa:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.campos['placa'] = ttk.Combobox(
            main_frame,
            width=28,
            values=self.gerenciador_veiculos.obter_veiculos_ativos_formatado()
        )
        self.campos['placa'].grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Status
        ttk.Label(main_frame, text="📊 Status:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.campos['status'] = ttk.Combobox(
            main_frame,
            width=28,
            values=['PENDENTE', 'PROGRAMADO', 'EM ANDAMENTO', 'CONCLUÍDO', 'CANCELADO'],
            state='readonly'
        )
        self.campos['status'].grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.campos['status'].set('PENDENTE')
        
        # Observação
        ttk.Label(main_frame, text="📝 Observação:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        frame_obs = ttk.Frame(main_frame)
        frame_obs.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.campos['observacao'] = tk.Text(frame_obs, height=8, width=40, font=('Arial', 10))
        self.campos['observacao'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_obs = ttk.Scrollbar(frame_obs, command=self.campos['observacao'].yview)
        scroll_obs.pack(side=tk.RIGHT, fill=tk.Y)
        self.campos['observacao'].config(yscrollcommand=scroll_obs.set)
        
        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(frame_botoes, text="💾 Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="❌ Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    
    def preencher_dados(self, nota):
        """Preenche formulário com dados da nota"""
        self.campos['data_programada'].delete(0, tk.END)
        self.campos['data_programada'].insert(0, nota['data_programada'])
        
        self.campos['placa'].set(nota['placa'])
        
        if nota['status']:
            self.campos['status'].set(nota['status'])
        
        if nota['observacao']:
            self.campos['observacao'].delete('1.0', tk.END)
            self.campos['observacao'].insert('1.0', nota['observacao'])
    
    
    def salvar(self):
        """Salva nota no banco"""
        data_prog = self.campos['data_programada'].get().strip()
        placa_full = self.campos['placa'].get().strip()
        status = self.campos['status'].get().strip()
        obs = self.campos['observacao'].get('1.0', tk.END).strip()
        
        # Validações
        if not data_prog:
            messagebox.showwarning("Atenção", "Informe a data programada!")
            return
        
        if not placa_full:
            messagebox.showwarning("Atenção", "Selecione uma placa!")
            return
        
        # Extrai placa do formato "TIPO - PLACA"
        placa = self.gerenciador_veiculos.extrair_placa_da_selecao(placa_full)
        
        try:
            from src.controllers.nota_controller import NotaController
            nota_controller = NotaController()
            sucesso, msg = nota_controller.salvar_nota(dados, id_nota=self.nota.get('id') if self.nota else None)
            if not sucesso:
                messagebox.showerror("Erro", msg)
                return
            messagebox.showinfo("Sucesso", "Nota salva com sucesso!")
            
            if self.callback:
                self.callback()
            
            self.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe uma nota para esta placa nesta data!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar nota: {e}")

