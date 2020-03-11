import asyncio
import os
import discord
import psycopg2
import uuid
import random
from random import randint
import globals
from globals import Duel, DuelUser
from discord.ext import commands
from bot import duels, lastMessages

DATABASE_URL = os.environ['DATABASE_URL']

class UserCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready')

    async def createTablesForUser(self, user):
        print("Creating data tables for user", user.id)

        global DATABASE_URL

        print(user.nick)

        cmds = (
        f"""
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
        ({user.id}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ON CONFLICT (user_id) DO NOTHING
        """,
        f"""
        INSERT INTO duel_users (user_id, nick, wins, losses) 
        VALUES 
        ({user.id}, '{user.nick}', 0, 0)
        ON CONFLICT (user_id) DO NOTHING
        """
        )

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            for command in cmds:
                cur.execute(command)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("TABLE CREATION ERROR", error)
        finally:
            if conn is not None:
                conn.close()

    # begin a duel command
    @commands.command()
    async def fight(self, message):

        await self.createDuel(message)

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            print("This shouldn't ever throw")
            return

        # await self.startCancelCountdown(message, channelDuel.uuid)

    @commands.command(name='commands')
    async def cmds(self, message):
        embed = discord.Embed(title="Duel bot commands", color = discord.Color.orange())
        embed.add_field(name="Commands", value="**.fight**: Begins a duel \n"
        "**.kd**: View your kill/death ratio \n"
        "**.rares**: See all of the rares you've won", inline = False)
        embed.add_field(name="Weapons", value="**.dds**: Hits twice, max of **18** each hit, uses 25% special, 25% chance to poison \n"
        "**.whip**: Hits once, max of **27** \n"
        "**.ags**: Hits once, max of **46**, uses 50% of special \n"
        "**.sgs**: Hits once, max of **39**, uses 50% of special, heals for 50% of damage \n"
        "**.zgs**: Hits once, max of **36**, uses 50% of special, has a 25% chance to freeze enemy \n"
        "**.dwh**: Hits once, max of **39**, uses 50% special \n"
        "**.ss**: Hits twice, max of **27** each hit, uses 100% special \n"
        "**.gmaul**: Hits three times, max of **24** each hit, uses 100% special \n"
        "**.dclaws**: Hits up to four times, halving each successive hit, max of 31, uses 50% special \n"
        "**.bp**: Hits once, max of **27**, uses 50% special, heals for 50% of damage, 25% chance to poison \n"
        "**.ice**: Hits once, max of **30**, has a 12.5% chance to freeze enemy\n"
        "**.blood**: Hits once, max of **28**, heals for 25% of damage \n"
        "**.smoke**: Hits once, max of **27**, 25% chance to poison"
        , inline=False)
        await message.send(embed=embed)

    @commands.command()
    async def rares(self, message):

        await self.createTablesForUser(message.author)

        cmds = f"""
        SELECT 
            red_partyhat red_partyhat,
            blue_partyhat blue_partyhat,
            yellow_partyhat yellow_partyhat,
            green_partyhat green_partyhat,
            purple_partyhat purple_partyhat,
            white_partyhat white_partyhat,
            christmas_cracker christmas_cracker,
            red_hween_mask red_hween_mask,
            blue_hween_mask blue_hween_mask,
            green_hween_mask green_hween_mask,
            santa_hat santa_hat,
            pumpkin pumpkin,
            easter_egg easter_egg

        FROM duel_rares
        WHERE user_id = {message.author.id}"""

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            print(DATABASE_URL)
            cur.execute(cmds)

            rows = cur.fetchall()

            for row in rows:
                embed = discord.Embed(title=f"{message.author.nick}'s rares", color = discord.Color.blurple())
                embed.add_field(name="**Red partyhat**", value=row[0])
                embed.add_field(name="**Blue partyhat**", value=row[1])
                embed.add_field(name="**Yellow partyhat**", value=row[2])
                embed.add_field(name="**Green partyhat**", value=row[3])
                embed.add_field(name="**Purple partyhat**", value=row[4])
                embed.add_field(name="**White partyhat**", value=row[5])
                embed.add_field(name="**Christmas cracker**", value=row[6])
                embed.add_field(name="**Red halloween mask**", value=row[7])
                embed.add_field(name="**Blue halloween mask**", value=row[8])
                embed.add_field(name="**Green halloween mask**", value=row[9])
                embed.add_field(name="**Santa hat**", value=row[10])
                embed.add_field(name="**Pumpkin**", value=row[11])
                embed.add_field(name="**Easter egg**", value=row[12])

                await message.send(embed=embed)

            cur.close()
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print("RARES ERROR", error)
        finally:
            if conn is not None:
                conn.close()

    @commands.command()
    async def kd(self, message):
        print("author", message.author.id)
        await self.createTablesForUser(message.author)

        sql = f"""
        SELECT
        nick nick,
        wins wins,
        losses losses

        FROM duel_users
        WHERE user_id = {message.author.id}"""

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()

            cur.execute(sql)

            rows = cur.fetchall()

            for row in rows:

                embed = discord.Embed(title=f"K/D for {message.author.nick}", color = discord.Color.green())
                embed.add_field(name="**Wins**", value=row[1])
                embed.add_field(name="**Losses**", value=row[2])

                await message.send(embed=embed)

            cur.close()
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print("KD ERROR", error)
            return
        finally:
            if conn is not None:
                conn.close()

    async def createDuel(self, message):

        channelDuel = globals.duels.get(message.channel.id, None)

        # Check to see if a duel exists in the channel
        if channelDuel == None:
            globals.duels[message.channel.id] = Duel(DuelUser(message.author), uuid.uuid4())
            channelDuel = globals.duels.get(message.channel.id, None)
            globals.lastMessages[message.channel.id] = await message.send(f"{message.author.nick} has started a duel. Type **.fight** to duel them.")
            self.startCancelCountdown(message, channelDuel.uuid)
            return

        # Check to see if the person is dueling themselves
        if self.check(message.author, message.channel.id) == False:
            await message.send("You cannot duel yourself.")
            return

        # Check to see if a duel already exists between two people
        if channelDuel.user_1 != None and channelDuel.user_2 != None:
            await message.send("There are already two people dueling.")
            return

        # If it passed the other checks, add duel user 2 to the fight
        channelDuel.user_2 = DuelUser(message.author)

        # Randomly pick a starting user
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

        if channelDuel.user_1 != None and channelDuel.user_2 != None:
            await self.beginFightTurnChecker(message, channelDuel)


    async def beginFightTurnChecker(self, message, duel):

        channelDuel = globals.duels.get(message.channel.id, None)

        # switches who's turn it is
        savedTurn = channelDuel.turn

        attackTypes = [",dds",
                       ",ags",
                       ",sgs",
                       ",claws",
                       ",whip",
                       ",zgs",
                       ",dlong",
                       ",dmace",
                       ",dwh",
                       ",ss",
                       ",gmaul",
                       ",ice",
                       ",blood",
                       ",smoke",
                       ",bp"]

        def checkParameters(message):
            channelDuel = globals.duels.get(message.channel.id, None)
            attackTypes = [",dds",
                           ",ags",
                           ",sgs",
                           ",claws",
                           ",whip",
                           ",zgs",
                           ",dlong",
                           ",dmace",
                           ",dwh",
                           ",ss",
                           ",gmaul",
                           ",ice",
                           ",blood",
                           ",smoke",
                           ",bp"]

            attackTypeCheck = None

            if message.content in attackTypes:
                attackTypeCheck = True
            else:
                attackTypeCheck = False

            return channelDuel != None and message.author.id == savedTurn.user.id and attackTypeCheck == True and savedTurnCount == globals.duels[message.channel.id].turnCount
        
        try:
            msg = await self.bot.wait_for('message', check=checkParameters, timeout=90)

        except asyncio.TimeoutError:
            # called when it times out
            print(f'Duel in channel {message.channel.id} timed out.')

            turnUser = None
            notTurn = None

            channelDuel = globals.duels.get(message.channel.id, None)

            if channelDuel.turn.user.id == channelDuel.user_1.user.id:
                turnUser = channelDuel.user_1
                notTurn = channelDuel.user_2
            else:
                turnUser = channelDuel.user_2
                notTurn = channelDuel.user_1
            print("Cancelling duel from inside of beginFightTurnChecker in usercommands.py")
            await message.channel.send(f'{turnUser.user.nick} took too long to take their turn. {notTurn.user.nick} wins the duel.')
            await self.updateDB(notTurn.user, turnUser.user)
            globals.duels[message.channel.id] = None

    def check(self, user, channelId):
        channelDuel = globals.duels.get(channelId, None)

        if channelDuel == None:
            print("This shouldn't ever call from check")

        return user != channelDuel.user_1.user

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

    async def startCancelCountdown(self, message, saved_uuid):

        await asyncio.sleep(60.0)

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            return

        if channelDuel.user_2 == None and channelDuel.uuid == saved_uuid:       
            del globals.duels[message.channel.id]
            await message.send("Nobody accepted the duel.")

        elif channelDuel.user_2 != None:
            return

def setup(bot):
    bot.add_cog(UserCommands(bot))