#Bibliotecas importadas
import random #para itens aleatórios
import arcade #para o jogo 2D

#Constantes da janela
LARGURA = 800
ALTURA = 600
TITULO = "Meu Joguinho"

#Constantes do jogador
VELOCIDADE_JOGADOR = 5

#Constantes do item
NUMERO_MOEDAS = 12

# Classe Player
class Player(arcade.Sprite): #Herda a função sprite do arcade

    def __init__(self): 
        super().__init__("buxa.jpg", scale=0.4) #Construindo o jogador

    def update(self, delta_time: float = 0):
        super().update(delta_time) #Atualiza a posição do jogador

        # Mantém o jogador dentro do limite da janela
        if self.left < 0: #esquerda
            self.left = 0

        if self.right > LARGURA: #direita
            self.right = LARGURA

        if self.bottom < 0: #baixo
            self.bottom = 0

        if self.top > ALTURA: #alto
            self.top = ALTURA


# Classe Moeda
class Moeda(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__("moeda.png", scale=0.2) #Cria o objeto do item, no caso moeda
        self.center_x = x #coloca a moeda no eixo X sorteado
        self.center_y = y #coloca a moeda no eixo Y sorteado


# Tela Inicial
class TelaInicial(arcade.View): #O evento view, representa uma janela, pode ser de vitória, derrota...

    def __init__(self):
        super().__init__() #Sua criação
        
    def on_draw(self): #Função para escrever nessa tela
        self.clear() #Limpa a tela antes de desenhar para não bugar
        arcade.draw_text("Jogo - O coletor de moedas", LARGURA // 2, ALTURA // 2, arcade.color.BLACK, 30, anchor_x="center")
        arcade.draw_text("Pressione ENTER para começar", LARGURA // 2, ALTURA // 2 - 50, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Pressione ESC para sair", LARGURA // 2, ALTURA // 2 - 80, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Use as teclas W, A, S, D para se mover", LARGURA // 2, ALTURA // 2 - 120, arcade.color.WHITE, 20, anchor_x="center")
        #Textos dentro da tela, tendo conteúdo, largura, altura, cor, posição

    def on_key_press(self, key, modifiers): #Definir teclas relacionadas a essa tela
        if key == arcade.key.ENTER:
            self.window.show_view(TelaJogo()) #Enter abre o jogo
        elif key == arcade.key.ESCAPE: 
            arcade.close_window() #Esc fecha a tela

# Tela do Jogo
class TelaJogo(arcade.View):

    def __init__(self):
        super().__init__() #Criação da tela definitiva do jogo
        arcade.set_background_color(arcade.color.BABY_BLUE_EYES) #Cor de fundo

        #Criando o jogador na tela e posicionando
        self.jogador = Player() 
        self.jogador.center_x = LARGURA // 2
        self.jogador.center_y = 200 

        #Atualiza o jogador constante
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.jogador)

        #Adicionando as moedas e criando
        self.sprite_moeda = arcade.SpriteList()
        self._criar_moedas()

    #Criação da moeda
    def _criar_moedas(self):
        for _ in range(NUMERO_MOEDAS):
            x = random.randint(50, LARGURA - 50)
            y = random.randint(50, ALTURA - 50)
            moeda = Moeda(x, y)
            self.sprite_moeda.append(moeda)

    #Limpa a tela e adiciona tudo
    def on_draw(self):
        self.clear()
        self.sprite_moeda.draw()
        self.sprite_jogador.draw()

    def on_update(self, delta_time):
        # Atualiza os sprites passando o delta_time para propagar movimento
        self.sprite_jogador.update(delta_time)

        #Detecta quais moedas o jogador enconsta e as remove
        moedas_coletadas = arcade.check_for_collision_with_list(self.jogador, self.sprite_moeda)
        for moeda in moedas_coletadas:
            moeda.remove_from_sprite_lists()

        # Se não houver mais moedas, mostrar a tela de vitória
        if len(self.sprite_moeda) == 0:
            print("[DEBUG] Todas as moedas coletadas — mostrando TelaVitoria")
            self.window.show_view(TelaVitoria())

    #Define a movimentação do jogaodor para as direções e as teclas
    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            self.jogador.change_x = -VELOCIDADE_JOGADOR
        elif key == arcade.key.D:
            self.jogador.change_x = VELOCIDADE_JOGADOR
        elif key == arcade.key.W:
            self.jogador.change_y = VELOCIDADE_JOGADOR
        elif key == arcade.key.S:
            self.jogador.change_y = -VELOCIDADE_JOGADOR
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

    #Parar movimento soltando a tecla
    def on_key_release(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.D:
            self.jogador.change_x = 0
        elif key == arcade.key.W or key == arcade.key.S:
            self.jogador.change_y = 0

#Criação da tela de vitória do jogo
class TelaVitoria(arcade.View):

    def __init__(self):
        super().__init__()

    #Definir cor
    def on_show(self):
        arcade.set_background_color(arcade.color.LIGHT_GREEN)
        print("[DEBUG] TelaVitoria exibida")

    #Escrever na tela
    def on_draw(self):
        self.clear()
        arcade.draw_text("Parabéns! Você coletou todas as moedas!", LARGURA // 2, ALTURA // 2, arcade.color.YELLOW, 30, anchor_x="center")
        arcade.draw_text("Pressione ENTER ou R para jogar novamente", LARGURA // 2, ALTURA // 2 - 50, arcade.color.BLACK, 20, anchor_x="center")
        arcade.draw_text("Pressione ESC para sair", LARGURA // 2, ALTURA // 2 - 80, arcade.color.BLACK, 20, anchor_x="center")

    #Teclas e suas funções
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.R:
            self.window.show_view(TelaJogo())
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

#Por fim criar a janela do jogo
class MeuJogo(arcade.Window):

    def __init__(self):
        super().__init__(LARGURA, ALTURA, TITULO) #Define suas propriedades
        self.show_view(TelaInicial()) #Mostra a tela


def executar(): #Executa todo o jogo
    tela = MeuJogo()
    arcade.run()


if __name__ == "__main__": #Garante que o jogo rode se o arquivo for executado diretamente
    executar()
     