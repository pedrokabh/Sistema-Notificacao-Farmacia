from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class Vendedor(db.Model):
    __tablename__ = 'login'
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    usuario = db.Column(db.String(30), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), nullable=True)
    ddi = db.Column(db.String(3), nullable=False)
    ddd = db.Column(db.String(3), nullable=False)
    numero = db.Column(db.String(15), nullable=False)

class Venda(db.Model):
    __tablename__= 'Venda'
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, nullable=False)
    id_vendedor = db.Column(db.Integer, nullable=False)
    medicacao = db.Column(db.String(100), nullable=False)
    receita = db.Column(db.LargeBinary, nullable=False)
    dataRevenda = db.Column(db.Date, nullable=False)
    dataVenda = db.Column(db.Date, nullable=False)
    notification = db.Column(db.Boolean, nullable=False)
