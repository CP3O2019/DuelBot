import asyncio
import discord
import os
import random
import math
import psycopg2
from random import randint
import globals
from discord.ext import commands
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

DATABASE_URL = os.environ['DATABASE_URL']

class AttackCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # weapon commands
    @commands.command()
    async def dds(self, message):
        await self.useAttack(message, "DDS", 25, 2, 18, 0, True)

    @commands.command()
    async def whip(self, message):
        await self.useAttack(message, "Abyssal whip", 0, 1, 27, 0, False)

    @commands.command()
    async def ags(self, message):
        await self.useAttack(message, "Armadyl godsword", 50, 1, 46, 0, False)

    @commands.command()
    async def zgs(self, message):
        await self.freezeAttack(message, "Zamorak godsword", 50, 1, 36, 25)

    @commands.command()
    async def dlong(self, message):
        await self.useAttack(message, "Dragon longsword", 25, 1, 26, 0, False)

    @commands.command()
    async def dmace(self, message):
        await self.useAttack(message, "Dragon mace", 25, 1, 30, 0, False)

    @commands.command()
    async def dwh(self, message):
        await self.useAttack(message, "Dragon warhammer", 50, 1, 39, 0, False)

    @commands.command()
    async def ss(self, message):
        await self.useAttack(message, "Saradomin sword", 100, 2, 27, 0, False)

    @commands.command()
    async def gmaul(self, message):
        await self.useAttack(message, "Granite maul", 100, 3, 24, 0, False)

    @commands.command()
    async def ice(self, message):
        await self.freezeAttack(message, "Ice barrage", 0, 1, 30, 12.5)

    @commands.command()
    async def sgs(self, message):
        await self.useAttack(message, "Saradomin godsword", 50, 1, 37, 50, False)

    @commands.command()
    async def dclaws(self, message):

        sendingUser = None
        receivingUser = None

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            return

        if message.author.id == channelDuel.user_1.user.id:
            sendingUser = channelDuel.user_1
            receivingUser = channelDuel.user_2

        if message.author.id == channelDuel.user_2.user.id:
            sendingUser = channelDuel.user_2
            receivingUser = channelDuel.user_1

        if sendingUser == None:
            return

        # if the wrong user is trying to go
        if sendingUser.user.id != channelDuel.turn.user.id:
            await message.send("It's not your turn.")
            return

        # records last attack to prevent using spamming
        if sendingUser.lastAttack == "claws":
            await message.send("You cannot use that type of attack twice in a row.")
            return
        else:
            sendingUser.lastAttack = "claws"

        # if the user does not have enough special attack
        if sendingUser.special < 50:
            await message.send(f"Using the Dragon claws requires 50% special attack energy.")
            return

        hitArray = []

        # calculate each damage roll
        hit = randint(0, 21)

        # if first hit 10 or higher, keep it. If it's lower, scrap it.
        if hit >= 10:
            hitArray.append(hit)  # First hit does full
            # Second hit does half of the first hit
            hitArray.append(math.floor(hit/2))
            # Third and fourth hits do a quarter of the first hit
            hitArray.append(math.floor(hit/4))
            hitArray.append(math.floor(hit/4))

        else:
            hitArray.append(0)  # First hit is a 0
            secondHit = randint(0, 21)
            if secondHit >= 10:
                hitArray.append(secondHit)  # Second hit rolls for max
                # Third and fourth hits are half of second
                hitArray.append(math.floor(secondHit/2))
                hitArray.append(math.floor(secondHit/2))
            else:
                hitArray.append(0)  # Second hit is 0
                thirdHit = randint(0, 21)
                if thirdHit >= 10:
                    # Third and fourth hits do 75% of max
                    hitArray.append(thirdHit)
                    hitArray.append(thirdHit - 1)
                else:
                    hitArray.append(0)  # Third hit is a 0
                    fourthHit = randint(0, 21)
                    if fourthHit >= 10:
                        hitArray.append(31)  # Fourth hit is a 0
                    else:
                        hitArray[2] = 1
                        hitArray.append(1)

        # calculate poison
        poisonRoll = randint(0, 3)

        if receivingUser.poisoned == True:
            # if the user is already poisoned and the poison roll succeeded, apply damage.
            if poisonRoll == 0:
                receivingUser.hitpoints -= 6

        # calculate damage dealt
        leftoverHitpoints = receivingUser.hitpoints - sum(hitArray)
        receivingUser.hitpoints = leftoverHitpoints

        # calculate special remaining
        sendingUser.special -= 50

        # create the image for the remaining hitpoints
        if leftoverHitpoints > 0:
            if poisonRoll == 0:
                self.makeImage(leftoverHitpoints, False, True)
            else:
                self.makeImage(leftoverHitpoints, False, False)
        else:
            self.makeImage(0, False, False)

        sending = ""

        sending += f'{message.author.nick} uses their **Dragon claws** and hits **{hitArray[0]}-{hitArray[1]}-{hitArray[2]}-{hitArray[3]}** on {receivingUser.user.nick}.'

        if poisonRoll == 0 and receivingUser.poisoned == True:
            sending += f' {receivingUser.user.nick} is hit for **6** poison damage.'

        # winning message
        if leftoverHitpoints <= 0:
            await message.send(content=f'{sending} \n{message.author.nick} has won the duel with **{sendingUser.hitpoints}** HP left!', file=discord.File('./hpbar.png'))
            await self.updateDB(sendingUser.user, receivingUser.user)
            await self.rollForRares(message, sendingUser.user)
            del channelDuel
            return

        # calculates special energy remaining and adds to message
        sending += f' {message.author.nick} has {sendingUser.special}% special attack energy left.'

        # send message and add image below
        await message.send(content=sending, file=discord.File('./hpbar.png'))

        # remove image from local file
        os.remove('./hpbar.png')
        channelDuel.turnCount += 1
        await self.turnChecker(message, channelDuel)

    @commands.command()
    async def bp(self, message):
        await self.useAttack(message, "Toxic blowpipe", 50, 1, 27, 50, False)

    @commands.command()
    async def blood(self, message):
        await self.useAttack(message, "Blood barrage", 0, 1, 29, 25, False)

    @commands.command()
    async def smoke(self, message):
        await self.useAttack(message, "Smoke barrage", 0, 1, 27, 0, True)

    # Checking to see if the player who's turn it is has taken their turn
    # Takes in a message from the previous turn

    async def freezeAttack(self, message, weapon, special, rolls, max, freezeChance):

        sendingUser = None
        receivingUser = None

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            print("Couldn't find duel")
            return

        if message.author.id == channelDuel.user_1.user.id:
            sendingUser = channelDuel.user_1
            receivingUser = channelDuel.user_2

        if message.author.id == channelDuel.user_2.user.id:
            sendingUser = channelDuel.user_2
            receivingUser = channelDuel.user_1

        if sendingUser == None:
            print("Couldn't find sending user")
            return

        print("sending user:", sendingUser.user.id)
        print("turn user:", channelDuel.turn.user.id)
        if sendingUser.user.id != channelDuel.turn.user.id:
            await message.send("It's not your turn.")
            return

        # records last attack to prevent using spamming
        if weapon == "DDS" or weapon == "Abyssal whip":
            sendingUser.lastAttack = weapon
        elif sendingUser.lastAttack == weapon:
            await message.send("You cannot use that type of attack twice in a row.")
            return
        else:
            print("saving weapon")
            sendingUser.lastAttack = weapon

        hitArray = []

        for n in range(0, rolls):
            hit = randint(0, max)
            hitArray.append(hit)

        # calculate poison
        poisonRoll = randint(0, 3)

        if receivingUser.poisoned == True:
            # if the user is already poisoned and the poison roll succeeded, apply damage.
            if poisonRoll == 0:
                receivingUser.hitpoints -= 6

        # calculate damage dealt
        leftoverHitpoints = receivingUser.hitpoints - sum(hitArray)
        receivingUser.hitpoints = leftoverHitpoints

        # calculate special remaining
        sendingUser.special -= special

        rand = randint(0, math.floor((100/freezeChance))-1)

        if leftoverHitpoints > 0:
            if poisonRoll == 0 and rand == 0:
                self.makeImage(leftoverHitpoints, True, True)
            elif poisonRoll == 0 and rand != 0:
                self.makeImage(leftoverHitpoints, False, True)
            elif poisonRoll != 0 and rand == 0:
                self.makeImage(leftoverHitpoints, True, False)
            elif poisonRoll != 0 and rand != 0:
                self.makeImage(leftoverHitpoints, False, False)    
        else:
            self.makeImage(0, False, False)

        sending = ""

        if len(hitArray) == 1:
            sending += f'{message.author.nick} uses **{weapon}** and hits a **{hitArray[0]}** on {receivingUser.user.nick}.'

        if leftoverHitpoints <= 0:
            await message.send(content=f'{sending} \n{message.author.nick} has won the duel with **{sendingUser.hitpoints}** HP left!', file=discord.File('./hpbar.png'))
            await self.updateDB(sendingUser.user, receivingUser.user)
            channelDuel = None
            return

        if poisonRoll == 0 and receivingUser.poisoned == True:
            sending += f' {receivingUser.user.nick} is hit for **6** poison damage.'

        if rand == 0:
            print("freeze")
            sending += f' {receivingUser.user.nick} is **frozen** and loses their turn.'
            await message.send(sending)
            await message.send(file=discord.File('./hpbar.png'))
            return

        await message.send(sending)
        await message.send(file=discord.File('./hpbar.png'))
        
        os.remove('./hpbar.png')
        channelDuel.turnCount += 1
        await self.turnChecker(message, channelDuel)

    async def useAttack(self, message, weapon, special, rolls, max, healpercent, poison):

        sendingUser = None
        receivingUser = None

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            return

        if message.author.id == channelDuel.user_1.user.id:
            sendingUser = channelDuel.user_1
            receivingUser = channelDuel.user_2

        if message.author.id == channelDuel.user_2.user.id:
            sendingUser = channelDuel.user_2
            receivingUser = channelDuel.user_1

        if sendingUser == None:
            return

        # if the wrong user is trying to go
        print("sending user:", sendingUser.user.id)
        print("turn user:", channelDuel.turn.user.id)
        if sendingUser.user.id != channelDuel.turn.user.id:
            await message.send("It's not your turn.")
            return

        # records last attack to prevent using spamming
        if weapon == "DDS" or weapon == "Abyssal whip":
            sendingUser.lastAttack = weapon
        elif sendingUser.lastAttack == weapon:
            await message.send("You cannot use that type of attack twice in a row.")
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
        poisonRoll = randint(0, 3)

        if poison == True and receivingUser.poisoned == False:
            if poisonRoll == 0:  # checks roll to see if the user is now poisoned. If yes, apply damage.
                receivingUser.poisoned = True
                receivingUser.hitpoints -= 6
        elif receivingUser.poisoned == True:
            # if the user is already poisoned and the poison roll succeeded, apply damage.
            if poisonRoll == 0:
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
            if poisonRoll == 0:
                self.makeImage(leftoverHitpoints, False, True)
            else:
                self.makeImage(leftoverHitpoints, False, False)
        else:
            self.makeImage(0, False, False)

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
            await self.updateDB(sendingUser.user, receivingUser.user)
            await self.rollForRares(message, sendingUser.user)
            print("attempting to delete channel duel in useAttack")
            del globals.duels[message.channel.id]
            return

        # calculates special energy remaining and adds to message
        if special != 0:
            sending += f' {message.author.nick} has {sendingUser.special}% special attack energy left.'

        # send message and add image below
        await message.send(content=sending, file=discord.File('./hpbar.png'))

        # remove image from local file
        os.remove('./hpbar.png')
        channelDuel.turnCount += 1
        await self.turnChecker(message, channelDuel)

    async def turnChecker(self, message, duel):

        channelDuel = globals.duels.get(message.channel.id, None)

        # switches who's turn it is
        savedTurn = channelDuel.turn
        savedTurnCount = channelDuel.turnCount

        print("channel duel", channelDuel.turn.user.nick)
        print("global duel", globals.duels[message.channel.id].turn.user.nick)
        if channelDuel.turn == channelDuel.user_1:
            channelDuel.turn = channelDuel.user_2
        else:
            channelDuel.turn = channelDuel.user_1

        print("channel duel", channelDuel.turn.user.nick)
        print("global duel", globals.duels[message.channel.id].turn.user.nick)

        attackTypes = [".dds",
                       ".ags",
                       ".sgs",
                       ".dlaws",
                       ".whip",
                       ".zgs",
                       ".dlong",
                       ".dmace",
                       ".dwh",
                       ".ss",
                       ".gmaul",
                       ".ice",
                       ".blood",
                       ".smoke",
                       ".bp"]

        def checkParameters(message):
            channelDuel = globals.duels.get(message.channel.id, None)
            attackTypes = [".dds",
                           ".ags",
                           ".sgs",
                           ".dclaws",
                           ".whip",
                           ".zgs",
                           ".dlong",
                           ".dmace",
                           ".dwh",
                           ".ss",
                           ".gmaul",
                           ".ice",
                           ".blood",
                           ".smoke",
                           ".bp"]

            attackTypeCheck = None

            if message.content in attackTypes:
                attackTypeCheck = True
            else:
                attackTypeCheck = False

            if globals.duels.get(message.channel.id, None) == None:
                return

            return channelDuel != None and message.author.id == savedTurn.user.id and attackTypeCheck == True and savedTurnCount == globals.duels[message.channel.id].turnCount
        
        try:
            msg = await self.bot.wait_for('message', check=checkParameters, timeout=90)

        except asyncio.TimeoutError:
            # called when it times out
            print(f'Duel in channel {message.channel.id} timed out.')

            turnUser = None
            notTurn = None

            channelDuel = globals.duels.get(message.channel.id, None)

            if channelDuel == None:
                return

            if channelDuel.turn.user.id == channelDuel.user_1.user.id:
                turnUser = channelDuel.user_1
                notTurn = channelDuel.user_2
            else:
                turnUser = channelDuel.user_2
                notTurn = channelDuel.user_1

            await message.channel.send(f'{turnUser.user.nick} took tong to take their turn. {notTurn.user.nick} wins the duel.')

            globals.duels[message.channel.id] = None

    async def updateDB(self, winner, loser):

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

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()

            for command in commands:
                cur.execute(command)

            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR", error)
        finally:
            if conn is not None:
                conn.close()

    async def rollForRares(self, message, winner):

        item = None
        itemText = None

        tableRoll = randint(0, 9)

        # winner hits the rares table
        if tableRoll == 0:
            raresRoll = randint(0, 99)
            if raresRoll == 0:  # hit table for cracker
                item = "christmas_cracker"
                itemText = "Christmas cracker"
            elif raresRoll <= 18:  # hit table for a partyhat
                phatRoll = randint(0, 5)
                if phatRoll == 0:
                    item = "red_partyhat"
                    itemText = "a Red partyhat"
                elif phatRoll == 1:
                    item = "blue_partyhat"
                    itemText = "a Blue partyhat"
                elif phatRoll == 2:
                    item = "yellow_partyhat"
                    itemText = "a Yellow partyhat"
                elif phatRoll == 3:
                    item = "green_partyhat"
                    itemText = "a Green partyhat"
                elif phatRoll == 4:
                    item = "purple_partyhat"
                    itemText = "a Purple partyhat"
                elif phatRoll == 5:
                    item = "white_partyhat"
                    itemText = "a White partyhat"
            elif raresRoll <= 39:  # hit table for a mask
                maskRoll = randint(0, 2)
                if maskRoll == 0:
                    item = "red_hween_mask"
                    itemText = "a Red h'ween mask"
                elif maskRoll == 1:
                    item = "blue_hween_mask"
                    itemText = "a Blue h'ween mask"
                elif maskRoll == 2:
                    item = "green_hween_mask"
                    itemText = "a Green h'ween mask"
            elif raresRoll <= 49:  # hit table for a santa hat
                item = "santa_hat"
                itemText = "a Santa hat"
            elif raresRoll <= 74:  # hit table for a pumpkin
                item = "pumpkin"
                itemText = "a Pumpkin"
            elif raresRoll <= 99:  # hit table for an easter egg
                item = "easter_egg"
                itemText = "an Easter egg"

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
            christmas_cracker,
            red_hween_mask,
            blue_hween_mask,
            green_hween_mask,
            santa_hat,
            pumpkin,
            easter_egg) 
            VALUES 
            ({winner.id}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) 
            ON CONFLICT (user_id) DO UPDATE 
            SET {item} = duel_rares.{item} + 1 
            """
        else:
            print(f"{message.author.nick} did not hit the rares table")
            return

        conn = None

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

        await message.send(f"*{message.author.nick} received {itemText} for winning!*")

    def makeImage(self, hitpoints, freeze, poison):

        primary = (252, 3, 3)
        secondary = (0, 255, 26)

        if poison == True:
            primary = (0, 255, 26)
            secondary = (34, 148, 72)

        if freeze == True:
            primary = (69, 155, 217)
            secondary = (130, 203, 255)

        img = Image.new('RGB', (198, 40), primary)
        img.paste(secondary, (0, 0, 2 * hitpoints, 40))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(r'./HelveticaNeue.ttc', 16)
        draw.text((80, 10), f"{hitpoints}/99", (0, 0, 0), font=font)
        img.save('./hpbar.png')


def setup(bot):
    bot.add_cog(AttackCommands(bot))
