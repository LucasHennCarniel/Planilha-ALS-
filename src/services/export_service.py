import os
import pandas as pd
from tkinter import messagebox

class ExportService:
    """Serviço responsável por exportações do sistema (Excel, etc)"""
    
    @staticmethod
    def exportar_excel(df, arquivo):
        """Exporta um DataFrame para Excel com formatação básica"""
        try:
            # Cria writer do Excel com formatação
            with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Manutenção')
                
                # Ajusta largura das colunas
                worksheet = writer.sheets['Manutenção']
                for i, col in enumerate(df.columns):
                    max_len = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    ) + 2
                    worksheet.column_dimensions[chr(65 + i)].width = min(max_len, 50)
            
            messagebox.showinfo("Sucesso", f"✅ Dados exportados para Excel:\n{arquivo}")
            os.startfile(arquivo)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar Excel: {e}")
            return False
