import asyncio
import discord
import os
import random
import math
import psycopg2
import json
import datetime
from datetime import datetime, timedelta
import requests
from cogs.osrsEmojis import ItemEmojis
from cogs.mathHelpers import RSMathHelpers
from cogs.economy import Economy
from cogs.loots import PotentialItems
from osrsbox import items_api
from random import randint
from random import choice
import globals
import time
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']


class Wilderness(commands.Cog):

    locations = {
        "wests": {
            "nicknames": [],
            "risk": 0.6,
            "uniques": [],
            "players": []
        },

        "easts": {
            "nicknames": [],
            "risk": 0.7,
            "uniques": [],
            "players": []
        },

        "mb": {
            "nicknames": [],
            "risk": 0.8,
            "uniques": [],
            "players": []
        },

        "edge": {
            "nicknames": [],
            "risk": 0.6,
            "uniques": [],
            "players": []
        },

        "lavas": {
            "nicknames": [],
            "risk": 0.9,
            "uniques": [],
            "players": []
        },

        "revs": {
            "nicknames": [],
            "risk": 1.0,
            "uniques": [21804, 21807, 21810, 21813, 21817, 22299, 22302, 22305, 4087, 4585, 22542, 22547, 22552],
            "players": []
        }

    }

    def addPlayerToRegion(self, region, player):
        locations[region]["players"].append(player)

    def removePlayerFromRegion(self, region, player):
        locations[region]["players"].remove(player)

    async def checkTripTime(self, userId):

        sql = f"""
        SELECT
        activitystatus,
        activitytime
        FROM duel_users
        WHERE user_id = {userId}
        """

        conn = None
        activityInfo = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:
                activityInfo = row
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 90", error)
        finally:
            if conn is not None:
                conn.close()

        return row

    # Updates the DB to show the latest activity begin time    
    async def startTripSQL(self, userId):

        now = math.floor(time.time())

        sql = f"""
        UPDATE duel_users
        SET 
        activitystatus = 'pking',
        activitytime = {now}
        WHERE user_id = {userId}
        """

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 25", error)
        finally:
            if conn is not None:
                conn.close()

    async def endTripSQL(self, userId):
        sql = f"""
        UPDATE duel_users
        SET 
        activitystatus = 'idle'
        WHERE user_id = {userId}
        """

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 34", error)
        finally:
            if conn is not None:
                conn.close()

    def endTripLocal(self, userId, location):
        self.locations[location]['players'].remove(userId)

    async def stealOpponentsLoot(self, winner, loser):
        sql = f"""
            SELECT
            DU.user_id,
            DU.gp,
            DR._1038,
            DR._1040,
            DR._1042,
            DR._1044,
            DR._1046,
            DR._1048,
            DR._962,
            DR._1053,
            DR._1055,
            DR._1057,
            DR._1050,
            DR._1959,
            DR._1961,
            PI._13652,
            PI._11802,
            PI._11804,
            PI._11806,
            PI._11808,
            PI._11838,
            PI._4153,
            PI._13576,
            PI._12924

            FROM ((duel_users DU
            LEFT JOIN duel_rares DR ON DU.user_id = DR.user_id)
            LEFT JOIN pking_items PI ON DU.user_id = PI.user_id)
            WHERE DU.user_id = {loser}
            """

        itemRow = None
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:
                itemRow = row
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 3", error)
        finally:
            if conn is not None:
                conn.close()
        

            # Check to see if the user has... any items or gp at all
            if len(list(filter(lambda x: x != 0, itemRow[1:23]))) == 0:

                # If they have absolutely no gp, rares, or items
                return False

            coins = itemRow[1]
            raresList = itemRow[2:14]
            itemList = itemRow[15:23]

            choices = [coins, coins, coins, itemList, itemList, raresList]

            # If the 
            if len(list(filter(lambda x: x != 0, raresList))) == 0:
                choices = list(filter(lambda x: x == raresList, choices))
            if len(list(filter(lambda x: x != 0, itemList))) == 0:
                choices = list(filter(lambda x: x == itemList, choices))
            if coins == 0:
                choices = list(filter(lambda x: x == coins, choices))

            if len(choices) == 0:
                # All options were removed, user has no gp, rares, or items
                return None

            tableRoll = random.choice(choices)

            # user_id is index 0

            # Roll until you hit a number in the array that isn't 0
            def rollForItem(myList, listName):
                roll = randint(0, len(myList)-1)

                if myList[roll] == 0:
                    rollForItem(myList, listName)
                else:
                    return [roll, 1, listName]
            
            rolledItem = None

            while rolledItem == None:
                if tableRoll == raresList:
                    print('Rolling the rares table')
                    # Rolled the rares table
                    # Indeces include 2-14
                    rolledItem = rollForItem(raresList, 'duel_rares')
                    print("Rolled item in tableRoll", rolledItem)
                    
                elif tableRoll == itemList:
                    print('Rolling the items table')
                    # Rolled the items table
                    # Indeces include 15-23
                    rolledItem = rollForItem(itemList, 'pking_items')
                    print("Rolled item in tableRoll", rolledItem)

                    # Steal 1 of the item

                elif tableRoll == coins:
                    print('Rolling the gp table')
                    # Rolled the gp Table
                    # Index 1
                    # Steal between 0 and 1/10th of the player's GP net worth
                    rolledItem = [0, randint(0, math.floor(coins * 0.1)), 'duel_users']


            # Formatted as [index, quantity, table]
            # e.g. [5, 1, 'pking_items']
            def convertToSQL():
                index = rolledItem[0]
                quantity = rolledItem[1]
                table = rolledItem[2]
                
                completeInfo = {}


                # Convert the roll into SQL query-able information (the right colmumn)
                if table == 'duel_users':
                    completeInfo['column'] = 'gp'
                    completeInfo['emoji'] = ItemEmojis.Coins.coins
                    completeInfo['itemName'] = 'gp'

                elif table == 'duel_rares':

                    info = None
                    itemName = None
                    emoji = None

                    if index == 0:
                        info = '_1038'
                        itemName = 'Red partyhat'
                        emoji = ItemEmojis.Rares.redPartyhat
                    elif index == 1:
                        info = '_1040'
                        itemName = 'Yellow partyhat'
                        emoji = ItemEmojis.Rares.yellowPartyhat
                    elif index == 2:
                        info = '_1042'
                        itemName = 'Blue partyhat'
                        emoji = ItemEmojis.Rares.bluePartyhat
                    elif index == 3:
                        info = '_1044'
                        itemName = 'Green partyhat'
                        emoji = ItemEmojis.Rares.greenPartyhat
                    elif index == 4:
                        info = '_1046'
                        itemName = 'Purple partyhat'
                        emoji = ItemEmojis.Rares.purplePartyhat
                    elif index == 5:
                        info = '_1048'
                        itemName = 'White partyhat'
                        emoji = ItemEmojis.Rares.whitePartyhat
                    elif index == 6:
                        info = '_962'
                        itemName = 'Christmas cracker'
                        emoji = ItemEmojis.Rares.christmasCracker
                    elif index == 7:
                        info = '_1057'
                        itemName = 'Red halloween mask'
                        emoji = ItemEmojis.Rares.redHween
                    elif index == 8:
                        info = '_1055'
                        itemName = 'Blue halloween mask'
                        emoji = ItemEmojis.Rares.blueHween
                    elif index == 9:
                        info = '_1053'
                        itemName = 'Green halloween mask'
                        emoji = ItemEmojis.Rares.greenHween
                    elif index == 10:
                        info = '_1050'
                        itemName = 'Santa hat'
                        emoji = ItemEmojis.Rares.santaHat
                    elif index == 11:
                        info = '_1959'
                        itemName = 'Pumpkin'
                        emoji = ItemEmojis.Rares.pumpkin
                    elif index == 12:
                        info = '_1961'
                        itemName = 'Easter egg'
                        emoji = ItemEmojis.Rares.easterEgg

                    completeInfo['column'] = info
                    completeInfo['emoji'] = emoji
                    completeInfo['itemName'] = itemName

                elif table == 'pking_items':

                    info = None
                    itemName = None
                    emoji = None

                    if index == 0:
                        info = '_13652'
                        itemName = 'Dragon claws'
                        emoji = ItemEmojis.RaidsItems.dragonClaws
                    elif index == 1:
                        info = '_11802'
                        itemName = 'Armadyl godsword'
                        emoji = ItemEmojis.Armadyl.armadylGodsword
                    elif index == 2:
                        info = '_11804'
                        itemName = 'Bandos godsword'
                        emoji = ItemEmojis.Bandos.bandosGodsword
                    elif index == 3:
                        info = '_11806'
                        itemName = 'Saradomin godsword'
                        emoji = ItemEmojis.Saradomin.saradominGodsword
                    elif index == 4:
                        info = '_11808'
                        itemName = 'Zamorak godsword'
                        emoji = ItemEmojis.Zamorak.zamorakGodsword
                    elif index == 5:
                        info = '_11838'
                        itemName = 'Saradomin sword'
                        emoji = ItemEmojis.Saradomin.saradominSword
                    elif index == 6:
                        info = '_4153'
                        itemName = 'Granite maul'
                        emoji = ItemEmojis.SlayerItems.graniteMaul
                    elif index == 7:
                        info = '_13576'
                        itemName = 'Dragon warhammer'
                        emoji = ItemEmojis.DragonItems.dragonWarhammer
                    elif index == 8:
                        info = '_12924'
                        itemName = 'Toxic blowpipe'
                        emoji = ItemEmojis.ZulrahItems.toxicBlowpipe

                    completeInfo['column'] = info
                    completeInfo['emoji'] = emoji
                    completeInfo['itemName'] = itemName

                return completeInfo

            itemDict = convertToSQL()
            itemDict['quantity'] = rolledItem[1]

            await Economy(self.bot).removeItemFromUser(loser, rolledItem[2], itemDict['column'], rolledItem[1])
            await Economy(self.bot).giveItemToUser(winner, rolledItem[2], itemDict['column'], rolledItem[1])

            return itemDict

    async def rollPlayerKills(self, ctx, region):
        # Iterate through each region
        for region, data in self.locations.items():

            for player in data["players"]:

                # Create a version of the play array that doesn't include the current player being rolled
                dataCopy = data["players"].copy()
                dataCopy.remove(player)
                playerListMinusCurrent = dataCopy
                print("Available players to attack:", playerListMinusCurrent)

                # Number of players in the region
                numPlayersInRegion = len(playerListMinusCurrent)

                # Base chance of running into another player in the region
                modifier = 32

                # Calculate chance of running into another player
                if numPlayersInRegion < 28:
                    modifier = modifier - numPlayersInRegion
                else:
                    modifier = 4

                # Roll the chance of finding another player
                # 0 means that another player is found
                # Minimum chance: 3.125% (for 1 other player)
                # Maximum chance: 25% (for 31+ other players)
                roll = randint(0, modifier)

                # If the player found another opponent in the wilderness
                if roll == 0:

                    # Pick a random player to attack
                    playerRoll = randint(0, numPlayersInRegion - 1)

                    # Find the attacked player
                    attackedPlayer = playerListMinusCurrent[playerRoll]

                    # Pick a winner for the fight
                    winner = random.choice([player, attackedPlayer])

                    # Remove the attacked player from the regional player list
                    # The attacking player was removed earlier when we ceated playerListMinusCurrent
                    data["players"].remove(player)
                    data["players"].remove(attackedPlayer)

                    loser = None

                    #  
                    if winner == player:
                        loser = attackedPlayer
                    elif winner == attackedPlayer:
                        loser = player

                    # Steal the item
                    stolenItem = await self.stealOpponentsLoot(winner, loser) 

                    # Sort the quantity of the item (most likely 1, but if it's gp it will format)
                    quant = RSMathHelpers(self.bot).shortNumify(stolenItem['quantity'], 1)

                    # Send message notifying person that their item has been stolem
                    await ctx.send(f"<@!{winner}> has killed <@!{loser}> for **{quant} {stolenItem['itemName']}** {stolenItem['emoji']}")

                    # Update SQL status for the winner
                    await self.endTripSQL(winner)

                    # Remove winner from location player array
                    self.endTripLocal(ctx.author.id, winner)

                    # Update SQL status for the lower
                    await self.endTripSQL(loser)

                    # Remove loser from location play array
                    self.endTripLocal(ctx.author.id, loser)

                    # Return successful player kill attempt
                    return True

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pk(self, ctx, *args):

        async def scry():
            playerCountArray = []
            for location in self.locations.values():
                playerCountArray.append(len(location['players']))

            embed = discord.Embed(title='You gaze into your scrying orb and see...', color=discord.Color.greyple())
            description = f""" Wests: {playerCountArray[0]} players
            Easts: {playerCountArray[1]} players
            Mage bank: {playerCountArray[2]} players
            Edgeville: {playerCountArray[3]} players
            Lava dragon isle: {playerCountArray[4]} players
            Revenant caves: {playerCountArray[5]} players 
            """
            embed.add_field(name="\u200b", value = description)
            embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/d/db/Harmonised_orb.png?0ed98')
            await ctx.send(embed=embed)

        commandList = ['wests', 'easts', 'mb', 'edge', 'lavas', 'revs', 'scry']

        if len(args) == 0 or args[0].lower() not in commandList:
            description = """**Pking has been revamped!** use .pk (region) to select a region to PK in.
            If there are other players in your region, there is a chance to pk them for their items, rares, or GP.
            You receive **extra loot** for pking at revs, lavas, and the mage bank.
            *example: ".pk revs*"""
            embed = discord.Embed(title='PKing commands', description=description, color=discord.Color.greyple())
            embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/a/a1/Skull_%28status%29_icon.png?fa6d8')
            embed.add_field(name='Regions', value= '**wests** | **easts** | **mb** | **edge** | **lavas** | **revs**', inline=False)
            embed.add_field(name ='Utility', value='**scry** - view how many players in each region \n**hs** - view .pk leaderboards (COMING SOON) \n**kd** - view your pk stats (COMING SOON)', inline=False)
            await ctx.send(embed=embed)
            return
        if args[0].lower() == 'scry':
            await scry()
            return

        timeStatus = await self.checkTripTime(ctx.author.id)
        # print("Difference", math.floor(time.time()) - timeStatus[1])

        if timeStatus[0] == 'idle' or timeStatus[0] == None: 
            await self.startTripSQL(ctx.author.id)

        # If the current time minus the time the activity started is less than 30 seconds apart, return this stuff
        elif timeStatus[0] != 'idle':
            timeDiff = math.floor(time.time()) - timeStatus[1]
            minutes = 20 - math.floor(timeDiff/60)
            await ctx.send(f"You are currently out {timeStatus[0]}. You should be back in around {minutes} minutes or less.")
            return

        self.locations[args[0].lower()]['players'].append(ctx.author.id)

        def convertToLongName(short):
            if short == 'wests':
                return 'Wests'
            if short == 'easts':
                return 'Easts'
            if short == 'mb':
                return 'the Mage bank'
            if short == 'edge':
                return 'Edgeville'
            if short == 'lavas':
                return 'Lava Dragon Isle'
            if short == 'revs':
                return 'the Revenant caves'
            else:
                return short

        await ctx.send(f'You head out into the wilderness on a PK trip to {convertToLongName(args[0])}. You should return in 20 minutes or less.')

        for n in range(1, 4):
            
            # Wait 4 minutes, 55 seconds
            await asyncio.sleep(4 * 59)

            # Grab the user's status (were they pked?)
            activityInfo = await self.checkTripTime(ctx.author.id)

            # If they're still pking
            if activityInfo[0] == 'pking':
                # Roll to see if they killed a player
                await self.rollPlayerKills(ctx, args[0])
            else:
                # If the trip is over (they got pked between their rolls)
                return

        loot = None
        if args[0] == 'revs' or args[0] == 'lavas' or args[0] == 'mb':
            loot = await PotentialItems(self.bot).rollLoot(ctx, 2, 3, 1)
        else:
            loot = await PotentialItems(self.bot).rollLoot(ctx, 2, 3, 0)

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

            embed = discord.Embed(title=f"**Pking trip loot for {ctx.author.nick}:**", description=lootMessage,
                                  thumbnail='https://oldschool.runescape.wiki/images/a/a1/Skull_%28status%29_icon.png?fa6d8')

            await ctx.send(f"{ctx.author.mention} you have returned from your pking trip. Type **y** to go out again.", embed=embed)
            await self.endTripSQL(ctx.author.id)
            self.endTripLocal(ctx.author.id, args[0])

            def timeoutCheck(message):
                print('Doing a timeout check', message.content.lower(), message.author.id, ctx.author.id)
                return message.content.lower() == 'y' and message.author.id == ctx.author.id

            try:
                await self.bot.wait_for('message', check=timeoutCheck, timeout=60)
                print('Attempting to pk')
                print("Ctx", ctx, " | args", args)
                await self.pk(ctx, args[0])
            except Exception as e:
                print("ERROR", e)
                await ctx.send('Didnt redo')
                pass


def setup(bot):
    bot.add_cog(Wilderness(bot))
