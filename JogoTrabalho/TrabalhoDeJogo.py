# Arcade fornece a janela, as telas, os sprites, o desenho e os motores de física.
import arcade #funcionamento do código
# random é usado para variar as posições e direções dos elementos do jogo.
import random #posições e movimentos aleatórios
import math
import datetime
import os
from pathlib import Path
import sys
import unittest

# Pillow permite recortar, redimensionar e espelhar imagens para as animações.
from PIL import Image
from peewee import (
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
    Model,
    SqliteDatabase,
)


# Banco SQLite e modelos usados para persistir os resultados das partidas.
BANCO = SqliteDatabase(Path(__file__).with_name("ranking.db"))


class BaseModel(Model):
    class Meta:
        database = BANCO


class Pontuacao(BaseModel):
    nome_jogador = CharField()
    pontos = IntegerField()
    tempo_partida = FloatField()
    data_hora = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return (
            f"{self.nome_jogador} - {self.pontos} pts "
            f"({self.tempo_partida:.1f}s)"
        )


def inicializar_banco():
    if BANCO.is_closed():
        BANCO.connect()
    BANCO.create_tables([Pontuacao])


def registrar_resultado(nome_jogador, pontos, tempo_partida):
    inicializar_banco()
    return Pontuacao.create(
        nome_jogador=nome_jogador,
        pontos=pontos,
        tempo_partida=tempo_partida,
    )


def obter_ranking():
    inicializar_banco()
    return list(
        Pontuacao.select().order_by(
            Pontuacao.pontos.desc(),
            Pontuacao.tempo_partida.asc(),
        ).limit(10)
    )

#Propriedades da janela
# Configuração global da área de jogo; coordenadas e limites usam esses valores.
ESCALA = 1.5
LARGURA_BASE = 800
ALTURA_BASE = 600
LARGURA = int(LARGURA_BASE * ESCALA)
ALTURA = int(ALTURA_BASE * ESCALA)
GRAVIDADE = 0.45 * ESCALA


def escalar(valor):
    return valor * ESCALA


def desenhar_texto(texto, x, y, cor, tamanho, *args, **kwargs):
    arcade.draw_text(
        texto, escalar(x), escalar(y), cor, escalar(tamanho), *args, **kwargs
    )


