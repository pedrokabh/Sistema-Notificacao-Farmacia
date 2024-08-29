import sys, os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, abort
import io
from .loginValidation import login_required
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Cliente, Venda, Vendedor, db
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Importação para criar serviço com driver chrome
from selenium.webdriver.chrome.service import Service
import time
from selenium.common.exceptions import TimeoutException

venda_route = Blueprint('venda', __name__)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@venda_route.route('/<int:cliente_id>')
@login_required
def listar_vendas(cliente_id):
    cliente = db.session.query(Cliente).get_or_404(cliente_id)
    vendas = db.session.query(Venda).filter(Venda.id_cliente == cliente_id).all()
    
    for venda in vendas:
        venda.ativa = "Ativa" if venda.notification else "Inativa"
        vendedor = db.session.query(Vendedor).get(venda.id_vendedor)
        venda.nome_vendedor = vendedor.nome if vendedor else "Desconhecido"

    return render_template('listar_vendaCliente.html', cliente=cliente, vendas=vendas)

@venda_route.route('/<int:cliente_id>/cadastrar/', methods=["GET", "POST"])
@login_required
def cadastrar_venda(cliente_id, min_date=None):
    cliente = db.session.query(Cliente).get_or_404(cliente_id)
    vendedor = db.session.query(Vendedor).get(session['vendedor_id'])

    if request.method == "POST":
        medicacao = request.form['medicacao']
        data_revenda = request.form['dataRevenda']
        
        if 'receita' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        file = request.files['receita']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            file_content = file.read()

            # Verificação do tamanho do arquivo
            print(f"File size before saving: {len(file_content)} bytes")

            nova_venda = Venda(
                id_cliente=cliente.id,
                id_vendedor=vendedor.id,
                medicacao=medicacao,
                receita=file_content,
                dataVenda=datetime.now(),
                dataRevenda=data_revenda,
                notification=True
            )
            db.session.add(nova_venda)
            db.session.commit()

            flash('Venda cadastrada com sucesso!', 'success')
            return redirect(url_for('venda.listar_vendas', cliente_id=cliente.id))
    
    # min_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    min_date = (datetime.now()).strftime('%Y-%m-%d')
    return render_template('cadastrar_venda.html', cliente=cliente, vendedor=vendedor, min_date=min_date)

@venda_route.route('/download_receita/<int:venda_id>')
@login_required
def download_receita(venda_id):
    venda = db.session.query(Venda).get_or_404(venda_id)
    
    if venda.receita:
        try:

            return send_file(
                io.BytesIO(venda.receita),
                as_attachment=True,
                download_name=f'{venda.medicacao}.pdf',
                mimetype='application/pdf'
            )
        except Exception as e:
            print(f"Erro ao processar o arquivo: {e}")
            abort(500, description="Erro ao processar o arquivo.")
    else:
        abort(404, description="Arquivo não encontrado.")

@venda_route.route('/notification')
@login_required
def listar_notificacoes():
    hoje = (datetime.now()).strftime('%Y-%m-%d')
    vendas = db.session.query(Venda).filter(
        Venda.dataRevenda == hoje #, Venda.notification == 1
    ).all()

    if not vendas:
        flash(f"Nenhuma venda cadastrada para notificar no dia {hoje}.")
        return redirect(url_for('home.menu'))
    
    for venda in vendas:
        vendedor = db.session.query(Vendedor).get(venda.id_vendedor)
        cliente = db.session.query(Cliente).get(venda.id_cliente)
        venda.ativa = "Ativa" if venda.notification else "Inativa"
        venda.nome_cliente = cliente.nome if cliente else "Não Identificado"
        venda.nome_vendedor = vendedor.nome if vendedor else "Não Identificado"
        venda.numeroCompleto = cliente.ddi+cliente.ddd+cliente.numero
        venda.clienteEmail =  cliente.email
    return render_template('listar_notificacoes.html', vendas=vendas)

"""
    1.0 - Para o envio de e-mail necessário conta de e-mail com acesso via API/Aplicações externas.
"""
@venda_route.route('/notificar/')
@login_required
def enviar_email():
    try:
        flash("[Função de envio de email comentada.]")
        vendas = db.session.query(Venda).filter( Venda.dataRevenda == (datetime.now()).strftime('%Y-%m-%d') ).all()
        return render_template('listar_no tificacoes.html', vendas=vendas)
        # hoje = (datetime.now()).strftime('%Y-%m-%d')
        # vendas = db.session.query(Venda).filter(Venda.dataRevenda == hoje).all()
        # if not vendas:
        #     flash(f"Nenhuma venda cadastrada para notificar no dia {hoje}.")
        #     return redirect(url_for('home.menu'))
        
        # for venda in vendas:
        #     vendedor = db.session.query(Vendedor).get(venda.id_vendedor)
        #     cliente = db.session.query(Cliente).get(venda.id_cliente)
        #     venda.ativa = "Ativa" if venda.notification else "Inativa"
        #     venda.nome_cliente = cliente.nome if cliente else "Não Identificado"
        #     venda.nome_vendedor = vendedor.nome if vendedor else "Não Identificado"
        #     venda.numeroCompleto = cliente.ddi+cliente.ddd+cliente.numero
        #     venda.clienteEmail =  cliente.email
        #     venda.logStatus, venda.log = enviar_email(
        #         assunto="Lembre-se de Compra Medicação",
        #         corpo= str(f"Olá {venda.nome_cliente} sua medicação {venda.medicacao} está acabando, lembre-se de comprar o mais rápido possível.\n Farmácia Saúde Popural - Rua Alegria, 666, bairro inferno, Lago de fogo - MG."),
        #         destinatario=venda.clienteEmail
        #     )
        #     # VERIFICAÇÃO DE SUCESSO / SE LOG = 0 entao venda. notification=0 ou se log != 0
            
        # flash('Lista de Notificação via e-mail Executada!')
        # return render_template('listar_notificacoes.html', vendas=vendas)
    except:
        flash('Falha ao enviar notificação via e-mail.')
        return redirect(url_for('home.menu'))

