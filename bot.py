import discord
import os
import psycopg2

from discord.ext import commands
import math

import asyncio

import random
from random import randint

import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

DATABASE_URL = os.environ['DATABASE_URL']

bot = discord.ext.commands.Bot(command_prefix = '.')
duel = None
lastMessage = None

def createTables():

    commands = ("""
    CREATE TABLE IF NOT EXISTS duel_users (
        user_id BIGINT PRIMARY KEY,
        wins integer NOT NULL,
        losses integer NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS duel_rares (
        user_id BIGINT PRIMARY KEY,
        red_partyhat integer NOT NULL,
        blue_partyhat integer NOT NULL,
        yellow_partyhat integer NOT NULL,
        green_partyhat integer NOT NULL,
        purple_partyhat integer NOT NULL,
        white_partyhat integer NOT NULL,
        christmas_cracker integer NOT NULL,
        red_hween_mask integer NOT NULL,
        blue_hween_mask integer NOT NULL,
        green_hween_mask integer NOT NULL,
        santa_hat integer NOT NULL,
        pumpkin integer NOT NULL,
        easter_egg integer NOT NULL
        )
    """
    )

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    createTables()

# called when the bot loads up
@bot.event
async def on_ready():
    print('Bot is ready')

@bot.command()
async def commands(message):
    embed = discord.Embed(title="Duel bot commands", color = discord.Color.orange())
    embed.add_field(name="Weapons", value="**.dds**: Hits twice, max of **20** each hit, uses 25% special, 25% chance to poison \n"
    "**.whip**: Hits once, max of 25 \n"
    "**.ags**: Hits once, max of 46, uses 50% of special \n"
    "**.sgs**: Hits once, max of 39, uses 50% of special, heals for 50% of damage \n"
    "**.dlong**: Hits once, max of 26, uses 25% special \n"
    "**.dmace**: Hits once, max of 30, uses 25% special \n"
    "**.dwh**: Hits once, max of 46, uses 50% special \n"
    "**.ss**: Hits twice, max of 27 each hit, uses 100% special \n"
    "**.gmaul**: Hits three times, max of 26 each hit, uses 100% special \n"
    "**.bp**: Hits once, max of 27, uses 50% special, heals for 50% of damage, 25% chance to poison \n"
    "**.ice**: Hits once, max of 30, has a 25% chance to freeze enemy and skip their turn \n"
    "**.blood**: Hits once, max of 28, heals for 25% of damage \n"
    "**.smoke**: Hits once, max of 27, 25% chance to poison"
    
    , inline=True)
    await message.send(embed=embed)

# begin a duel command
@bot.command()
async def fight(message):
    await createDuel(message)

    await startCancelCountdown(message)

def check(user):
    return user != duel.user_1.user

async def startCancelCountdown(message):

    await asyncio.sleep(30.0)

    global duel

    if duel == None:
        return

    if duel.user_2 == None:       
        duel = None
        await message.send("Nobody accepted the duel.")

    elif duel.user_2 != None:
        return

async def checkDuelTimeout(message, turnCount):

    await asyncio.sleep(30.0)

    global duel

    # if the turn hasn't changed in 30 seconds

    if duel == None:
        return

    if turnCount == duel.turnCount:

        notTurn = None

        # gets the player who's turn it is not
        if duel.turn == duel.user_1:
            notTurn = duel.user_2
        else:
            notTurn = duel.user_1

        await message.send(f"{notTurn.user.nick} took too long for their turn. {duel.turn.user.nick} wins the duel.")
        await updateDB(duel.turn.user.id, notTurn.user.id)
        duel = None

    return

async def createDuel(message):

    global duel
    global lastMessage

    if duel == None:
        # duel = Duel(DuelUser(message.author))
        print(f'Duel created for {message.author.nick}')
        duel = Duel(DuelUser(message.author))
        lastMessage = await message.send(f"{message.author.nick} has started a duel. Type **.fight** to duel them.")
        return

    if check(message.author) == False:
        await message.send("You cannot duel yourself.")
        return

    if duel.user_1 != None and duel.user_2 != None:
        await message.send("There are already two people dueling.")
        return

    duel.user_2 = DuelUser(message.author)

    startingUserBool = bool(random.getrandbits(1))

    startingUser = None

    if startingUserBool == True:
        startingUser = duel.user_1
        duel.turn = duel.user_1
        print("ok")
    else:
        startingUser = duel.user_2
        duel.turn = duel.user_2
        print("uhm")

    await lastMessage.delete()
    await message.send(f"Beginning duel between {duel.user_1.user.nick} and {duel.user_2.user.nick} \n**{startingUser.user.nick}** goes first.")
    
