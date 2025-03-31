import mysql.connector                  
from mysql.connector import Error       
from PySide6.QtWidgets import QMessageBox
import datetime
import hashlib

print("Carregando model.py correto!")   

class CardapioModel:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.total_mesas = self.carregar_total_mesas()
        self.conectar()

    def conectar(self):                 
        try:                            
            self.conn = mysql.connector.connect(  
                host='localhost',       
                user='root',            
                password='',            
                database='cardapio_app' 
            )
            self.cursor = self.conn.cursor()  
            print('Conectado ao MySQL!')      
        except Error as e:                   
            print(f'Erro ao conectar: {e}')   

    def validar_login(self, username, password):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute(
                "SELECT id, tipo FROM usuarios WHERE username = %s AND password = %s",
                (username, hashed_password)
            )
            result = self.cursor.fetchone()
            return result if result else None
        except Error as e:
            print(f"Erro ao validar login: {e}")
            return None

    def adicionar_item(self, nome, preco, imagem, categoria):  
        try:                           
           
            self.cursor.execute("SELECT id FROM categorias WHERE nome = %s", (categoria,))
            categoria_id = self.cursor.fetchone()  
            if not categoria_id:       
                raise Error(f"Categoria '{categoria}' não encontrada!")
            categoria_id = categoria_id[0]  

            query = "INSERT INTO itens (nome, preco, imagem, categoria_id) VALUES (%s, %s, %s, %s)"
            valores = (str(nome), float(preco), str(imagem) if imagem else None, categoria_id)  
            self.cursor.execute(query, valores)  
            self.conn.commit()          
            print(f"Item adicionado: {nome} na categoria {categoria}")  
        except Error as e:           
            print(f"Erro ao adicionar item: {e}") 

    def listar_itens(self, termo_busca=None):
        try:
            if termo_busca:
                self.cursor.execute("""
                    SELECT i.id, i.nome, i.preco, c.nome AS categoria, i.imagem 
                    FROM itens i
                    LEFT JOIN categorias c ON i.categoria_id = c.id
                    WHERE i.nome LIKE %s
                """, (f"%{termo_busca}%",))
            else:
                self.cursor.execute("""
                    SELECT i.id, i.nome, i.preco, c.nome AS categoria, i.imagem 
                    FROM itens i
                    LEFT JOIN categorias c ON i.categoria_id = c.id
                """)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar itens: {e}")
            return []

    def remover_item(self, id):
        try:
            
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM pedidos 
                WHERE item_id = %s
            """, (id,))
            pedidos_count = self.cursor.fetchone()[0]
            if pedidos_count > 0:
                raise Error("Item não pode ser removido porque possui pedidos no histórico.")
            
            
            query = "DELETE FROM itens WHERE id = %s"
            self.cursor.execute(query, (id,))
            self.conn.commit()
            print(f"Item ID {id} removido")
            return True
        except Error as e:
            print(f"Erro ao remover item: {e}")
            return False

    def atualizar_item(self, id, nome, preco, imagem, categoria):  
        try:                            
            
            self.cursor.execute("SELECT id FROM categorias WHERE nome = %s", (categoria,))
            categoria_id = self.cursor.fetchone()  
            if not categoria_id:        
                raise Error(f"Categoria '{categoria}' não encontrada!")
            categoria_id = categoria_id[0]  

            query = "UPDATE itens SET nome = %s, preco = %s, imagem = %s, categoria_id = %s WHERE id = %s"
            valores = (str(nome), float(preco), str(imagem) if imagem else None, categoria_id, id)
            self.cursor.execute(query, valores)  
            self.conn.commit()          
            print(f"Item ID {id} atualizado: {nome}, {preco}, {imagem}, Categoria: {categoria}")
        except Error as e:            
            print(f"Erro ao atualizar item: {e}")

    def adicionar_pedido(self, cliente_id, item_id, quantidade, mesa, forma_pagamento):  
        try:                            
            query = "INSERT INTO pedidos (cliente_id, item_id, quantidade, mesa, forma_pagamento) VALUES (%s, %s, %s, %s, %s)"
            valores = (cliente_id, item_id, quantidade, mesa, forma_pagamento)  
            self.cursor.execute(query, valores)  
            self.conn.commit()          
            print(f"Pedido adicionado: Cliente {cliente_id}, Item {item_id}, Mesa {mesa}, Pagamento {forma_pagamento}")
        except Error as e:            
            print(f"Erro ao adicionar pedido: {e}")

    def cadastrar_usuario(self, nome, cpf, email, username, password, tipo):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute(
                "SELECT id FROM usuarios WHERE username = %s OR cpf = %s OR email = %s",
                (username, cpf, email)
            )
            if self.cursor.fetchone():
                self.cursor.execute("SELECT username, cpf, email FROM usuarios WHERE username = %s OR cpf = %s OR email = %s", (username, cpf, email))
                existente = self.cursor.fetchone()
                if existente[0] == username:
                    return False, "Este username já está em uso!"
                elif existente[1] == cpf:
                    return False, "Este CPF já está cadastrado!"
                else:
                    return False, "Este email já está em uso!"
            query = "INSERT INTO usuarios (nome, cpf, email, username, password, tipo) VALUES (%s, %s, %s, %s, %s, %s)"
            valores = (nome, cpf, email, username, hashed_password, tipo)
            self.cursor.execute(query, valores)
            self.conn.commit()
            return True, "Usuário cadastrado com sucesso!"
        except Error as e:
            print(f"Erro ao cadastrar usuário: {e}")
            return False, f"Erro ao cadastrar: {e}"  

    def carregar_total_mesas(self):
        try:
            self.conectar()
            self.cursor.execute("SELECT total_mesas FROM configuracoes WHERE id = 1")
            result = self.cursor.fetchone()
            return result[0] if result else 20
        except Error as e:
            print(f"Erro ao carregar total de mesas: {e}")
            return 20

    def salvar_total_mesas(self, total_mesas):
        try:
            self.cursor.execute("UPDATE configuracoes SET total_mesas = %s WHERE id = 1", (total_mesas,))
            if self.cursor.rowcount == 0:
                self.cursor.execute("INSERT INTO configuracoes (id, total_mesas) VALUES (1, %s)", (total_mesas,))
            self.conn.commit()
            self.total_mesas = total_mesas
            print(f"Total de mesas atualizado: {total_mesas}")
        except Error as e:
            print(f"Erro ao salvar total de mesas: {e}")

    def listar_pedidos(self):                     
        try:                            
            self.cursor.execute("""
                SELECT p.id, u.nome AS cliente, i.nome AS item, p.quantidade, p.mesa, 
                       p.forma_pagamento, COALESCE(p.status, 'Pendente') AS status
                FROM pedidos p
                JOIN usuarios u ON p.cliente_id = u.id
                JOIN itens i ON p.item_id = i.id
            """)                        
            return self.cursor.fetchall()  
        except Error as e:            
            print(f"Erro ao listar pedidos: {e}")
            return []                 

    def listar_pedidos_cliente(self, cliente_id):
        try:
            self.cursor.execute("""
                SELECT p.id, i.nome AS item, p.quantidade, i.preco, p.mesa, 
                    p.forma_pagamento, COALESCE(p.status, 'Pendente') AS status
                FROM pedidos p
                JOIN itens i ON p.item_id = i.id
                WHERE p.cliente_id = %s
                ORDER BY p.id DESC
            """, (cliente_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar pedidos do cliente: {e}")
            return []

    def atualizar_status_pedido(self, pedido_id, novo_status):
        try:
            self.cursor.execute(
                "UPDATE pedidos SET status = %s WHERE id = %s",
                (novo_status, pedido_id)
            )
            self.conn.commit()
            print(f"Status do pedido {pedido_id} atualizado para: {novo_status}")
            return True
        except Error as e:
            print(f"Erro ao atualizar status: {e}")
            return False

    def listar_categorias(self):
        try:                            
            self.cursor.execute("SELECT nome FROM categorias ORDER BY nome")  
            categorias = [row[0] for row in self.cursor.fetchall()]  
            return categorias           
        except Error as e:            
            print(f"Erro ao listar categorias: {e}")
            return []                 

    def adicionar_categoria(self, nome):
        try:
            self.cursor.execute("INSERT INTO categorias (nome) VALUES (%s)", (nome,))
            self.conn.commit()
            print(f"Categoria adicionada: {nome}")
            return True  
        except Error as e:
            if "Duplicate entry" in str(e):
                print(f"Erro: Categoria '{nome}' já existe!")
                return False, "Categoria já existe!"
            print(f"Erro ao adicionar categoria: {e}")
            return False, str(e)

    def remover_categoria(self):
        item = self.lista_categorias.currentItem()
        if item:
            categoria = item.text()
            if self.model.remover_categoria(categoria):
                self.atualizar_lista_categorias()
                self.parent().atualizar_combo_categorias()  
                self.parent().atualizar_filtro_categorias()  
                self.parent().atualizar_lista()  
                QMessageBox.information(self, "Sucesso", "Categoria removida!")
            else:
                QMessageBox.warning(self, "Erro", "Categoria não pode ser removida: possui itens associados!")
        else:
            QMessageBox.warning(self, "Erro", "Selecione uma categoria para remover!")  

    def remover_categoria(self, nome):
        try:
            self.cursor.execute("SELECT id FROM categorias WHERE nome = %s", (nome,))
            categoria_id = self.cursor.fetchone()
            if not categoria_id:
                raise Error(f"Categoria '{nome}' não encontrada!")
            categoria_id = categoria_id[0]

            self.cursor.execute("SELECT COUNT(*) FROM itens WHERE categoria_id = %s", (categoria_id,))
            itens_count = self.cursor.fetchone()[0]
            if itens_count > 0:
                raise Error("Categoria não pode ser removida porque tem itens associados!")

            self.cursor.execute("DELETE FROM categorias WHERE id = %s", (categoria_id,))
            self.conn.commit()
            print(f"Categoria removida: {nome}")
            return True
        except Error as e:
            print(f"Erro ao remover categoria: {e}")
            return False
        



        
    
    def remover_pedido(self, pedido_id):
        try:
            self.cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
            self.conn.commit()
            print(f"Pedido ID {pedido_id} removido")
            return True
        except Error as e:
            print(f"Erro ao remover pedido: {e}")
            return False
    
    def listar_itens_por_categoria(self, categoria=None, termo_busca=None):
        try:
            query = """
                SELECT i.id, i.nome, i.preco, c.nome AS categoria, i.imagem 
                FROM itens i
                LEFT JOIN categorias c ON i.categoria_id = c.id
            """
            params = []
            conditions = []
            
            if categoria:
                conditions.append("c.nome = %s")
                params.append(categoria)
            if termo_busca:
                conditions.append("i.nome LIKE %s")
                params.append(f"%{termo_busca}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar itens por categoria: {e}")
            return []

    def limpar_historico_ao_fechar(self):
        try:
            
            self.cursor.execute("""
                UPDATE pedidos 
                SET status = 'Cancelado' 
                WHERE status IN ('Pendente', 'Preparando')
            """)
            
            
            self.cursor.execute("""
                DELETE FROM pedidos 
                WHERE status = 'Entregue'
            """)
            
            self.conn.commit()
            print("Histórico ajustado ao fechar: entregues removidos, pendentes/preparando cancelados.")
        except Error as e:
            print(f"Erro ao limpar histórico ao fechar: {e}")

    def listar_mesas_ocupadas(self):
        try:
            self.cursor.execute("""
                SELECT DISTINCT mesa 
                FROM pedidos 
                WHERE status IN ('Pendente', 'Preparando')
            """)
            return [row[0] for row in self.cursor.fetchall()]
        except Error as e:
            print(f"Erro ao listar mesas ocupadas: {e}")
            return []

    def listar_mesas_ocupadas_por_outros(self, cliente_id):
        try:
            self.cursor.execute("""
                SELECT DISTINCT mesa 
                FROM pedidos 
                WHERE status IN ('Pendente', 'Preparando') 
                AND cliente_id != %s
            """, (cliente_id,))
            return [row[0] for row in self.cursor.fetchall()]
        except Error as e:
            print(f"Erro ao listar mesas ocupadas por outros: {e}")
            return []

    def listar_mesas_ocupadas_por_cliente(self, cliente_id):
        try:
            self.cursor.execute("""
                SELECT DISTINCT mesa 
                FROM pedidos 
                WHERE status IN ('Pendente', 'Preparando') 
                AND cliente_id = %s
            """, (cliente_id,))
            return [row[0] for row in self.cursor.fetchall()]
        except Error as e:
            print(f"Erro ao listar mesas ocupadas pelo cliente: {e}")
            return []

    def cancelar_pedido(self, pedido_id, cliente_id):
        try:
            
            self.cursor.execute("""
                SELECT status FROM pedidos 
                WHERE id = %s AND cliente_id = %s
            """, (pedido_id, cliente_id))
            resultado = self.cursor.fetchone()
            if resultado and resultado[0] == "Pendente":
                self.cursor.execute("""
                    DELETE FROM pedidos 
                    WHERE id = %s AND cliente_id = %s
                """, (pedido_id, cliente_id))
                self.conn.commit()
                return True
            return False
        except Error as e:
            print(f"Erro ao cancelar pedido: {e}")
            return False

    def total_vendas_dia(self, data=None):
        try:
            query = """
                SELECT SUM(i.preco * p.quantidade)
                FROM pedidos p
                JOIN itens i ON p.item_id = i.id
                WHERE p.status = 'Entregue'
                AND DATE(p.data_pedido) = %s
            """
            data = data if data else datetime.date.today().isoformat()
            self.cursor.execute(query, (data,))
            total = self.cursor.fetchone()[0]
            print(f"Total vendas calculado para {data}: {total}")
            return total if total else 0.0
        except Error as e:
            print(f"Erro ao calcular total de vendas: {e}")
            return 0.0

    def verificar_pedidos_dia(self, data=None):
        try:
            
            self.cursor.execute("""
                SELECT p.id, i.nome, p.quantidade, i.preco, p.mesa, p.forma_pagamento, COALESCE(p.status, 'Pendente') AS status
                FROM pedidos p
                JOIN itens i ON p.item_id = i.id
            """)
            pedidos = self.cursor.fetchall()
            print(f"Todos os pedidos: {pedidos}")
            return pedidos
        except Error as e:
            print(f"Erro ao verificar pedidos: {e}")
            return []

    def itens_mais_pedidos(self, limite=3):
        try:
            self.cursor.execute("""
                SELECT i.nome, SUM(p.quantidade) AS total
                FROM pedidos p
                JOIN itens i ON p.item_id = i.id
                GROUP BY i.id, i.nome
                ORDER BY total DESC
                LIMIT %s
            """, (limite,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar itens mais pedidos: {e}")
            return []

    def limpar_historico_ao_fechar(self):
        try:
            
            self.cursor.execute("""
                DELETE FROM pedidos 
                WHERE status IN ('Pendente', 'Preparando')
            """)
            self.conn.commit()
            print("Histórico ajustado ao fechar: pendentes/preparando removidos.")
        except Error as e:
            print(f"Erro ao limpar histórico ao fechar: {e}")
    
    def pedidos_por_mesa(self, mesa):
        try:
            self.cursor.execute("""
                SELECT p.id, i.nome, p.quantidade, p.forma_pagamento, COALESCE(p.status, 'Pendente') AS status
                FROM pedidos p
                JOIN itens i ON p.item_id = i.id
                WHERE p.mesa = %s AND p.status IN ('Pendente', 'Preparando')
            """, (mesa,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar pedidos por mesa: {e}")
            return []
    
    def fechar(self):                   
        if self.conn and self.conn.is_connected():  
            self.cursor.close()         
            self.conn.close()           
            print("Conexão fechada.")   