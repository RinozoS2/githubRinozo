from pathlib import Path

from peewee import FloatField, IntegerField, Model, SqliteDatabase


BANCO = SqliteDatabase(Path(__file__).with_name("ranking.db"))


class ModeloBase(Model):
    class Meta:
        database = BANCO


class Resultado(ModeloBase):
    pontuacao = IntegerField()
    tempo = FloatField()


def inicializar_banco():
    if BANCO.is_closed():
        BANCO.connect()
    BANCO.create_tables([Resultado])


def registrar_resultado(pontuacao, tempo):
    inicializar_banco()
    Resultado.create(pontuacao=pontuacao, tempo=tempo)


def obter_ranking():
    inicializar_banco()
    return list(
        Resultado.select().order_by(
            Resultado.pontuacao.desc(),
            Resultado.tempo.asc()
        )
    )