# checks kill/death ratio of user
@bot.command()
async def rares(message):

    sql = f"""
    SELECT 
        red_partyhat redphat,
        blue_partyhat bluephat,
        yellow_partyhat yelphat,
        green_partyhat greenphat,
        purple_partyhat purpphat,
        white_partyhat whitephat,
        christmas_cracker xmasc,
        red_hween_mask redhw,
        blue_hween_mask bluehw,
        green_hween_mask greenhw,
        santa_hat santah,
        pumpkin pump,
        easter_egg egg

    FROM duel_users
    WHERE user_id = {message.author.id}"""

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(sql)

        rows = cur.fetchall()

        for row in rows:
            print(row)

            embed = discord.Embed(title=f"{message.author.nick}'s rares'", color = discord.Color.blurple())
            embed.add_field(name="**Red artyhat**", value=row[0])
            embed.add_field(name="**Blue partyhat**", value=row[1])
            embed.add_field(name="**Yellow partyhat**", value=row[2])
            embed.add_field(name="**Green partyhat**", value=row[3])
            embed.add_field(name="**Purple partyhat**", value=row[4])
            embed.add_field(name="**White partyhat**", value=row[5])
            embed.add_field(name="**Red halloween mask**", value=row[6])
            embed.add_field(name="**Blue halloween mask**", value=row[7])
            embed.add_field(name="**Green halloween mask**", value=row[8])
            embed.add_field(name="**Santa hat**", value=row[9])
            embed.add_field(name="**Pumpkin**", value=row[10])
            embed.add_field(name="**Easter egg**", value=row[11])

            await message.send(embed=embed)

        cur.close()
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print("SOME ERROR", error)
    finally:
        if conn is not None:
            conn.close()

@bot.command()
async def kd(message):
    sql = f"""
    SELECT 
    wins wins,
    losses losses

    FROM duel_rares
    WHERE user_id = {message.author.id}"""

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(sql)

        rows = cur.fetchall()

        for row in rows:
            print(row)

            embed = discord.Embed(title=f"K/D for {message.author.nick}", color = discord.Color.green())
            embed.add_field(name="**Wins**", value=row[0])
            embed.add_field(name="**Losses**", value=row[1])

            await message.send(embed=embed)

        cur.close()
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print("SOME ERROR", error)
        return
    finally:
        if conn is not None:
            conn.close()

# weapon commands
@bot.command()
async def dds(message):
    await useAttack(message, "DDS", 25, 2, 20, 0, True)

@bot.command()
async def whip(message):
    await useAttack(message, "Abyssal whip", 0, 1, 25, 0, False)

@bot.command()
async def ags(message):
    await useAttack(message, "Armadyl godsword", 50, 1, 46, 0, False)

@bot.command()
async def zgs(message):
    await freezeAttack(message, "Zamorak godsword", 50, 1, 36, 50)

@bot.command()
async def dlong(message):
    await useAttack(message, "Dragon longsword", 25, 1, 26, 0, False)

@bot.command()
async def dmace(message):
    await useAttack(message, "Dragon mace", 25, 1, 30, 0, False)

@bot.command()
async def dwh(message):
    await useAttack(message, "Dragon warhammer", 50, 1, 39, 0, False)

@bot.command()
async def ss(message):
    await useAttack(message, "Saradomin sword", 100, 2, 27, 0, False)

@bot.command()
async def gmaul(message):
    await useAttack(message, "Granite maul", 100, 3, 26, 0, False)

@bot.command()
async def ice(message):
    await freezeAttack(message, "Ice barrage", 0, 1, 30, 25)

@bot.command()
async def sgs(message):
    await useAttack(message, "Saradomin godsword", 50, 1, 37, 50, False)

@bot.command()
async def bp(message):
    await useAttack(message, "Toxic lowpipe", 50, 1, 27, 50, False)

@bot.command()
async def blood(message):
    await useAttack(message, "Blood barrage", 0, 1, 29, 25, False)

@bot.command()
async def smoke(message):
    await useAttack(message, "Smoke barrage", 0, 1, 27, 0, True)

def makeImage(hitpoints):
    img = Image.new('RGB', (198, 40), color = 'red')
    img.paste((0, 255, 26),(0, 0, 2 * hitpoints, 40))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(r'./HelveticaNeue.ttc', 16)      
    draw.text((80, 10),f"{hitpoints}/99",(0,0,0),font=font)
    img.save('./hpbar.png')

