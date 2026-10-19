# Arcade fornece a janela, as telas, os sprites, o desenho e os motores de física.
import arcade #funcionamento do código
# random é usado para variar as posições e direções dos elementos do jogo.
import random #posições e movimentos aleatórios
# Pillow permite recortar, redimensionar e espelhar imagens para as animações.
from PIL import Image
# Funções da camada de persistência: inicialização e leitura/gravação do ranking.
from ranking import inicializar_banco, obter_ranking, registrar_resultado

#Propriedades da janela
# Configuração global da área de jogo; coordenadas e limites usam esses valores.
LARGURA = 800
ALTURA = 600
GRAVIDADE = 0.45

TITULO = "Ataque do titã"

#Fisíca das bordas, impede que sai da tela
#Se rebater for True, ele retorna
# Mantém um sprite dentro da janela. Quando rebater=True, a velocidade inverte
# no eixo da colisão, que é o modelo simples de reflexão usado para os itens móveis.
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
# Cada classe de sprite encapsula aparência, estado e atualização de um objeto do jogo.

#Moeda comum, que dá 1 ponto, estática e coletável
# Moedas comuns são coletáveis e valem um ponto; sua posição não muda por padrão.
class Moeda(arcade.Sprite):

    def __init__(self):
        # Sprite carrega a imagem e a escala define seu tamanho visual.
        super().__init__("coin_sp.png", scale = 0.12)
        self.change_x = 0
        self.change_y = 0

    def update(self, delta_time):
        # Integra o movimento somando a velocidade às coordenadas atuais.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Inverte a componente da velocidade ao tocar nas laterais.
        if self.left < 0 or self.right > LARGURA:
            self.change_x *= -1

        # Inverte o movimento vertical quando ultrapassa o topo ou o chão.
        if self.bottom < 0 or self.top > ALTURA:
            self.change_y *= -1  

        # A segunda verificação limita a posição às bordas da janela.
        confBordas(self, rebater = False)  

#Moeda especial, única e coletável, da 5 pontos e tem física para se mover
# Moeda especial única: a tela de jogo configura sua velocidade e ela vale cinco pontos.
class MoedaEspecial(arcade.Sprite):
    def __init__(self):
        super().__init__("coin_sp2.png", scale = 0.35)
        self.change_x = 0
        self.change_y = 0

    def update(self, delta_time):
        # Movimento linear simples, com uma componente de velocidade por eixo.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Reflete em todas as bordas, preservando a moeda dentro da área visível.
        confBordas(self, rebater = True)

