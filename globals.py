import os
from osrsbox import items_api

def init():
    global duels
    duels = {}
    global lastMessages
    lastMessages = {}
    global all_db_items
    all_db_items = items_api.load()



class DuelUser:
    hitpoints = 99
    special = 100
    poisoned = False
    lastAttack = None
    user = None

    def __init__(self, user):
        self.user = user

        if user.nick == None:
            user.nick = user.display_name

class Duel:
    # Players in the duel
    user_1 = None
    user_2 = None

    # Holds a DuelUser object that determines who the turn belongs to
    turn = None

    # Counts the turns
    turnCount = 0

    # Unique ID for the duel
    uuid = None

    # Discord channel ID for the duel
    channel = None

    # Table and ItemID for the duel to give rewards to in Postgres
    table = None
    stakeItem = None # Is normally _ID, but may be gp

    # Item long name
    itemLongName = None

    # Item short quantity
    shortQuantity = None

    # Quantity being staked
    stakeQuantity = None

    def __init__(self, user, uuid, channel, stakeItem, stakeQuantity, table, itemLongName, shortQuantity):
        self.user_1 = user
        self.uuid = uuid
        self.channel = channel
        self.stakeItem = stakeItem
        self.stakeQuantity = stakeQuantity
        self.table = table
        self.itemLongName = itemLongName
        self.shortQuantity = shortQuantity
