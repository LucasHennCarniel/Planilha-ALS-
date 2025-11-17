"""
Sistema de Controle de Manutenção de Frota - ALS
Aplicação standalone em Python com Tkinter, Pandas e Excel
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import os


class ExcelDatabase:
    """Gerenciador de base de dados Excel"""
    
    def __init__(self, filename='manutencao_frota.xlsx'):
        self.filename = filename
        self.initialize_database()
    
    def initialize_database(self):
        """Inicializa ou carrega a base de dados Excel"""
        if not os.path.exists(self.filename):
            # Criar planilha com estrutura inicial
            df = pd.DataFrame(columns=[
                'ID',
                'Data',
                'Veiculo',
                'Placa',
                'Tipo_Manutencao',
                'Descricao',
                'Custo',
                'KM_Atual',
                'Proximo_KM',
                'Status',
                'Responsavel',
                'Observacoes'
            ])
            df.to_excel(self.filename, index=False, sheet_name='Manutencoes')
            print(f"Base de dados criada: {self.filename}")
    
    def load_data(self):
        """Carrega dados do Excel"""
        try:
            df = pd.read_excel(self.filename, sheet_name='Manutencoes')
            return df
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
            return pd.DataFrame()
    
    def save_data(self, df):
        """Salva dados no Excel"""
        try:
            df.to_excel(self.filename, index=False, sheet_name='Manutencoes')
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar dados: {str(e)}")
            return False
    
    def add_record(self, record):
        """Adiciona novo registro"""
        df = self.load_data()
        
        # Gerar novo ID
        if len(df) == 0:
            new_id = 1
        else:
            new_id = df['ID'].max() + 1
        
        record['ID'] = new_id
        record['Data'] = datetime.now().strftime('%d/%m/%Y')
        
        # Adicionar registro
        new_row = pd.DataFrame([record])
        df = pd.concat([df, new_row], ignore_index=True)
        
        return self.save_data(df)
    
    def update_record(self, record_id, updated_data):
        """Atualiza registro existente"""
        df = self.load_data()
        
        if record_id in df['ID'].values:
            for key, value in updated_data.items():
                df.loc[df['ID'] == record_id, key] = value
            return self.save_data(df)
        else:
            messagebox.showerror("Erro", "Registro não encontrado!")
            return False
    
    def delete_record(self, record_id):
        """Remove registro"""
        df = self.load_data()
        df = df[df['ID'] != record_id]
        return self.save_data(df)
    
    def search_records(self, search_term, field='Veiculo'):
        """Busca registros"""
        df = self.load_data()
        if search_term:
            mask = df[field].astype(str).str.contains(search_term, case=False, na=False)
            return df[mask]
        return df


class MaintenanceApp:
    """Aplicação Principal de Controle de Manutenção"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Controle de Manutenção - ALS")
        self.root.geometry("1200x700")
        
        self.db = ExcelDatabase()
        self.selected_id = None
        
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        """Configura interface gráfica"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Controle de Manutenção de Frota", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=10)
        
        # Frame de formulário
        form_frame = ttk.LabelFrame(main_frame, text="Cadastro de Manutenção", padding="10")
        form_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Campos do formulário
        ttk.Label(form_frame, text="Veículo:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.veiculo_entry = ttk.Entry(form_frame, width=20)
        self.veiculo_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Placa:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.placa_entry = ttk.Entry(form_frame, width=15)
        self.placa_entry.grid(row=0, column=3, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Tipo:").grid(row=0, column=4, sticky=tk.W, pady=2)
        self.tipo_combo = ttk.Combobox(form_frame, width=18, state='readonly')
        self.tipo_combo['values'] = ('Preventiva', 'Corretiva', 'Preditiva', 'Revisão', 'Outros')
        self.tipo_combo.grid(row=0, column=5, sticky=tk.W, pady=2, padx=5)
        self.tipo_combo.current(0)
        
        ttk.Label(form_frame, text="Descrição:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.descricao_entry = ttk.Entry(form_frame, width=40)
        self.descricao_entry.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        ttk.Label(form_frame, text="Custo (R$):").grid(row=1, column=4, sticky=tk.W, pady=2)
        self.custo_entry = ttk.Entry(form_frame, width=15)
        self.custo_entry.grid(row=1, column=5, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(form_frame, text="KM Atual:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.km_atual_entry = ttk.Entry(form_frame, width=15)
        self.km_atual_entry.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Próximo KM:").grid(row=2, column=2, sticky=tk.W, pady=2)
        self.proximo_km_entry = ttk.Entry(form_frame, width=15)
        self.proximo_km_entry.grid(row=2, column=3, sticky=tk.W, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Status:").grid(row=2, column=4, sticky=tk.W, pady=2)
        self.status_combo = ttk.Combobox(form_frame, width=18, state='readonly')
        self.status_combo['values'] = ('Concluída', 'Pendente', 'Em Andamento', 'Agendada')
        self.status_combo.grid(row=2, column=5, sticky=tk.W, pady=2, padx=5)
        self.status_combo.current(0)
        
        ttk.Label(form_frame, text="Responsável:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.responsavel_entry = ttk.Entry(form_frame, width=30)
        self.responsavel_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        ttk.Label(form_frame, text="Observações:").grid(row=3, column=3, sticky=tk.W, pady=2)
        self.observacoes_entry = ttk.Entry(form_frame, width=30)
        self.observacoes_entry.grid(row=3, column=4, columnspan=2, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        # Botões de ação
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Adicionar", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Atualizar", command=self.update_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Excluir", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        
        # Frame de busca
        search_frame = ttk.LabelFrame(main_frame, text="Busca", padding="10")
        search_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(search_frame, text="Buscar por:").pack(side=tk.LEFT, padx=5)
        self.search_field = ttk.Combobox(search_frame, width=15, state='readonly')
        self.search_field['values'] = ('Veiculo', 'Placa', 'Tipo_Manutencao', 'Status')
        self.search_field.current(0)
        self.search_field.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Buscar", command=self.search_records).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Mostrar Todos", command=self.refresh_table).pack(side=tk.LEFT, padx=5)
        
        # Botões de relatório e exportação
        report_frame = ttk.Frame(search_frame)
        report_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(report_frame, text="Relatório", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(report_frame, text="Exportar", command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        # Frame de tabela
        table_frame = ttk.LabelFrame(main_frame, text="Registros de Manutenção", padding="10")
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Criar Treeview
        columns = ('ID', 'Data', 'Veiculo', 'Placa', 'Tipo', 'Descricao', 'Custo', 
                   'KM_Atual', 'Proximo_KM', 'Status', 'Responsavel')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        self.tree.heading('ID', text='ID')
        self.tree.heading('Data', text='Data')
        self.tree.heading('Veiculo', text='Veículo')
        self.tree.heading('Placa', text='Placa')
        self.tree.heading('Tipo', text='Tipo')
        self.tree.heading('Descricao', text='Descrição')
        self.tree.heading('Custo', text='Custo')
        self.tree.heading('KM_Atual', text='KM Atual')
        self.tree.heading('Proximo_KM', text='Próximo KM')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Responsavel', text='Responsável')
        
        # Configurar larguras
        self.tree.column('ID', width=40)
        self.tree.column('Data', width=80)
        self.tree.column('Veiculo', width=100)
        self.tree.column('Placa', width=80)
        self.tree.column('Tipo', width=100)
        self.tree.column('Descricao', width=150)
        self.tree.column('Custo', width=80)
        self.tree.column('KM_Atual', width=80)
        self.tree.column('Proximo_KM', width=90)
        self.tree.column('Status', width=90)
        self.tree.column('Responsavel', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind event para seleção
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Pronto", relief=tk.SUNKEN)
        self.status_label.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
    
    def clear_form(self):
        """Limpa formulário"""
        self.veiculo_entry.delete(0, tk.END)
        self.placa_entry.delete(0, tk.END)
        self.tipo_combo.current(0)
        self.descricao_entry.delete(0, tk.END)
        self.custo_entry.delete(0, tk.END)
        self.km_atual_entry.delete(0, tk.END)
        self.proximo_km_entry.delete(0, tk.END)
        self.status_combo.current(0)
        self.responsavel_entry.delete(0, tk.END)
        self.observacoes_entry.delete(0, tk.END)
        self.selected_id = None
        self.status_label.config(text="Formulário limpo")
    
    def add_record(self):
        """Adiciona novo registro"""
        if not self.veiculo_entry.get() or not self.placa_entry.get():
            messagebox.showwarning("Atenção", "Preencha os campos obrigatórios: Veículo e Placa")
            return
        
        record = {
            'Veiculo': self.veiculo_entry.get(),
            'Placa': self.placa_entry.get(),
            'Tipo_Manutencao': self.tipo_combo.get(),
            'Descricao': self.descricao_entry.get(),
            'Custo': self.custo_entry.get() or '0',
            'KM_Atual': self.km_atual_entry.get() or '0',
            'Proximo_KM': self.proximo_km_entry.get() or '0',
            'Status': self.status_combo.get(),
            'Responsavel': self.responsavel_entry.get(),
            'Observacoes': self.observacoes_entry.get()
        }
        
        if self.db.add_record(record):
            messagebox.showinfo("Sucesso", "Registro adicionado com sucesso!")
            self.clear_form()
            self.refresh_table()
            self.status_label.config(text="Registro adicionado")
    
    def update_record(self):
        """Atualiza registro selecionado"""
        if self.selected_id is None:
            messagebox.showwarning("Atenção", "Selecione um registro para atualizar")
            return
        
        if not self.veiculo_entry.get() or not self.placa_entry.get():
            messagebox.showwarning("Atenção", "Preencha os campos obrigatórios: Veículo e Placa")
            return
        
        updated_data = {
            'Veiculo': self.veiculo_entry.get(),
            'Placa': self.placa_entry.get(),
            'Tipo_Manutencao': self.tipo_combo.get(),
            'Descricao': self.descricao_entry.get(),
            'Custo': self.custo_entry.get() or '0',
            'KM_Atual': self.km_atual_entry.get() or '0',
            'Proximo_KM': self.proximo_km_entry.get() or '0',
            'Status': self.status_combo.get(),
            'Responsavel': self.responsavel_entry.get(),
            'Observacoes': self.observacoes_entry.get()
        }
        
        if self.db.update_record(self.selected_id, updated_data):
            messagebox.showinfo("Sucesso", "Registro atualizado com sucesso!")
            self.clear_form()
            self.refresh_table()
            self.status_label.config(text="Registro atualizado")
    
    def delete_record(self):
        """Remove registro selecionado"""
        if self.selected_id is None:
            messagebox.showwarning("Atenção", "Selecione um registro para excluir")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este registro?"):
            if self.db.delete_record(self.selected_id):
                messagebox.showinfo("Sucesso", "Registro excluído com sucesso!")
                self.clear_form()
                self.refresh_table()
                self.status_label.config(text="Registro excluído")
    
    def refresh_table(self):
        """Atualiza tabela com todos os registros"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Carregar dados
        df = self.db.load_data()
        
        # Preencher tabela
        for _, row in df.iterrows():
            self.tree.insert('', tk.END, values=(
                row['ID'],
                row['Data'],
                row['Veiculo'],
                row['Placa'],
                row['Tipo_Manutencao'],
                row['Descricao'],
                f"R$ {row['Custo']}" if row['Custo'] else 'R$ 0',
                row['KM_Atual'],
                row['Proximo_KM'],
                row['Status'],
                row['Responsavel']
            ))
        
        self.status_label.config(text=f"Total de registros: {len(df)}")
    
    def search_records(self):
        """Busca registros"""
        search_term = self.search_entry.get()
        field = self.search_field.get()
        
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar
        df = self.db.search_records(search_term, field)
        
        # Preencher tabela
        for _, row in df.iterrows():
            self.tree.insert('', tk.END, values=(
                row['ID'],
                row['Data'],
                row['Veiculo'],
                row['Placa'],
                row['Tipo_Manutencao'],
                row['Descricao'],
                f"R$ {row['Custo']}" if row['Custo'] else 'R$ 0',
                row['KM_Atual'],
                row['Proximo_KM'],
                row['Status'],
                row['Responsavel']
            ))
        
        self.status_label.config(text=f"Encontrados: {len(df)} registros")
    
    def on_select(self, event):
        """Evento de seleção na tabela"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            # Preencher formulário
            self.selected_id = values[0]
            self.veiculo_entry.delete(0, tk.END)
            self.veiculo_entry.insert(0, values[2])
            self.placa_entry.delete(0, tk.END)
            self.placa_entry.insert(0, values[3])
            self.tipo_combo.set(values[4])
            self.descricao_entry.delete(0, tk.END)
            self.descricao_entry.insert(0, values[5])
            
            # Limpar "R$ " do custo
            custo = str(values[6]).replace('R$ ', '')
            self.custo_entry.delete(0, tk.END)
            self.custo_entry.insert(0, custo)
            
            self.km_atual_entry.delete(0, tk.END)
            self.km_atual_entry.insert(0, values[7])
            self.proximo_km_entry.delete(0, tk.END)
            self.proximo_km_entry.insert(0, values[8])
            self.status_combo.set(values[9])
            self.responsavel_entry.delete(0, tk.END)
            self.responsavel_entry.insert(0, values[10])
            
            # Carregar observações
            df = self.db.load_data()
            obs = df[df['ID'] == self.selected_id]['Observacoes'].values
            if len(obs) > 0:
                self.observacoes_entry.delete(0, tk.END)
                self.observacoes_entry.insert(0, obs[0] if pd.notna(obs[0]) else '')
            
            self.status_label.config(text=f"Registro selecionado: ID {self.selected_id}")
    
    def generate_report(self):
        """Gera relatório"""
        df = self.db.load_data()
        
        if len(df) == 0:
            messagebox.showinfo("Relatório", "Nenhum registro encontrado!")
            return
        
        # Estatísticas
        total_registros = len(df)
        total_custo = df['Custo'].astype(float).sum()
        
        # Contar por status
        status_counts = df['Status'].value_counts().to_dict()
        
        # Contar por tipo
        tipo_counts = df['Tipo_Manutencao'].value_counts().to_dict()
        
        # Montar mensagem
        report = f"=== RELATÓRIO DE MANUTENÇÕES ===\n\n"
        report += f"Total de Registros: {total_registros}\n"
        report += f"Custo Total: R$ {total_custo:.2f}\n\n"
        
        report += "Por Status:\n"
        for status, count in status_counts.items():
            report += f"  - {status}: {count}\n"
        
        report += "\nPor Tipo de Manutenção:\n"
        for tipo, count in tipo_counts.items():
            report += f"  - {tipo}: {count}\n"
        
        messagebox.showinfo("Relatório de Manutenções", report)
        self.status_label.config(text="Relatório gerado")
    
    def export_data(self):
        """Exporta dados para novo arquivo"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Exportar Dados"
        )
        
        if filename:
            df = self.db.load_data()
            try:
                df.to_excel(filename, index=False, sheet_name='Manutencoes')
                messagebox.showinfo("Sucesso", f"Dados exportados para: {filename}")
                self.status_label.config(text=f"Dados exportados")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")


def main():
    """Função principal"""
    root = tk.Tk()
    app = MaintenanceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
