from peewee import Model, DateTimeField, CharField
from database.database import db
import datetime

class Cliente(Model):
    # map attribute `nome` to existing DB column `name` to avoid migration
    nome = CharField(column_name='name')
    email = CharField(unique=True)
    data_registro = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db