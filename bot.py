import discord
import os
import psycopg2
import uuid
import globals
globals.init()
from discord.ext import commands
import math
import asyncio
import random
from random import randint
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

bot = discord.ext.commands.Bot(command_prefix = '=')
duels = {}
lastMessages = {}
DATABASE_URL = os.environ['DATABASE_URL']

def createTables():

        command = """
        CREATE TABLE IF NOT EXISTS lottery (
        user_id BIGINT PRIMARY KEY,
        nick TEXT,
        numTickets integer NOT NULL
        )
        """   

        conn = None
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(command)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

if __name__ == '__main__':
    print("booting up")
    createTables()
    
def check(user, channelId):

    channelDuel = globals.duels.get(channelId, None)

    if channelDuel == None:
        print("This shouldn't ever call from check")

    return user != channelDuel.user_1.user

async def startCancelCountdown(message, saved_uuid):

    await asyncio.sleep(60.0)

    channelDuel = globals.duels.get(message.channel.id, None)

    if channelDuel == None:
        return

    if channelDuel.user_2 == None and channelDuel.uuid == saved_uuid:       
        del globals.duels[message.channel.id]
        await message.send("Nobody accepted the duel.")


    elif channelDuel.user_2 != None:
        return

async def createDuel(message):

    global duels
    global lastMessages

    channelDuel = globals.duels.get(message.channel.id, None)

    if channelDuel == None:
        duels[message.channel.id] = Duel(DuelUser(message.author), uuid.uuid4())
        channelDuel = globals.duels.get(message.channel.id, None)
        globals.lastMessages[message.channel.id] = await message.send(f"{message.author.nick} has started a duel. Type **.fight** to duel them.")
        return

    if check(message.author, message.channel.id) == False:
        await message.send("You cannot duel yourself.")
        return

    if channelDuel.user_1 != None and channelDuel.user_2 != None:
        await message.send("There are already two people dueling.")
        return

    channelDuel.user_2 = DuelUser(message.author)

    startingUserBool = bool(random.getrandbits(1))

    startingUser = None

    if startingUserBool == True:
        startingUser = channelDuel.user_1
        channelDuel.turn = channelDuel.user_1
    else:
        startingUser = channelDuel.user_2
        channelDuel.turn = channelDuel.user_2

    del globals.lastMessages[message.channel.id]
    await message.send(f"Beginning duel between {channelDuel.user_1.user.nick} and {channelDuel.user_2.user.nick} \n**{startingUser.user.nick}** goes first.")

class DuelUser:
    hitpoints = 99
    special = 100
    poisoned = False
    lastAttack = None
    user = None

    def __init__(self, user):
        self.user = user

        if user.nick == None:
            user.nick = user.id

class Duel:
    user_1 = None
    user_2 = None
    turn = None
    turnCount = 0
    uuid = None

    def __init__(self, user, uuid):
        self.user_1 = user
        self.uuid = uuid

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(os.environ['DISCORD_KEY'])
