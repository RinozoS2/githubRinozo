from interfaceweb import app
from flask import render_template #rendereniza o html

@app.route('/') # @ = decorate, linha de código que atribui uma nova funcionalidade a função que vem embaixo
def homepage(): 
    return render_template('homepage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')