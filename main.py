from flask import Flask
from routes.home import home_route
from routes.cliente import cliente_route
from routes.venda import venda_route
import os
from models import db

"""
ATUALIZAÇÃO FUTURA -> implementar gerenciamento de vendedores / cadastrar vendedor - (desativar) vendedor
"""

os.system("cls")

# Criação do aplicativo Flask
app = Flask(__name__)
app.secret_key = ''  # Chave secreta para sessões

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Registra Blueprints
app.register_blueprint(home_route)
app.register_blueprint(cliente_route, url_prefix="/clientes")
app.register_blueprint(venda_route, url_prefix="/venda")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
