#Criando site em flask em 3 etapas
from flask import Flask #1-importa o flask

app = Flask(__name__, template_folder='template') #2-cria a instância de app do flask

#3-cria suas rotas (no arquivo views.py)
from views import *

if __name__ == '__main__':
    app.run(debug = True)