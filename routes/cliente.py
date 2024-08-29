import sys,os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .loginValidation import login_required
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Cliente, Venda, db
from datetime import datetime

"""
IMPLEMENTAR
VERIFICAÇÃO DE EXISTÊNCIA DE NÚMERO CADASTRADO / (ATIVO OU NÃO)
"""

cliente_route = Blueprint('clientes', __name__)

@cliente_route.route("/")
@login_required
def listar_clientes():
    clientes = db.session.query(Cliente).all() 
    """ Listar os clientes existentes no banco de dados. """
    return render_template("listar_clientes.html", clientes=clientes)

@cliente_route.route("/cadastrar", methods=["GET","POST"])
@login_required
def cadastrar_clientes():
    """
    GET -> Formulário em Branco / POST -> Cadastra Novo Cliente.
    """
    if request.method == "POST":
        cpf = (request.form['cpf']).replace(".","").replace("-","")
        nome = request.form['nome']
        data_nascimento = datetime.strptime(request.form['data_nascimento'], '%Y-%m-%d').date()
        email = request.form['email']
        ddi = (request.form['ddi']).replace("+","")
        ddd = request.form['ddd']
        numero = request.form['celular']
        
        novo_cliente = Cliente(
            cpf=cpf,
            nome=nome,
            data_nascimento=data_nascimento,
            email=email,
            ddi=ddi,
            ddd=ddd,
            numero=numero
        )
        db.session.add(novo_cliente)
        db.session.commit()

        flash(f'Cliente ({nome}) adicionado com sucesso!  ')
        return redirect(url_for('clientes.listar_clientes'))
        
    else:
        return render_template("cadastrar_clientes.html")

@cliente_route.route('/<int:cliente_id>', methods=["GET",'POST'])
@login_required
def editar_clientes(cliente_id):
    cliente = db.session.query(Cliente).get_or_404(cliente_id)

    if request.method == "POST":
        cliente.cpf = (request.form['cpf']).replace(".","").replace("-","")
        cliente.nome = request.form["nome"]
        cliente.data_nascimento = datetime.strptime(request.form['data_nascimento'], '%Y-%m-%d').date()
        cliente.email = request.form['email']
        cliente.ddi = (request.form['ddi']).replace("+","")
        cliente.ddd = request.form['ddd']
        cliente.numero = request.form['celular']

        try:
            db.session.commit()
            flash(f'Cliente ({cliente.nome}) atualizado com sucesso!')
            return redirect(url_for('clientes.listar_clientes'))
        except Exception as err:
            db.session.rollback()
            flash(f'Error ao atualizar cliente, tente novamente.\n{err}', 'danger')
            return render_template("editar_clientes.html", cliente=cliente)
    else:
        print("GET GET")
        return render_template("editar_clientes.html", cliente=cliente)

@cliente_route.route('/<int:cliente_id>/apagar', methods=["GET"])
@login_required
def apagar_clientes(cliente_id):
    cliente = db.session.query(Cliente).get_or_404(cliente_id)
    try:
        #  GAMBIARRA PARA APAGAR VENDAS ATÉ RESOLVER O B.O *1.0*
        vendas = db.session.query(Venda).filter(Venda.id_cliente == cliente_id).all()
        for venda in vendas:
            db.session.delete(venda)
            db.session.commit()
        #

        cliente_nome = cliente.nome
        db.session.delete(cliente)
        db.session.commit()

        flash(f'"{cliente_nome}", e suas respectivas vendas cadastradas, apagado com sucesso!')
        return redirect(url_for('clientes.listar_clientes'))
    
    except Exception as err:
        flash(f'Falha ao remover "{cliente_nome}", tente novamente ou contate o administrados.\n{err}','danger')
        return redirect(url_for('clientes.listar_clientes'))