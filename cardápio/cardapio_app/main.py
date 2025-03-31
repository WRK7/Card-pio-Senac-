import sys
from PySide6.QtWidgets import QApplication
from model import CardapioModel
from view import LoginView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = CardapioModel()
    window = LoginView(model)
    window.show()
    
    try:
        exit_code = app.exec()
    finally:
        model.limpar_historico_ao_fechar()
        model.fechar() 
        sys.exit(exit_code)