import asyncio
import discord
import os
import random
import math
import psycopg2
import json
import requests
from cogs.osrsEmojis import ItemEmojis
from cogs.mathHelpers import RSMathHelpers
from osrsbox import items_api
from random import randint
import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']


class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Formatted as ID:[price, name]
    rareIDs = {
        "redpartyhat": [1038, 225000000, "Red partyhat"],
        "bluepartyhat": [1042, 250000000, "Blue partyhat"],
        "yellowpartyhat": [1040, 225000000, "Yellow partyhat"],
        "greenpartyhat": [1044, 225000000, "Green partyhat"],
        "purplepartyhat": [1046, 200000000, "Purple partyhat"],
        "whitepartyhat": [1048, 225000000, "White partyhat"],
        "christmascracker": [962, 750000000, "Christmas cracker"],
        "redhalloweenmask": [1057, 50000000, "Red halloween mask"],
        "bluehalloweenmask": [1055, 50000000, "Blue halloween mask"],
        "greenhalloweenmask": [1053, 50000000, "Green halloween mask"],
        "santahat": [1050, 100000000, "Santa hat"],
        "pumpkin": [1959, 20000000, "Pumpkin"],
        "easteregg": [1961, 25000000, "Easter egg"]
    }

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

    # Removes an item from an user's table
    async def removeItemFromUser(self, userId, table, columnName, quantity):

        sql = f"""
        UPDATE {table}
        SET {columnName} = {columnName} - {quantity} 
        WHERE user_id = {userId}
        """

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR REMOVING ITEM", error)
            return False
        finally:
            if conn is not None:
                conn.close()
            return True

    # Gives an item to an user
    async def giveItemToUser(self, userId, table, columnName, quantity):

        sql = f"""
        UPDATE {table}
        SET {columnName} = {columnName} + {quantity} 
        WHERE user_id = {userId}
        """

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR REMOVING ITEM", error)
            return False
        finally:
            if conn is not None:
                conn.close()
            return True

    # Returns the number of an item that belong to an user
    async def getNumberOfItem(self, userId, table, columnName):

        sql = f"""
        SELECT
        {columnName} {columnName}
        FROM {table}
        WHERE user_id = {userId}
        """
        value = 0

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)

            rows = cur.fetchall()

            for row in rows:
                value = row[0]

            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME GETTING NUMBER OF ITEM", error)
            return 0
        finally:
            if conn is not None:
                conn.close()
            return value

    # Returns the value of an item based on the API call as an integer. Must use the item ID to make the API call
    async def getItemValue(self, itemId):
        print("Trying to find price for", itemId)
        url = f'http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={itemId}'

        try:
            response = requests.get(url)
            jsonResponse = response.json()
            itemPrice = jsonResponse['item']['current']['price']
            print("Price found", itemPrice)
            return RSMathHelpers.numify(self, itemPrice)
        except:
            print(f"Err fetching item {itemId} from Database.")
            return None

    # Creates the appropriate item tables for users when using item commands
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

    @commands.command()
    async def buy(self, ctx, *args):

        def get_key(val, itemDict):
            for key, value in itemDict.items():
                if val == value:
                    return key
            return None

        def getFullItemName(itemId):
            for item in globals.all_db_items:
                if item.id == itemId:
                    return item.name
        # Convert the arguments to a string usable for other searches
        async def convertArgsToItemString(args):

            itemName = ""

            if len(args) == 1:  # If the user didn't include an item to purchase
                await ctx.send('Please enter a valid item.')
                return
            elif len(args) == 2:  # If the args was one word long
                itemName = args[1]
            elif len(args) == 3:  # If the args was two words long
                itemName = args[1] + args[2]
            else:  # If the args was more than two words long, default to two words to concatenate for the item to purchase
                for n in range(1, len(args)):
                    itemName += args[n]

            itemName = itemName.lower()
            return itemName

        async def convertArgsToQuantity(arg):
            itemQuantity = 0
            # If the user does not enter a valid integer quantity of items to purchase
            try:
                itemQuantity = int(arg)

                if itemQuantity > 0:
                    return itemQuantity
                else:
                    await ctx.send('You must buy at least one item.')
                    return

            except TypeError:

                await ctx.send('Please enter a valid amount.')
                return

            except ValueError:

                await ctx.send('Proper syntax is *.buy [quantity] [item name].*')
                return

        # Create a table row for the user if it does not exist already
        await self.createPlayerItemTable(ctx.author.id)

        # Get the string of the items, formatted without spaces
        # i.e. redpartyhat
        itemName = await convertArgsToItemString(args)

        # Get the quantity of the item, formatted as int
        itemQuantity = await convertArgsToQuantity(args[0])

        # Get user's cash stack
        userGP = await self.getNumberOfItem(ctx.author.id, "duel_users", "gp")

        itemPrice = None
        itemId = None
        itemString = None
        table = None

        # Find item in one of the dictionaries
        if itemName in self.rareIDs.keys():
            # If the item is a rare
            itemId = self.rareIDs[itemName][0]
            itemPrice = self.rareIDs[itemName][1]
            itemString = self.rareIDs[itemName][2]
            table = "duel_rares"
        elif itemName in self.itemList.values():
            # if the item is a regular item
            itemId = get_key(itemName, self.itemList)
            itemPrice = await self.getItemValue(itemId)

            itemString = getFullItemName(itemId)
            table = "pking_items"
        else:
            await ctx.send("I don't sell that item.")
            return

        if itemPrice == None:
            await ctx.send("There was an error fetching the item price. Please try again.")
            return

        totalPurchasePrice = itemPrice * itemQuantity
        commaMoney = "{:,d}".format(totalPurchasePrice)

        if userGP >= totalPurchasePrice:

            await self.removeItemFromUser(ctx.author.id, "duel_users", "gp", totalPurchasePrice)
            await self.giveItemToUser(ctx.author.id, table, f"_{itemId}", itemQuantity)
            await ctx.send(f"You have bought {itemQuantity}x {itemString} for {commaMoney} GP.")
            return

        elif userGP < totalPurchasePrice:

            await ctx.send(f"You need {commaMoney} GP to purchase {itemQuantity}x {itemString}.")
            return

    @commands.command()
    async def sell(self, ctx, *args):
        def get_key(val, itemDict):
            for key, value in itemDict.items():
                if val == value:
                    return key
            return None

        def getFullItemName(itemId):
            for item in globals.all_db_items:
                if item.id == itemId:
                    return item.name
        # Convert the arguments to a string usable for other searches
        async def convertArgsToItemString(args):

            itemName = ""

            if len(args) == 1:  # If the user didn't include an item to purchase
                await ctx.send('Please enter a valid item.')
                return
            elif len(args) == 2:  # If the args was one word long
                itemName = args[1]
            elif len(args) == 3:  # If the args was two words long
                itemName = args[1] + args[2]
            else:  # If the args was more than two words long, default to two words to concatenate for the item to purchase
                for n in range(1, len(args)):
                    itemName += args[n]

            return itemName

        async def convertArgsToQuantity(arg):
            itemQuantity = 0
            # If the user does not enter a valid integer quantity of items to purchase
            try:
                itemQuantity = int(arg)

                if itemQuantity > 0:
                    return itemQuantity
                else:
                    await ctx.send('You must sell at least one item.')
                    return

            except TypeError:

                await ctx.send('Please enter a valid amount.')
                return

            except ValueError:

                await ctx.send('Proper syntax is *.buy [quantity] [item name].*')
                return

        # Create a table row for the user if it does not exist already
        await self.createPlayerItemTable(ctx.author.id)

        # Get the string of the items, formatted without spaces
        # i.e. redpartyhat

        itemName = await convertArgsToItemString(args)

        # Get the quantity of the item, formatted as int
        itemQuantity = await convertArgsToQuantity(args[0])

        itemPrice = None
        itemId = None
        itemString = None
        table = None

        # Find item in one of the dictionaries
        if itemName in self.rareIDs.keys():
            # If the item is a rare
            itemId = self.rareIDs[itemName][0]
            itemPrice = self.rareIDs[itemName][1]
            itemString = self.rareIDs[itemName][2]
            table = "duel_rares"
        elif itemName in self.itemList.values():
            # if the item is a regular item
            itemId = get_key(itemName, self.itemList)
            itemPrice = await self.getItemValue(itemId)
            itemString = getFullItemName(itemId)
            table = "pking_items"
        else:
            await ctx.send("I don't buy that item.")
            return

        if itemPrice == None:
            await ctx.send("There was an error fetching the item price. Please try again.")
            return

        playerQuantity = await self.getNumberOfItem(ctx.author.id, table, f"_{itemId}")

        if itemQuantity > playerQuantity:
            await ctx.send(f"You do not have {itemQuantity}x {itemString} to sell.")
            return

        totalSalePrice = math.floor(itemPrice * itemQuantity * 0.8)
        commaMoney = "{:,d}".format(totalSalePrice)

        await self.removeItemFromUser(ctx.author.id, table, f"_{itemId}", itemQuantity)
        await self.giveItemToUser(ctx.author.id, "duel_users", "gp", totalSalePrice)
        await ctx.send(f"You have sold {itemQuantity}x {itemString} for {commaMoney} GP.")
        return


def setup(bot):
    bot.add_cog(Economy(bot))
