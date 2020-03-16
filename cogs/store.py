import asyncio
import discord
import os
import random
import math
import json
import requests
from osrsbox import items_api
from cogs.mathHelpers import RSMathHelpers
from cogs.osrsEmojis import ItemEmojis
import psycopg2
from random import randint
import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']


class StoreCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def getUserGP(self, userId):
        sql = f"""
                SELECT 
                gp gp
                FROM duel_users
                WHERE user_id = {userId}
                """

        userGP = 0
        # totalCost = 0
        conn = None
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)

            rows = cur.fetchall()

            # Get the user's GP in their coffers and set the val
            for row in rows:
                userGP = row[0]

            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

            return userGP

    async def getUserItem(self, userId, itemId):
        sql = f"""
                SELECT 
                _{itemId} _{itemId}
                FROM pking_items
                WHERE user_id = {userId}
                """

        itemCount = 0

        conn = None
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)

            rows = cur.fetchall()

            # Get the user's GP in their coffers and set the val
            for row in rows:
                itemCount = row[0]

            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return -1
        finally:
            if conn is not None:
                conn.close()

            return itemCount

    async def getItemValue(self, itemId):
        url = f'http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={itemId}'

        try:
            response = requests.get(url)
            jsonResponse = response.json()
            itemPrice = jsonResponse['item']['current']['price']
            return RSMathHelpers.numify(self, itemPrice)
        except err:
            print(f"Err fetching item {itemId} from Database.")
            return 0

    async def createPlayerItemTable(self, userId):
        sql = f"""
        INSERT INTO pking_items (
            user_id,
            _13652,
            _11802,
            _11804,
            _11806,
            _11808,
            _11838,
            _4153,
            _13576,
            _12924
            ) 
        VALUES
        ({userId}, 0, 0, 0, 0, 0, 0, 0, 0, 0) 
        ON CONFLICT (user_id) DO NOTHING
        """
        conn = None
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return
        finally:
            if conn is not None:
                conn.close()

    async def purchaseItem(self, userId, itemId, itemQuantity):

        await self.createPlayerItemTable(userId)

        # Get price of the item
        itemPrice = await self.getItemValue(itemId)

        # Calculate the price of the purchase
        purchasePrice = itemPrice * itemQuantity

        # Remove the funds
        commands = (f"""
        UPDATE duel_users 
        SET gp = gp - {RSMathHelpers.numify(self, purchasePrice)}
        WHERE user_id = {userId}
        """,
                    f"""
        UPDATE pking_items 
        SET _{itemId} = _{itemId} + {itemQuantity}
        WHERE user_id = {userId}
        """
                    )

        # Execute sequel commands.
        # Return True if succeeds
        # Return False if fails
        # When using this command, return to a variable to ensure you can check for database failure
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
            return False
        finally:
            if conn is not None:
                conn.close()
            return True

    async def sellItem(self, userId, itemId, itemQuantity):

        # Create row for user if it does not exist
        await self.createPlayerItemTable(userId)

        # Get price of the item
        itemPrice = await self.getItemValue(itemId)

        # Calculate the price of the purchase

        salePrice = math.floor(RSMathHelpers.numify(
            self, itemPrice) * itemQuantity * 0.8)

        userItemQuantity = await self.getUserItem(userId, itemId)

        if itemQuantity > userItemQuantity:
            return False

        # Remove the funds
        commands = (f"""
        UPDATE duel_users 
        SET gp = gp + {RSMathHelpers.numify(self, salePrice)}
        WHERE user_id = {userId}
        """,
                    f"""
        UPDATE pking_items 
        SET _{itemId} = _{itemId} - {itemQuantity}
        WHERE user_id = {userId}
        """
                    )
        

        # Execute sequel commands.
        # Return True if succeeds
        # Return False if fails
        # When using this command, return to a variable to ensure you can check for database failure
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
            return False
        finally:
            if conn is not None:
                conn.close()
            return True

    @commands.command()
    async def buy(self, ctx, *args):
        def get_key(val, itemDict):
            for key, value in itemDict.items():
                if val == value:
                    return key

            return None

        itemQuantity = 0

        # If the user does not enter a valid integer quantity of items to purchase
        try:
            itemQuantity = int(args[0])
        except TypeError:
            await ctx.send('Please enter a valid amount.')
            return

        itemList = {
            13652: "dragonclaws",  # Dragon claws
            11802: "armadylgodsword",  # Armadyl godsword
            11804: "bandosgodsword",  # Bandos godsword
            11806: "saradomingodsword",  # Saradomin godsword
            11808: "zamorakgodsword",  # Zamorak godsword
            11838: "saradominsword",  # Saradomin sword
            4153: "granitemaul",  # Granite maul
            13576: "dragonwarhammer",  # Dragon warhammer
            12924: "toxicblowpipe"  # Toxic blowpipe
        }

        itemName = ""

        if len(args) == 1:  # If the user didn't include an item to purchase
            await ctx.send('Please enter a valid item.')
            return
        elif len(args) == 2:  # If the args was one word long
            itemName = args[1]
        elif len(args) == 3:  # If the args was two words long
            itemName = args[1] + args[2]
        else:  # If the args was more than two words long, default to two words to concatenate for the item to purchase
            itemName = args[1] + args[2]

        # Retrieve the ID of the item
        itemId = get_key(itemName, itemList)

        # Return if the item is not found in the item list
        if itemId == None:
            await ctx.send("I don't sell that item.")
            return

        # Get user's gp
        userGP = await self.getUserGP(ctx.author.id)
        itemValString = await self.getItemValue(itemId)
        itemPrice = RSMathHelpers.numify(self, itemValString)

        purchasePrice = itemPrice * itemQuantity

        fullItemName = ""

        for item in globals.all_db_items:
            if item.id == itemId:
                fullItemName = item.name

        # Attempt to purchase the item
        if userGP >= purchasePrice:

            # If the user has enough GP to buy the item
            purchase = await self.purchaseItem(ctx.author.id, itemId, itemQuantity)

            if purchase == False:
                # If something went wrong with the database
                await ctx.send('Something went wrong. Please try again.')
                return
            commaMoney = "{:,d}".format(purchasePrice)
            await ctx.send(f'You have bought {itemQuantity}x {fullItemName} for {commaMoney} GP.')
            return

        else:
            # If the user does not have enough GP to buy the item
            await ctx.send(f'You do not have enough GP to buy {itemQuantity}x {fullItemName}.')
            return

    @commands.command()
    async def sell(self, ctx, *args):
        def get_key(val, itemDict):
            for key, value in itemDict.items():
                if val == value:
                    return key

            return None

        itemQuantity = 0

        # If the user does not enter a valid integer quantity of items to purchase
        try:
            itemQuantity = int(args[0])
        except TypeError:
            await ctx.send('Please enter a valid amount.')
            return

        itemList = {
            13652: "dragonclaws",  # Dragon claws
            11802: "armadylgodsword",  # Armadyl godsword
            11804: "bandosgodsword",  # Bandos godsword
            11806: "saradomingodsword",  # Saradomin godsword
            11808: "zamorakgodsword",  # Zamorak godsword
            11838: "saradominsword",  # Saradomin sword
            4153: "granitemaul",  # Granite maul
            13576: "dragonwarhammer",  # Dragon warhammer
            12924: "toxicblowpipe"  # Toxic blowpipe
        }

        itemName = ""

        if len(args) == 1:  # If the user didn't include an item to purchase
            await ctx.send('Please enter a valid item.')
            return
        elif len(args) == 2:  # If the args was one word long
            itemName = args[1]
        elif len(args) == 3:  # If the args was two words long
            itemName = args[1] + args[2]
        else:  # If the args was more than two words long, default to two words to concatenate for the item to purchase
            itemName = args[1] + args[2]

        # Retrieve the ID of the item
        itemId = get_key(itemName, itemList)

        # Return if the item is not found in the item list
        if itemId == None:
            await ctx.send("I don't buy that item.")
            return

        itemPrice = await self.getItemValue(itemId)

        salePrice = itemPrice * itemQuantity

        fullItemName = ""

        for item in globals.all_db_items:
            if item.id == itemId:
                fullItemName = item.name

        # Attempt to sell the item
        sale = await self.sellItem(ctx.author.id, itemId, itemQuantity)

        if sale == False:
            # If something went wrong with the database
            await ctx.send("You don't have enough of that item.")
            return

        commaMoney = "{:,d}".format(math.floor(salePrice * 0.8))
        await ctx.send(f'You have sold {itemQuantity}x {fullItemName} for {commaMoney} GP.')

    @commands.command()
    async def items(self, ctx):
        sql = f"""
                SELECT 
                _13652 dragon_claws,
                _11802 armadyl_godsword,
                _11804 bandos_godsword,
                _11806 saradomin_godsword,
                _11808 zamorak_godsword,
                _11838 saradomin_sword,
                _4153 granite_maul,
                _13576 dragon_warhammer,
                _12924 toxic_blowpipe
                FROM pking_items
                WHERE user_id = {ctx.author.id}
                """

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            # Get the user's GP in their coffers and set the val
            for row in rows:
                embed = discord.Embed(title=f"{ctx.author.nick}'s items", color = discord.Color.blurple())
                embed.add_field(name=f"**Dragon claws** {ItemEmojis.RaidsItems.dragonClaws}", value=row[0])
                embed.add_field(name=f"**Armadyl godsword** {ItemEmojis.Armadyl.armadylGodsword}", value=row[1])
                embed.add_field(name=f"**Bandos godsword** {ItemEmojis.Bandos.bandosGodsword}", value=row[2])
                embed.add_field(name=f"**Saradomin godsword** {ItemEmojis.Saradomin.saradominGodsword}", value=row[3])
                embed.add_field(name=f"**Zamorak godsword** {ItemEmojis.Zamorak.zamorakGodsword}", value=row[4])
                embed.add_field(name=f"**Saradomin sword** {ItemEmojis.Saradomin.saradominSword}", value=row[5])
                embed.add_field(name=f"**Granite maul** {ItemEmojis.SlayerItems.graniteMaul}", value=row[6])
                embed.add_field(name=f"**Dragon warhammer** {ItemEmojis.DragonItems.dragonWarhammer}", value=row[7])
                embed.add_field(name=f"**Toxic blowpipe** {ItemEmojis.ZulrahItems.toxicBlowpipe}", value=row[7])

                await ctx.send(embed=embed)

            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return
        finally:
            if conn is not None:
                conn.close()
            


def setup(bot):
    bot.add_cog(StoreCommands(bot))
