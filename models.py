#!/usr/bin/python
# -*- coding: utf-8 -*-

USE_SQLITE = True

import time
import json
import random
import os
from peewee import Model, MySQLDatabase, SqliteDatabase, InsertQuery,\
                   IntegerField, CharField, DoubleField, BooleanField,\
                   DateTimeField, BigIntegerField, OperationalError, ForeignKeyField




db = None
root_path = os.path.dirname(os.path.realpath(__file__))

def init_database():
    global db
    if db is not None:
        return db

    if not USE_SQLITE:
        db = MySQLDatabase(
            '',
            user='',
            password='',
            host='',
        )
    else:
        db = SqliteDatabase(root_path + '/FUTBot.db')

    return db

class BaseModel(Model):
    class Meta:
        database = init_database()

    @classmethod
    def get_all(cls):
        results = [m for m in cls.select().dicts()]
        return results


class AssetName(BaseModel):
    asset_id = BigIntegerField(primary_key=True)
    name = CharField()

class Player(BaseModel):
    asset_id = BigIntegerField(primary_key=True)
    unique_id = BigIntegerField()
    rating = IntegerField()
    team = IntegerField()
    discard_value = IntegerField()
    position = CharField()

    def update_player(cls, asset_id, unique_id, rating, team, discard_value, position):
        query = (Player
                .insert(asset_id=asset_id, unique_id=unique_id, rating=rating, team=team, discard_value=discard_value,
                        position=position).upsert())
        query.execute()

class Auction_Sample(BaseModel):
    trade_id = BigIntegerField(primary_key=True)
    asset_id = BigIntegerField()
    buy_price = IntegerField()
    current_bid = IntegerField()
    starting_bid = IntegerField()
    rare = BooleanField()
    offers = IntegerField()
    sample_time = IntegerField()

    @classmethod
    def add_sample(cls, trade_id, asset_id, buy_price, current_bid, starting_bid, rare, offers):
        query = (Auction_Sample
                 .insert(trade_id=trade_id, asset_id=asset_id, buy_price=buy_price, current_bid=current_bid,
                         starting_bid=starting_bid, rare=rare, offers=offers).upsert())
        query.execute()


def create_tables(db):
    db.connect()
    print "Creating Tables"
    db.create_tables([AssetName, Player, Auction_Sample], safe=True)
    db.close()
