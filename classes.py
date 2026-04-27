class Jogador:
    def __init__(self, nome, nickname,  turma):
        self.nome = nome
        self.nickname = nickname
        self.turma = turma

    def exibir_dados (self):
        print(f"nome: {self.nome}")
        print(f"nick: {self.nickname}")
        print(f"turma: {self.turma}")

class Equipe:
    def __init__(self, nome, jogo):
        self.nome = nome
        self.jogo = jogo
        self.jogadores = []

    def adicionar_jogador(self,jogador):
        self.jogadores.append(jogador)

    def listar_jogadores(self):
        if len(self.jogadores) == 0:
            print("nenhum jogador")
        else:
            for jogador in self.jogadores:
                jogador.exibir_dados()
                print("---")

    def buscar_jogador(self,nickname):
        for jogador in self.jogadores:
            if jogador.nickname == nickname:
                return jogador
        return None
        
                