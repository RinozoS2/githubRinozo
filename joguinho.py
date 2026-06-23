import random
import arcade

# Constantes
LARGURA = 800
ALTURA = 600
TITULO = "Meu Joguinho"
VELOCIDADE_JOGADOR = 5
NUMERO_MOEDAS = 12

# Classe Player
class Player(arcade.Sprite):

    def __init__(self):
        super().__init__("buxa.jpg", scale=0.4)

    def update(self, delta_time: float = 0):
        super().update(delta_time)
        # Mantém o jogador dentro da janela
        if self.left < 0:
            self.left = 0
        if self.right > LARGURA:
            self.right = LARGURA
        if self.bottom < 0:
            self.bottom = 0
        if self.top > ALTURA:
            self.top = ALTURA


# Classe Moeda
class Moeda(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__("moeda.png", scale=0.2)
        self.center_x = x
        self.center_y = y


# Tela Inicial
class TelaInicial(arcade.View):

    def __init__(self):
        super().__init__()
        
    def on_draw(self):
        self.clear()
        arcade.draw_text("Jogo - O coletor de moedas", LARGURA // 2, ALTURA // 2, arcade.color.BLACK, 30, anchor_x="center")
        arcade.draw_text("Pressione ENTER para começar", LARGURA // 2, ALTURA // 2 - 50, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Pressione ESC para sair", LARGURA // 2, ALTURA // 2 - 80, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Use as teclas W, A, S, D para se mover", LARGURA // 2, ALTURA // 2 - 120, arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            self.window.show_view(TelaJogo())
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

# Tela do Jogo
class TelaJogo(arcade.View):

    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BABY_BLUE_EYES)

        self.jogador = Player()
        self.jogador.center_x = LARGURA // 2
        self.jogador.center_y = 200

        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.jogador)

        self.sprite_moeda = arcade.SpriteList()
        self._criar_moedas()

    def _criar_moedas(self):
        for _ in range(NUMERO_MOEDAS):
            x = random.randint(50, LARGURA - 50)
            y = random.randint(50, ALTURA - 50)
            moeda = Moeda(x, y)
            self.sprite_moeda.append(moeda)

    def on_draw(self):
        self.clear()
        self.sprite_moeda.draw()
        self.sprite_jogador.draw()

    def on_update(self, delta_time):
        # Atualiza os sprites passando o delta_time para propagar movimento
        self.sprite_jogador.update(delta_time)

        moedas_coletadas = arcade.check_for_collision_with_list(self.jogador, self.sprite_moeda)
        for moeda in moedas_coletadas:
            moeda.remove_from_sprite_lists()

        # Se não houver mais moedas, mostrar a tela de vitória
        if len(self.sprite_moeda) == 0:
            print("[DEBUG] Todas as moedas coletadas — mostrando TelaVitoria")
            self.window.show_view(TelaVitoria())

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

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.D:
            self.jogador.change_x = 0
        elif key == arcade.key.W or key == arcade.key.S:
            self.jogador.change_y = 0

class TelaVitoria(arcade.View):

    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.LIGHT_GREEN)
        print("[DEBUG] TelaVitoria exibida")

    def on_draw(self):
        self.clear()
        arcade.draw_text("Parabéns! Você coletou todas as moedas!", LARGURA // 2, ALTURA // 2, arcade.color.YELLOW, 30, anchor_x="center")
        arcade.draw_text("Pressione ENTER ou R para jogar novamente", LARGURA // 2, ALTURA // 2 - 50, arcade.color.BLACK, 20, anchor_x="center")
        arcade.draw_text("Pressione ESC para sair", LARGURA // 2, ALTURA // 2 - 80, arcade.color.BLACK, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.R:
            self.window.show_view(TelaJogo())
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

class MeuJogo(arcade.Window):

    def __init__(self):
        super().__init__(LARGURA, ALTURA, TITULO)
        self.show_view(TelaInicial())


def executar():
    tela = MeuJogo()
    arcade.run()


if __name__ == "__main__":
    executar()
     