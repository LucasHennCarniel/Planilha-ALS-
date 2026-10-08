import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class ModalRelatorio(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        self.title("Gerar Relatório")
        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 125
        self.geometry(f"400x250+{x}+{y}")
        
        tk.Label(self, text="Escolha o formato do relatório:", font=('Arial', 12, 'bold')).pack(pady=20)
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="📄 Texto (.txt)", command=self.gerar_txt, 
                 width=20, height=2, bg='#95a5a6', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        
        tk.Button(btn_frame, text="📕 PDF (.pdf)", command=self.gerar_pdf, 
                 width=20, height=2, bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        
        tk.Button(btn_frame, text="📘 Word (.docx)", command=self.gerar_word, 
                 width=20, height=2, bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
                 
    def obter_estatisticas(self):
        stats = self.db.obter_estatisticas()
        return {
            'total': stats['total'],
            'em_servico': stats['em_servico'],
            'finalizados': stats['finalizados'],
            'tempo_medio': stats['tempo_medio'],
            'placas_unicas': 0 # not implemented yet natively in compat
        }

    def gerar_txt(self):
        stats = self.obter_estatisticas()
        relatorio = f"""
╔══════════════════════════════════════════╗
║       RELATÓRIO DE MANUTENÇÃO - ALS      ║
╚══════════════════════════════════════════╝

 ESTATÍSTICAS GERAIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total de Registros: {stats['total']}
Veículos em Serviço: {stats['em_servico']}
Manutenções Finalizadas: {stats['finalizados']}
Tempo Médio de Manutenção: {stats['tempo_medio']:.1f} dias

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        import os
        os.makedirs("output", exist_ok=True)
        arquivo = f"output/Relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        self.destroy()
        messagebox.showinfo("Relatório Gerado", f"Relatório salvo em:\n{arquivo}")

    def gerar_pdf(self):
        from src.utils import gerar_relatorio_pdf
        estatisticas = self.obter_estatisticas()
        arquivo = f"output/Relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        sucesso, resultado = gerar_relatorio_pdf(self.db.df.copy(), estatisticas, arquivo)
        self.destroy()
        
        if sucesso:
            messagebox.showinfo("Relatório PDF", f"Relatório PDF salvo em:\n{resultado}")
        else:
            messagebox.showerror("Erro", resultado)

    def gerar_word(self):
        from src.utils import gerar_relatorio_word
        estatisticas = self.obter_estatisticas()
        arquivo = f"output/Relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        sucesso, resultado = gerar_relatorio_word(self.db.df.copy(), estatisticas, arquivo)
        self.destroy()
        
        if sucesso:
            messagebox.showinfo("Relatório Word", f"Relatório Word salvo em:\n{resultado}")
        else:
            messagebox.showerror("Erro", resultado)
