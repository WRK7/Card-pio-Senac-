from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QLabel, QListWidget, QMessageBox, 
                               QFileDialog, QSpinBox, QDialog, QListWidgetItem, QComboBox, 
                               QSizePolicy, QMenuBar, QMenu, QGridLayout,QScrollArea)
from PySide6.QtGui import QPixmap, QIcon, QFont, QDoubleValidator
from PySide6.QtCore import QSize, Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os
import shutil

class LoginView(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Login - Cardápio")

        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(30)
        self.layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Faça Login")
        self.label.setAlignment(Qt.AlignCenter)

        self.form_container = QWidget()
        self.form_container.setMaximumWidth(400)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setAlignment(Qt.AlignCenter)

        self.entrada_username = QLineEdit()
        self.entrada_username.setPlaceholderText("Usuário")
        self.entrada_username.setMinimumHeight(40)
        self.entrada_username.setMaximumWidth(350)
        self.entrada_password = QLineEdit()
        self.entrada_password.setPlaceholderText("Senha")
        self.entrada_password.setEchoMode(QLineEdit.Password)
        self.entrada_password.setMinimumHeight(40)
        self.entrada_password.setMaximumWidth(350)

        self.button_container = QWidget()
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(20)
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.botao_login = QPushButton("Entrar")
        self.botao_login.setMinimumHeight(45)
        self.botao_login.setMinimumWidth(150)
        self.button_registro_cliente = QPushButton("Crie seu cadastro")
        self.button_registro_cliente.setMinimumHeight(45)
        self.button_registro_cliente.setMinimumWidth(150)
        self.button_layout.addWidget(self.botao_login)
        self.button_layout.addWidget(self.button_registro_cliente)
        self.button_container.setLayout(self.button_layout)

        self.form_layout.addWidget(self.entrada_username)
        self.form_layout.addWidget(self.entrada_password)
        self.form_layout.addWidget(self.button_container)
        
        self.form_container.setLayout(self.form_layout)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.form_container)
        self.widget_central.setLayout(self.layout)

        self.botao_login.clicked.connect(self.fazer_login)
        self.button_registro_cliente.clicked.connect(self.cadastro_cliente)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2f3542;
                margin-bottom: 20px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4dabf7;
            }
            QPushButton {
                background-color: #4dabf7;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c0fc;
            }
            QPushButton:pressed {
                background-color: #339af0;
            }
        """)
        self.showMaximized()

    def fazer_login(self):
        username = self.entrada_username.text().strip()
        password = self.entrada_password.text().strip()
        result = self.model.validar_login(username, password)
        if result:
            user_id, tipo = result
            if tipo == "admin":
                self.admin_view = AdminView(self.model, user_id)  # Corrigido: passa user_id
                self.admin_view.show()
                self.close()
            elif tipo == "cliente":
                self.cliente_view = ClienteView(self.model, user_id)
                self.cliente_view.show()
                self.close()
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos!")

    def cadastro_cliente(self):
        cadastrar_cliente = CadastrarCliente(self.model, self)
        cadastrar_cliente.exec()

class AdminView(QMainWindow):
    def __init__(self, model, usuario_id, parent=None):
        super().__init__(parent)
        self.model = model
        self.usuario_id = usuario_id
        self.setWindowTitle("Admin - Cardápio")

        self.menu_bar = self.menuBar()
        self.menu_gerenciar = QMenu("☰ Gerenciar", self)
        self.menu_bar.addMenu(self.menu_gerenciar)
        self.menu_gerenciar.addAction("Gerenciar Mesas", self.gerenciar_mesas)
        self.menu_gerenciar.addAction("Gerenciar Categorias", self.gerenciar_categorias)
        self.menu_gerenciar.addAction("Cadastrar Admin", self.cadastrar_admin)
        self.menu_gerenciar.addAction("Ver Comanda", self.mostrar_comanda)
        self.menu_gerenciar.addAction("Ver Relatórios", self.mostrar_relatorios)
        self.menu_gerenciar.addAction("Atualizar Mesas", self.atualizar_mesas)
        self.menu_gerenciar.addAction("Voltar ao Login", self.voltar_login)

        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(30)

        self.title_label = QLabel("Gerenciar Cardápio")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.main_container = QWidget()
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(30)

        self.itens_container = QWidget()
        self.itens_layout = QVBoxLayout()
        self.itens_layout.setSpacing(20)

        self.top_container = QWidget()
        self.top_layout = QHBoxLayout()
        self.top_layout.setSpacing(30)

        self.form_container = QWidget()
        self.form_container.setMaximumWidth(400)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(15)
        self.filtro_categoria = QComboBox()
        self.filtro_categoria.setMinimumHeight(40)
        self.filtro_categoria.addItem("Todas")
        self.atualizar_filtro_categorias()
        self.filtro_categoria.currentTextChanged.connect(self.atualizar_lista)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar item...")
        self.search_bar.setMinimumHeight(40)
        self.search_bar.textChanged.connect(self.atualizar_lista)
        self.entrada_nome = QLineEdit()
        self.entrada_nome.setPlaceholderText("Nome do item")
        self.entrada_nome.setMinimumHeight(40)
        self.entrada_preco = QLineEdit()
        self.entrada_preco.setPlaceholderText("Preço (ex.: 12.50)")
        self.entrada_preco.setMinimumHeight(40)
        self.combo_categoria = QComboBox()
        self.combo_categoria.setMinimumHeight(40)
        self.atualizar_combo_categorias()
        self.botao_imagem = QPushButton("Selecionar Imagem")
        self.botao_imagem.setMinimumHeight(45)
        self.botao_imagem.setMinimumWidth(200)
        self.label_imagem = QLabel("Nenhuma imagem selecionada")
        self.botao_adicionar = QPushButton("Adicionar Item")
        self.botao_adicionar.setMinimumHeight(45)
        self.botao_adicionar.setMinimumWidth(200)

        self.form_layout.addWidget(QLabel("Filtrar por Categoria:"))
        self.form_layout.addWidget(self.filtro_categoria)
        self.form_layout.addWidget(self.search_bar)
        self.form_layout.addWidget(self.entrada_nome)
        self.form_layout.addWidget(self.entrada_preco)
        self.form_layout.addWidget(QLabel("Categoria:"))
        self.form_layout.addWidget(self.combo_categoria)
        self.form_layout.addWidget(self.botao_imagem)
        self.form_layout.addWidget(self.label_imagem)
        self.form_layout.addWidget(self.botao_adicionar)
        self.form_layout.addStretch()
        self.form_container.setLayout(self.form_layout)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout()
        self.lista_itens = QListWidget()
        self.lista_itens.setIconSize(QSize(200, 200))
        self.lista_itens.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list_layout.addWidget(self.lista_itens)
        self.list_container.setLayout(self.list_layout)

        self.top_layout.addWidget(self.form_container)
        self.top_layout.addWidget(self.list_container, 1)
        self.top_container.setLayout(self.top_layout)

        self.bottom_container = QWidget()
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setSpacing(20)
        self.botao_remover = QPushButton("Remover Selecionado")
        self.botao_remover.setMinimumHeight(45)
        self.botao_remover.setMinimumWidth(200)
        self.botao_editar = QPushButton("Editar Item")
        self.botao_editar.setMinimumHeight(45)
        self.botao_editar.setMinimumWidth(200)

        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.botao_remover)
        self.bottom_layout.addWidget(self.botao_editar)
        self.bottom_layout.addStretch()
        self.bottom_container.setLayout(self.bottom_layout)

        self.itens_layout.addWidget(self.top_container, 1)
        self.itens_layout.addWidget(self.bottom_container)
        self.itens_container.setLayout(self.itens_layout)

        self.mesas_container = QWidget()
        self.mesas_layout = QVBoxLayout()
        self.mesas_widget = MesasWidget(self.model, self)
        self.mesas_layout.addWidget(self.mesas_widget)
        self.mesas_container.setLayout(self.mesas_layout)

        self.main_layout.addWidget(self.itens_container, 2)
        self.main_layout.addWidget(self.mesas_container, 1)
        self.main_container.setLayout(self.main_layout)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.main_container, 1)
        self.widget_central.setLayout(self.layout)

        self.entrada_preco.setValidator(QDoubleValidator(0.0, 9999.99, 2))

        self.botao_imagem.clicked.connect(self.selecionar_imagem)
        self.botao_adicionar.clicked.connect(self.adicionar_item)
        self.botao_remover.clicked.connect(self.remover_item)
        self.botao_editar.clicked.connect(self.editar_item)

        self.imagem_path = None
        self.atualizar_lista()


        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.atualizar_lista)
        self.search_bar.textChanged.connect(self.iniciar_timer)


        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            QMenuBar { background-color: #4dabf7; color: white; font-size: 18px; font-weight: bold; padding: 5px; }
            QMenuBar::item { padding: 5px 15px; border-radius: 4px; }
            QMenuBar::item:selected { background-color: #74c0fc; }
            QMenu { background-color: #f5f6fa; border: 2px solid #dfe4ea; font-size: 16px; }
            QMenu::item { padding: 8px 25px; }
            QMenu::item:selected { background-color: #74c0fc; color: white; }
            QLabel { font-size: 20px; color: #2f3542; }
            QLineEdit, QComboBox { padding: 10px; border: 2px solid #dfe4ea; border-radius: 6px; font-size: 16px; background-color: white; }
            QLineEdit:focus, QComboBox:focus { border-color: #4dabf7; }
            QPushButton { background-color: #4dabf7; color: white; border-radius: 6px; padding: 12px; font-size: 16px; }
            QPushButton:hover { background-color: #74c0fc; }
            QListWidget { border: 2px solid #dfe4ea; border-radius: 6px; padding: 5px; background-color: white; }
            QListWidget::item { padding: 10px; font-size: 16px; color: #2f3542; }
            QListWidget::item:selected { background-color: #74c0fc; color: white; }
        """)
        self.showMaximized()



    def atualizar_mesas(self):
        self.mesas_widget.atualizar_mesas()

    def atualizar_lista(self):
        self.lista_itens.clear()
        categoria = self.filtro_categoria.currentText()
        termo_busca = self.search_bar.text().strip()
        
        print(f"Filtrando por categoria: {categoria}, busca: {termo_busca}")
        itens = self.model.listar_itens_por_categoria(termo_busca=termo_busca if categoria == "Todas" else None, categoria=categoria if categoria != "Todas" else None)
        print(f"Itens retornados: {itens}")
        
        if categoria == "Todas":
            categorias = sorted(set(item[3] for item in itens if item[3]))
            for cat in categorias:
                item_titulo = QListWidgetItem(f" {cat} ")
                item_titulo.setBackground(Qt.lightGray)
                item_titulo.setFont(QFont("Arial", 18, QFont.Bold))
                item_titulo.setTextAlignment(Qt.AlignCenter)
                item_titulo.setFlags(Qt.NoItemFlags)
                self.lista_itens.addItem(item_titulo)
                for id, nome, preco, categoria, imagem in itens:
                    if categoria == cat:
                        texto = f"{nome}  |  R${preco:.2f}  |  {imagem if imagem else 'Sem imagem'}"
                        item = QListWidgetItem(texto)
                        item.setData(Qt.UserRole, id)
                        if imagem:
                            caminho_imagem = os.path.join("imagens", imagem)
                            print(f"Tentando carregar imagem: {caminho_imagem}")
                            if os.path.exists(caminho_imagem):
                                pixmap = QPixmap(caminho_imagem).scaled(200, 200, Qt.KeepAspectRatio)
                                if not pixmap.isNull():
                                    item.setIcon(QIcon(pixmap))
                                else:
                                    print(f"Erro: Imagem {caminho_imagem} não pôde ser carregada!")
                            else:
                                print(f"Erro: Arquivo {caminho_imagem} não encontrado!")
                        self.lista_itens.addItem(item)
        else:
            for id, nome, preco, categoria, imagem in itens:
                texto = f"{nome}  |  R${preco:.2f}  |  {imagem if imagem else 'Sem imagem'}"
                item = QListWidgetItem(texto)
                item.setData(Qt.UserRole, id)
                if imagem:
                    caminho_imagem = os.path.join("imagens", imagem)
                    print(f"Tentando carregar imagem: {caminho_imagem}")
                    if os.path.exists(caminho_imagem):
                        pixmap = QPixmap(caminho_imagem).scaled(200, 200, Qt.KeepAspectRatio)
                        if not pixmap.isNull():
                            item.setIcon(QIcon(pixmap))
                        else:
                            print(f"Erro: Imagem {caminho_imagem} não pôde ser carregada!")
                    else:
                        print(f"Erro: Arquivo {caminho_imagem} não encontrado!")
                self.lista_itens.addItem(item)

    def selecionar_imagem(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "", "Imagens (*.png *.jpg *.jpeg)")
        if arquivo:
            nome_arquivo = os.path.basename(arquivo)
            destino = os.path.abspath(os.path.join("imagens", nome_arquivo))  # Caminho absoluto do destino
            os.makedirs("imagens", exist_ok=True)
            arquivo_absoluto = os.path.abspath(arquivo)  # Caminho absoluto do arquivo selecionado
            if arquivo_absoluto != destino:
                shutil.copy(arquivo_absoluto, destino)
                print(f"Imagem copiada para: {destino}")
            else:
                print(f"Imagem já está em: {destino}")
            self.imagem_path = nome_arquivo  # Salva só o nome do arquivo
            self.label_imagem.setText(f"Imagem: {nome_arquivo}")

    def adicionar_item(self):
        nome = self.entrada_nome.text()
        preco = self.entrada_preco.text()
        categoria = self.combo_categoria.currentText()
        try:
            preco = float(preco)
            if nome and preco >= 0 and categoria != "Sem categorias":
                self.model.adicionar_item(nome, preco, self.imagem_path, categoria)
                self.atualizar_lista()
                self.entrada_nome.clear()
                self.entrada_preco.clear()
                self.imagem_path = None
                self.label_imagem.setText("Nenhuma imagem selecionada")
                QMessageBox.information(self, "Sucesso", "Item adicionado com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Preencha todos os campos corretamente!")
        except ValueError:
            QMessageBox.warning(self, "Erro", "Preço deve ser um número válido!")

    def remover_item(self):
        item = self.lista_itens.currentItem()
        if item:
            id = item.data(Qt.UserRole)
            if self.model.remover_item(id):
                self.atualizar_lista()
                QMessageBox.information(self, "Sucesso", "Item removido com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Este item não pode ser removido: possui pedidos no histórico!")
        else:
            QMessageBox.warning(self, "Erro", "Selecione um item para remover!")

    def editar_item(self):
        item = self.lista_itens.currentItem()
        if item:
            id = item.data(Qt.UserRole)
            texto = item.text()
            dados = [parte.strip() for parte in texto.split(" | ")]
            nome_antigo = dados[0]
            preco_antigo = float(dados[1].replace("R$", "").strip())
            imagem_antiga = dados[2] if dados[2] != "Sem imagem" else None
            
            self.model.cursor.execute("SELECT c.nome FROM itens i LEFT JOIN categorias c ON i.categoria_id = c.id WHERE i.id = %s", (id,))
            categoria_antiga = self.model.cursor.fetchone()[0] or "Sem categoria"

            dialog = EditarItemDialog(self.model, id, nome_antigo, preco_antigo, categoria_antiga, imagem_antiga, self)
            if dialog.exec():
                self.atualizar_lista()
        else:
            QMessageBox.warning(self, "Erro", "Selecione um item para editar!")

    def voltar_login(self):
        self.login_view = LoginView(self.model)
        self.login_view.show()
        self.close()

    def gerenciar_mesas(self):
        dialog = GerenciarMesasDialog(self.model, self)
        dialog.exec()

    def cadastrar_admin(self):
        dialog = CadastrarAdmin(self.model, self)
        dialog.exec()

    def mostrar_comanda(self):
        dialog = ComandaDialog(self.model, self)
        dialog.exec()

    def gerenciar_categorias(self):
        dialog = GerenciarCategoriasDialog(self.model, self)
        if dialog.exec():
            self.atualizar_combo_categorias()
            self.atualizar_filtro_categorias()
            self.atualizar_lista()

    def atualizar_filtro_categorias(self):
        self.filtro_categoria.clear()
        self.filtro_categoria.addItem("Todas")
        categorias = self.model.listar_categorias()
        if categorias:
            self.filtro_categoria.addItems(categorias)

    def atualizar_combo_categorias(self):
        self.combo_categoria.clear()
        categorias = self.model.listar_categorias()
        if categorias:
            self.combo_categoria.addItems(categorias)
        else:
            self.combo_categoria.addItem("Sem categorias")

    def mostrar_relatorios(self):
        dialog = RelatoriosDialog(self.model, self)
        dialog.exec()


    def iniciar_timer(self):
        self.timer.start(300)  # 300ms de delay

