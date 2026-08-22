from interfaceweb import app
from flask import render_template #rendereniza o html

@app.route('/')
def homepage(): 
    return render_template('homepage.html')