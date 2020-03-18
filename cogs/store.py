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
from cogs.economy import Economy
import psycopg2
from random import randint
import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']


class StoreCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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

    async def getItemData(self, itemId):
        url = f'http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={itemId}'

        try:
            response = requests.get(url)
            jsonResponse = response.json()
            return jsonResponse
        except:
            print(f"Err fetching item {itemId} from Database.")
            return None

    @commands.command()
    async def items(self, ctx):

        await self.createPlayerItemTable(ctx.author.id)

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

    @commands.command()
    async def price(self, ctx, *args):
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

            if len(args) == 0:  # If the user didn't include an item to purchase
                await ctx.send('Please enter a valid item.')
                return
            elif len(args) == 1:  # If the args was one word long
                itemName = args[0]
            elif len(args) == 2:  # If the args was two words long
                itemName = args[0] + args[1]
            else:  # If the args was more than two words long, default to two words to concatenate for the item to purchase
                for n in range(0, len(args)):
                    itemName += args[n]

            return itemName

        # Get the string of the items, formatted without spaces
        # i.e. redpartyhat
        itemName = await convertArgsToItemString(args)

        itemPrice = None
        itemId = None
        itemString = None
        isCustom = False

        # Find item in one of the dictionaries
        if itemName in Economy.rareIDs.keys():
            # If the item is a rare
            itemId = Economy.rareIDs[itemName][0]
            itemPrice = Economy.rareIDs[itemName][1]
            itemString = Economy.rareIDs[itemName][2]
            isCustom = True
        else:

            # Find the item in the global database of items
            for item in globals.all_db_items:
                # If the item name matches the queried item
                if item.name.replace(' ', '').lower() == itemName:
                    # If the item is tradable on the G/
                    if item.tradeable_on_ge == True:
                        itemPrice = await Economy.getItemValue(self, item.id)
                        itemId = item.id
                        break
                else:
                    pass

        if itemPrice == None:
            await ctx.send("There was an error fetching the item price. Please try again.")
            return

        itemJSON = await self.getItemData(itemId)
        print(itemJSON)

        if itemJSON == None:
            await ctx.send("There was an error fetching the item data. Please try again.")

        commaMoney = "{:,d}".format(itemPrice)
        embed = discord.Embed(title=itemJSON['item']['name'], description=f"*{itemJSON['item']['description']}*")
        embed.set_thumbnail(url=itemJSON['item']['icon'])

        embedDescription = f"{commaMoney} GP"
        
        if isCustom == True:
            embedDescription += "\n *This price is customized for this bot.*"

        embed.add_field(name="Price", value = embedDescription)


        await ctx.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(StoreCommands(bot))
