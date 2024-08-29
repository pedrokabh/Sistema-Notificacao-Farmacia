# Sistema Fámacia - Envio de mensagens semi-automática via WPP.

Esse sistema é uma interface simples, a qual tem o objetivo de guardar dados de contatos dos clientes, e também suas respectivas vendas. Apartir da venda, o sistema identifica o dia de vencimento da medicação, e faz uma lista de contatos todo dia, para notifica-los que sua medicação está acabando. As principais tecnologias utilizadas para desenvolver o projeto foi.

Este projeto é uma solução, para a fármacia de um amigo, que não quer pagar serviços de API´s como Twilio ou WhatsAppBusiness API.

1. A biblioteca Flask (Python) é utilizada para configurar rotas, e fazer todo o gerenciamento das requisições para o servidor de back-end.
2. HTML, CSS E JavaScript para apresentar a interface na Web.
3. SqlAlchemy para conversar com o nosso banco de dados (MariaDB).
4. Selenium para realizar o envio automático das mensagens via WhatsApp.

## Como Utilizar

Para utilizar esse simples sistema é necessário cadastrar os dados de contato do cliente, e cadastrar os medicamentos junto com a data estipulada para acabar a medicação. Apartir dessas informações, o sistema utiliza a funcionalidade de envio via WPP para avisar no dia de vencimento da medicação. O envio é feito apartir de uma semi-automação. Aonde o usuário irá precisar logar no seu WhatsApp Web via Qr Code, e após feita atutenticação o Selenium faz o envio através de um RPA.

### 1. Compilação e Execução local:
* Certifique-se de ter o Python Instalado na máquina (desenvolvido na versão Python 3).
* Certifique-se de ter um banco de dados instalado na máquina/servidor para guardar e recuperar os dados. (Maria DB)
* Certifique-se de ter as seguintes bibliotecas Python instaladas para execução do projeto:

```Python
    pip install Flask # Servidor Web
    pip install SQLAlchemy # Para comunicação e Ações no Banco de dados
    pip install Selenium # Para Web Scrapping e RPA.
    pip install webdriver-manager. # Gerenciador do driver do navegador
```
* Certifique-se de ter o driver correto referente ao tipo e versão do navegador instalado na máquina na pasta Other.

* Execute o programa compilado o seguinte arquivo na pasta Sistema-Farmacia:
```Python
    Python main.py 
```

* Certifique de ter criado o banco de dados e as tabelas necessárias para rodar o sistema. (Passo 2)

### 2. Script com a Query para criação do banco de dados:
```sql
    -- CREATE DATA BASE --
    CREATE DATABASE sistema_farmacia;
    USE sistema farmácia;

    -- CREATE TABLES --
    CREATE TABLE login (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cpf VARCHAR(11) NOT NULL UNIQUE,
        nome VARCHAR(50) NOT NULL,
        usuario VARCHAR(30) NOT NULL UNIQUE,
        senha VARCHAR(255) NOT NULL
    );

    CREATE TABLE cliente (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cpf VARCHAR(11) NOT NULL UNIQUE,
        nome VARCHAR(80) NOT NULL,
        data_nascimento DATE, -- Opcional
        email VARCHAR(100), -- Opcional
        ddi CHAR(3) NOT NULL,
        ddd CHAR(3) NOT NULL,
        numero VARCHAR(15) NOT NULL,
        UNIQUE (ddi, ddd, numero) -- Para garantir que a combinação de ddi, ddd e numero seja única
    );

    CREATE TABLE venda (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_cliente int NOT NULL,
        id_vendedor int NOT NULL,
        medicacao VARCHAR(100) NOT NULL,
        receita BLOB NOT NULL, 
        dataRevenda DATE NOT NULL,
        FOREIGN KEY (id_cliente) REFERENCES cliente(id),
        FOREIGN KEY (id_vendedor) REFERENCES login(id)
    );
```
### 3. Telas do Sistema:

#### Login
![Captura de tela](./Others/prints%20do%20sistema/login.png)

#### Menu
![Captura de tela](./Others/prints%20do%20sistema/home.png)

#### Notificar
![Captura de tela](./Others/prints%20do%20sistema/notificar.png)

## 4. Principais objetivos do projeto:
* Construir um sistema para guardar as receitas dos medicamentos (pdf), para se ter o controle organizado das mesmas em casos de auditorias junto ao orgãos do governo.
* Possuir uma função semi-automática para realizar o envio das mensagens aos clientes através do WPP.
* Adquirir conhecimentos utilizandos as tecnologias necessárias para alcançar os requisitos do projeto. 