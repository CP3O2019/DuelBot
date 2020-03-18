import asyncio
import os
import discord
import psycopg2
import uuid
import random
import math
from random import randint
from cogs.osrsEmojis import ItemEmojis
from cogs.loots import PotentialItems
import globals
from globals import Duel, DuelUser
from cogs.mathHelpers import RSMathHelpers
from discord.ext import commands
from bot import duels, lastMessages

DATABASE_URL = os.environ['DATABASE_URL']

class UserCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready')

    @commands.command() 
    async def invite(self, ctx):
        await ctx.send("""
        Click the link below to add the DuelBot to your server! \n
        https://cutt.ly/lthupdh
        """)

    @commands.command() 
    async def server(self, ctx):
        await ctx.send("""
        Click the link below to joib our server and get an extra loot roll every kill! \n
       https://discord.gg/8tvaT9
        """)

    async def createTablesForUser(self, user):

        global DATABASE_URL

        print(user.nick)

        cmds = (
        f"""
        INSERT INTO duel_rares (
            user_id,
            _1038,
            _1040,
            _1042,
            _1044,
            _1046,
            _1048,
            _962,
            _1057,
            _1055,
            _1053,
            _1050,
            _1959,
            _1961) 
        VALUES 
        ({user.id}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ON CONFLICT (user_id) DO NOTHING
        """,
        f"""
        INSERT INTO duel_users (user_id, nick, wins, losses, gp) 
        VALUES 
        ({user.id}, '{user.nick}', 0, 0, 0)
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
            return

    @commands.command(name='commands')
    async def cmds(self, message):
        embed = discord.Embed(title="Duel bot commands", color = discord.Color.orange())
        embed.add_field(name="Commands", value="**.fight**: Begins a duel \n"
        "**.kd**: View your kill/death ratio \n"
        "**.rares**: See all of the rares you've won \n"
        "**.gp**: See how much GP you have", inline = False)
        embed.add_field(name="Weapons", value="**.dds**: Hits twice, max of **18** each hit, uses 25% special, 25% chance to poison \n"
        "**.whip**: Hits once, max of **27** \n"
        "**.ags**: Hits once, max of **46**, uses 50% of special \n"
        "**.sgs**: Hits once, max of **39**, uses 50% of special, heals for 50% of damage \n"
        "**.zgs**: Hits once, max of **36**, uses 50% of special, has a 25% chance to freeze enemy \n"
        "**.dwh**: Hits once, max of **39**, uses 50% special \n"
        "**.ss**: Hits twice, max of **27** each hit, uses 100% special \n"
        "**.gmaul**: Hits three times, max of **24** each hit, uses 100% special \n"
        # "**.dclaws**: Hits up to four times, halving each successive hit, max of **31**, uses 50% special \n"
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
            _1038 red_partyhat,
            _1040 yellow_partyhat,
            _1042 blue_partyhat,
            _1044 green_partyhat,
            _1046 purple_partyhat,
            _1048 white_partyhat,
            _962 christmas_cracker,
            _1057 red_hween_mask,
            _1055 blue_hween_mask,
            _1053 green_hween_mask,
            _1050 santa_hat,
            _1959 pumpkin,
            _1961 easter_egg

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
                embed.add_field(name="**Yellow partyhat**", value=row[1])
                embed.add_field(name="**Blue partyhat**", value=row[2])
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

    @commands.command()
    async def gp(self, message):
        await self.createTablesForUser(message.author)

        sql = f"""
        SELECT
        gp gp
        FROM duel_users
        WHERE user_id = {message.author.id}
        """

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

            for row in rows:
                commaMoney = "{:,d}".format(row[0])
                await message.send(f'{ItemEmojis.Coins.coins} You have {commaMoney} GP {ItemEmojis.Coins.coins}')

            cur.close()
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print("GP ERROR", error)
            return
        finally:
            if conn is not None:
                conn.close()

    @commands.command()
    async def dice(self, message, *args):

        diceAmount = 0
        helper = RSMathHelpers(self.bot)


        try:
            diceAmount = helper.numify(args[0])

            if diceAmount <= 0:
                await message.send("You can't dice less than 1 GP.")
                return

            diceAmountStrings = helper.shortNumify(diceAmount, 1)

            hasMoney = await helper.removeGPFromUser(message, message.author.id, diceAmount)

            if hasMoney == False:
                return

            rand = randint(1, 100)
            diceDescription = ''
            winStatus = ""
            if rand >= 55:
                await helper.giveGPToUser(message, message.author.id, diceAmount * 2)
                diceDescription = f'You rolled a **{rand}** and won {diceAmountString} GP'
                winStatus = "won"
            else:
                diceDescription = f'You rolled a **{rand}** and lost {diceAmountString} GP.'
                winStatus = "lost"

            embed = discord.Embed(title='**Dice Roll**', description=diceDescription, color = discord.Color.orange())
            embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/runescape2/images/f/f2/Dice_bag_detail.png/revision/latest?cb=20111120013858')
            await message.send(embed=embed)
        except:
            await message.send('You must dice a valid amount.')

        # If over 100M is diced, send it to the global notifications channel
        if diceAmount >= 100000000:
                notifChannel = self.bot.get_channel(689313376286802026)
                await notifChannel.send(f"{ItemEmojis.Coins.coins} {message.author.nick} has just diced **{helper.shortNumify(self, diceAmount)}** and **{winStatus}**.")

    async def createDuel(self, message):

        channelDuel = globals.duels.get(message.channel.id, None)

        # Check to see if a duel exists in the channel
        if channelDuel == None:
            globals.duels[message.channel.id] = globals.Duel(globals.DuelUser(message.author), uuid.uuid4(), message.channel.id)
            channelDuel = globals.duels.get(message.channel.id, None)
            globals.lastMessages[message.channel.id] = await message.send(f"{message.author.nick} has started a duel. Type **.fight** to duel them.")
            await self.startCancelCountdown(message, channelDuel.uuid)
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
        channelDuel.user_2 = globals.DuelUser(message.author)

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

        attackTypes = [".dds",
                       ".ags",
                       ".sgs",
                       ".claws",
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
                       ".claws",
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

            return channelDuel != None and message.author.id == savedTurn.user.id and attackTypeCheck == True and duel.turnCount == globals.duels[message.channel.id].turnCount
        
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

            if channelDuel.turn.user.id == channelDuel.user_1.user.id and channelDuel.uuid == duel.uuid:
                turnUser = channelDuel.user_1
                notTurn = channelDuel.user_2
            elif channelDuel.uuid == duel.uuid and channelDuel.turnCount == duel.turnCount:
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
        INSERT INTO duel_users (user_id, wins, losses, gp) 
        VALUES 
        ({winner.id}, 1, 0, 0) 
        ON CONFLICT (user_id) DO UPDATE 
        SET wins = duel_users.wins + 1 
        """,

            f"""
        INSERT INTO duel_users (user_id, wins, losses, gp) 
        VALUES 
        ({loser.id}, 0, 1, 0) 
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
            print("SOME ERROR 4", error)
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

    @commands.is_owner()
    @commands.command()
    async def test(self, message):
        await PotentialItems.generateLoot(self, message)


    @commands.command()
    async def hs(self, ctx):
        placeholderEmbed = discord.Embed(title="Wins highscores", description = "Checking the highscores...", color=discord.Color.gold())
        msg = await ctx.send(embed=placeholderEmbed)

        async def getWinsHighscores(ctx):
            sql = f"""
            SELECT nick, wins
            FROM duel_users
            ORDER BY wins DESC
            """

            conn = None
            leaderboard = []

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)

                rows = cur.fetchall()

                counter = 0
                for row in rows:
                    leaderboard.append(row)
                    counter += 1
                    if counter == 10:
                        return leaderboard

                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 4", error)
                return leaderboard
            finally:
                if conn is not None:
                    conn.close()
                return leaderboard

        # For when we have different high scores
        # if args == None:
        frontPage = await getWinsHighscores(ctx)

        description = ""

        if len(frontPage) == 0:
            errorEmbed = discord.Embed(title="Wins highscores", description="Something went wrong.", color=discord.Color.dark_red())
            await msg.edit(embed=errorEmbed)

        for n in range(0, len(frontPage)):
            description += f"**{frontPage[n][0]}**: {frontPage[n][1]} \n"

        frontPageEmbed = discord.Embed(title="Wins highscores", description=description, color=discord.Color.gold())
        await msg.edit(embed=frontPageEmbed)

    @commands.command()
    @commands.cooldown(1, 60*20, commands.BucketType.user)
    async def pk(self, ctx):
        await ctx.send('You head out into the wilderness on a PK trip...')

        await asyncio.sleep(60*20)

        randSuccessInt = randint(0, 6)
        
        if randint == 0:
                # USER DIED ON THEIR PKING TRIP
                await ctx.send(f"{ctx.author.mention}, you died on your pking trip. Type .pk to re-gear and go on another trip.")
                return

        loot = await PotentialItems(self.bot).rollLoot(ctx, 2, 3)

        sql = f"""
        UPDATE duel_users 
        SET gp = gp + {loot[995][1]} 
        WHERE user_id = {ctx.author.id}
        """
        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 3", error)
        finally:
            if conn is not None:
                conn.close()

            lootMessage = ""

            for item in loot.values():
                if item[0] != 'Coins':
                    
                    each = ''

                    if item[3] > 1 and type(item[2]) != int:
                        each = ' each' 

                    lootMessage += f"*{item[3]}x {item[4]} {item[0]} worth {item[2]} GP{each}* \n"
                    
            commaMoney = "{:,d}".format(loot[995][1])
            lootMessage += f"Total pking trip loot value: **{commaMoney} GP** {ItemEmojis.Coins.coins}"

            embed = discord.Embed(title=f"**Pking trip loot for {ctx.author.nick}:**", description=lootMessage, thumbnail='https://oldschool.runescape.wiki/images/a/a1/Skull_%28status%29_icon.png?fa6d8')

            await ctx.send(f"{ctx.author.mention} you have returned from your pking trip. Type .pk to go out again.", embed=embed)

    @pk.error
    async def pk_error(self, ctx, error):
        def getTime(seconds):

            seconds = int(seconds)
            hours = math.floor(seconds / 3600)
            minutes = math.floor((seconds / 60) % 60)
            timeSeconds = math.ceil(seconds - (hours * 3600) - (minutes * 60))
            
            return [hours, minutes, timeSeconds]

        if isinstance(error, commands.CommandOnCooldown):

            timeValues = getTime(error.retry_after)

            msg = f"You're already out on a pk trip. You should return in {timeValues[1]} minutes, and {timeValues[2]} seconds.".format(error.retry_after)
            await ctx.send(msg)
            return
        else:
            raise error

def setup(bot):
    bot.add_cog(UserCommands(bot))