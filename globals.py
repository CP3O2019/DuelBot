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
    user_1 = None
    user_2 = None
    turn = None
    turnCount = 0
    uuid = None

    def __init__(self, user, uuid):
        self.user_1 = user
        self.uuid = uuid