def carregar_quadros_sprite(
    caminho, colunas, total, tamanho_canvas, chave, indices=None,
    limites_x=None, margem_base=0, limpar_canto_inferior_direito=False,
):
    folha = arcade.load_texture(caminho).image.convert("RGBA")
    largura_quadro = folha.width / colunas
    quadros = []
    indices = range(total) if indices is None else indices
    for indice in indices:
        inicio_x, fim_x = (
            (round(indice * largura_quadro), round((indice + 1) * largura_quadro))
            if limites_x is None
            else (limites_x[indice], limites_x[indice + 1])
        )
        limites = (
            inicio_x,
            0,
            fim_x,
            folha.height,
        )
        quadro = folha.crop(limites)
        if limpar_canto_inferior_direito:
            for y in range(quadro.height * 2 // 3, quadro.height):
                for x in range(quadro.width // 2, quadro.width):
                    vermelho, verde, azul, alfa = quadro.getpixel((x, y))
                    if alfa >= 80 and max(vermelho, verde, azul) <= 18:
                        quadro.putpixel((x, y), (vermelho, verde, azul, 0))
        mascara = quadro.getchannel("A").point(
            lambda valor: 255 if valor >= 80 else 0
        )
        limites_sprite = mascara.getbbox()
        recorte = quadro.crop(limites_sprite)
        recorte.putalpha(
            recorte.getchannel("A").point(
                lambda valor: valor if valor >= 80 else 0
            )
        )
        proporcao = min(
            tamanho_canvas[0] / recorte.width,
            tamanho_canvas[1] / recorte.height,
        )
        tamanho = (
            max(1, round(recorte.width * proporcao)),
            max(1, round(recorte.height * proporcao)),
        )
        recorte = recorte.resize(tamanho, Image.Resampling.LANCZOS)
        imagem = Image.new("RGBA", tamanho_canvas)
        imagem.alpha_composite(
            recorte,
            ((tamanho_canvas[0] - tamanho[0]) // 2,
             tamanho_canvas[1] - margem_base - tamanho[1]),
        )
        quadros.append(arcade.Texture(imagem, hash=f"{chave}-{indice}"))
    return quadros


def carregar_estados_barra():
    folha = arcade.load_texture("barra.png").image.convert("RGBA")
    faixas = [(8, 205), (212, 404), (408, 598), (604, 796), (800, 1009)]
    estados = []
    for indice, (topo, base) in enumerate(faixas):
        faixa = folha.crop((0, topo, folha.width, base))
        mascara = faixa.getchannel("A").point(
            lambda valor: 255 if valor >= 80 else 0
        )
        limites = mascara.getbbox()
        recorte = faixa.crop(limites)
        recorte.putalpha(
            recorte.getchannel("A").point(
                lambda valor: valor if valor >= 80 else 0
            )
        )
        estados.append(arcade.Texture(recorte, hash=f"titan-meter-{indice}"))
    return estados


class Raio(arcade.Sprite):
    def __init__(self):
        textura = arcade.load_texture("raio.png")
        imagem = textura.image.convert("RGBA")
        limites = imagem.getchannel("A").getbbox()
        imagem = imagem.crop(limites)
        imagem.putalpha(
            imagem.getchannel("A").point(
                lambda valor: valor if valor >= 80 else 0
            )
        )
        textura_raio = arcade.Texture(imagem, hash="collectible-lightning")
        super().__init__(textura_raio, scale=0.055)
        self.change_y = -4.5

    def update(self, delta_time):
        self.center_y += self.change_y
        if self.top < 0:
            self.remove_from_sprite_lists()

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
        super().__init__("coin_sp.png", scale = 0.12 * ESCALA)
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
        super().__init__("coin_sp2.png", scale = 0.35 * ESCALA)
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
        super().__init__("p1_idle.png", scale=ESCALA * 0.85)
        # Estado inicial do movimento e dos temporizadores da animação/dano.
        self.change_x = 0
        self.change_y = 0
        self.texture_parado = arcade.load_texture("p1_idle.png")
        self.texture_parado_esquerda = self.texture_parado.flip_left_right()
        self.virado_para = "direita"
        self.em_forma_tita = False
        self.em_transformacao = False
        self.tempo_transformacao = 0
        self.indice_transformacao = 0
        self.duracao_quadro_transformacao = 0.12
        self.esta_pulando = False
        self.animacao_pulo_ativa = False
        self.animacao_pulo_concluida = False
        self.tempo_animacao_pulo = 0
        self.indice_animacao_pulo = 0
        self.duracao_quadro_pulo = 0.12
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
        canvas_tita = (
            round(imagem_parada.width * 1.9),
            round(imagem_parada.height * 1.9),
        )
        self.texturas_transformacao = carregar_quadros_sprite(
            "transformacao.png", 6, 6, canvas_tita, "titan-transform",
            limites_x=(0, 230, 470, 705, 950, 1215, 1528),
            margem_base=3,
        )
        self.texturas_tita_idle = carregar_quadros_sprite(
            "titaidle.png", 1, 1, canvas_tita, "titan-idle",
            margem_base=3,
        )
        self.textura_tita_idle = self.texturas_tita_idle[0]
        self.textura_tita_idle_esquerda = arcade.Texture(
            self.textura_tita_idle.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
            hash="titan-idle-left",
        )
        self.texturas_tita_andando = carregar_quadros_sprite(
            "titawalk.png", 4, 4, canvas_tita, "titan-walk",
            margem_base=3,
        )
        self.texturas_tita_andando_esquerda = [
            arcade.Texture(
                quadro.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                hash=f"titan-walk-left-{indice}",
            )
            for indice, quadro in enumerate(self.texturas_tita_andando)
        ]
        self.texturas_tita_pulo = carregar_quadros_sprite(
            "titapulo.png", 4, 4, canvas_tita, "titan-jump",
            margem_base=3, limpar_canto_inferior_direito=True,
        )
        self.texturas_tita_pulo_esquerda = [
            arcade.Texture(
                quadro.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                hash=f"titan-jump-left-{indice}",
            )
            for indice, quadro in enumerate(self.texturas_tita_pulo)
        ]
        self.texturas_andando = []
        self.texturas_andando_esquerda = []
        self.texturas_pulo = []
        self.texturas_pulo_esquerda = []
        self.texturas_inicio = []

        folha_pulo = arcade.load_texture("pulo.png").image.convert("RGBA")
        largura_quadro_pulo = folha_pulo.width / 4
        for indice in range(4):
            limites = (
                round(indice * largura_quadro_pulo),
                0,
                round((indice + 1) * largura_quadro_pulo),
                folha_pulo.height,
            )
            quadro_pulo = folha_pulo.crop(limites)
            mascara = quadro_pulo.getchannel("A").point(
                lambda valor: 255 if valor >= 180 else 0
            )
            limites_sprite = mascara.getbbox()
            recorte_pulo = quadro_pulo.crop(limites_sprite)
            recorte_pulo.putalpha(
                recorte_pulo.getchannel("A").point(
                    lambda valor: valor if valor >= 180 else 0
                )
            )
            proporcao = min(
                tamanho_personagem[0] / recorte_pulo.width,
                tamanho_personagem[1] / recorte_pulo.height,
            )
            tamanho_quadro = (
                max(1, round(recorte_pulo.width * proporcao)),
                max(1, round(recorte_pulo.height * proporcao)),
            )
            recorte_pulo = recorte_pulo.resize(
                tamanho_quadro, Image.Resampling.LANCZOS
            )
            imagem_pulo = Image.new("RGBA", imagem_parada.size)
            imagem_pulo.alpha_composite(
                recorte_pulo,
                (
                    esquerda + (tamanho_personagem[0] - tamanho_quadro[0]) // 2,
                    base - tamanho_quadro[1],
                ),
            )
            self.texturas_pulo.append(
                arcade.Texture(imagem_pulo, hash=f"p1-jump-right-{indice}")
            )
            self.texturas_pulo_esquerda.append(
                arcade.Texture(
                    imagem_pulo.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                    hash=f"p1-jump-left-{indice}",
                )
            )

        folha_inicio = arcade.load_texture("inicio.png").image.convert("RGBA")
        quadros_inicio = [
            (15, 240, 205, 430),
            (215, 230, 410, 430),
            (445, 220, 585, 430),
            (605, 205, 745, 430),
            (775, 185, 925, 430),
            (950, 165, 1080, 430),
            (1135, 145, 1280, 430),
            (1330, 130, 1490, 430),
            (55, 570, 205, 840),
            (245, 570, 405, 840),
            (445, 570, 595, 840),
            (630, 570, 800, 840),
            (885, 570, 1040, 840),
        ]
        max_largura = direita - esquerda
        max_altura = base - topo
        for indice, limites_folha in enumerate(quadros_inicio):
            quadro = folha_inicio.crop(limites_folha)
            alfa = quadro.getchannel("A")
            mascara = alfa.point(lambda valor: 255 if valor >= 180 else 0)
            limites_sprite = mascara.getbbox()
            recorte_inicio = quadro.crop(limites_sprite)
            recorte_inicio.putalpha(
                recorte_inicio.getchannel("A").point(
                    lambda valor: valor if valor >= 180 else 0
                )
            )
            proporcao = min(
                max_largura / recorte_inicio.width,
                max_altura / recorte_inicio.height,
            )
            tamanho = (
                max(1, round(recorte_inicio.width * proporcao)),
                max(1, round(recorte_inicio.height * proporcao)),
            )
            recorte_inicio = recorte_inicio.resize(
                tamanho, Image.Resampling.LANCZOS
            )
            imagem_inicio = Image.new("RGBA", imagem_parada.size)
            imagem_inicio.alpha_composite(
                recorte_inicio,
                (
                    (imagem_parada.width - tamanho[0]) // 2,
                    base - tamanho[1],
                ),
            )
            self.texturas_inicio.append(
                arcade.Texture(imagem_inicio, hash=f"p1-start-{indice}")
            )

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

    def iniciar_animacao_pulo(self):
        self.animacao_pulo_ativa = True
        self.animacao_pulo_concluida = False
        self.tempo_animacao_pulo = 0
        self.indice_animacao_pulo = 0

    def transformar_em_tita(self):
        base_anterior = self.bottom
        self.em_forma_tita = True
        self.em_transformacao = True
        self.tempo_transformacao = 0
        self.indice_transformacao = 0
        self.tempo_dano = 0
        self.change_x = 0
        self.texture = self.texturas_transformacao[0]
        self.bottom = base_anterior
        self.indice_animacao = 0
        self.tempo_animacao = 0
        if self.esta_pulando:
            self.iniciar_animacao_pulo()
        else:
            self.animacao_pulo_ativa = False
            self.animacao_pulo_concluida = False

    def voltar_forma_normal(self):
        base_anterior = self.bottom
        self.em_forma_tita = False
        self.em_transformacao = False
        self.texture = (
            self.texture_parado_esquerda
            if self.virado_para == "esquerda"
            else self.texture_parado
        )
        self.bottom = base_anterior
        self.indice_animacao = 0
        self.tempo_animacao = 0
        if self.esta_pulando:
            self.iniciar_animacao_pulo()
        else:
            self.animacao_pulo_ativa = False
            self.animacao_pulo_concluida = False

    def update(self, delta_time):
        if self.em_transformacao:
            self.tempo_transformacao += delta_time
            self.indice_transformacao = min(
                int(
                    self.tempo_transformacao
                    / self.duracao_quadro_transformacao
                ),
                len(self.texturas_transformacao) - 1,
            )
            self.texture = self.texturas_transformacao[
                self.indice_transformacao
            ]
            if self.tempo_transformacao >= (
                len(self.texturas_transformacao)
                * self.duracao_quadro_transformacao
            ):
                self.em_transformacao = False
                if self.esta_pulando:
                    self.iniciar_animacao_pulo()
                else:
                    self.texture = (
                        self.textura_tita_idle_esquerda
                        if self.virado_para == "esquerda"
                        else self.textura_tita_idle
                    )
            return

        # Movimento horizontal e contenção: o jogador para na borda em vez de sair.
        self.center_x += self.change_x

        if self.right > LARGURA:
            self.change_x = 0
            self.right = LARGURA

        if self.left < 0:
            self.change_x = 0
            self.left = 0

        confBordas(self, rebater =False)

        if self.change_x != 0:
            self.virado_para = "esquerda" if self.change_x < 0 else "direita"

        # Dano tem prioridade visual sobre as demais animações até o temporizador
        # acabar; max evita que o tempo restante fique negativo.
        if self.tempo_dano > 0:
            self.tempo_dano = max(0, self.tempo_dano - delta_time)
            if self.tempo_dano > 0:
                self.texture = self.textura_dano
                return

        if self.animacao_pulo_ativa and not self.esta_pulando:
            self.animacao_pulo_ativa = False
            self.animacao_pulo_concluida = False
            self.tempo_animacao_pulo = 0
            self.indice_animacao_pulo = 0

        if self.animacao_pulo_ativa:
            self.tempo_animacao_pulo += delta_time
            if self.em_forma_tita:
                quadros_pulo = (
                    self.texturas_tita_pulo_esquerda
                    if self.virado_para == "esquerda"
                    else self.texturas_tita_pulo
                )
            else:
                quadros_pulo = (
                    self.texturas_pulo_esquerda
                    if self.virado_para == "esquerda"
                    else self.texturas_pulo
                )
            self.indice_animacao_pulo = int(
                self.tempo_animacao_pulo / self.duracao_quadro_pulo
            )
            self.indice_animacao_pulo = min(
                self.indice_animacao_pulo, len(quadros_pulo) - 1
            )
            if self.tempo_animacao_pulo >= (
                len(quadros_pulo) * self.duracao_quadro_pulo
            ):
                self.animacao_pulo_ativa = False
                self.animacao_pulo_concluida = True
            self.texture = quadros_pulo[self.indice_animacao_pulo]
        elif self.animacao_pulo_concluida and self.esta_pulando:
            if self.em_forma_tita:
                quadros_pulo = (
                    self.texturas_tita_pulo_esquerda
                    if self.virado_para == "esquerda"
                    else self.texturas_tita_pulo
                )
            else:
                quadros_pulo = (
                    self.texturas_pulo_esquerda
                    if self.virado_para == "esquerda"
                    else self.texturas_pulo
                )
            self.texture = quadros_pulo[-1]
        elif self.esta_pulando:
            self.animacao_pulo_concluida = False
            self.tempo_animacao = 0
            self.indice_animacao = 0
            self.texture = (
                self.texture_parado_esquerda
                if self.virado_para == "esquerda"
                else self.texture_parado
            )
        elif self.change_x != 0:
            self.animacao_pulo_concluida = False
            if self.em_forma_tita:
                quadros = (
                    self.texturas_tita_andando_esquerda
                    if self.change_x < 0
                    else self.texturas_tita_andando
                )
            else:
                quadros = (
                    self.texturas_andando_esquerda
                    if self.change_x < 0
                    else self.texturas_andando
                )
            # Acumula tempo real e avança um ou mais quadros conforme a duração
            # configurada, fazendo a animação depender do tempo e não do FPS.
            self.tempo_animacao += delta_time
            while self.tempo_animacao >= self.duracao_quadro:
                self.tempo_animacao -= self.duracao_quadro
                self.indice_animacao = (self.indice_animacao + 1) % len(
                    quadros
                )
            self.texture = quadros[self.indice_animacao]
        else:
            self.animacao_pulo_concluida = False
            # Parado: reinicia o ciclo para que a próxima caminhada comece no quadro 0.
            self.tempo_animacao = 0
            self.indice_animacao = 0
            if self.em_forma_tita:
                self.texture = (
                    self.textura_tita_idle_esquerda
                    if self.virado_para == "esquerda"
                    else self.textura_tita_idle
                )
            else:
                self.texture = (
                    self.texture_parado_esquerda
                    if self.virado_para == "esquerda"
                    else self.texture_parado
                )

    def atualizar_animacao_inicio(self, indice):
        self.texture = self.texturas_inicio[indice]

    
#Inimigo simples que anda de forma aleatória e repetidade,
#retira 1 ponto do jogador ao colidir e aparece em outra posição
# Bloco de cenário usado como chão e plataforma; o motor de física trata-o como
# obstáculo estático contra o qual o jogador e inimigos podem colidir.
class Bloco(arcade.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__("muro.jpg", scale=ESCALA)

        # As coordenadas recebidas definem o centro do bloco no cenário.
        self.center_x = x
        self.center_y = y

class TitaIrracional(arcade.Sprite):

    def __init__(self):
        #Define a velocidade e a direção aleatória que o titã seguirá
        # Começa com componentes de velocidade aleatórias nos dois eixos.
        super().__init__("enemy_1.png", scale=ESCALA * 0.85)
        self.change_x = random.choice([-1.5, -1.0, 1.0, 1.5]) * ESCALA
        self.change_y = random.choice([-1.5, -1.0, 1.0, 1.5]) * ESCALA
        self.multiplicador_velocidade = 1.0

    def update(self, delta_time):
        # Atualiza a posição; ocasionalmente sorteia outra direção para tornar
        # a trajetória imprevisível sem depender de uma rota pré-definida.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # A cada atualização, há 1% de chance de escolher uma nova direção.
        if random.random() < 0.01:
            self.change_x = (
                random.choice([-1.5, -1.0, 1.0, 1.5])
                * ESCALA
                * self.multiplicador_velocidade
            )
            self.change_y = (
                random.choice([-1.5, -1.0, 1.0, 1.5])
                * ESCALA
                * self.multiplicador_velocidade
            )

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
        super().__init__("enemy_2.png", scale=0.8 * ESCALA * 0.85)

        #Define quem ele vai perseguir desde o começo e sua velocidade
        self.jogador = jogador
        self.velocidade = 2.0 * ESCALA
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
        desenhar_texto("Ataque do Titã", LARGURA_BASE / 2, 520,
                         arcade.color.WHITE, 50, anchor_x="center")
        desenhar_texto("MENU", LARGURA_BASE / 2, 420,
                         arcade.color.WHITE, 40, anchor_x="center")

        desenhar_texto("J - JOGAR", 220, 320, arcade.color.WHITE, 20, anchor_x="left")
        desenhar_texto("S - SOBRE O JOGO", 220, 280, arcade.color.WHITE, 20, anchor_x="left")
        desenhar_texto("I - INSTRUÇÃO", 220, 240, arcade.color.WHITE, 20, anchor_x="left")
        desenhar_texto("R - RANKING", 220, 200, arcade.color.WHITE, 20, anchor_x="left")

        desenhar_texto("Pressione a tecla correspondente", LARGURA_BASE / 2, 150,
                         arcade.color.WHITE, 16, anchor_x="center")
        desenhar_texto("ESC - SAIR", LARGURA_BASE / 2, 120,
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
        self.melhores = obter_ranking()

    def on_draw(self):
        # Mostra até dez posições por página, formatando pontuação e duração.
        self.clear()
        desenhar_texto("RANKING", LARGURA_BASE / 2, 530, arcade.color.WHITE,
                         40, anchor_x="center")
        desenhar_texto("POS.       PONTOS                 TEMPO", 180, 475,
                         arcade.color.YELLOW, 20, anchor_x="left")

        if not self.melhores:
            desenhar_texto("Nenhuma partida registrada.", LARGURA_BASE / 2, 400,
                             arcade.color.WHITE, 20, anchor_x="center")
        else:
            for posicao, resultado in enumerate(self.melhores, start=1):
                y = 435 - (posicao - 1) * 35
                desenhar_texto(
                    f"{posicao:>3}. {resultado.nome_jogador:<20} "
                    f"{resultado.pontos:>3} pontos   "
                    f"{resultado.tempo_partida:.1f}s",
                    180, y, arcade.color.WHITE, 18, anchor_x="left"
                )

        desenhar_texto("ESC ou M voltar ao menu",
                 LARGURA_BASE / 2, 70, arcade.color.WHITE, 16,
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        # O índice limita a rolagem à primeira posição válida de uma página.
        if key == arcade.key.ESCAPE or key == arcade.key.M:
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
        desenhar_texto("INSTRUÇÃO", LARGURA_BASE / 2, 520,
                         arcade.color.BLUE, 40, anchor_x="center")

        desenhar_texto("OBJETIVOS", 120, 440,
                         arcade.color.BLUE, 24, anchor_x="left")
        desenhar_texto("- Colete 25 Titãs (1 ponto)", 120, 410,
                         arcade.color.WHITE, 16, anchor_x="left")
        desenhar_texto("- Colete 1 Filtro de gás (5 pontos)", 120, 385,
                         arcade.color.WHITE, 16, anchor_x="left")
        desenhar_texto("- Total de 26 pontos para vencer", 120, 360,
                         arcade.color.WHITE, 16, anchor_x="left")

        desenhar_texto("INIMIGOS", 120, 320,
                         arcade.color.BLUE, 24, anchor_x="left")
        desenhar_texto("Titã Irracional: Anda de forma aleatória para te atacar (-1 ponto)", 120, 290,
                         arcade.color.WHITE, 16, anchor_x="left")
        desenhar_texto("Titã Puro: te persegue para sempre, não fique perto dele! (Eliminado)", 120, 265,
                         arcade.color.WHITE, 16, anchor_x="left")

        desenhar_texto("CONTROLES", 450, 440,
                         arcade.color.BLUE, 24, anchor_x="left")
        desenhar_texto("W - subir", 450, 410,
                         arcade.color.WHITE, 16, anchor_x="left")
        desenhar_texto("A - esquerda", 450, 385,
                         arcade.color.WHITE, 16, anchor_x="left")
        desenhar_texto("D - direita", 450, 360,
                         arcade.color.WHITE, 16, anchor_x="left")
        desenhar_texto("S - baixo", 450, 335,
                         arcade.color.WHITE, 16, anchor_x="left")

        desenhar_texto("ESC ou M para voltar ao menu", LARGURA_BASE / 2, 80,
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

        desenhar_texto("SOBRE O JOGO", LARGURA_BASE / 2, 520,
                         arcade.color.BLUE, 40, anchor_x="center")
        desenhar_texto("Feito por Enzo e Brian", LARGURA_BASE / 2, 460,
                         arcade.color.WHITE, 18, anchor_x="center")
        desenhar_texto("Inspirado em Attack on Titan", LARGURA_BASE / 2, 435,
                         arcade.color.WHITE, 18, anchor_x="center")
        desenhar_texto("Com ajuda do professor", LARGURA_BASE / 2, 410,
                         arcade.color.WHITE, 18, anchor_x="center")

        desenhar_texto("Objetivo:", 120, 340,
                         arcade.color.BLUE, 20, anchor_x="left")
        desenhar_texto("Colete todos os recursos sem ser pego pelos inimigos.", 120, 310,
                         arcade.color.WHITE, 16, anchor_x="left")

        desenhar_texto("Teclas:", 120, 260,
                         arcade.color.BLUE, 20, anchor_x="left")
        desenhar_texto("W ou SPACE, A, D para mover", 120, 230,
                         arcade.color.WHITE, 16, anchor_x="left")

        desenhar_texto("ESC ou M para voltar ao menu", LARGURA_BASE / 2, 90,
                         arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        # Troca a View ativa para retornar à navegação principal.
        if key == arcade.key.ESCAPE or key == arcade.key.M:
            tela_menu = TelaMenu()
            self.window.show_view(tela_menu)


#Tela de vitória,  recebe os parametros da pontuação e do tempo do jogador
#Valores numérios que são descontados ou aumentados
# Tela final de sucesso; recebe uma cópia dos valores da partida encerrada.
class TelaFim(arcade.View):
    def __init__(self, pontuacao, tempo):
        super().__init__()
        self.pontuacao = pontuacao
        self.tempo = tempo
        self.nome_jogador = ""
        self.resultado_salvo = False

    def on_text(self, text):
        if self.resultado_salvo:
            return
        self.nome_jogador = (self.nome_jogador + text)[:30]

    def salvar_resultado(self):
        nome = self.nome_jogador.strip()
        if nome and not self.resultado_salvo:
            registrar_resultado(nome, self.pontuacao, self.tempo)
            self.resultado_salvo = True

    def desenhar_campo_nome(self):
        if self.resultado_salvo:
            texto = "Resultado salvo. R - ranking"
        else:
            texto = f"Nome: {self.nome_jogador or '_'}  |  ENTER - salvar"
        desenhar_texto(texto, LARGURA_BASE / 2, 115, arcade.color.WHITE,
                         18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.BACKSPACE and not self.resultado_salvo:
            self.nome_jogador = self.nome_jogador[:-1]
        elif key == arcade.key.ENTER:
            self.salvar_resultado()
        elif key == arcade.key.R and self.resultado_salvo:
            self.window.show_view(TelaRanking())
        elif key == arcade.key.ESCAPE:
            self.salvar_resultado()
            self.window.show_view(TelaMenu())


class TelaGanhou(TelaFim):
    def __init__(self, pontuacao, tempo):
        super().__init__(pontuacao, tempo)
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
        desenhar_texto("PARABÉNS", LARGURA_BASE / 2, 470,
                         arcade.color.WHITE, 50, anchor_x="center")
        if self.pontuacao == 30:
            desenhar_texto("INACREDITÁVEL", LARGURA_BASE / 2, 380,
                             arcade.color.WHITE, 50, anchor_x="center")
        desenhar_texto(f"PONTUAÇÃO {self.pontuacao}", LARGURA_BASE / 2, 300,
                         arcade.color.WHITE, 40, anchor_x="center")
        desenhar_texto(f"TEMPO {self.tempo:.1f}s", LARGURA_BASE / 2, 240,
                         arcade.color.WHITE, 24, anchor_x="center")
        self.desenhar_campo_nome()


#Tela de derrota, é disparada através do evento no titã puro, que persegue o jogador
# Tela final de derrota, exibida quando o inimigo perseguidor alcança o jogador.
class TelaPerdeu(TelaFim):
    def __init__(self, pontuacao, tempo):
        super().__init__(pontuacao, tempo)
        arcade.set_background_color(arcade.color.DARK_RED)

    def on_draw(self):
        # Informa o motivo da derrota junto com os dados acumulados até então.
        self.clear()
        desenhar_texto("VOCÊ PERDEU", LARGURA_BASE / 2, ALTURA_BASE / 2 + 40,
                         arcade.color.WHITE, 50, anchor_x="center")
        desenhar_texto("O Titã Puro te alcançou.", LARGURA_BASE / 2, ALTURA_BASE / 2,
                         arcade.color.WHITE, 24, anchor_x="center")
        desenhar_texto(f"Pontuação: {self.pontuacao}   Tempo: {self.tempo:.1f}s",
             LARGURA_BASE / 2, ALTURA_BASE / 2 - 35,
                 arcade.color.WHITE, 20, anchor_x="center")
        self.desenhar_campo_nome()

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
        self.velocidade = 5 * ESCALA
        self.velocidade_tita = self.velocidade - 1.5
        self.tempo = 0
        self.tempo_preparacao = 5.0
        self.jogo_iniciado = False
        self.tempo_mensagem_inicio = 0
        self.tempo_tremor_inicio = 0
        self.mensagem = ""
        self.tempo_mensagem = 0
        self.velocidade_ini = 2 * ESCALA
        self.jogo_rodando = True
        self.is_invencivel = False
        self.imortal_admin = False
        self.fase_atual = 1
        self.total_fases = 3
        self.aguardando_proxima_fase = False
        self.tempo_cooldown_fase = 0
        self.duracao_cooldown_fase = 3.0
        self.dificuldades = ("FÁCIL", "MÉDIO", "DIFÍCIL")
        self.multiplicadores_inimigos = (0.65, 1.0, 1.4)
        self.tempo_invencibilidade = 0
        self.temporizador_tita_iniciado = False
        self.raios_coletados = 0
        self.intervalo_raio = 3.0
        self.tempo_proximo_raio = 1.5
        self.duracao_modo_tita = 7.5
        # O tempo restante controla simultaneamente o tremor e o filtro vermelho.
        self.tempo_efeito_colisao = 0
        self.duracao_efeito_colisao = 0.4

        self.sprite_raios = arcade.SpriteList()
        self.texturas_barra_tita = carregar_estados_barra()
        self.barra_tita = arcade.Sprite(self.texturas_barra_tita[0], scale=0.3)
        self.barra_tita.left = escalar(18)
        self.barra_tita.center_y = ALTURA - escalar(115)
        self.sprite_barra_tita = arcade.SpriteList()
        self.sprite_barra_tita.append(self.barra_tita)

        # Cria o jogador e uma lista de sprites para atualizar/desenhar em conjunto.
        self.jogador = Player()
        self.jogador.center_x = escalar(400)
        self.jogador.center_y = escalar(100)
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.jogador)

        # O chão é formado por blocos lado a lado; outros blocos elevam plataformas.
        self.sprite_blocos = arcade.SpriteList()
        for x in range(32, LARGURA_BASE + 32, 64):
            chao = Bloco(x=escalar(x), y=escalar(30))
            self.sprite_blocos.append(chao)

        # Coordenadas dos centros das duas plataformas suspensas.
        posicoes_plataforma = [(escalar(300), escalar(250)),
                       (escalar(500), escalar(250))]
        for x, y in posicoes_plataforma:
            plataforma = Bloco(x,y)
            self.sprite_blocos.append(plataforma)

        #Criar TitaPuro antes do engine de física
        # O inimigo recebe a referência do jogador para calcular sua perseguição.
        self.sprite_titas_puros = arcade.SpriteList()
        self.tita_puro = TitaPuro(self.jogador)
        self.tita_puro.center_x = escalar(LARGURA_BASE)
        self.tita_puro.center_y = escalar(ALTURA_BASE)
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

        self.sprite_moedas = arcade.SpriteList()

        # Cria o inimigo que muda de direção aleatoriamente durante a partida.
        self.tita_irracional = TitaIrracional()
        self.tita_irracional.center_x = 0
        self.tita_irracional.center_y = escalar(90)
        self.tita_irracional.change_x = self.velocidade_ini
        self.tita_irracional.change_y = self.velocidade_ini
        self.sprite_titas_irracionais = arcade.SpriteList()
        self.sprite_titas_irracionais.append(self.tita_irracional)
        self.tita_irracional.multiplicador_velocidade = 1.0

        # A moeda especial também começa em posição livre e depois se move
        # diagonalmente, refletindo nas bordas da janela.
        self.sprite_moeda_especial = arcade.SpriteList()
        self.definir_dificuldade()
        self.criar_coletaveis()

    def definir_dificuldade(self):
        multiplicador = self.multiplicadores_inimigos[self.fase_atual - 1]
        self.tita_puro.velocidade = 2.0 * ESCALA * multiplicador
        self.tita_irracional.multiplicador_velocidade = multiplicador
        velocidade_base = self.velocidade_ini * multiplicador
        direcao_x = -1 if self.tita_irracional.change_x < 0 else 1
        direcao_y = -1 if self.tita_irracional.change_y < 0 else 1
        self.tita_irracional.change_x = direcao_x * velocidade_base
        self.tita_irracional.change_y = direcao_y * velocidade_base

    def criar_coletaveis(self):
        self.sprite_moedas.clear()
        self.sprite_moeda_especial.clear()

        for _ in range(25):
            moeda = Moeda()
            while True:
                moeda.center_x = escalar(random.randint(50, LARGURA_BASE - 50))
                moeda.center_y = escalar(random.randint(50, ALTURA_BASE - 50))
                blocos_colididos = arcade.check_for_collision_with_list(
                    moeda, self.sprite_blocos
                )
                moedas_colididas = arcade.check_for_collision_with_list(
                    moeda, self.sprite_moedas
                )
                if not blocos_colididos and not moedas_colididas:
                    break
            self.sprite_moedas.append(moeda)

        moeda_especial = MoedaEspecial()
        while True:
            moeda_especial.center_x = escalar(
                random.randint(100, LARGURA_BASE - 100)
            )
            moeda_especial.center_y = escalar(
                random.randint(100, ALTURA_BASE - 100)
            )
            blocos_colididos = arcade.check_for_collision_with_list(
                moeda_especial, self.sprite_blocos
            )
            moedas_colididas = arcade.check_for_collision_with_list(
                moeda_especial, self.sprite_moedas
            )
            if not blocos_colididos and not moedas_colididas:
                break

        moeda_especial.change_x = self.velocidade
        moeda_especial.change_y = self.velocidade
        self.sprite_moeda_especial.append(moeda_especial)

    def avancar_fase(self):
        self.fase_atual += 1
        self.aguardando_proxima_fase = False
        self.definir_dificuldade()
        self.criar_coletaveis()
        self.mensagem = f"FASE {self.fase_atual}: {self.dificuldades[self.fase_atual - 1]}"
        self.tempo_mensagem = 2.0

    def iniciar_modo_tita(self):
        self.is_invencivel = True
        self.temporizador_tita_iniciado = False
        self.tempo_invencibilidade = 0
        self.jogador.transformar_em_tita()
        self.sprite_raios.clear()
        self.mensagem = "MODO TITÃ: INVENCÍVEL!"
        self.tempo_mensagem = 2.0

    def encerrar_modo_tita(self):
        self.is_invencivel = False
        self.temporizador_tita_iniciado = False
        self.tempo_invencibilidade = 0
        self.jogador.voltar_forma_normal()
        self.raios_coletados = 0
        self.barra_tita.texture = self.texturas_barra_tita[0]
        self.tempo_proximo_raio = self.intervalo_raio

    def atualizar_raios(self, delta_time):
        if not self.is_invencivel:
            self.tempo_proximo_raio -= delta_time
            if self.tempo_proximo_raio <= 0:
                raio = Raio()
                margem = raio.width / 2
                raio.center_x = random.uniform(margem, LARGURA - margem)
                raio.bottom = ALTURA
                self.sprite_raios.append(raio)
                self.tempo_proximo_raio = self.intervalo_raio

        self.sprite_raios.update(delta_time)
        raios_coletados = arcade.check_for_collision_with_list(
            self.jogador, self.sprite_raios
        )
        for raio in raios_coletados:
            raio.remove_from_sprite_lists()
            self.raios_coletados = min(4, self.raios_coletados + 1)
            self.barra_tita.texture = self.texturas_barra_tita[
                self.raios_coletados
            ]
            if self.raios_coletados == 4:
                self.iniciar_modo_tita()
                break

    def on_draw(self):
        # Desenha as camadas do jogo e o HUD (informações sobrepostas à área de jogo).
        self.clear()
        # O tremor diminui junto com o tempo restante do efeito após a colisão.
        intensidade_tremor_colisao = escalar(10) * (
            self.tempo_efeito_colisao / self.duracao_efeito_colisao
        )
        intensidade_tremor_inicio = escalar(24) * (
            self.tempo_tremor_inicio / 0.75
        )
        intensidade_tremor = max(
            intensidade_tremor_colisao, intensidade_tremor_inicio
        )
        self.camera.position = (
            LARGURA / 2 + random.uniform(-intensidade_tremor, intensidade_tremor),
            ALTURA / 2 + random.uniform(-intensidade_tremor, intensidade_tremor),
        )
        self.camera.use()
        if self.jogo_iniciado:
            self.sprite_titas_irracionais.draw()
        self.sprite_raios.draw()
        self.sprite_moedas.draw()
        self.sprite_moeda_especial.draw()
        self.sprite_blocos.draw()
        self.sprite_jogador.draw()
        if self.jogo_iniciado:
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
        arcade.draw_lrbt_rectangle_filled(
            0, LARGURA, ALTURA - escalar(80), ALTURA, (12, 20, 28, 210)
        )
        desenhar_texto(f"PONTOS {self.pontuacao}", 14, 560,
                       arcade.color.WHITE, 14)
        desenhar_texto(f"TEMPO {self.tempo:.1f}s", 180, 560,
                       arcade.color.WHITE, 14, anchor_x="center")
        desenhar_texto(f"FASE {self.fase_atual}/{self.total_fases}", 330, 560,
                       arcade.color.WHITE, 14, anchor_x="center")
        desenhar_texto(
            f"NÍVEL {self.dificuldades[self.fase_atual - 1]}", 490, 560,
            arcade.color.YELLOW, 14, anchor_x="center"
        )
        desenhar_texto(
            f"ITENS {len(self.sprite_moedas) + len(self.sprite_moeda_especial)}",
            635, 560, arcade.color.WHITE, 14, anchor_x="center"
        )
        desenhar_texto(
            f"IMORTAL {'ON' if self.imortal_admin else 'OFF'} (L)",
            LARGURA_BASE - 14, 560, arcade.color.GREEN, 14, anchor_x="right"
        )
        self.sprite_barra_tita.draw()
        if self.tempo_mensagem > 0:
            desenhar_texto(self.mensagem, LARGURA_BASE / 2, 470,
                           arcade.color.WHITE, 20, anchor_x="center")
        if (
            not self.jogo_iniciado
            or self.tempo_mensagem_inicio > 0
            or self.aguardando_proxima_fase
        ):
            arcade.draw_lrbt_rectangle_filled(
                0, LARGURA, 0, ALTURA, (0, 0, 0, 135)
            )
            if not self.jogo_iniciado:
                desenhar_texto(
                    "PREPARAÇÃO", LARGURA_BASE / 2, 365,
                    arcade.color.WHITE, 28, anchor_x="center"
                )
                desenhar_texto(
                    str(math.ceil(self.tempo_preparacao)),
                    LARGURA_BASE / 2, 265, arcade.color.WHITE, 86,
                    anchor_x="center"
                )
            elif self.aguardando_proxima_fase:
                desenhar_texto(
                    f"FASE CONCLUÍDA  |  PRÓXIMA EM "
                    f"{math.ceil(self.tempo_cooldown_fase)}",
                    LARGURA_BASE / 2, 320, arcade.color.WHITE, 30,
                    anchor_x="center"
                )
            else:
                desenhar_texto(
                    "COMEÇAR!", LARGURA_BASE / 2, 350,
                    arcade.color.YELLOW, 58, anchor_x="center"
                )
                desenhar_texto(
                    "COLETE TODAS AS MOEDAS!", LARGURA_BASE / 2, 275,
                    arcade.color.WHITE, 25, anchor_x="center"
                )



        

    def on_update(self, delta_time):
        if not self.jogo_iniciado:
            self.tempo_preparacao = max(
                0, self.tempo_preparacao - delta_time
            )
            tempo_decorrido = 5.0 - self.tempo_preparacao
            indice_animacao = min(
                int(tempo_decorrido / (5.0 / len(self.jogador.texturas_inicio))),
                len(self.jogador.texturas_inicio) - 1,
            )
            self.jogador.atualizar_animacao_inicio(indice_animacao)
            if self.tempo_preparacao == 0:
                self.jogo_iniciado = True
                self.tempo_mensagem_inicio = 1.8
                self.tempo_tremor_inicio = 0.75
                self.jogador.texture = self.jogador.texture_parado
            return

        if self.aguardando_proxima_fase:
            self.tempo_cooldown_fase = max(
                0, self.tempo_cooldown_fase - delta_time
            )
            self.tempo += delta_time
            if self.tempo_cooldown_fase == 0:
                self.avancar_fase()
            return

        if self.is_invencivel and self.temporizador_tita_iniciado:
            self.tempo_invencibilidade = max(
                0, self.tempo_invencibilidade - delta_time
            )
            if self.tempo_invencibilidade == 0:
                self.encerrar_modo_tita()

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
        if self.is_invencivel and not self.temporizador_tita_iniciado:
            if not self.jogador.em_transformacao:
                self.temporizador_tita_iniciado = True
                self.tempo_invencibilidade = self.duracao_modo_tita
        self.sprite_moedas.update(delta_time)
        self.sprite_titas_irracionais.update(delta_time)
        self.sprite_titas_puros.update(delta_time)
        self.sprite_moeda_especial.update(delta_time)
        self.atualizar_raios(delta_time)
        self.tempo += delta_time
        if self.tempo_mensagem_inicio > 0:
            self.tempo_mensagem_inicio = max(
                0, self.tempo_mensagem_inicio - delta_time
            )
        if self.tempo_tremor_inicio > 0:
            self.tempo_tremor_inicio = max(
                0, self.tempo_tremor_inicio - delta_time
            )
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

        invulneravel = self.is_invencivel or self.imortal_admin
        if titas_puros and not invulneravel:
            # A colisão com o perseguidor encerra imediatamente a sessão.
            self.window.show_view(TelaPerdeu(self.pontuacao, self.tempo))
            return

        for tita in titas_irracionais if not invulneravel else []:
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
                tita.center_x = escalar(random.randint(50, LARGURA_BASE - 50))
                tita.center_y = escalar(random.randint(50, ALTURA_BASE - 50))
                if arcade.get_distance_between_sprites(
                    tita, self.jogador
                ) >= escalar(250):
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
        if (
            not self.sprite_moeda_especial
            and not self.sprite_moedas
            and not self.aguardando_proxima_fase
        ):
            if self.fase_atual < self.total_fases:
                self.aguardando_proxima_fase = True
                self.tempo_cooldown_fase = self.duracao_cooldown_fase
            else:
                tela_final = TelaGanhou(self.pontuacao, self.tempo)
                self.window.show_view(tela_final)


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(TelaMenu())
            return
        if not self.jogo_iniciado:
            return
        if key == arcade.key.P and not self.is_invencivel:
            self.raios_coletados = 4
            self.barra_tita.texture = self.texturas_barra_tita[4]
            self.iniciar_modo_tita()
            return
        if key == arcade.key.L:
            self.imortal_admin = not self.imortal_admin
            self.mensagem = (
                "IMORTALIDADE ADMINISTRATIVA ATIVADA"
                if self.imortal_admin
                else "IMORTALIDADE ADMINISTRATIVA DESATIVADA"
            )
            self.tempo_mensagem = 2.0
            return

        # Pressionar uma tecla define velocidade horizontal; o motor de física
        # controla o salto e verifica se o jogador está apoiado antes de iniciá-lo.
        if key == arcade.key.D:
            self.jogador.change_x = (
                self.velocidade_tita
                if self.jogador.em_forma_tita
                else self.velocidade
            )
        elif key == arcade.key.A:
            self.jogador.change_x = -(
                self.velocidade_tita
                if self.jogador.em_forma_tita
                else self.velocidade
            )
        elif key == arcade.key.W or key == arcade.key.SPACE:
            if self.engine_fisica.can_jump():
                self.jogador.change_y = escalar(16)
                self.jogador.esta_pulando = True
                self.jogador.iniciar_animacao_pulo()

    def on_key_release(self, key, modifiers):
        # Ao soltar A ou D, zera a velocidade para interromper o movimento lateral.
        if key == arcade.key.A or key == arcade.key.D:
            self.jogador.change_x = 0
        
    


class TestDamageAnimation(unittest.TestCase):
    def setUp(self):
        self.diretorio_original = Path.cwd()
        os.chdir(Path(__file__).parent)
        self.jogador = Player()

    def tearDown(self):
        os.chdir(self.diretorio_original)

    def test_damage_animation_returns_to_normal_movement(self):
        self.jogador.receber_dano()
        self.jogador.update(0.01)

        self.assertEqual(self.jogador.texture, self.jogador.textura_dano)
        self.jogador.update(1.6)

        self.assertEqual(self.jogador.tempo_dano, 0)
        self.assertEqual(self.jogador.texture, self.jogador.texture_parado)
        self.assertEqual(self.jogador.change_x, 0)
        self.assertEqual(self.jogador.change_y, 0)

    def test_titan_form_uses_directional_walk_and_jump_textures(self):
        self.jogador.center_x = 300
        self.jogador.center_y = 200
        base_anterior = self.jogador.bottom
        self.jogador.receber_dano()
        self.jogador.transformar_em_tita()

        self.assertTrue(self.jogador.em_forma_tita)
        self.assertEqual(self.jogador.tempo_dano, 0)
        self.assertTrue(self.jogador.em_transformacao)
        self.assertEqual(
            self.jogador.texture, self.jogador.texturas_transformacao[0]
        )
        self.assertAlmostEqual(self.jogador.bottom, base_anterior)

        self.jogador.update(
            len(self.jogador.texturas_transformacao)
            * self.jogador.duracao_quadro_transformacao
        )
        self.assertFalse(self.jogador.em_transformacao)
        self.assertEqual(
            self.jogador.texture, self.jogador.textura_tita_idle
        )
        self.assertEqual(len(self.jogador.texturas_tita_pulo), 4)
        for textura in (
            self.jogador.texturas_transformacao
            + self.jogador.texturas_tita_andando
            + self.jogador.texturas_tita_pulo
        ):
            caixa_visivel = textura.image.getchannel("A").getbbox()
            self.assertLess(caixa_visivel[3], textura.height)

        self.jogador.change_x = -1
        self.jogador.update(0.016)
        self.assertIn(
            self.jogador.texture, self.jogador.texturas_tita_andando_esquerda
        )

        self.jogador.change_x = 0
        self.jogador.change_y = 10
        self.jogador.esta_pulando = True
        self.jogador.iniciar_animacao_pulo()
        self.jogador.update(0.13)
        self.assertIn(
            self.jogador.texture, self.jogador.texturas_tita_pulo_esquerda
        )
        self.jogador.update(3 * self.jogador.duracao_quadro_pulo)
        self.assertFalse(self.jogador.animacao_pulo_ativa)
        self.assertTrue(self.jogador.animacao_pulo_concluida)
        self.assertEqual(self.jogador.indice_animacao_pulo, 3)
        self.assertEqual(
            self.jogador.texture, self.jogador.texturas_tita_pulo_esquerda[-1]
        )
        self.jogador.esta_pulando = False
        self.jogador.change_y = 0
        self.jogador.change_x = 0
        self.jogador.update(0.016)
        self.assertFalse(self.jogador.animacao_pulo_ativa)
        self.assertEqual(
            self.jogador.texture, self.jogador.textura_tita_idle_esquerda
        )

        self.jogador.voltar_forma_normal()
        self.assertFalse(self.jogador.em_forma_tita)
        self.assertAlmostEqual(self.jogador.bottom, base_anterior)
        self.assertEqual(self.jogador.texture, self.jogador.texture_parado_esquerda)

    def test_titan_walk_animation_wraps_in_both_directions(self):
        self.jogador.center_x = 300
        self.jogador.center_y = 200
        self.jogador.transformar_em_tita()
        self.jogador.update(
            len(self.jogador.texturas_transformacao)
            * self.jogador.duracao_quadro_transformacao
        )

        for velocidade in (1, -1):
            self.jogador.change_x = velocidade
            quadros = (
                self.jogador.texturas_tita_andando
                if velocidade > 0
                else self.jogador.texturas_tita_andando_esquerda
            )
            for _ in range(12):
                self.jogador.update(0.1)
                self.assertIn(self.jogador.texture, quadros)
                self.assertLess(self.jogador.indice_animacao, len(quadros))

    def test_lightning_falls_at_constant_speed(self):
        raio = Raio()
        raio.center_y = 400
        altura_inicial = raio.center_y
        velocidade = raio.change_y

        raio.update(0.1)
        primeira_altura = raio.center_y
        raio.update(0.1)

        self.assertAlmostEqual(primeira_altura - altura_inicial, velocidade)
        self.assertAlmostEqual(raio.center_y - primeira_altura, velocidade)

    def test_transformation_bar_has_five_progress_states(self):
        self.assertEqual(len(carregar_estados_barra()), 5)


def main():
    # Prepara a persistência antes de abrir a janela e iniciar o loop de eventos.
    inicializar_banco()
    janela = arcade.Window(LARGURA, ALTURA, TITULO)
    tela_inicial = TelaMenu()
    janela.show_view(tela_inicial)
    # arcade.run mantém o ciclo de desenho, entrada e atualização ativo.
    arcade.run()


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        # Executa o jogo ao iniciar o arquivo sem a opção de testes.
        main()