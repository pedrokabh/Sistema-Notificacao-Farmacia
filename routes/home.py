import os, sys
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.loginValidation import login_required
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Vendedor, db
from werkzeug.security import check_password_hash
# -- EXECUÇÃO -- #

home_route = Blueprint('home', __name__)

@home_route.route("/suporte/")
def suporte():
    return render_template("suporte.html")

@home_route.route("/menu/")
@login_required
def menu():
    vendedor = db.session.query(Vendedor).get(session['vendedor_id'])
    vendedor.text = "Administrador do sistema" if vendedor.admin else "Vendedor"
    
    return render_template("menu.html", vendedor=vendedor)

@home_route.route('/', methods=["GET", "POST"])
def login():
    """ 
        GET -> Acessa Página de Login / POST -> Tenta Efetuar Login.
    """
    # SE REQUISIÇÃO FOR 'POST'
    if request.method == "POST":

        form_usuario = str(request.form.get("username"))
        form_senha = str(request.form.get("password"))
        vendedor = db.session.query(Vendedor).filter_by(usuario=form_usuario).first()

        if vendedor and check_password_hash(vendedor.senha, form_senha):
            if vendedor.ativo:
                session['logged_in'] = True
                session['vendedor_id'] = vendedor.id
                return redirect(url_for('home.menu'))
            else:
                flash('Usuário Inativo, contate o suporte!', 'error')
                return redirect(url_for("home.login"))
        
        # SE LOGIN FALHAR LOGIN FALHAR.
        flash('Usuário ou senha incorretos!', 'error')
        return redirect(url_for("home.login"))
    
    # SE REQUISIÇÃO FOR 'GET'
    else:
        if session.get('logged_in'):
            return redirect(url_for('home.menu'))
        else:
            session.pop('logged_in', None) 
            return render_template("login.html")
    
@home_route.route("/desconectar/")
@login_required
def desconectar():
    """ Faz o logout do usuário || Redireciona para a página de login """
    session.pop('logged_in', None) 
    session.pop('vendedor_id', None)
    flash('Você foi desconectado.', 'info') 
    return redirect(url_for('home.login')) 


