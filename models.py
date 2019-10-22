import datetime

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('arabi.db')

class User(UserMixin, Model):
    name = CharField(max_length=100)
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    
    class Meta:
        database = DATABASE

class Deck(Model):
    user = CharField()
    name = CharField(max_length=50)
    slug = CharField(max_length=50)

    class Meta:
        database = DATABASE

class Card(Model):
    user = CharField()
    deck = ForeignKeyField(Deck, backref='cards')
    front = CharField(max_length=100)
    back = CharField(max_length=100)
    date_add = DateTimeField(default=datetime.datetime.now() - datetime.timedelta(days=1))
    level = IntegerField(default=1)

    class Meta:
        database = DATABASE
        order_by = ('-date_add',)
    
    @classmethod
    def create_card(cls, user, deck, front, back):
        cls.create(
            user=user,
            deck=deck,
            front=front,
            back=back,)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Deck, Card], safe=True)
    DATABASE.close()