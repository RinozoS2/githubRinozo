import arcade #funcionamento do código
import random #posições e movimentos aleatórios

#Propriedades da janela
LARGURA = 800
ALTURA = 600
TITULO = "Ataque do titã"

#Fisíca das bordas, impede que sai da tela
#Se rebater for True, ele retorna
def confBordas(objeto, rebater=False):
    if objeto.right > LARGURA:
        objeto.right = LARGURA
        if rebater:
            objeto.change_x *= -1

    if objeto.left < 0:
        objeto.left = 0
        if rebater:
            objeto.change_x *= -1

    if objeto.top > ALTURA:
        objeto.top = ALTURA
        if rebater:
            objeto.change_y *= -1
        else:
            objeto.change_y = 0

    if objeto.bottom < 0:
        objeto.bottom = 0
        if rebater:
            objeto.change_y *= -1
        else:
            objeto.change_y = 0


#As classes são como fábricas de objetos,
#Cada um tem sua perculariedade

#Moeda comum, que dá 1 ponto, estática e coletável
class Moeda(arcade.Sprite):

    def __init__(self):
        super().__init__("coin_sp.png", scale = 0.12)
        self.change_x = 0
        self.change_y = 0

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left < 0 or self.right > LARGURA:
            self.change_x *= -1

        if self.bottom < 0 or self.top > ALTURA:
            self.change_y *= -1  

        confBordas(self, rebater = False)  

#Moeda especial, única e coletável, da 5 pontos e tem física para se mover
class MoedaEspecial(arcade.Sprite):
    def __init__(self):
        super().__init__("coin_sp2.png", scale = 0.35)
        self.change_x = 0
        self.change_y = 0

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        confBordas(self, rebater = True)

#Classe do jogador, personagem principal, se move em AWSD
#Possuí animação de acordo com a direção, não sai da tela   
class Player(arcade.Sprite):

    def __init__(self):
        super().__init__("p1_idle.png",scale = 1)
        self.change_x = 0
        self.change_y = 0
        self.texture_parado = arcade.load_texture("p1_idle.png")
        self.textura_direita = arcade.load_texture("p1_right.png")
        self.textura_esquerda = arcade.load_texture("p1_left.png")
        self.textura_cima = arcade.load_texture("p1_up.png")
        self.textura_baixo = arcade.load_texture("p1_down.png")

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y
      
        if self.change_x > 0:
            self.texture = self.textura_direita
        elif self.change_x < 0:
            self.texture = self.textura_esquerda

        if self.change_y > 0:
            self.texture = self.textura_cima
        elif self.change_y < 0:
            self.texture = self.textura_baixo

        if self.right > LARGURA:
            self.change_x = 0
            self.right = LARGURA

        if self.left < 0:
            self.change_x = 0
            self.left = 0

        if self.top > ALTURA:
            self.change_y = 0
            self.top = ALTURA

        if self.bottom < 0:
            self.change_y = 0
            self.bottom = 0    

        confBordas(self, rebater =False)

    
#Inimigo simples que anda de forma aleatória e repetidade,
#retira 1 ponto do jogador ao colidir e aparece em outra posição
class TitaIrracional(arcade.Sprite):

    def __init__(self):
        #Define a velocidade e a direção aleatória que o titã seguirá
        super().__init__("enemy_1.png", scale = 1)
        self.change_x = random.choice([-1.5, -1.0, 1.0, 1.5])
        self.change_y = random.choice([-1.5, -1.0, 1.0, 1.5])

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if random.random() < 0.01:
            self.change_x = random.choice([-1.5, -1.0, 1.0, 1.5])
            self.change_y = random.choice([-1.5, -1.0, 1.0, 1.5])

        confBordas(self, rebater = False)
        if self.right >= LARGURA or self.left <= 0:
            self.change_x *= -1
        if self.top >= ALTURA or self.bottom <= 0:
            self.change_y *= -1


#Inimigo que persegue o jogador, pode causar a eliminação do player
class TitaPuro(arcade.Sprite):

    def __init__(self, jogador):
        super().__init__("enemy_2.png", scale = 0.8)

        #Define quem ele vai perseguir desde o começo e sua velocidade
        self.jogador = jogador
        self.velocidade = 2.5

    def update(self, delta_time):
        dx = self.jogador.center_x - self.center_x
        dy = self.jogador.center_y - self.center_y

        distancia = (dx ** 2 + dy ** 2) ** 0.5
        if distancia > 0:
            dx /= distancia
            dy /= distancia

        self.change_x = dx * self.velocidade
        self.change_y = dy * self.velocidade

        self.center_x += self.change_x
        self.center_y += self.change_y

        confBordas(self, rebater = False)


