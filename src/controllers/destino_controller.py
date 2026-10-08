from src.models.destino_model import DestinoModel

class DestinoController:
    """
    Controlador para gerenciar lógicas de negócio dos Destinos
    """
    
    def __init__(self, model=None):
        self.model = model or DestinoModel()
        self.garantir_destinos_padrao()
        
    def garantir_destinos_padrao(self):
        """Garante que os destinos padrão existam no banco"""
        destinos_padrao = [
            'AGYLE', 'BOM SUCESSO', 'FARROUPILHA', 'FLORIÓPOLIS',
            'G&V', 'GARIBALDI', 'JOINVILLE/SC', 'NOVA TRENTO', 'SALTO VELOSO'
        ]
        
        for destino in destinos_padrao:
            # Tenta inserir de forma silenciosa. Se já existir, a exception ou a busca previne.
            if not self.model.obter_por_nome(destino):
                try:
                    self.model.inserir(destino)
                except Exception:
                    pass
    
    def adicionar_destino(self, nome):
        """
        Valida e adiciona um novo destino
        Retorna: (bool_sucesso, str_mensagem)
        """
        nome = nome.strip().upper()
        if not nome:
            return False, "O nome do destino não pode ser vazio."
            
        try:
            if self.model.obter_por_nome(nome):
                return False, "Destino já cadastrado!"
                
            self.model.inserir(nome)
            return True, "Destino cadastrado com sucesso!"
        except Exception as e:
            import logging
            logging.error(f"Erro no controller ao adicionar destino: {e}")
            return False, "Erro interno ao cadastrar destino."
            
    def atualizar_destino(self, id_destino, nome, ativo):
        """
        Valida e atualiza um destino
        Retorna: (bool_sucesso, str_mensagem)
        """
        nome = nome.strip().upper()
        if not nome:
            return False, "O nome do destino não pode ser vazio."
            
        try:
            sucesso = self.model.atualizar(id_destino, nome, ativo)
            if sucesso:
                return True, "Destino atualizado com sucesso!"
            return False, "Destino não encontrado."
        except Exception as e:
            import logging
            logging.error(f"Erro no controller ao atualizar destino: {e}")
            return False, "Erro interno ao atualizar destino."
            
    def excluir_destino(self, id_destino):
        """
        Desativa um destino logicamente
        Retorna: (bool_sucesso, str_mensagem)
        """
        try:
            sucesso = self.model.desativar(id_destino)
            if sucesso:
                return True, "Destino excluído com sucesso!"
            return False, "Destino não encontrado."
        except Exception as e:
            import logging
            logging.error(f"Erro no controller ao excluir destino: {e}")
            return False, "Erro interno ao excluir destino."
            
    def obter_destinos_ativos(self):
        """
        Retorna lista simplificada apenas com os nomes dos destinos ativos
        Usado para preencher Comboboxes na interface
        """
        destinos = self.model.obter_ativos()
        return [d['nome_destino'] for d in destinos]

    def obter_todos(self):
        """
        Retorna a lista completa de destinos (dicionários com id, nome, ativo)
        """
        return self.model.obter_todos()
