#!/usr/bin/python
# -*- coding: utf-8 -*-

USE_SQLITE = True

import time
import json
import random
import os
import config
from peewee import Model, MySQLDatabase, SqliteDatabase, InsertQuery,\
                   IntegerField, CharField, DoubleField, BooleanField,\
                   DateTimeField, BigIntegerField, OperationalError, ForeignKeyField



db = None
root_path = os.path.dirname(os.path.realpath(__file__))

def init_database():
    global db
    if db is not None:
        return db

    if config.console == "ps4":
        db = SqliteDatabase(root_path + '/FUTBot-PS4.db')
    elif config.console == "xbox":
        db = SqliteDatabase(root_path + '/FUTBot-Xbox.db')
    else:
        raise Exception(str("Unknown Console:" + config.console))

    return db

def current_time():
    return int(time.time())

class BaseModel(Model):

    @classmethod
    def get_all(cls):
        results = [m for m in cls.select().dicts()]
        return results



class AssetName(BaseModel):
    asset_id = BigIntegerField(primary_key=True)
    name = CharField()

    @classmethod
    def add_name(cls, player_name, id):
        query = (AssetName
                .insert(asset_id=id, name=player_name).upsert())
        query.execute()

    @classmethod
    def name_for_id(cls, id):
        query = (AssetName
                 .select(AssetName.name)
                 .where(AssetName.asset_id == id))
        names = query.dicts()
        if (len(names) == 1):
            return names[0]['name']
        print "Invalid ID: "+str(id)
        return "?"

class Player(BaseModel):
    asset_id = BigIntegerField(primary_key=True)
    unique_id = BigIntegerField()
    rating = IntegerField()
    team = IntegerField()
    country = IntegerField()
    discard_value = IntegerField()
    position = CharField()
    rare = BooleanField()

    @classmethod
    def update_player(cls, asset_id, unique_id, rating, team, country, discard_value, position, rare):
        query = (Player
                .insert(asset_id=asset_id, unique_id=unique_id, rating=rating, team=team, country=country, discard_value=discard_value,
                        position=position, rare=rare).upsert())
        query.execute()

class Auction_Sample(BaseModel):
    trade_id = BigIntegerField(primary_key=True)
    asset_id = BigIntegerField()
    buy_price = IntegerField()
    current_bid = IntegerField()
    starting_bid = IntegerField()
    offers = IntegerField()
    sample_time = IntegerField()

    @classmethod
    def player_price(cls, player_id, time_range):
        query = (Auction_Sample
                 .select(Auction_Sample.buy_price)
                 .where(Auction_Sample.asset_id == player_id, Auction_Sample.sample_time > time.time() - time_range)
                 )
        prices = query.dicts()
        return [price['buy_price'] for price in prices]

    @classmethod
    def add_sample(cls, trade_id, asset_id, buy_price, current_bid, starting_bid, offers):
        query = (Auction_Sample
                 .insert(trade_id=trade_id, asset_id=asset_id, buy_price=buy_price, current_bid=current_bid,
                         starting_bid=starting_bid, offers=offers, sample_time=current_time()).upsert())
        query.execute()


def create_tables():
    db = init_database()
    db.connect()
    print "Creating Tables"
    db.create_tables([AssetName, Player, Auction_Sample], safe=True)
    db.close()
