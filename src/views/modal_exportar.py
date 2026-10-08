import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

class ModalExportar(tk.Toplevel):
    def __init__(self, parent, db, tree, export_service):
        super().__init__(parent)
        self.db = db
        self.tree = tree
        self.export_service = export_service
        
        self.title("Exportar Dados")
        self.geometry("450x350")
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 225
        y = (self.winfo_screenheight() // 2) - 175
        self.geometry(f"450x350+{x}+{y}")
        
        self.criar_interface()
        
    def criar_interface(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📤 Exportar Dados", font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        ttk.Label(frame, text="Escolha o formato de exportação:", font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 10))
        
        self.formato_var = tk.StringVar(value="excel")
        
        frame_formatos = ttk.Frame(frame)
        frame_formatos.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(frame_formatos, text="📊 Excel (.xlsx)", variable=self.formato_var, value="excel").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(frame_formatos, text="📄 PDF (.pdf)", variable=self.formato_var, value="pdf").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(frame_formatos, text="📝 Word (.docx)", variable=self.formato_var, value="word").pack(anchor=tk.W, pady=3)
        
        self.usar_filtros_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame, 
            text="Usar filtros atuais (exportar apenas dados visíveis)",
            variable=self.usar_filtros_var
        ).pack(anchor=tk.W, pady=15)
        
        qtd_total = len(self.db.df)
        qtd_visivel = len(self.tree.get_children())
        
        ttk.Label(frame, text=f"📋 Total: {qtd_total} registros | Visíveis: {qtd_visivel} registros", font=('Arial', 9)).pack(pady=5)
        
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(pady=20)
        
        ttk.Button(frame_botoes, text="Cancelar", command=self.destroy, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_botoes, text="Exportar", command=self.executar_exportacao, width=15, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        
    def executar_exportacao(self):
        formato = self.formato_var.get()
        usar_filtros = self.usar_filtros_var.get()
        self.destroy()
        
        if usar_filtros:
            import pandas as pd
            indices_visiveis = []
            for item in self.tree.get_children():
                try:
                    idx = int(self.tree.item(item)['tags'][0])
                    indices_visiveis.append(idx)
                except: pass
            
            if not indices_visiveis:
                messagebox.showwarning("Aviso", "Não há dados visíveis para exportar.")
                return
            df_exportar = self.db.df.loc[indices_visiveis].copy()
        else:
            df_exportar = self.db.df.copy()
            
        data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if formato == "excel":
            arquivo = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=f"Manutencoes_{data_atual}.xlsx", filetypes=[("Excel", "*.xlsx")])
            if arquivo:
                self.export_service.exportar_excel(df_exportar, arquivo)
                
        elif formato == "pdf":
            from src.utils import gerar_relatorio_pdf
            arquivo = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Manutencoes_{data_atual}.pdf", filetypes=[("PDF", "*.pdf")])
            if arquivo:
                stats = self.db.obter_estatisticas()
                estatisticas = {
                    'total': stats['total'],
                    'em_servico': stats['em_servico'],
                    'finalizados': stats['finalizados'],
                    'tempo_medio': stats['tempo_medio'],
                    'placas_unicas': 0
                }
                sucesso, res = gerar_relatorio_pdf(df_exportar, estatisticas, arquivo)
                if sucesso:
                    messagebox.showinfo("Sucesso", "Exportação concluída.")
                else:
                    messagebox.showerror("Erro", res)
                    
        elif formato == "word":
            from src.utils import gerar_relatorio_word
            arquivo = filedialog.asksaveasfilename(defaultextension=".docx", initialfile=f"Manutencoes_{data_atual}.docx", filetypes=[("Word", "*.docx")])
            if arquivo:
                stats = self.db.obter_estatisticas()
                estatisticas = {
                    'total': stats['total'],
                    'em_servico': stats['em_servico'],
                    'finalizados': stats['finalizados'],
                    'tempo_medio': stats['tempo_medio'],
                    'placas_unicas': 0
                }
                sucesso, res = gerar_relatorio_word(df_exportar, estatisticas, arquivo)
                if sucesso:
                    messagebox.showinfo("Sucesso", "Exportação concluída.")
                else:
                    messagebox.showerror("Erro", res)