def enviar_email(destinatario, assunto, corpo):
    remetente = "pedrocamarabh@gmail.com"
    senha = 'ljiw ockq fqmp nkyq'

    if not remetente or not senha:
        return 1, "Configurar Login do E-mail Remetente."

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto

    msg.attach(MIMEText(corpo, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
            return 0, 'E-mail enviado com sucesso!'
    except smtplib.SMTPAuthenticationError as e:
        return 1 , f'Erro de autenticação: {e}'
    except Exception as e:
        return 1, f'Erro ao enviar e-mail: {e}'

@venda_route.route('/enviar_wpp')
@login_required
def enviar_wpp():
    try:

        hoje = (datetime.now()).strftime('%Y-%m-%d')
        vendas = db.session.query(Venda).filter(
            Venda.dataRevenda == hoje,
            Venda.notification == 1 # Vendas Ativas
        ).all()
        if not vendas:
            flash(f"Nenhuma venda cadastrada ativa para notificar no dia: {(datetime.now()).strftime('%d-%m-%Y')}.")
            return redirect(url_for('venda.listar_notificacoes'))

        browser = webdriver.Chrome(service=Service(r".\Others\chromedriver.exe"))

        browser.get('https://web.whatsapp.com/')

        if WebDriverWait(browser,60).until(EC.element_to_be_clickable(('xpath',"//div[contains(text(), 'Pesquisar')]"))):
            pass
        else:
            flash("Tempo de autenticação excedido. [60s]\nTente autenticar novamente.")
            return url_for('venda.listar_notificacoes')
        
        for venda in vendas:
            vendedor = db.session.query(Vendedor).get(venda.id_vendedor)
            cliente = db.session.query(Cliente).get(venda.id_cliente)

            # Definindo atributos dinâmicos
            setattr(venda, 'ativa', "Ativa" if venda.notification else "Inativa")
            setattr(venda, 'nome_cliente', cliente.nome if cliente else "Não Identificado")
            setattr(venda, 'nome_vendedor', vendedor.nome if vendedor else "Não Identificado")
            setattr(venda, 'numeroCompleto', cliente.ddi + cliente.ddd + cliente.numero if cliente else "")
            setattr(venda, 'clienteEmail', cliente.email if cliente else "")

            logStatus, log = notificar_via_WPP(
                browser=browser,
                mensagem=f"Olá {venda.nome_cliente}, sua medicação {venda.medicacao} está acabando. Não se esqueça de comprar mais. (mensagem de teste)",
                numero=venda.numeroCompleto
            )

            if logStatus == 0:
                print('Venda Notificada')
                venda.notification = 0
                db.session.commit()

        flash('Lista de Notificação via Wpp Executada!')
        browser.quit()
        return redirect(url_for('venda.listar_notificacoes'))
    except:
        flash('Falha ao enviar notificação via WPP.')
        browser.quit()
        return redirect(url_for('home.menu'))

def notificar_via_WPP(mensagem, numero, browser):
    try:
        browser.get(f'https://wa.me/{str(numero)}?text={str(mensagem)}')
        WebDriverWait(browser,10).until(EC.element_to_be_clickable(('xpath','//*[@id="action-button"]'))).click()

        mensagem_com_link = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH, "//a//span[contains(text(), 'usar o WhatsApp Web')]")))
        mensagem_com_link.find_element(By.XPATH, "ancestor::a").click()
        
        try:
            # Fluxo: Caso número tenha Whatsapp
            element = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH,"//button[@aria-label='Enviar']")))
            element.click()

            if WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.XPATH,f"//span[contains(text(), '{mensagem}')]"))):
                time.sleep(3)
                status = 0
                log = f"Mensagem encaminhada para (+{numero}) [Sucesso]"
            else:
                status = 2
                log = f"Encaminhamento de mensagem para (+{numero}) [Sem confirmação de envio]"
            
            return status, log
        except TimeoutException:
            WebDriverWait(browser,10).until(EC.element_to_be_clickable((
                By.XPATH,
                f"//div[contains(text(), 'O número de telefone compartilhado por url é inválido.')]"
            )))
            log = f"[Warning] Tempo para inicializar chat +{numero} expirado.\n[Warning] O número de telefone compartilhado por url é inválido."
            return 1, log
    except Exception as err:
        log = "[Notificar WPP] Falha ao executar método notificar WhatsApp."
        return 1, log