#Classe do jogador, personagem principal, se move em AWSD
#Possuí animação de acordo com a direção, não sai da tela   
# Jogador controlado pelo teclado. As texturas representam repouso, salto,
# dano e caminhada para cada lado; a física vertical é aplicada pela tela do jogo.
class Player(arcade.Sprite):

    def __init__(self):
        super().__init__("p1_idle.png",scale = 1)
        # Estado inicial do movimento e dos temporizadores da animação/dano.
        self.change_x = 0
        self.change_y = 0
        self.texture_parado = arcade.load_texture("p1_idle.png")
        self.textura_pulo = arcade.load_texture("p1_up.png")
        self.textura_pulo_esquerda = self.textura_pulo.flip_left_right()
        self.esta_pulando = False
        self.tempo_dano = 0
        self.tempo_animacao = 0
        self.indice_animacao = 0
        self.duracao_quadro = 0.1

        imagem_parada = self.texture_parado.image
        imagem_dano = arcade.load_texture("damage.png").image
        # A imagem de dano é redimensionada ao tamanho da textura normal para
        # que a troca de aparência não altere a caixa de colisão do personagem.
        self.textura_dano = arcade.Texture(
            imagem_dano.resize(imagem_parada.size, Image.Resampling.LANCZOS),
            hash="p1-damage",
        )
        # A caixa alfa identifica somente os pixels visíveis do personagem.
        # Ela serve de referência para padronizar os quadros do spritesheet.
        esquerda, topo, direita, base = imagem_parada.getchannel("A").getbbox()
        tamanho_personagem = (direita - esquerda, base - topo)
        self.texturas_andando = []
        self.texturas_andando_esquerda = []

        # Divide a folha em oito quadros e normaliza o tamanho/alinhamento de
        # cada recorte; a versão espelhada evita manter uma segunda animação.
        quadros = arcade.load_spritesheet("p1_animation.png").get_texture_grid(
            (271, 724), columns=8, count=8
        )
        for indice, quadro in enumerate(quadros):
            imagem_quadro = quadro.image
            limites = imagem_quadro.getchannel("A").getbbox()
            recorte = imagem_quadro.crop(limites).resize(
                tamanho_personagem, Image.Resampling.LANCZOS
            )
            imagem_normalizada = Image.new("RGBA", imagem_parada.size)
            imagem_normalizada.alpha_composite(recorte, (esquerda, topo))
            self.texturas_andando.append(
                arcade.Texture(imagem_normalizada, hash=f"p1-walk-right-{indice}")
            )
            self.texturas_andando_esquerda.append(
                arcade.Texture(
                    imagem_normalizada.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                    hash=f"p1-walk-left-{indice}",
                )
            )

    def receber_dano(self):
        # Reinicia a janela de tempo durante a qual o sprite aparece danificado.
        self.tempo_dano = 1.5

    def update(self, delta_time):
        # Movimento horizontal e contenção: o jogador para na borda em vez de sair.
        self.center_x += self.change_x

        if self.right > LARGURA:
            self.change_x = 0
            self.right = LARGURA

        if self.left < 0:
            self.change_x = 0
            self.left = 0

        confBordas(self, rebater =False)

        # Dano tem prioridade visual sobre as demais animações até o temporizador
        # acabar; max evita que o tempo restante fique negativo.
        if self.tempo_dano > 0:
            self.tempo_dano = max(0, self.tempo_dano - delta_time)
            if self.tempo_dano > 0:
                self.texture = self.textura_dano
                return

        # No ar, usa a pose de salto orientada para o lado do deslocamento.
        if self.esta_pulando:
            self.texture = (
                self.textura_pulo_esquerda if self.change_x < 0
                else self.textura_pulo
            )
        elif self.change_x != 0:
            # Acumula tempo real e avança um ou mais quadros conforme a duração
            # configurada, fazendo a animação depender do tempo e não do FPS.
            self.tempo_animacao += delta_time
            while self.tempo_animacao >= self.duracao_quadro:
                self.tempo_animacao -= self.duracao_quadro
                self.indice_animacao = (self.indice_animacao + 1) % len(
                    self.texturas_andando
                )
            quadros = (
                self.texturas_andando_esquerda
                if self.change_x < 0
                else self.texturas_andando
            )
            self.texture = quadros[self.indice_animacao]
        else:
            # Parado: reinicia o ciclo para que a próxima caminhada comece no quadro 0.
            self.tempo_animacao = 0
            self.indice_animacao = 0
            self.texture = self.texture_parado

    