async def freezeAttack(message, weapon, special, rolls, max, freezeChance):
    sendingUser = None
    receivingUser = None
    global duel

    if message.author.id == duel.user_1.user.id:
        sendingUser = duel.user_1
        receivingUser = duel.user_2

    if message.author.id == duel.user_2.user.id:
        sendingUser = duel.user_2
        receivingUser = duel.user_1

    if sendingUser == None:
        return

    if sendingUser.user.id != duel.turn.user.id:
        print(sendingUser.user.nick)
        print(sendingUser)
        print(duel.turn)
        await message.send("It's not your turn.")
        return


    hitArray = []

    for n in range(0, rolls):
        hit = randint(0, max)
        hitArray.append(hit)

    # calculate damage dealt
    leftoverHitpoints = receivingUser.hitpoints - sum(hitArray)
    receivingUser.hitpoints = leftoverHitpoints

    if leftoverHitpoints > 0:
        makeImage(leftoverHitpoints)
    else:
        makeImage(0)

    rand = randint(0, (100/freezeChance)-1)

    sending = ""

    if len(hitArray) == 1:
        sending += f'{message.author.nick} uses **{weapon}** and hits a **{hitArray[0]}** on {receivingUser.user.nick}.'

    if leftoverHitpoints <= 0:
        await message.send(content=f'{sending} \n{message.author.nick} has won the duel with **{sendingUser.hitpoints}** HP left!', file=discord.File('./hpbar.png'))
        await updateDB(sendingUser.user, receivingUser.user)
        duel = None
        return
    
    if rand == 0:
        sending += f' {receivingUser.user.nick} is **frozen** and loses their turn.'
        await message.send(sending)
        await message.send(file=discord.File('./hpbar.png'))
        return

    await message.send(sending)
    await message.send(file=discord.File('./hpbar.png'))


    if duel.turn == duel.user_1:
        duel.turn = duel.user_2
    else:
        duel.turn = duel.user_1

    os.remove('./hpbar.png')

async def useAttack(message, weapon, special, rolls, max, healpercent, poison):

    sendingUser = None
    receivingUser = None

    global duel

    if message.author.id == duel.user_1.user.id:
        sendingUser = duel.user_1
        receivingUser = duel.user_2

    if message.author.id == duel.user_2.user.id:
        sendingUser = duel.user_2
        receivingUser = duel.user_1

    if sendingUser == None:
        return

    # if the wrong user is trying to go
    if sendingUser.user.id != duel.turn.user.id:
        await message.send("It's not your turn.")
        return

    # records last attack to prevent using spamming
    if sendingUser.lastAttack == weapon:
        await message.send("You cannot use the same type of attack twice in a row.")
        return
    else:
        sendingUser.lastAttack = weapon

    # if the user does not have enough special attack
    if sendingUser.special < special:
        await message.send(f"Using the {weapon} requires {special}% special attack energy.")
        return

    hitArray = []
    
    # calculate each damage roll
    for n in range(0, rolls):
        hit = randint(0, max)
        hitArray.append(hit)

    # calculate poison
    poisonRoll = randint(0,3)

    if poison == True and receivingUser.poisoned == False:
        if poisonRoll == 0: # checks roll to see if the user is now poisoned. If yes, apply damage.
            receivingUser.poisoned = True
            receivingUser.hitpoints -= 6
    elif receivingUser.poisoned == True:
        if poisonRoll == 0: # if the user is already poisoned and the poison roll succeeded, apply damage.
            receivingUser.hitpoints -= 6

    # calculate damage dealt
    leftoverHitpoints = receivingUser.hitpoints - sum(hitArray)
    receivingUser.hitpoints = leftoverHitpoints


    # calculate special remaining
    sendingUser.special -= special

    # calculate any healing
    healAmount = math.floor(healpercent/100 * hitArray[0])

    # sets lowest possible heal for SGS
    if weapon == "Saradomin godsword" and healAmount < 10:
        healAmount = 10

    # prevents healing over 99 HP
    if sendingUser.hitpoints + healAmount < 99:
        sendingUser.hitpoints += healAmount
    else:
        sendingUser.hitpoints = 99

    # create the image for the remaining hitpoints
    if leftoverHitpoints > 0:
        makeImage(leftoverHitpoints)
    else:
        makeImage(0)

    sending = ""

    # 1 attack roll
    if len(hitArray) == 1:
        sending += f'{message.author.nick} uses their **{weapon}** and hits **{hitArray[0]}** on {receivingUser.user.nick}.'

    # 2 attack rolls 
    if len(hitArray) == 2:
        sending += f'{message.author.nick} uses their **{weapon}** and hits **{hitArray[0]}-{hitArray[1]}** on {receivingUser.user.nick}.'


    # 3 attack rolls
    if len(hitArray) == 3:
        sending += f'{message.author.nick} uses their **{weapon}** and hits **{hitArray[0]}-{hitArray[1]}-{hitArray[2]}** on {receivingUser.user.nick}.'

    if poisonRoll == 0 and receivingUser.poisoned == True:
        sending += f' {receivingUser.user.nick} is hit for **6** poison damage.'

    # healing message
    if healpercent > 0:
        sending = f'{message.author.nick} uses their **{weapon}** and hits **{hitArray[0]}**, healing for **{healAmount}**. {sendingUser.user.nick} now has **{sendingUser.hitpoints}** HP.'

    # winning message
    if leftoverHitpoints <= 0:
        await message.send(content=f'{sending} \n{message.author.nick} has won the duel with **{sendingUser.hitpoints}** HP left!', file=discord.File('./hpbar.png'))
        await updateDB(sendingUser.user, receivingUser.user)
        await rollForRares(message, sendingUser.user)
        duel = None
        return

    # calculates special energy remaining and adds to message
    if special != 0:
        sending += f' {message.author.nick} has {sendingUser.special}% special attack energy left.'

    # send message and add image below
    await message.send(content=sending, file=discord.File('./hpbar.png'))
    # await message.send(file=discord.File('./desktop/duelbot/hpbar.png'))

    # switch the turn
    if duel.turn == duel.user_1:
        print('it is now the turn of', duel.user_2.user.nick)
        duel.turn = duel.user_2
    else:
        print('it is now the turn of', duel.user_1.user.nick)
        duel.turn = duel.user_1

    # remove image from local file
    os.remove('./hpbar.png')
    duel.turnCount += 1
    await checkDuelTimeout(message, duel.turnCount)

