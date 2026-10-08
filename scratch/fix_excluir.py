import codecs
import re

with codecs.open('src/main.py', 'r', 'utf-8') as f:
    content = f.read()

# Fix excluir_registro
replacement_excluir = '''    def excluir_registro(self):
        """Exclui o registro selecionado."""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um registro para excluir")
            return
            
        if len(selecao) > 1:
            messagebox.showinfo("Dica", "Você selecionou múltiplos registros.\\n\\nUse o botão '🗑️ Excluir Múltiplos' para excluir vários de uma vez.")
            return
            
        item = self.tree.item(selecao[0])
        indice = item['tags'][0] if item['tags'] else None
        
        if indice is None:
            messagebox.showwarning("Aviso", "Não foi possível identificar o registro")
            return
            
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este registro?"
        )
        
        if resposta:
            try:
                # indice é o índice do dataframe Pandas
                registro = self.db.df.iloc[int(indice)].to_dict()
                id_registro = registro.get('ID')
                
                sucesso = self.db.excluir_registro(id_registro)
                if sucesso:
                    self.atualizar_tabela()
                    self.atualizar_estatisticas()
                    self.indice_selecionado = None
                    messagebox.showinfo("Sucesso", "Registro excluído com sucesso!")
                else:
                    messagebox.showerror("Erro", "Erro ao excluir no banco de dados")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {e}")'''

content = re.sub(
    r'    def excluir_registro\(self\):.*?messagebox\.showerror\("Erro", "Registro excluído mas não foi possível salvar no banco de dados"\)',
    replacement_excluir,
    content,
    flags=re.DOTALL
)

# Fix excluir_multiplos
replacement_multiplos = '''    def excluir_multiplos(self):
        """
        Exclui múltiplos registros selecionados
        """
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um ou mais registros para excluir\\n\\n💡 Dica: Use Ctrl+Clique ou Shift+Clique para selecionar múltiplos")
            return

        qtd = len(selecao)
        resposta = messagebox.askyesno(
            "Confirmar Exclusão Múltipla",
            f"Tem certeza que deseja excluir {qtd} registro(s) selecionado(s)?\\n\\n⚠️ Esta ação não pode ser desfeita!"
        )

        if resposta:
            excluidos = 0
            df_atual = self.db.df
            
            for item_id in selecao:
                item = self.tree.item(item_id)
                indice = item['tags'][0] if item['tags'] else None
                if indice is not None:
                    try:
                        registro = df_atual.iloc[int(indice)].to_dict()
                        id_registro = registro.get('ID')
                        if self.db.excluir_registro(id_registro):
                            excluidos += 1
                    except Exception as e:
                        print(f"Erro ao excluir {indice}: {e}")
                        
            self.atualizar_tabela()
            self.atualizar_estatisticas()
            self.indice_selecionado = None
            
            if excluidos > 0:
                messagebox.showinfo("Sucesso", f"{excluidos} registro(s) excluído(s) com sucesso!")
            else:
                messagebox.showwarning("Aviso", "Nenhum registro pôde ser excluído.")'''

content = re.sub(
    r'    def excluir_multiplos\(self\):.*?messagebox\.showwarning\("Aviso", "Nenhum registro foi excluído\."\)',
    replacement_multiplos,
    content,
    flags=re.DOTALL
)

with codecs.open('src/main.py', 'w', 'utf-8') as f:
    f.write(content)
