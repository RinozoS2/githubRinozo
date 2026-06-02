# No terminal, execute: pip install arcade
import arcade

# Constantes
LARGURA = 800
ALTURA = 600
TITULO = "Meu Joguinho"


class Player(arcade.Sprite):

    def __init__(self):
        super().__init__("buxa.jpg", scale=0.6)
        self.textura_direita = arcade.load_texture("buxa.jpg")
        self.textura_esquerda = arcade.load_texture("buxa.jpg")

    def update(self, delta_time):
        pass


class Moeda(arcade.Sprite):
    def __init__(self):
        super().__init__("moeda.png", scale=0.2)
        self.textura_direita = arcade.load_texture("moeda.png")

    def update(self, delta_time):
        pass
class MeuJogo(arcade.Window):

    def __init__(self):
        super().__init__(LARGURA, ALTURA, TITULO)
        arcade.set_background_color((arcade.color.BABY_BLUE_EYES))

        # Configuração do jogador
        self.jogador = Player()
        self.jogador.center_x = LARGURA // 2
        self.jogador.center_y = 200

        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.jogador)

        self.moeda = Moeda()
        self.moeda.center_x = 280
        self.moeda.center_y = 100

        self.sprite_moeda = arcade.SpriteList()
        self.sprite_moeda.append(self.moeda)


    def on_draw(self):
        self.clear()
        self.sprite_jogador.draw()
        self.sprite_moeda.draw()

    def on_update(self, delta_time):
        # Atualiza a lógica do jogo a cada quadro
        self.sprite_jogador.update()


def executar():
    tela = MeuJogo()
    arcade.run()


if __name__ == "__main__":
    executar()
    