class ClienteView(QMainWindow):
    def __init__(self, model, cliente_id):
        super().__init__()
        self.model = model
        self.cliente_id = cliente_id
        self.setWindowTitle("Cliente - Cardápio")

        self.menu_bar = self.menuBar()
        self.menu_opcoes = QMenu("☰ Opções", self)
        self.menu_bar.addMenu(self.menu_opcoes)
        self.menu_opcoes.addAction("Ver Histórico", self.mostrar_historico)
        self.menu_opcoes.addAction("Voltar ao Login", self.voltar_login)

        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(30)

        self.title_label = QLabel("Cardápio Disponível")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.filter_container = QWidget()
        self.filter_container.setMaximumWidth(600)
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setSpacing(15)
        self.filtro_categoria = QComboBox()
        self.filtro_categoria.setMinimumHeight(40)
        self.filtro_categoria.setMaximumWidth(300)
        self.filtro_categoria.addItem("Todas")
        self.atualizar_filtro_categorias()
        self.filtro_categoria.currentTextChanged.connect(self.atualizar_lista)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar item...")
        self.search_bar.setMinimumHeight(40)
        self.search_bar.setMaximumWidth(300)
        self.search_bar.textChanged.connect(self.atualizar_lista)
        self.filter_layout.addWidget(QLabel("Filtrar por Categoria:"))
        self.filter_layout.addWidget(self.filtro_categoria)
        self.filter_layout.addWidget(self.search_bar)
        self.filter_layout.addStretch()
        self.filter_container.setLayout(self.filter_layout)

        self.lista_itens = QListWidget()
        self.lista_itens.setIconSize(QSize(200, 200))
        self.lista_itens.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.order_container = QWidget()
        self.order_container.setMaximumWidth(600)
        self.order_layout = QHBoxLayout()
        self.order_layout.setSpacing(20)
        self.quantidade = QSpinBox()
        self.quantidade.setRange(1, 99)
        self.quantidade.setValue(1)
        self.quantidade.setMinimumHeight(40)
        self.quantidade.setMaximumWidth(100)
        self.botao_pedir = QPushButton("Fazer Pedido")
        self.botao_pedir.setMinimumHeight(45)
        self.botao_pedir.setMinimumWidth(200)
        self.order_layout.addStretch()
        self.order_layout.addWidget(QLabel("Quantidade:"))
        self.order_layout.addWidget(self.quantidade)
        self.order_layout.addWidget(self.botao_pedir)
        self.order_layout.addStretch()
        self.order_container.setLayout(self.order_layout)

        self.botao_pedir.clicked.connect(self.fazer_pedido)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.filter_container)
        self.layout.addWidget(self.lista_itens, 1)
        self.layout.addWidget(self.order_container)
        self.widget_central.setLayout(self.layout)

        self.atualizar_lista()

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            QMenuBar { background-color: #4dabf7; color: white; font-size: 18px; font-weight: bold; padding: 5px; }
            QMenuBar::item { padding: 5px 15px; border-radius: 4px; }
            QMenuBar::item:selected { background-color: #74c0fc; }
            QMenu { background-color: #f5f6fa; border: 2px solid #dfe4ea; font-size: 16px; }
            QMenu::item { padding: 8px 25px; }
            QMenu::item:selected { background-color: #74c0fc; color: white; }
            QLabel { font-size: 20px; color: #2f3542; }
            QComboBox, QLineEdit { padding: 10px; border: 2px solid #dfe4ea; border-radius: 6px; font-size: 16px; background-color: white; }
            QComboBox:focus, QLineEdit:focus { border-color: #4dabf7; }
            QSpinBox { padding: 10px; border: 2px solid #dfe4ea; border-radius: 6px; font-size: 16px; background-color: white; min-width: 80px; }
            QSpinBox:focus { border-color: #4dabf7; }
            QSpinBox::up-button, QSpinBox::down-button { width: 20px; background-color: #dfe4ea; border: none; border-radius: 3px; }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #74c0fc; }
            QPushButton { background-color: #4dabf7; color: white; border-radius: 6px; padding: 12px; font-size: 16px; }
            QPushButton:hover { background-color: #74c0fc; }
            QListWidget { border: 2px solid #dfe4ea; border-radius: 6px; padding: 5px; background-color: white; }
            QListWidget::item { padding: 10px; font-size: 16px; color: #2f3542; }
            QListWidget::item:selected { background-color: #74c0fc; color: white; }
        """)
        self.showMaximized()

    def voltar_login(self):
        self.login_view = LoginView(self.model)
        self.login_view.show()
        self.close()

    def atualizar_filtro_categorias(self):
        self.filtro_categoria.clear()
        self.filtro_categoria.addItem("Todas")
        categorias = self.model.listar_categorias()
        if categorias:
            self.filtro_categoria.addItems(categorias)

    def atualizar_lista(self):
        self.lista_itens.clear()
        categoria = self.filtro_categoria.currentText()
        termo_busca = self.search_bar.text().strip()
        
        print(f"Filtrando por categoria: {categoria}, busca: {termo_busca}")
        itens = self.model.listar_itens_por_categoria(termo_busca=termo_busca if categoria == "Todas" else None, categoria=categoria if categoria != "Todas" else None)
        print(f"Itens retornados: {itens}")
        
        if categoria == "Todas":
            categorias = sorted(set(item[3] for item in itens if item[3]))
            for cat in categorias:
                item_titulo = QListWidgetItem(f" {cat} ")
                item_titulo.setBackground(Qt.lightGray)
                item_titulo.setFont(QFont("Arial", 18, QFont.Bold))
                item_titulo.setTextAlignment(Qt.AlignCenter)
                item_titulo.setFlags(Qt.NoItemFlags)
                self.lista_itens.addItem(item_titulo)
                for id, nome, preco, categoria, imagem in itens:
                    if categoria == cat:
                        texto = f"{nome}  |  R${preco:.2f}  |  {imagem if imagem else 'Sem imagem'}"
                        item = QListWidgetItem(texto)
                        item.setData(Qt.UserRole, id)
                        if imagem:
                            caminho_imagem = os.path.join("imagens", imagem)
                            print(f"Tentando carregar imagem: {caminho_imagem}")
                            if os.path.exists(caminho_imagem):
                                pixmap = QPixmap(caminho_imagem).scaled(200, 200, Qt.KeepAspectRatio)
                                if not pixmap.isNull():
                                    item.setIcon(QIcon(pixmap))
                                else:
                                    print(f"Erro: Imagem {caminho_imagem} não pôde ser carregada!")
                            else:
                                print(f"Erro: Arquivo {caminho_imagem} não encontrado!")
                        self.lista_itens.addItem(item)
        else:
            for id, nome, preco, categoria, imagem in itens:
                texto = f"{nome}  |  R${preco:.2f}  |  {imagem if imagem else 'Sem imagem'}"
                item = QListWidgetItem(texto)
                item.setData(Qt.UserRole, id)
                if imagem:
                    caminho_imagem = os.path.join("imagens", imagem)
                    print(f"Tentando carregar imagem: {caminho_imagem}")
                    if os.path.exists(caminho_imagem):
                        pixmap = QPixmap(caminho_imagem).scaled(200, 200, Qt.KeepAspectRatio)
                        if not pixmap.isNull():
                            item.setIcon(QIcon(pixmap))
                        else:
                            print(f"Erro: Imagem {caminho_imagem} não pôde ser carregada!")
                    else:
                        print(f"Erro: Arquivo {caminho_imagem} não encontrado!")
                self.lista_itens.addItem(item)

    def fazer_pedido(self):
        item = self.lista_itens.currentItem()
        if item and not item.flags() & Qt.NoItemFlags:
            item_id = item.data(Qt.UserRole)
            quantidade = self.quantidade.value()
            dialog = ConfirmarPedidoDialog(self.model, self.cliente_id, item_id, quantidade, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Erro", "Selecione um item válido pra pedir!")

    def mostrar_historico(self):
        dialog = HistoricoDialog(self.model, self.cliente_id, self)
        dialog.exec()

class EditarItemDialog(QDialog):
    def __init__(self, model, item_id, nome_atual, preco_atual, categoria_atual, imagem_atual, parent=None):
        super().__init__(parent)
        self.model = model
        self.item_id = item_id
        self.setWindowTitle("Editar Item")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        self.container = QWidget()
        self.container.setMaximumWidth(400)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(15)

        self.entrada_nome = QLineEdit()
        self.entrada_nome.setText(nome_atual)
        self.entrada_nome.setMinimumHeight(40)
        self.entrada_preco = QLineEdit()
        self.entrada_preco.setText(str(preco_atual))
        self.entrada_preco.setMinimumHeight(40)
        self.combo_categoria = QComboBox()
        self.combo_categoria.setMinimumHeight(40)
        categorias = model.listar_categorias()
        if categorias:
            self.combo_categoria.addItems(categorias)
        self.combo_categoria.setCurrentText(categoria_atual)
        self.botao_imagem = QPushButton("Selecionar Nova Imagem")
        self.botao_imagem.setMinimumHeight(45)
        self.botao_imagem.setMinimumWidth(200)
        self.label_imagem = QLabel(imagem_atual if imagem_atual else "Sem imagem")
        self.botao_salvar = QPushButton("Salvar Alterações")
        self.botao_salvar.setMinimumHeight(45)
        self.botao_salvar.setMinimumWidth(200)

        self.form_layout.addWidget(QLabel("Nome:"))
        self.form_layout.addWidget(self.entrada_nome)
        self.form_layout.addWidget(QLabel("Preço:"))
        self.form_layout.addWidget(self.entrada_preco)
        self.form_layout.addWidget(QLabel("Categoria:"))
        self.form_layout.addWidget(self.combo_categoria)
        self.form_layout.addWidget(self.botao_imagem)
        self.form_layout.addWidget(self.label_imagem)
        self.form_layout.addWidget(self.botao_salvar)
        self.container.setLayout(self.form_layout)

        self.botao_imagem.clicked.connect(self.selecionar_imagem)
        self.botao_salvar.clicked.connect(self.salvar_alteracoes)

        self.layout.addWidget(self.container)
        self.layout.addStretch()
        self.setLayout(self.layout)

        self.imagem_path = imagem_atual

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                font-size: 16px;
                color: #2f3542;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 2px solid #dfe4ea;
                border-radius: 6px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #4dabf7;
            }
            QPushButton {
                background-color: #4dabf7;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #74c0fc;
            }
        """)

    def selecionar_imagem(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "", "Imagens (*.png *.jpg *.jpeg)")
        if arquivo:
            nome_arquivo = os.path.basename(arquivo)
            destino = os.path.abspath(os.path.join("imagens", nome_arquivo))  # Caminho absoluto do destino
            os.makedirs("imagens", exist_ok=True)
            arquivo_absoluto = os.path.abspath(arquivo)  # Caminho absoluto do arquivo selecionado
            if arquivo_absoluto != destino:
                shutil.copy(arquivo_absoluto, destino)
                print(f"Imagem copiada para: {destino}")
            else:
                print(f"Imagem já está em: {destino}")
            self.imagem_path = nome_arquivo  # Salva só o nome do arquivo
            self.label_imagem.setText(f"Imagem: {nome_arquivo}")

    def salvar_alteracoes(self):
        nome = self.entrada_nome.text().strip()
        preco = self.entrada_preco.text().strip()
        categoria = self.combo_categoria.currentText()
        try:
            preco = float(preco)
            if nome and preco >= 0:
                self.model.atualizar_item(self.item_id, nome, preco, self.imagem_path, categoria)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Preencha nome e preço válidos!")
        except ValueError:
            QMessageBox.warning(self, "Erro", "Preço deve ser um número (ex.: 12.50)!")

class CadastrarAdmin(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Cadastro de Admin")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        self.container = QWidget()
        self.container.setMaximumWidth(400)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(15)

        self.label_titulo = QLabel("Cadastro do Admin")
        self.label_descricao = QLabel("Preencha todas as informações")
        self.entrada_nome_admin = QLineEdit()
        self.entrada_nome_admin.setPlaceholderText("Nome do admin")
        self.entrada_nome_admin.setMinimumHeight(40)
        self.entrada_cpf_admin = QLineEdit()
        self.entrada_cpf_admin.setPlaceholderText("CPF do admin (11 dígitos)")
        self.entrada_cpf_admin.setMinimumHeight(40)
        self.entrada_email_admin = QLineEdit()
        self.entrada_email_admin.setPlaceholderText("E-mail do admin")
        self.entrada_email_admin.setMinimumHeight(40)
        self.entrada_usuario_admin = QLineEdit()
        self.entrada_usuario_admin.setPlaceholderText("Usuário do admin")
        self.entrada_usuario_admin.setMinimumHeight(40)
        self.entrada_senha_admin = QLineEdit()
        self.entrada_senha_admin.setPlaceholderText("Senha do admin")
        self.entrada_senha_admin.setEchoMode(QLineEdit.Password)
        self.entrada_senha_admin.setMinimumHeight(40)
        self.button_register = QPushButton("Concluir Registro")
        self.button_register.setMinimumHeight(45)
        self.button_register.setMinimumWidth(200)

        self.form_layout.addWidget(self.label_titulo)
        self.form_layout.addWidget(self.label_descricao)
        self.form_layout.addWidget(self.entrada_nome_admin)
        self.form_layout.addWidget(self.entrada_cpf_admin)
        self.form_layout.addWidget(self.entrada_email_admin)
        self.form_layout.addWidget(self.entrada_usuario_admin)
        self.form_layout.addWidget(self.entrada_senha_admin)
        self.form_layout.addWidget(self.button_register)
        self.container.setLayout(self.form_layout)

        self.button_register.clicked.connect(self.concluir_registro)

        self.layout.addWidget(self.container)
        self.layout.addStretch()
        self.setLayout(self.layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                font-size: 16px;
                color: #2f3542;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dfe4ea;
                border-radius: 6px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4dabf7;
            }
            QPushButton {
                background-color: #4dabf7;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #74c0fc;
            }
        """)

    def concluir_registro(self):
        nome = self.entrada_nome_admin.text().strip()
        cpf = self.entrada_cpf_admin.text().strip()
        email = self.entrada_email_admin.text().strip()
        username = self.entrada_usuario_admin.text().strip()
        password = self.entrada_senha_admin.text().strip()

        if nome and cpf and email and username and password:
            if len(cpf) != 11 or not cpf.isdigit():
                QMessageBox.warning(self, "Erro", "CPF deve ter 11 dígitos numéricos!")
                return
            sucesso, mensagem = self.model.cadastrar_usuario(nome, cpf, email, username, password, "admin")
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
        else:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")

class CadastrarCliente(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Cadastro de Cliente")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        self.container = QWidget()
        self.container.setMaximumWidth(400)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(15)

        self.label_titulo = QLabel("Cadastro do Cliente")
        self.label_descricao = QLabel("Preencha todas as informações")
        self.entrada_nome_cliente = QLineEdit()
        self.entrada_nome_cliente.setPlaceholderText("Nome do cliente")
        self.entrada_nome_cliente.setMinimumHeight(40)
        self.entrada_cpf_cliente = QLineEdit()
        self.entrada_cpf_cliente.setPlaceholderText("CPF do cliente (11 dígitos)")
        self.entrada_cpf_cliente.setMinimumHeight(40)
        self.entrada_email_cliente = QLineEdit()
        self.entrada_email_cliente.setPlaceholderText("E-mail do cliente")
        self.entrada_email_cliente.setMinimumHeight(40)
        self.entrada_usuario_cliente = QLineEdit()
        self.entrada_usuario_cliente.setPlaceholderText("Usuário do cliente")
        self.entrada_usuario_cliente.setMinimumHeight(40)
        self.entrada_senha_cliente = QLineEdit()
        self.entrada_senha_cliente.setPlaceholderText("Senha do cliente")
        self.entrada_senha_cliente.setEchoMode(QLineEdit.Password)
        self.entrada_senha_cliente.setMinimumHeight(40)
        self.button_register = QPushButton("Concluir Registro")
        self.button_register.setMinimumHeight(45)
        self.button_register.setMinimumWidth(200)

        self.form_layout.addWidget(self.label_titulo)
        self.form_layout.addWidget(self.label_descricao)
        self.form_layout.addWidget(self.entrada_nome_cliente)
        self.form_layout.addWidget(self.entrada_cpf_cliente)
        self.form_layout.addWidget(self.entrada_email_cliente)
        self.form_layout.addWidget(self.entrada_usuario_cliente)
        self.form_layout.addWidget(self.entrada_senha_cliente)
        self.form_layout.addWidget(self.button_register)
        self.container.setLayout(self.form_layout)

        self.button_register.clicked.connect(self.concluir_registro)

        self.layout.addWidget(self.container)
        self.layout.addStretch()
        self.setLayout(self.layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                font-size: 16px;
                color: #2f3542;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dfe4ea;
                border-radius: 6px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4dabf7;
            }
            QPushButton {
                background-color: #4dabf7;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #74c0fc;
            }
        """)

    def concluir_registro(self):
        nome = self.entrada_nome_cliente.text().strip()
        cpf = self.entrada_cpf_cliente.text().strip()
        email = self.entrada_email_cliente.text().strip()
        username = self.entrada_usuario_cliente.text().strip()
        password = self.entrada_senha_cliente.text().strip()

        if nome and cpf and email and username and password:
            if len(cpf) != 11 or not cpf.isdigit():
                QMessageBox.warning(self, "Erro", "CPF deve ter 11 dígitos numéricos!")
                return
            sucesso, mensagem = self.model.cadastrar_usuario(nome, cpf, email, username, password, "cliente")
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
        else:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")

class GerenciarMesasDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Gerenciar Mesas")
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        self.container = QWidget()
        self.container.setMaximumWidth(400)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(15)

        # Label e campo para número de mesas
        self.label_mesas = QLabel("Número Total de Mesas:")
        self.entrada_mesas = QSpinBox()
        self.entrada_mesas.setMinimum(1)  # Valor mínimo
        self.entrada_mesas.setMaximum(100)  # Valor máximo
        self.entrada_mesas.setValue(self.model.total_mesas)  # Define o valor inicial
        self.entrada_mesas.setFixedHeight(40)  # Tamanho fixo para visibilidade

        # Botão para salvar
        self.botao_salvar = QPushButton("Salvar")
        self.botao_salvar.setMinimumHeight(45)
        self.botao_salvar.clicked.connect(self.salvar_mesas)

        # Adiciona widgets ao layout
        self.form_layout.addWidget(self.label_mesas)
        self.form_layout.addWidget(self.entrada_mesas)
        self.form_layout.addWidget(self.botao_salvar)
        self.container.setLayout(self.form_layout)
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        # Estilização simplificada para evitar conflitos
        self.setStyleSheet("""
            QDialog { background-color: #f5f6fa; }
            QLabel { font-size: 20px; color: #2f3542; }
            QSpinBox { 
                padding: 10px; 
                border: 2px solid #dfe4ea; 
                border-radius: 6px; 
                font-size: 16px; 
                background-color: white; 
            }
            QSpinBox:focus { border-color: #4dabf7; }
            QSpinBox::up-button, QSpinBox::down-button { width: 20px; }
            QPushButton { 
                background-color: #4dabf7; 
                color: white; 
                border-radius: 6px; 
                padding: 12px; 
                font-size: 16px; 
            }
            QPushButton:hover { background-color: #74c0fc; }
        """)

    def salvar_mesas(self):
        total_mesas = self.entrada_mesas.value()
        self.model.salvar_total_mesas(total_mesas)
        QMessageBox.information(self, "Sucesso", f"Total de mesas atualizado para {total_mesas}!")
        self.accept()

class ConfirmarPedidoDialog(QDialog):
    def __init__(self, model, cliente_id, item_id, quantidade, parent=None):
        super().__init__(parent)
        self.model = model
        self.cliente_id = cliente_id
        self.item_id = item_id
        self.quantidade = quantidade
        self.setWindowTitle("Confirmar Pedido")
        self.setup_ui()

    def setup_ui(self):
        self.model.cursor.execute("SELECT nome FROM itens WHERE id = %s", (self.item_id,))
        item_nome = self.model.cursor.fetchone()[0]
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)
        self.container = QWidget()
        self.container.setMaximumWidth(400)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(15)
        self.label_item = QLabel(f"Item: {item_nome} (Quantidade: {self.quantidade})")
        self.label_mesa = QLabel("Mesa:")
        self.combo_mesa = QComboBox()
        self.label_pagamento = QLabel("Forma de Pagamento:")
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(["Dinheiro", "Cartão", "Pix"])
        self.botao_confirmar = QPushButton("Confirmar Pedido")
        self.botao_confirmar.setMinimumHeight(45)
        self.botao_confirmar.clicked.connect(self.confirmar_pedido)

        self.form_layout.addWidget(self.label_mesa)
        self.form_layout.addWidget(self.combo_mesa)
        self.form_layout.addWidget(self.label_pagamento)
        self.form_layout.addWidget(self.combo_pagamento)
        self.form_layout.addWidget(self.botao_confirmar)
        self.form_layout.addWidget(self.label_item)

        self.container.setLayout(self.form_layout)
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        self.atualizar_mesas()

        self.setStyleSheet("""
            QDialog { background-color: #f5f6fa; }
            QLabel { font-size: 20px; color: #2f3542; }
            QComboBox { padding: 10px; border: 2px solid #dfe4ea; border-radius: 6px; font-size: 16px; background-color: white; }
            QComboBox:focus { border-color: #4dabf7; }
            QPushButton { background-color: #4dabf7; color: white; border-radius: 6px; padding: 12px; font-size: 16px; }
            QPushButton:hover { background-color: #74c0fc; }
        """)

    def atualizar_mesas(self):
        self.combo_mesa.clear()
        mesas_ocupadas_por_outros = self.model.listar_mesas_ocupadas_por_outros(self.cliente_id)
        mesas_do_cliente = self.model.listar_mesas_ocupadas_por_cliente(self.cliente_id)

        if mesas_do_cliente:  # Cliente já tem uma mesa ocupada
            mesa_atual = mesas_do_cliente[0]  # Assume que só há uma mesa por cliente
            texto = f"Mesa {mesa_atual} (Sua Mesa)"
            self.combo_mesa.addItem(texto, userData=mesa_atual)
            # Apenas a mesa atual é mostrada e selecionável
        else:  # Cliente ainda não tem mesa
            for i in range(1, self.model.total_mesas + 1):
                if i in mesas_ocupadas_por_outros:
                    texto = f"Mesa {i} (Ocupada)"
                    self.combo_mesa.addItem(texto, userData=i)
                    self.combo_mesa.model().item(self.combo_mesa.count() - 1).setEnabled(False)
                else:
                    texto = f"Mesa {i} (Livre)"
                    self.combo_mesa.addItem(texto, userData=i)

    def confirmar_pedido(self):
        mesa = self.combo_mesa.currentData()
        forma_pagamento = self.combo_pagamento.currentText()
        mesas_ocupadas_por_outros = self.model.listar_mesas_ocupadas_por_outros(self.cliente_id)
        if mesa is not None and forma_pagamento:
            if mesa in mesas_ocupadas_por_outros:
                QMessageBox.warning(self, "Erro", "Esta mesa está ocupada por outro cliente!")
                return
            self.model.adicionar_pedido(self.cliente_id, self.item_id, self.quantidade, mesa, forma_pagamento)
            QMessageBox.information(self, "Sucesso", "Pedido confirmado com sucesso!")
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", "Selecione uma mesa e forma de pagamento!")

class ComandaDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Comanda")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        self.title_label = QLabel("Comanda - Pedidos Atuais")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.lista_pedidos = QListWidget()
        self.lista_pedidos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.atualizar_comanda()

        self.botao_remover = QPushButton("Remover Pedido Selecionado")
        self.botao_remover.setMinimumHeight(45)
        self.botao_remover.setMinimumWidth(200)
        self.botao_remover.clicked.connect(self.remover_pedido)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.lista_pedidos, 1)
        self.layout.addWidget(self.botao_remover)
        self.setLayout(self.layout)

        self.lista_pedidos.itemDoubleClicked.connect(self.alterar_status)

        self.setStyleSheet("""
            QDialog { background-color: #f5f6fa; }
            QLabel { font-size: 16px; color: #2f3542; }
            QListWidget { border: 2px solid #dfe4ea; border-radius: 6px; padding: 5px; background-color: white; }
            QListWidget::item { padding: 10px; font-size: 16px; color: #2f3542; }
            QListWidget::item:selected { background-color: #74c0fc; color: white; }
            QPushButton { background-color: #4dabf7; color: white; border-radius: 6px; padding: 12px; font-size: 16px; }
            QPushButton:hover { background-color: #74c0fc; }
        """)
    def remover_pedido(self):
        item = self.lista_pedidos.currentItem()
        if item:
            pedido_id = item.data(Qt.UserRole)
            if self.model.remover_pedido(pedido_id):
                self.atualizar_comanda()
                QMessageBox.information(self, "Sucesso", "Pedido removido com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível remover o pedido!")
        else:
            QMessageBox.warning(self, "Erro", "Selecione um pedido para remover!")


    def atualizar_comanda(self):
        self.lista_pedidos.clear()
        pedidos = self.model.listar_pedidos()
        mesas_ocupadas = self.model.listar_mesas_ocupadas()

        # Agrupar pedidos por mesa
        pedidos_por_mesa = {}
        for pedido in pedidos:
            id, cliente, item, qtd, mesa, pagamento, status = pedido
            if mesa not in pedidos_por_mesa:
                pedidos_por_mesa[mesa] = []
            pedidos_por_mesa[mesa].append((id, cliente, item, qtd, pagamento, status))

        # Ordenar mesas
        for mesa in sorted(pedidos_por_mesa.keys()):
            # Título da mesa
            mesa_titulo = QListWidgetItem(f"Mesa {mesa} ({'Ocupada' if mesa in mesas_ocupadas else 'Livre'})")
            mesa_titulo.setBackground(Qt.lightGray)
            mesa_titulo.setFont(QFont("Arial", 14, QFont.Bold))
            mesa_titulo.setFlags(Qt.NoItemFlags)
            self.lista_pedidos.addItem(mesa_titulo)

            # Itens da mesa
            for id, cliente, item, qtd, pagamento, status in pedidos_por_mesa[mesa]:
                texto = f"  {cliente}: {qtd}x {item} | {pagamento} | Status: {status}"
                item = QListWidgetItem(texto)
                item.setData(Qt.UserRole, id)
                self.lista_pedidos.addItem(item)

    def alterar_status(self, item):
        pedido_id = item.data(Qt.UserRole)
        dialog = QDialog(self)
        dialog.setWindowTitle("Alterar Status")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        combo = QComboBox()
        combo.addItems(["Pendente", "Preparando", "Entregue"])
        combo.setMinimumHeight(40)
        botao_salvar = QPushButton("Salvar")
        botao_salvar.setMinimumHeight(45)
        botao_salvar.setMinimumWidth(200)
        botao_salvar.clicked.connect(lambda: self.salvar_status(pedido_id, combo.currentText(), dialog))
        layout.addWidget(QLabel("Novo Status:"))
        layout.addWidget(combo)
        layout.addWidget(botao_salvar)
        layout.addStretch()
        dialog.setLayout(layout)
        dialog.exec()

        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                font-size: 16px;
                color: #2f3542;
            }
            QComboBox {
                padding: 10px;
                border: 2px solid #dfe4ea;
                border-radius: 6px;
                font-size: 16px;
                background-color: white;
            }
            QPushButton {
                background-color: #4dabf7;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #74c0fc;
            }
        """)

    def salvar_status(self, pedido_id, novo_status, dialog):
        if self.model.atualizar_status_pedido(pedido_id, novo_status):
            self.atualizar_comanda()
            dialog.accept()

class HistoricoDialog(QDialog):
    def __init__(self, model, cliente_id, parent=None):
        super().__init__(parent)
        self.model = model
        self.cliente_id = cliente_id
        self.setWindowTitle("Histórico de Pedidos")
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        self.lista_pedidos = QListWidget()
        self.lista_pedidos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lista_pedidos.setSpacing(10)
        self.lista_pedidos.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Desativa scroll horizontal
        self.layout.addWidget(self.lista_pedidos)

        self.botao_fechar = QPushButton("Fechar")
        self.botao_fechar.setMinimumHeight(45)
        self.botao_fechar.clicked.connect(self.accept)
        self.layout.addWidget(self.botao_fechar, alignment=Qt.AlignRight)

        self.setLayout(self.layout)
        self.atualizar_lista()

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QListWidget {
                border: 2px solid #dfe4ea;
                border-radius: 6px;
                padding: 10px;
                background-color: white;
            }
            QListWidget::item {
                font-size: 16px;
                color: #2f3542;
            }
            QLabel {
                font-size: 16px;
                color: #2f3542;
                padding: 5px;
            }
            QPushButton {
                background-color: #4dabf7;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #74c0fc;
            }
            QPushButton#cancelar {
                background-color: #ff6b6b;
            }
            QPushButton#cancelar:hover {
                background-color: #ff8787;
            }
        """)
        self.setMinimumSize(1000, 600)

    def atualizar_lista(self):
        self.lista_pedidos.clear()
        pedidos = self.model.listar_pedidos_cliente(self.cliente_id)
        for pedido in pedidos:
            id, item_nome, quantidade, preco, mesa, forma_pagamento, status = pedido
            texto = f"{item_nome} | Qtd: {quantidade} | R${preco:.2f} | Mesa {mesa} | {forma_pagamento} | {status}"
            
            # Widget personalizado
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(5, 5, 5, 5)
            item_layout.setSpacing(10)  # Espaçamento fixo e pequeno
            
            # Label com o texto
            item_label = QLabel(texto)
            item_label.setWordWrap(True)
            item_label.setMinimumWidth(700)  # Largura suficiente pro texto
            item_label.setMaximumWidth(800)  # Limite pra não invadir o botão
            item_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
            item_layout.addWidget(item_label)
            
            # Botão "Cancelar" ou espaço vazio
            if status == "Pendente":
                botao_cancelar = QPushButton("Cancelar")
                botao_cancelar.setObjectName("cancelar")
                botao_cancelar.setFixedSize(120, 40)
                botao_cancelar.clicked.connect(lambda checked, pid=id: self.cancelar_pedido(pid))
                item_layout.addWidget(botao_cancelar)
            else:
                item_layout.addSpacing(120)  # Espaço fixo pro alinhamento
            
            item_widget.setLayout(item_layout)
            
            # Define o tamanho do item
            list_item = QListWidgetItem(self.lista_pedidos)
            altura = max(item_widget.sizeHint().height(), 80)
            list_item.setSizeHint(QSize(900, altura))  # Largura ajustada pra caber na janela
            self.lista_pedidos.addItem(list_item)
            self.lista_pedidos.setItemWidget(list_item, item_widget)

    def cancelar_pedido(self, pedido_id):
        if self.model.cancelar_pedido(pedido_id, self.cliente_id):
            QMessageBox.information(self, "Sucesso", "Pedido cancelado com sucesso!")
            self.atualizar_lista()
        else:
            QMessageBox.warning(self, "Erro", "Não foi possível cancelar o pedido. Ele pode já estar em preparo!")

class GerenciarCategoriasDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Gerenciar Categorias")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        self.container = QWidget()
        self.container.setMaximumWidth(400)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(15)

        self.title_label = QLabel("Categorias Existentes")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.entrada_categoria = QLineEdit()
        self.entrada_categoria.setPlaceholderText("Nome da nova categoria")
        self.entrada_categoria.setMinimumHeight(40)
        self.botao_adicionar = QPushButton("Adicionar Categoria")
        self.botao_adicionar.setMinimumHeight(45)
        self.botao_adicionar.setMinimumWidth(200)
        self.lista_categorias = QListWidget()
        self.botao_remover = QPushButton("Remover Selecionada")
        self.botao_remover.setMinimumHeight(45)
        self.botao_remover.setMinimumWidth(200)

        self.form_layout.addWidget(self.title_label)
        self.form_layout.addWidget(self.entrada_categoria)
        self.form_layout.addWidget(self.botao_adicionar)
        self.form_layout.addWidget(self.lista_categorias)
        self.form_layout.addWidget(self.botao_remover)
        self.container.setLayout(self.form_layout)

        self.botao_adicionar.clicked.connect(self.adicionar_categoria)
        self.botao_remover.clicked.connect(self.remover_categoria)

        self.layout.addWidget(self.container)
        self.layout.addStretch()
        self.setLayout(self.layout)

        self.atualizar_lista_categorias()

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                font-size: 20px;
                color: #2f3542;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dfe4ea;
                border-radius: 6px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4dabf7;
            }
            QPushButton {
                background-color: #4dabf7;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #74c0fc;
            }
            QListWidget {
                border: 2px solid #dfe4ea;
                border-radius: 6px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                font-size: 16px;
                color: #2f3542;
            }
            QListWidget::item:selected {
                background-color: #74c0fc;
                color: white;
            }
        """)

    def adicionar_categoria(self):
        categoria = self.entrada_categoria.text().strip()
        if categoria:
            resultado = self.model.adicionar_categoria(categoria)
            if resultado is True:  # Se retornar True
                self.atualizar_lista_categorias()
                self.entrada_categoria.clear()
                self.parent().atualizar_combo_categorias()
                self.parent().atualizar_filtro_categorias()
                self.parent().atualizar_lista()
                QMessageBox.information(self, "Sucesso", "Categoria adicionada!")
            else:
                QMessageBox.warning(self, "Erro", resultado[1] if isinstance(resultado, tuple) else "Erro ao adicionar categoria!")
        else:
            QMessageBox.warning(self, "Erro", "Digite um nome para a categoria!")

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

    def atualizar_lista_categorias(self):
        self.lista_categorias.clear()
        categorias = self.model.listar_categorias()
        if categorias:
            self.lista_categorias.addItems(categorias)

class RelatoriosDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Relatórios")
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Label de total de vendas (será atualizado dinamicamente)
        self.label_vendas = QLabel("")
        self.atualizar_total_vendas()  # Chama na inicialização
        self.label_vendas.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_vendas)

        # Itens mais pedidos
        self.layout.addWidget(QLabel("Itens Mais Pedidos:"))
        itens = self.model.itens_mais_pedidos()
        print(f"Itens mais pedidos para o gráfico: {itens}")
        for nome, total in itens:
            item_label = QLabel(f"{nome}: {total} unidades")
            self.layout.addWidget(item_label)

        # Gráfico
        if itens:
            nomes = [item[0] for item in itens]
            quantidades = [item[1] for item in itens]
            self.fig = plt.Figure(figsize=(6, 4))
            self.ax = self.fig.add_subplot(111)
            self.ax.bar(nomes, quantidades, color='#4dabf7')
            self.ax.set_title("Itens Mais Pedidos")
            self.ax.set_ylabel("Quantidade")
            self.ax.tick_params(axis='x', rotation=45)
            self.fig.tight_layout()
            self.canvas = FigureCanvas(self.fig)
            self.layout.addWidget(self.canvas)
            self.canvas.draw()
        else:
            self.layout.addWidget(QLabel("Nenhum pedido registrado para gerar gráfico."))

        self.botao_fechar = QPushButton("Fechar")
        self.botao_fechar.setMinimumHeight(45)
        self.botao_fechar.clicked.connect(self.accept)
        self.layout.addWidget(self.botao_fechar, alignment=Qt.AlignRight)

        self.setLayout(self.layout)
        self.setStyleSheet("""
            QDialog { background-color: #f5f6fa; }
            QLabel { font-size: 16px; color: #2f3542; }
            QPushButton { background-color: #4dabf7; color: white; border-radius: 6px; padding: 8px; font-size: 16px; }
            QPushButton:hover { background-color: #74c0fc; }
        """)
        self.setMinimumSize(600, 700)

    def atualizar_total_vendas(self):
        total_vendas = self.model.total_vendas_dia()
        self.label_vendas.setText(f"Total de Vendas (Hoje, Entregues): R${total_vendas:.2f}")

class MesasWidget(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)

        # Filtro de mesas
        self.filtro_container = QWidget()
        self.filtro_layout = QHBoxLayout()
        self.filtro_mesa = QLineEdit()
        self.filtro_mesa.setPlaceholderText("Filtrar mesa (ex.: 136)")
        self.filtro_mesa.setMaximumWidth(200)
        self.filtro_mesa.textChanged.connect(self.atualizar_mesas)
        self.combo_mesa = QComboBox()
        self.combo_mesa.setMaximumWidth(200)
        self.combo_mesa.addItem("Todas as mesas")
        self.combo_mesa.addItem("Mesas ocupadas")
        self.combo_mesa.currentTextChanged.connect(self.atualizar_mesas)
        self.filtro_layout.addWidget(QLabel("Filtrar:"))
        self.filtro_layout.addWidget(self.filtro_mesa)
        self.filtro_layout.addWidget(self.combo_mesa)
        self.filtro_layout.addStretch()
        self.filtro_container.setLayout(self.filtro_layout)

        # Lista de mesas
        self.lista_mesas = QListWidget()
        self.lista_mesas.setMaximumHeight(200)  # Limite pra não crescer demais
        self.lista_mesas.itemClicked.connect(self.mostrar_pedidos_mesa)

        self.layout.addWidget(self.filtro_container)
        self.layout.addWidget(self.lista_mesas)
        self.setLayout(self.layout)

        self.atualizar_mesas()

        self.setStyleSheet("""
            QLineEdit { padding: 8px; border: 2px solid #dfe4ea; border-radius: 5px; font-size: 14px; }
            QComboBox { padding: 8px; border: 2px solid #dfe4ea; border-radius: 5px; font-size: 14px; }
            QListWidget { border: 2px solid #dfe4ea; border-radius: 5px; padding: 5px; }
            QListWidget::item { padding: 8px; font-size: 14px; }
            QListWidget::item:selected { background-color: #74c0fc; color: white; }
        """)

    def atualizar_mesas(self):
        self.lista_mesas.clear()
        filtro = self.filtro_mesa.text().strip()
        modo = self.combo_mesa.currentText()
        mesas_ocupadas = set(self.model.listar_mesas_ocupadas())
        total_mesas = self.model.total_mesas

        for mesa in range(1, total_mesas + 1):
            texto = f"Mesa {mesa} - {'Ocupada' if mesa in mesas_ocupadas else 'Livre'}"
            if filtro and filtro.isdigit() and int(filtro) != mesa:
                continue
            if modo == "Mesas ocupadas" and mesa not in mesas_ocupadas:
                continue
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, mesa)
            if mesa in mesas_ocupadas:
                item.setBackground(Qt.yellow)
            else:
                item.setBackground(Qt.green)
            self.lista_mesas.addItem(item)

    def mostrar_pedidos_mesa(self, item):
        mesa = item.data(Qt.UserRole)
        pedidos = self.model.pedidos_por_mesa(mesa)
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Pedidos da Mesa {mesa}")
        layout = QVBoxLayout()
        if pedidos:
            for pedido in pedidos:
                id, item, qtd, forma, status = pedido
                layout.addWidget(QLabel(f"ID {id}: {item} | Qtd: {qtd} | {forma} | {status}"))
        else:
            layout.addWidget(QLabel("Nenhum pedido ativo nesta mesa."))
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(dialog.accept)
        layout.addWidget(btn_fechar, alignment=Qt.AlignRight)
        dialog.setLayout(layout)
        dialog.exec()
