# Path localiza o arquivo do banco ao lado deste módulo, independentemente
# da pasta de onde o jogo foi iniciado.
from pathlib import Path

# Peewee fornece os campos, modelos e conexão SQLite usados para persistir
# pontuação e duração das partidas.
from peewee import FloatField, IntegerField, Model, SqliteDatabase


# Banco SQLite compartilhado pelas operações de leitura e gravação do ranking.
BANCO = SqliteDatabase(Path(__file__).with_name("ranking.db"))


# Modelo base associa os modelos derivados à conexão do banco.
class ModeloBase(Model):
    class Meta:
        database = BANCO


# Cada linha representa o resultado de uma partida concluída.
class Resultado(ModeloBase):
    # Pontuação é inteira; o tempo pode incluir frações de segundo.
    pontuacao = IntegerField()
    tempo = FloatField()


def inicializar_banco():
    # Abre a conexão somente quando ainda não estiver aberta.
    if BANCO.is_closed():
        BANCO.connect()
    # Cria as tabelas necessárias sem recriar as que já existem.
    BANCO.create_tables([Resultado])


def registrar_resultado(pontuacao, tempo):
    # Garante que o banco esteja pronto antes de inserir o resultado.
    inicializar_banco()
    # Persiste a pontuação e o tempo recebidos da partida.
    Resultado.create(pontuacao=pontuacao, tempo=tempo)


def obter_ranking():
    # Inicializa o armazenamento também no caso de uma primeira execução.
    inicializar_banco()
    # Ordena por maior pontuação; em empate, vence o menor tempo.
    return list(
        Resultado.select().order_by(
            Resultado.pontuacao.desc(),
            Resultado.tempo.asc()
        )
    )