async def updateDB(winner, loser):

    commands = (
    f"""
    INSERT INTO duel_users (user_id, wins, losses) 
    VALUES 
    ({winner.id}, 1, 0) 
    ON CONFLICT (user_id) DO UPDATE 
    SET wins = duel_users.wins + 1 
    """,

    f"""
    INSERT INTO duel_users (user_id, wins, losses) 
    VALUES 
    ({loser.id}, 0, 1) 
    ON CONFLICT (user_id) DO UPDATE 
    SET losses = duel_users.losses + 1 
    """
    )

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        for command in commands:
            print("command executing")

            cur.execute(command)

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("SOME ERROR", error)
    finally:
        if conn is not None:
            conn.close()

async def rollForRares(message, winner):

    item = None

    tableRoll = rantint(0, 4)

    # winner hits the rares table
    if tableRoll == 0:
        raresRoll = randint(0, 99)
        if raresRoll == 0:
            item = "christmas_cracker"
        elif raresRoll <= 18:
            phatRoll = randint(0, 5)
            if phatRoll == 0:
                item = "red_partyhat"
            elif phatRoll == 1:
                item = "blue_partyhat"
            elif phatRoll == 2:
                item = "yellow_partyhat"
            elif phatRoll == 3:
                item = "green_partyhat"
            elif phatRoll == 4:
                item = "purple_partyhat"
            elif phatRoll == 5:
                item = "white_partyhat"
        elif raresRoll <= 39:
            maskRoll = randInt(0, 2)
            if maskRoll == 0:
                item = "red_hween_mask"
            elif maskRoll == 1:
                item = "blue_hween_mask"
            elif maskRoll == 2:
                item = "green_hween_mask"
        elif raresRoll <= 49:
            item = "santa_hat"
        elif raresRoll <= 74:
            item = "pumpkin"
        elif raresRoll <= 99:
            item = "easter_egg"


    sql = None 

    if tableRoll == 0:    
        print(f"{message.author.nick} hit the rares table")
        sql = f"""
        INSERT INTO duel_rares (
        user_id,
        red_partyhat,
        blue_partyhat,
        yellow_partyhat,
        green_partyhat,
        purple_partyhat,
        white_partyhat,
        red_hween_mask,
        blue_hween_mask,
        green_hween_mask,
        santa_hat,
        pumpkin,
        easter_egg) 
        VALUES 
        ({winner.id}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) 
        ON CONFLICT (user_id) DO UPDATE 
        SET {item} = duel_rares.{item} + 1 
        """
    else:
        print(f"{message.author.nick} did not hit the rares table")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("SOME ERROR", error)
        return
    finally:
        if conn is not None:
            conn.close()

    await message.send (f"{message.author.nick} received a {item} for winning!")

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

    def __init__(self, user):
        self.user_1 = user

bot.run(os.environ['DISCORD_KEY'])