#Inimigo simples que anda de forma aleatória e repetidade,
#retira 1 ponto do jogador ao colidir e aparece em outra posição
# Bloco de cenário usado como chão e plataforma; o motor de física trata-o como
# obstáculo estático contra o qual o jogador e inimigos podem colidir.
class Bloco(arcade.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__("muro.jpg", scale = 1)

        # As coordenadas recebidas definem o centro do bloco no cenário.
        self.center_x = x
        self.center_y = y

class TitaIrracional(arcade.Sprite):

    def __init__(self):
        #Define a velocidade e a direção aleatória que o titã seguirá
        # Começa com componentes de velocidade aleatórias nos dois eixos.
        super().__init__("enemy_1.png", scale = 1)
        self.change_x = random.choice([-1.5, -1.0, 1.0, 1.5])
        self.change_y = random.choice([-1.5, -1.0, 1.0, 1.5])

    def update(self, delta_time):
        # Atualiza a posição; ocasionalmente sorteia outra direção para tornar
        # a trajetória imprevisível sem depender de uma rota pré-definida.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # A cada atualização, há 1% de chance de escolher uma nova direção.
        if random.random() < 0.01:
            self.change_x = random.choice([-1.5, -1.0, 1.0, 1.5])
            self.change_y = random.choice([-1.5, -1.0, 1.0, 1.5])

        # Limita o inimigo à janela e inverte a velocidade ao encostar nas bordas.
        confBordas(self, rebater = False)
        if self.right >= LARGURA or self.left <= 0:
            self.change_x *= -1
        if self.top >= ALTURA or self.bottom <= 0:
            self.change_y *= -1


#Inimigo que persegue o jogador, pode causar a eliminação do player
# Inimigo perseguidor: acompanha a posição do jogador e encerra a partida ao
# colidir com ele, segundo a regra implementada na atualização da tela de jogo.
class TitaPuro(arcade.Sprite):

    def __init__(self, jogador):
        super().__init__("enemy_2.png", scale = 0.8)

        #Define quem ele vai perseguir desde o começo e sua velocidade
        self.jogador = jogador
        self.velocidade = 2.0
        self.change_x = 0
        self.change_y = 0

    def update(self, delta_time):
        #Calcular a direção de perseguição em ambos os eixos
        # O vetor entre os centros aponta do inimigo para o jogador.
        dx = self.jogador.center_x - self.center_x
        dy = self.jogador.center_y - self.center_y

        #Calcular distância
        # Norma euclidiana do vetor: transforma a diferença em uma distância.
        distancia = (dx ** 2 + dy ** 2) ** 0.5
        
        if distancia > 0:
            #Normalizar a direção
            # Normalizar divide cada componente pelo comprimento do vetor.
            # Assim, a direção tem comprimento 1 e a velocidade não cresce
            # quando o jogador está mais distante.
            dx /= distancia
            dy /= distancia
            
            #Aplicar velocidade em ambas as direções
            # Multiplicar o vetor unitário pela velocidade fixa gera o movimento.
            self.change_x = dx * self.velocidade
            self.change_y = dy * self.velocidade
        else:
            # Quando os centros coincidem, a direção não pode ser normalizada.
            self.change_x = 0
            self.change_y = 0


#Criação da tela de menu com suas propriedades e o jpg
# Tela inicial: apresenta o fundo e encaminha cada tecla para a tela escolhida.
class TelaMenu(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.WHITE)
        # Ajusta o cenário à janela e guarda-o em SpriteList para desenhá-lo.
        self.cenario_sprite = arcade.Sprite("cenario_inicial.jpg")
        self.cenario_sprite.width = LARGURA
        self.cenario_sprite.height = ALTURA
        self.cenario_sprite.center_x = LARGURA / 2
        self.cenario_sprite.center_y = ALTURA / 2
        self.sprite_cenario = arcade.SpriteList()
        self.sprite_cenario.append(self.cenario_sprite)
       
        

    def on_draw(self):
        # on_draw é chamado pelo ciclo do Arcade para redesenhar a tela.
        self.clear()
        self.sprite_cenario.draw()

        # As posições definem a composição visual do título e das opções.
        arcade.draw_text("Ataque do Titã", LARGURA / 2, 520,
                         arcade.color.WHITE, 50, anchor_x="center")
        arcade.draw_text("MENU", LARGURA / 2, 420,
                         arcade.color.WHITE, 40, anchor_x="center")

        arcade.draw_text("J - JOGAR", 220, 320, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text("S - SOBRE O JOGO", 220, 280, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text("I - INSTRUÇÃO", 220, 240, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text("R - RANKING", 220, 200, arcade.color.WHITE, 20, anchor_x="left")

        arcade.draw_text("Pressione a tecla correspondente", LARGURA / 2, 150,
                         arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("ESC - SAIR", LARGURA / 2, 120,
                         arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self,key,modifiers):
        # Cada tecla troca a View ativa; ESC encerra o loop da janela.
        if key == arcade.key.I:
            tela_instrucao = TelaInstrucao()
            self.window.show_view(tela_instrucao)
        elif key == arcade.key.S:
            tela_sobre = TelaSobre()
            self.window.show_view(tela_sobre)
        elif key == arcade.key.J:
            tela_jogo = JogoAtaqueDoTita()
            self.window.show_view(tela_jogo)
        elif key == arcade.key.R:
            self.window.show_view(TelaRanking())
        elif key == arcade.key.ESCAPE:
            arcade.close_window()


class TelaRanking(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)
        # Carrega os resultados persistidos uma vez e inicia a lista no começo.
        self.resultados = obter_ranking()
        self.inicio = 0

    def on_draw(self):
        # Mostra até dez posições por página, formatando pontuação e duração.
        self.clear()
        arcade.draw_text("RANKING", LARGURA / 2, 530, arcade.color.WHITE,
                         40, anchor_x="center")
        arcade.draw_text("POS.       PONTOS                 TEMPO", 180, 475,
                         arcade.color.YELLOW, 20, anchor_x="left")

        if not self.resultados:
            arcade.draw_text("Nenhuma partida registrada.", LARGURA / 2, 400,
                             arcade.color.WHITE, 20, anchor_x="center")
        else:
            for posicao, resultado in enumerate(
                self.resultados[self.inicio:self.inicio + 10],
                start=self.inicio + 1
            ):
                # O recorte mostra no máximo dez posições e preserva a numeração real.
                y = 435 - (posicao - self.inicio - 1) * 35
                arcade.draw_text(
                    f"{posicao:>3}.             {resultado.pontuacao:>3} pontos"
                    f"                 {resultado.tempo:.1f}s",
                    180, y, arcade.color.WHITE, 18, anchor_x="left"
                )

        arcade.draw_text("↑ / ↓ navegar     ESC ou M voltar ao menu",
                         LARGURA / 2, 70, arcade.color.WHITE, 16,
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        # O índice limita a rolagem à primeira posição válida de uma página.
        if key == arcade.key.DOWN:
            self.inicio = min(self.inicio + 1, max(0, len(self.resultados) - 10))
        elif key == arcade.key.UP:
            self.inicio = max(0, self.inicio - 1)
        elif key == arcade.key.ESCAPE or key == arcade.key.M:
            self.window.show_view(TelaMenu())


#Criação da tela de instrução e suas propriedades
# Tela estática de ajuda: ilustra os objetivos, inimigos e controles do jogo.
class TelaInstrucao(arcade.View):

    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)
        # O fundo é redimensionado para preencher a janela sem mudar a resolução.
        self.cenario_sprite = arcade.Sprite("cenario_inicial.jpg")
        self.cenario_sprite.width = LARGURA
        self.cenario_sprite.height = ALTURA
        self.cenario_sprite.center_x = LARGURA / 2
        self.cenario_sprite.center_y = ALTURA / 2
        self.sprite_cenario = arcade.SpriteList()
        self.sprite_cenario.append(self.cenario_sprite)

    def on_draw(self):
        # Renderiza os textos explicativos agrupados por assunto.
        self.clear()
        self.sprite_cenario.draw()

        # Os textos estão separados em objetivos, inimigos e controles.
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
        # ESC e M são atalhos de retorno ao menu principal.
        if key == arcade.key.ESCAPE or key == arcade.key.M:
            tela_inicial = TelaMenu()
            self.window.show_view(tela_inicial)

#Criação da tela de Informações e suas prorpeidades
# Tela de créditos e resumo, com navegação de volta ao menu.
class TelaSobre(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)
        # Reutiliza a imagem de cenário como plano de fundo da tela informativa.
        self.cenario_sprite = arcade.Sprite("cenario_inicial.jpg")
        self.cenario_sprite.width = LARGURA
        self.cenario_sprite.height = ALTURA
        self.cenario_sprite.center_x = LARGURA / 2
        self.cenario_sprite.center_y = ALTURA / 2
        self.sprite_cenario = arcade.SpriteList()
        self.sprite_cenario.append(self.cenario_sprite)

    def on_draw(self):
        # Desenha os créditos, o objetivo geral e uma referência aos controles.
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
        arcade.draw_text("W ou SPACE, A, D para mover", 120, 230,
                         arcade.color.WHITE, 16, anchor_x="left")

        arcade.draw_text("ESC ou M para voltar ao menu", LARGURA / 2, 90,
                         arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        # Troca a View ativa para retornar à navegação principal.
        if key == arcade.key.ESCAPE or key == arcade.key.M:
            tela_menu = TelaMenu()
            self.window.show_view(tela_menu)


#Tela de vitória,  recebe os parametros da pontuação e do tempo do jogador
#Valores numérios que são descontados ou aumentados
# Tela final de sucesso; recebe uma cópia dos valores da partida encerrada.
class TelaGanhou(arcade.View):
    def __init__(self, pontuacao, tempo):
        super().__init__()
        # Guarda o resultado para que a tela final não dependa do estado do jogo.
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
        # Apresenta o resultado final e uma mensagem adicional para a pontuação especial.
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
        # A partida termina nesta tela; ESC permite iniciar outra pelo menu.
        if key == arcade.key.ESCAPE:
            self.window.show_view(TelaMenu())


#Tela de derrota, é disparada através do evento no titã puro, que persegue o jogador
# Tela final de derrota, exibida quando o inimigo perseguidor alcança o jogador.
class TelaPerdeu(arcade.View):
    def __init__(self, pontuacao, tempo):
        super().__init__()
        # Mantém os dados da sessão para apresentá-los após a troca de tela.
        self.pontuacao = pontuacao
        self.tempo = tempo
        arcade.set_background_color(arcade.color.DARK_RED)

    def on_draw(self):
        # Informa o motivo da derrota junto com os dados acumulados até então.
        self.clear()
        arcade.draw_text("VOCÊ PERDEU", LARGURA / 2, ALTURA / 2 + 40,
                         arcade.color.WHITE, 50, anchor_x="center")
        arcade.draw_text("O Titã Puro te alcançou.", LARGURA / 2, ALTURA / 2,
                         arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text(f"Pontuação: {self.pontuacao}   Tempo: {self.tempo:.1f}s",
                 LARGURA / 2, ALTURA / 2 - 35,
                 arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Pressione ESC para voltar ao menu", LARGURA / 2, ALTURA / 2 - 60,
                         arcade.color.WHITE, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        # Retorna à tela inicial para permitir uma nova partida.
        if key == arcade.key.ESCAPE:
            self.window.show_view(TelaMenu())

#Janela Final com as váriaveis necessárias
# View principal da partida: concentra o estado do jogo e coordena seus sprites.
class JogoAtaqueDoTita(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)
        self.camera = arcade.Camera2D()
        
        # Estado mutável da sessão: resultado, cronômetro, mensagens e parâmetros.
        self.pontuacao = 0
        self.registro = 0
        self.velocidade = 5
        self.tempo = 0
        self.resultado_registrado = False
        self.mensagem = ""
        self.tempo_mensagem = 0
        self.velocidade_ini = 2
        self.jogo_rodando = True
        self.is_invencivel = False
        self.tempo_invencibilidade = 0
        # O tempo restante controla simultaneamente o tremor e o filtro vermelho.
        self.tempo_efeito_colisao = 0
        self.duracao_efeito_colisao = 0.4

        # Cria o jogador e uma lista de sprites para atualizar/desenhar em conjunto.
        self.jogador = Player()
        self.jogador.center_x = 400
        self.jogador.center_y = 0
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.jogador)

        # O chão é formado por blocos lado a lado; outros blocos elevam plataformas.
        self.sprite_blocos = arcade.SpriteList()
        for x in range(32, LARGURA + 32, 64): 
            chao = Bloco(x = x, y = 30)
            self.sprite_blocos.append(chao)

        # Coordenadas dos centros das duas plataformas suspensas.
        posicoes_plataforma = [(300,250), (500, 250)]
        for x, y in posicoes_plataforma:
            plataforma = Bloco(x,y)
            self.sprite_blocos.append(plataforma)

        #Criar TitaPuro antes do engine de física
        # O inimigo recebe a referência do jogador para calcular sua perseguição.
        self.sprite_titas_puros = arcade.SpriteList()
        self.tita_puro = TitaPuro(self.jogador)
        self.tita_puro.center_x = 800
        self.tita_puro.center_y = 600
        self.sprite_titas_puros.append(self.tita_puro)

        #Adicionando a mecânica de física para o jogador
        # O motor Platformer aplica gravidade e colisão com o chão/plataformas.
        self.engine_fisica = arcade.PhysicsEnginePlatformer(
            player_sprite = self.jogador,
            walls= self.sprite_blocos,
            gravity_constant=GRAVIDADE
        )

        #Adicionando a mecânica de física para o TitaPuro (movimento livre com colisão)
        # Este motor trata colisões com os blocos sem aplicar gravidade ao inimigo.
        self.engine_fisica_tita_puro = arcade.PhysicsEngineSimple(
            player_sprite = self.tita_puro,
            walls = self.sprite_blocos
        )

        # Sorteia 25 moedas comuns; tenta novamente até encontrar área livre de
        # blocos e moedas já posicionadas (rejeição de posições inválidas).
        self.sprite_moedas = arcade.SpriteList()

        # Cada moeda só entra no jogo depois de ser posicionada sem sobreposições.
        for i in range(25):
            self.moeda = Moeda()
            #Gerar posição válida: sem colisão com blocos e sem sobreposição com outras moedas
            posicao_valida = False
            while not posicao_valida:
                self.moeda.center_x = random.randint(50, LARGURA - 50)
                self.moeda.center_y = random.randint(50, ALTURA - 50)
                
                #Verificar se não colide com blocos
                blocos_colididos = arcade.check_for_collision_with_list(self.moeda, self.sprite_blocos)
                
                #Verificar se não sobrepõe com outras moedas
                moedas_colididas = arcade.check_for_collision_with_list(self.moeda, self.sprite_moedas)
                
                #Se não tem colisão, a posição é válida
                if not blocos_colididos and not moedas_colididas:
                    posicao_valida = True
            
            self.sprite_moedas.append(self.moeda)
        print(len(self.sprite_moedas))

        # Cria o inimigo que muda de direção aleatoriamente durante a partida.
        self.tita_irracional = TitaIrracional()
        self.tita_irracional.center_x = 0
        self.tita_irracional.center_y = 90
        self.tita_irracional.change_x = self.velocidade_ini
        self.tita_irracional.change_y = self.velocidade_ini
        self.sprite_titas_irracionais = arcade.SpriteList()
        self.sprite_titas_irracionais.append(self.tita_irracional)

        # A moeda especial também começa em posição livre e depois se move
        # diagonalmente, refletindo nas bordas da janela.
        self.sprite_moeda_especial = arcade.SpriteList()
        self.moeda_especial = MoedaEspecial()
        
        # Escolhe uma posição inicial livre de blocos e moedas comuns.
        posicao_valida = False
        while not posicao_valida:
            self.moeda_especial.center_x = random.randint(100, LARGURA - 100)
            self.moeda_especial.center_y = random.randint(100, ALTURA - 100)
            
            #Verificar se não colide com blocos
            blocos_colididos = arcade.check_for_collision_with_list(self.moeda_especial, self.sprite_blocos)
            
            #Verificar se não sobrepõe com moedas simples
            moedas_colididas = arcade.check_for_collision_with_list(self.moeda_especial, self.sprite_moedas)
            
            #Se não tem colisão, a posição é válida
            if not blocos_colididos and not moedas_colididas:
                posicao_valida = True
        
        self.moeda_especial.change_x = self.velocidade
        self.moeda_especial.change_y = self.velocidade
        self.sprite_moeda_especial.append(self.moeda_especial)

    def salvar_resultado(self):
        # Guarda o placar uma única vez, mesmo que mais de um evento final ocorra.
        if not self.resultado_registrado:
            registrar_resultado(self.pontuacao, self.tempo)
            self.resultado_registrado = True

    def on_draw(self):
        # Desenha as camadas do jogo e o HUD (informações sobrepostas à área de jogo).
        self.clear()
        # O tremor diminui junto com o tempo restante do efeito após a colisão.
        intensidade_tremor = 10 * (
            self.tempo_efeito_colisao / self.duracao_efeito_colisao
        )
        self.camera.position = (
            LARGURA / 2 + random.uniform(-intensidade_tremor, intensidade_tremor),
            ALTURA / 2 + random.uniform(-intensidade_tremor, intensidade_tremor),
        )
        self.camera.use()
        self.sprite_titas_irracionais.draw()
        self.sprite_moedas.draw()
        self.sprite_moeda_especial.draw()
        self.sprite_blocos.draw()
        self.sprite_jogador.draw()
        self.sprite_titas_puros.draw()
        # Centraliza a câmera antes de desenhar a sobreposição e o HUD.
        self.camera.position = (LARGURA / 2, ALTURA / 2)
        self.camera.use()
        if self.tempo_efeito_colisao > 0:
            # A transparência do vermelho também diminui até o efeito desaparecer.
            opacidade = int(
                150 * self.tempo_efeito_colisao / self.duracao_efeito_colisao
            )
            arcade.draw_lrbt_rectangle_filled(
                0, LARGURA, 0, ALTURA, (255, 0, 0, opacidade)
            )
        arcade.draw_text(f"Pontos Coletados: {self.pontuacao}", 10, 570,
                         arcade.color.WHITE, 16)
        arcade.draw_text(f"Tempo: {self.tempo:.1f}s", 10, 545,
                         arcade.color.WHITE, 16)
        arcade.draw_text("Moedas restantes: " + str(len(self.sprite_moedas) + len(self.sprite_moeda_especial)),
                         10, 520, arcade.color.WHITE, 16)
        if self.tempo_mensagem > 0:
            arcade.draw_text(self.mensagem, 220, 515, arcade.color.WHITE, 20)



        

    def on_update(self, delta_time):
        #Atualizar a fisíca
        # Avança os motores de física e sincroniza o estado de salto com o contato
        # do jogador com o chão/plataformas.
        self.engine_fisica.update()
        self.engine_fisica_tita_puro.update()

        # Atualiza o estado usado pela animação para indicar se o jogador está no ar.
        pode_pular = self.engine_fisica.can_jump()
        if self.jogador.esta_pulando:
            if pode_pular and self.jogador.change_y <= 0:
                self.jogador.esta_pulando = False
        elif not pode_pular:
            self.jogador.esta_pulando = True

        # Atualiza lógica/animações de cada grupo e cronômetros em segundos.
        self.sprite_jogador.update(delta_time)
        self.sprite_moedas.update(delta_time)
        self.sprite_titas_irracionais.update(delta_time)
        self.sprite_titas_puros.update(delta_time)
        self.sprite_moeda_especial.update(delta_time)
        self.tempo += delta_time
        if self.tempo_mensagem > 0:
            self.tempo_mensagem -= delta_time
        if self.tempo_efeito_colisao > 0:
            self.tempo_efeito_colisao = max(
                0, self.tempo_efeito_colisao - delta_time
            )

        # Detecta colisões por grupo para separar coleta, dano e condição de derrota.
        moedas_colididas = arcade.check_for_collision_with_list(self.jogador, self.sprite_moedas)
        moeda_especial_colidida = arcade.check_for_collision_with_list(self.jogador, self.sprite_moeda_especial)
        titas_puros = arcade.check_for_collision_with_list(self.jogador, self.sprite_titas_puros)
        titas_irracionais = arcade.check_for_collision_with_list(self.jogador, self.sprite_titas_irracionais)

        if titas_puros:
            # A colisão com o perseguidor encerra imediatamente a sessão.
            self.salvar_resultado()
            self.window.show_view(TelaPerdeu(self.pontuacao, self.tempo))
            return

        for tita in titas_irracionais:
            # O contato reduz um ponto, mostra feedback temporário e reposiciona
            # o inimigo longe do jogador para evitar dano repetido no mesmo local.
            self.jogador.receber_dano()
            self.pontuacao -= 1
            self.tempo_efeito_colisao = self.duracao_efeito_colisao
            print("Colidiu com o Titã Irracional!")
            self.mensagem = "TOCOU NO TITÃ IRRACIONAL! PERDEU 1 PONTO"
            self.tempo_mensagem = 1.5
            # Repete o sorteio até o titã reaparecer a pelo menos 250 pixels.
            while True:
                tita.center_x = random.randint(50, LARGURA - 50)
                tita.center_y = random.randint(50, ALTURA - 50)
                if arcade.get_distance_between_sprites(tita, self.jogador) >= 250:
                    break

        for moeda in moedas_colididas:
            # Remove o coletável das listas para não pontuar novamente.
            moeda.remove_from_sprite_lists()
            # Moeda comum vale um ponto e conta como item coletado.
            self.pontuacao += 1
            self.registro += 1
            print(self.pontuacao)

        for moeda_especial in moeda_especial_colidida:
            # A moeda especial concede cinco pontos antes de ser removida.
            moeda_especial.remove_from_sprite_lists()
            # O registro conta itens coletados, não pontos concedidos.
            self.pontuacao += 5
            self.registro += 1
            print(self.pontuacao)

        #O len conta quantos elementos tem na lista, se for 0, significa que o jogador coletou todas as moedas
        # Uma SpriteList vazia sinaliza que todos os itens foram coletados e que
        # a condição de vitória foi atingida.
        if len(self.sprite_moeda_especial) == 0 and len(self.sprite_moedas) == 0:
            # Registra o resultado antes de trocar para a tela de vitória.
            self.salvar_resultado()
            tela_final = TelaGanhou(self.pontuacao, self.tempo)
            self.window.show_view(tela_final)


    def on_key_press(self, key, modifiers):
        # Pressionar uma tecla define velocidade horizontal; o motor de física
        # controla o salto e verifica se o jogador está apoiado antes de iniciá-lo.
        if key == arcade.key.D:
            self.jogador.change_x = self.velocidade
        elif key == arcade.key.A:
            self.jogador.change_x = -self.velocidade
        elif key == arcade.key.W or key == arcade.key.SPACE:
            if self.engine_fisica.can_jump():
                self.jogador.change_y = 16
                self.jogador.esta_pulando = True
        elif key == arcade.key.ESCAPE:
            tela_menu = TelaMenu()
            self.window.show_view(tela_menu)


    def on_key_release(self, key, modifiers):
        # Ao soltar A ou D, zera a velocidade para interromper o movimento lateral.
        if key == arcade.key.A or key == arcade.key.D:
            self.jogador.change_x = 0
        
    


def main():
    # Prepara a persistência antes de abrir a janela e iniciar o loop de eventos.
    inicializar_banco()
    janela = arcade.Window(LARGURA, ALTURA, TITULO)
    tela_inicial = TelaMenu()
    janela.show_view(tela_inicial)
    # arcade.run mantém o ciclo de desenho, entrada e atualização ativo.
    arcade.run()


if __name__ == "__main__":
    # Executa main apenas quando este arquivo é iniciado diretamente,
    # não quando suas classes/funções são importadas por outro módulo.
    main()