#Criação da tela de menu com suas propriedades e o jpg
class TelaMenu(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.WHITE)
        self.cenario_sprite = arcade.Sprite("cenario_inicial.jpg")
        self.cenario_sprite.width = LARGURA
        self.cenario_sprite.height = ALTURA
        self.cenario_sprite.center_x = LARGURA / 2
        self.cenario_sprite.center_y = ALTURA / 2
        self.sprite_cenario = arcade.SpriteList()
        self.sprite_cenario.append(self.cenario_sprite)
       
        

    def on_draw(self):
        self.clear()
        self.sprite_cenario.draw()

        arcade.draw_text("Ataque do Titã", LARGURA / 2, 520,
                         arcade.color.WHITE, 50, anchor_x="center")
        arcade.draw_text("MENU", LARGURA / 2, 420,
                         arcade.color.WHITE, 40, anchor_x="center")

        arcade.draw_text("J - JOGAR", 220, 320, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text("S - SOBRE O JOGO", 220, 280, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text("I - INSTRUÇÃO", 220, 240, arcade.color.WHITE, 20, anchor_x="left")

        arcade.draw_text("Pressione a tecla correspondente", LARGURA / 2, 160,
                         arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("ESC - SAIR", LARGURA / 2, 130,
                         arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self,key,modifiers):
        if key == arcade.key.I:
            tela_instrucao = TelaInstrucao()
            self.window.show_view(tela_instrucao)
        elif key == arcade.key.S:
            tela_sobre = TelaSobre()
            self.window.show_view(tela_sobre)
        elif key == arcade.key.J:
            tela_jogo = JogoAtaqueDoTita()
            self.window.show_view(tela_jogo)
        elif key == arcade.key.ESCAPE:
            arcade.close_window()


#Criação da tela de instrução e suas propriedades
class TelaInstrucao(arcade.View):

    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)
        self.cenario_sprite = arcade.Sprite("cenario_inicial.jpg")
        self.cenario_sprite.width = LARGURA
        self.cenario_sprite.height = ALTURA
        self.cenario_sprite.center_x = LARGURA / 2
        self.cenario_sprite.center_y = ALTURA / 2
        self.sprite_cenario = arcade.SpriteList()
        self.sprite_cenario.append(self.cenario_sprite)

    def on_draw(self):
        self.clear()
        self.sprite_cenario.draw()

        arcade.draw_text("INSTRUÇÃO", LARGURA / 2, 520,
                         arcade.color.BLUE, 40, anchor_x="center")

        arcade.draw_text("OBJETIVOS", 120, 440,
                         arcade.color.BLUE, 24, anchor_x="left")
        arcade.draw_text("- Colete 25 Titãs (1 ponto)", 120, 410,
                         arcade.color.WHITE, 16, anchor_x="left")
        arcade.draw_text("- Colete 1 Filtro de gás (5 pontos)", 120, 385,
                         arcade.color.WHITE, 16, anchor_x="left")
        arcade.draw_text("- Total de 26 pontos para vencer", 120, 360,
                         arcade.color.WHITE, 16, anchor_x="left")

        arcade.draw_text("INIMIGOS", 120, 320,
                         arcade.color.BLUE, 24, anchor_x="left")
        arcade.draw_text("Titã Irracional: Anda de forma aleatória para te atacar (-1 ponto)", 120, 290,
                         arcade.color.WHITE, 16, anchor_x="left")
        arcade.draw_text("Titã Puro: te persegue para sempre, não fique perto dele! (Eliminado)", 120, 265,
                         arcade.color.WHITE, 16, anchor_x="left")

        arcade.draw_text("CONTROLES", 450, 440,
                         arcade.color.BLUE, 24, anchor_x="left")
        arcade.draw_text("W - subir", 450, 410,
                         arcade.color.WHITE, 16, anchor_x="left")
        arcade.draw_text("A - esquerda", 450, 385,
                         arcade.color.WHITE, 16, anchor_x="left")
        arcade.draw_text("D - direita", 450, 360,
                         arcade.color.WHITE, 16, anchor_x="left")
        arcade.draw_text("S - baixo", 450, 335,
                         arcade.color.WHITE, 16, anchor_x="left")

        arcade.draw_text("ESC ou M para voltar ao menu", LARGURA / 2, 80,
                         arcade.color.WHITE, 16, anchor_x="center")
        
    def on_key_press(self, key,modyfiers):
        if key == arcade.key.ESCAPE or key == arcade.key.M:
            tela_inicial = TelaMenu()
            self.window.show_view(tela_inicial)

#Criação da tela de Informações e suas prorpeidades
class TelaSobre(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)
        self.cenario_sprite = arcade.Sprite("cenario_inicial.jpg")
        self.cenario_sprite.width = LARGURA
        self.cenario_sprite.height = ALTURA
        self.cenario_sprite.center_x = LARGURA / 2
        self.cenario_sprite.center_y = ALTURA / 2
        self.sprite_cenario = arcade.SpriteList()
        self.sprite_cenario.append(self.cenario_sprite)

    def on_draw(self):
        self.clear()
        self.sprite_cenario.draw()

        arcade.draw_text("SOBRE O JOGO", LARGURA / 2, 520,
                         arcade.color.BLUE, 40, anchor_x="center")
        arcade.draw_text("Feito por Enzo e Brian", LARGURA / 2, 460,
                         arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("Inspirado em Attack on Titan", LARGURA / 2, 435,
                         arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("Com ajuda do professor", LARGURA / 2, 410,
                         arcade.color.WHITE, 18, anchor_x="center")

        arcade.draw_text("Objetivo:", 120, 340,
                         arcade.color.BLUE, 20, anchor_x="left")
        arcade.draw_text("Colete todos os recursos sem ser pego pelos inimigos.", 120, 310,
                         arcade.color.WHITE, 16, anchor_x="left")

        arcade.draw_text("Teclas:", 120, 260,
                         arcade.color.BLUE, 20, anchor_x="left")
        arcade.draw_text("W, A, S, D para mover", 120, 230,
                         arcade.color.WHITE, 16, anchor_x="left")

        arcade.draw_text("ESC ou M para voltar ao menu", LARGURA / 2, 90,
                         arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.M:
            tela_menu = TelaMenu()
            self.window.show_view(tela_menu)


#Tela de vitória,  recebe os parametros da pontuação e do tempo do jogador
#Valores numérios que são descontados ou aumentados
class TelaGanhou(arcade.View):
    def __init__(self, pontuacao, tempo):
        super().__init__()
        self.pontuacao = pontuacao
        self.tempo = tempo
        arcade.set_background_color(arcade.color.PURPLE)
        self.cenario_sprite = arcade.Sprite("cenario_inicial.jpg")
        self.cenario_sprite.width = LARGURA
        self.cenario_sprite.height = ALTURA
        self.cenario_sprite.center_x = LARGURA / 2
        self.cenario_sprite.center_y = ALTURA / 2
        self.sprite_cenario = arcade.SpriteList()
        self.sprite_cenario.append(self.cenario_sprite)

    def on_draw(self):
        self.clear()
        self.sprite_cenario.draw()
        arcade.draw_text("PARABÉNS", LARGURA / 2, 470,
                         arcade.color.WHITE, 50, anchor_x="center")
        if self.pontuacao == 30:
            arcade.draw_text("INACREDITÁVEL", LARGURA / 2, 380,
                             arcade.color.WHITE, 50, anchor_x="center")
        arcade.draw_text(f"PONTUAÇÃO {self.pontuacao}", LARGURA / 2, 300,
                         arcade.color.WHITE, 40, anchor_x="center")
        arcade.draw_text(f"TEMPO {self.tempo:.1f}s", LARGURA / 2, 240,
                         arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("Pressione ESC para voltar ao menu", LARGURA / 2, 160,
                         arcade.color.WHITE, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(TelaMenu())


#Tela de derrota, é disparada através do evento no titã puro, que persegue o jogador
class TelaPerdeu(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_RED)

    def on_draw(self):
        self.clear()
        arcade.draw_text("VOCÊ PERDEU", LARGURA / 2, ALTURA / 2 + 40,
                         arcade.color.WHITE, 50, anchor_x="center")
        arcade.draw_text("O Titã Puro te alcançou.", LARGURA / 2, ALTURA / 2,
                         arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("Pressione ESC para voltar ao menu", LARGURA / 2, ALTURA / 2 - 60,
                         arcade.color.WHITE, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(TelaMenu())


#Janela Final com as váriaveis necessárias
class JogoAtaqueDoTita(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)
        
        self.pontuacao = 0
        self.registro = 0
        self.velocidade = 5
        self.tempo = 0
        self.mensagem = ""
        self.tempo_mensagem = 0
        self.velocidade_ini = 2
        self.jogo_rodando = True
        



        self.jogador = Player()
        self.jogador.center_x = 400
        self.jogador.center_y = 0
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.jogador)

        self.sprite_moedas = arcade.SpriteList()

        for i in range(25):
            self.moeda = Moeda()
            self.moeda.center_x = random.randint(50, LARGURA - 50)
            self.moeda.center_y = random.randint(50, ALTURA - 50)
            self.sprite_moedas.append(self.moeda)
        print(len(self.sprite_moedas))

        self.tita_irracional = TitaIrracional()
        self.tita_irracional.center_x = 0
        self.tita_irracional.center_y = 90
        self.tita_irracional.change_x = self.velocidade_ini
        self.tita_irracional.change_y = self.velocidade_ini
        self.sprite_titas_irracionais = arcade.SpriteList()
        self.sprite_titas_irracionais.append(self.tita_irracional)

        self.sprite_titas_puros = arcade.SpriteList()
        self.tita_puro = TitaPuro(self.jogador)
        self.tita_puro.center_x = 800
        self.tita_puro.center_y = 600
        self.sprite_titas_puros.append(self.tita_puro)


        

        self.sprite_moeda_especial = arcade.SpriteList()
        self.moeda_especial = MoedaEspecial()
        self.moeda_especial.center_x = random.randint(100, LARGURA - 100)
        self.moeda_especial.center_y = random.randint(100, ALTURA - 100)
        self.moeda_especial.change_x = self.velocidade
        self.moeda_especial.change_y = self.velocidade
        

        self.sprite_moeda_especial.append(self.moeda_especial)
    def on_draw(self):
        self.clear()
        self.sprite_titas_irracionais.draw()
        self.sprite_moedas.draw()
        self.sprite_moeda_especial.draw()
        self.sprite_jogador.draw()
        self.sprite_titas_puros.draw()
        arcade.draw_text(f"Pontos Coletados: {self.pontuacao}", 10, 570,
                         arcade.color.WHITE, 16)
        arcade.draw_text(f"Tempo: {self.tempo:.1f}s", 10, 545,
                         arcade.color.WHITE, 16)
        arcade.draw_text("Moedas restantes: " + str(len(self.sprite_moedas) + len(self.sprite_moeda_especial)),
                         10, 520, arcade.color.WHITE, 16)
        if self.tempo_mensagem > 0:
            arcade.draw_text(self.mensagem, 220, 515, arcade.color.WHITE, 20)



        

    def on_update(self, delta_time):
        self.sprite_jogador.update(delta_time)
        self.sprite_moedas.update(delta_time)
        self.sprite_titas_irracionais.update(delta_time)
        self.sprite_titas_puros.update(delta_time)
        self.sprite_moeda_especial.update(delta_time)
        self.tempo += delta_time
        if self.tempo_mensagem > 0:
            self.tempo_mensagem -= delta_time

        moedas_colididas = arcade.check_for_collision_with_list(self.jogador, self.sprite_moedas)
        moeda_especial_colidida = arcade.check_for_collision_with_list(self.jogador, self.sprite_moeda_especial)
        titas_puros = arcade.check_for_collision_with_list(self.jogador, self.sprite_titas_puros)
        titas_irracionais = arcade.check_for_collision_with_list(self.jogador, self.sprite_titas_irracionais)

        if titas_puros:
            self.window.show_view(TelaPerdeu())
            return

        for tita in titas_irracionais:
            self.pontuacao -= 1
            print("Colidiu com o Titã Irracional!")
            self.mensagem = "TOCOU NO TITÃ IRRACIONAL! PERDEU 1 PONTO"
            self.tempo_mensagem = 1.5
            while True:
                tita.center_x = random.randint(50, LARGURA - 50)
                tita.center_y = random.randint(50, ALTURA - 50)
                if arcade.get_distance_between_sprites(tita, self.jogador) >= 250:
                    break

        for moeda in moedas_colididas:
            moeda.remove_from_sprite_lists()
            self.pontuacao += 1
            self.registro += 1
            print(self.pontuacao)

        for moeda_especial in moeda_especial_colidida:
            moeda_especial.remove_from_sprite_lists()
            self.pontuacao += 5
            self.registro += 1
            print(self.pontuacao)

        #O len conta quantos elementos tem na lista, se for 0, significa que o jogador coletou todas as moedas
        if len(self.sprite_moeda_especial) == 0 and len(self.sprite_moedas) == 0:
            tela_final = TelaGanhou(self.pontuacao, self.tempo)
            self.window.show_view(tela_final)

        

        

                            
        

    def on_key_press(self, key, modifiers):
        if key == arcade.key.D:
            self.jogador.change_x = self.velocidade
        elif key == arcade.key.A:
            self.jogador.change_x = -self.velocidade
        elif key == arcade.key.W:
            self.jogador.change_y = self.velocidade
        elif key == arcade.key.S:
            self.jogador.change_y = -self.velocidade

        elif key == arcade.key.ESCAPE:
            tela_menu = TelaMenu()
            self.window.show_view(tela_menu)


    def on_key_release(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.D:
            self.jogador.change_x = 0
            self.jogador.texture = self.jogador.texture_parado
        elif key == arcade.key.W or key == arcade.key.S:
            self.jogador.change_y = 0
            self.jogador.texture = self.jogador.texture_parado
        
    


def main():
    janela = arcade.Window(LARGURA, ALTURA, TITULO)
    tela_inicial = TelaMenu()
    janela.show_view(tela_inicial)
    arcade.run()


if __name__ == "__main__":
    main()