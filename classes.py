#Começa pela criação da classe
class Campus:
    #Metodo construtor é obrigatório
    #Todo método deve ter o parâmetro "self"

    def __init__(self):
        #Self acessa os atributos do objeto
        self.nome = ""
        self.endereco = ""

    #Metodo usado ao imprimir um objeto
    def __str__(self):
        return f"Campus: {self.nome}"
    
class Estudante:
    def __init__(self):
        self.nome = ""
        self.cpf = ""
        self.data_nasc = ""

    def __str__(self):
        return f"Estudante: {self.nome}"
    
    def apresentar(self):
        print(f"O(a) {self.nome} masceu em {self.data_nasc}")
        if(self.cpf == ""):
            print("O(a) estudante não cadastrou CPF.")
        else:
            print("CPF:", self.cpf[0:3], "...")

#criacao de objetos
ryan = Estudante()
ryan.nome = "Ryan Carlos"
ryan.cpf = "111.111.111-11"
ryan.data_nasc = "22/01/2001"
ryan.apresentar()    
