# Path localiza o arquivo do banco ao lado deste módulo, independentemente
# da pasta de onde o jogo foi iniciado.
from pathlib import Path
import datetime

# Peewee fornece os campos, modelos e conexão SQLite usados para persistir
# pontuação e duração das partidas.
from peewee import (
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
    Model,
    SqliteDatabase,
)


# Banco SQLite compartilhado pelas operações de leitura e gravação do ranking.
BANCO = SqliteDatabase(Path(__file__).with_name("ranking.db"))


# Modelo base associa os modelos derivados à conexão do banco.
class BaseModel(Model):
    class Meta:
        database = BANCO


# Cada linha representa o resultado de uma partida concluída.
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
    # Abre a conexão somente quando ainda não estiver aberta.
    if BANCO.is_closed():
        BANCO.connect()
    # Cria as tabelas necessárias sem recriar as que já existem.
    BANCO.create_tables([Pontuacao])


def registrar_resultado(nome_jogador, pontos, tempo_partida):
    # Garante que o banco esteja pronto antes de inserir o resultado.
    inicializar_banco()
    # Persiste a pontuação e o tempo recebidos da partida.
    return Pontuacao.create(
        nome_jogador=nome_jogador,
        pontos=pontos,
        tempo_partida=tempo_partida,
    )


def obter_ranking():
    # Inicializa o armazenamento também no caso de uma primeira execução.
    inicializar_banco()
    # Ordena por maior pontuação; em empate, vence o menor tempo.
    return list(
        Pontuacao.select().order_by(
            Pontuacao.pontos.desc(),
            Pontuacao.tempo_partida.asc(),
        ).limit(10)
    )