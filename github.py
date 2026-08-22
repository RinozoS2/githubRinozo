import os

print("Configurando email")

comando_email = 'git config user.email "20241pvai0030029@estudantes.ifpr.edu.br"'
os.system(comando_email)

comando1 = "git add *"
os.system(comando1)

mensagem = input("Mensagem do commit ")

while len(mensagem) < 5:
    print("Mensagem muito pequena, detalhe mais...")
    mensagem = input("Mensagem do commit ")

comando2 = f'git commit -m "{mensagem}"'
os.system(comando2)

print("Atualizando o repositório...")
comando3 = "git pull --rebase origin main"
os.system(comando3)

print("Enviando para o GitHub...")
comando4 = "git push origin main"
os.system(comando4)