import arcade

LARGURA = 800
ALTURA = 600
TITULO = "subway surfers abrasileirado"

class Player(arcade.Sprite):

    def __init__(self):
        super().__init__("protagonista_parado.jpg",scale = 0.4)

class Moeda(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__("moeda_simples.jpg", scale = 0.2)

class Inimigo_1(arcade.Sprite):

    def __init__(self):
        super().__init__("Inimigos.png", scale = 0.4)

class Inimigo_2(arcade.Sprite):

    def __init__(self):
        super().__init__("InimigoParado.png", scale = 0.8)

class TelaInicial(arcade.View):

    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.draw_text("[J] Jogar",LARGURA // 2, ALTURA // 2, arcade.color.BLACK, 30, anchor_x="center")
        arcade.draw_text("[I] Instruções ",LARGURA // 2, ALTURA // 2, arcade.color.BLACK, 30, anchor_x="center")
        arcade.draw_text("[S] Sobre o jogo",LARGURA // 2, ALTURA // 2, arcade.color.BLACK, 30, anchor_x="center")
        arcade.draw_text("[ESC] Sair",LARGURA // 2, ALTURA // 2, arcade.color.BLACK, 30, anchor_x="center")

        def on_key_press(self, key, modifiers):
            ##Abrir as janelas
            pass

class telaInstrucoes(arcade.view):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.draw_text("[A] se move para a esquerda, [S] se move para baixo, [W] se move para cima e [D] se move para a direita, você deve coletar o máximo de moedas possíveis sem ser pego pelo LULE", LARGURA // 2, ALTURA // 2, arcade.color.BLACK, 30, anchor_x="center")

class sobre_o_jogo(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.draw_text("Este jogo foi criado pelos alunos Enzo Ryan Barbosa Ferreira e Brian Caetano Galdino, ambos do terceiro ano de informática do IFPR ",LARGURA // 2, ALTURA // 2, arcade.color.BLACK, 30, anchor_x="center")
class TelaJogo(arcade.View):

    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BABY_BLUE_EYES) 