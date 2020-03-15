import asyncio
import discord
import os
import random
import math
import psycopg2
from random import randint
import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']


class StoreCommands(commands.Cog):

    def createStoreDatabase(self):
        sql = """
        CREATE TABLE IF NOT EXISTS pkingItems (
            user_id BIGINT PRIMARY KEY,
            dragon_claws integer NOT NULL,
            armadyl_godsword integer NOT NULL,
            saradomin_godsword integer NOT NULL,
            zamorak_godsword integer NOT NULL,
            bandos_godsword integer NOT NULL,
            saradomin_sword integer NOT NULL,
            granite_maul integer NOT NULL,
            dragon_warhammer integer NOT NULL,
            blowpipe integer NOT NULL
            )
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
        finally:
            if conn is not None:
                conn.close()

    def __init__(self, bot):
        self.bot = bot
        self.createStoreDatabase()

    @commands.command()
    async def buy(self, ctx, *args):
        print(args[0])
        print(type(args[0]))

        itemQuantity = 0
        try:
            itemQuantity = int(args[0])
        except TypeError:
            await ctx.send('Please enter a valid amount.')
            return

        itemList = ["dclaws",
                    "dragonclaws",
                    "dclaws",
                    "ags",
                    "armadylgodsword",
                    "sgs",
                    "saradomingodsword",
                    "zgs",
                    "zamorakgodsword",
                    "bgs",
                    "bandosgodsword",
                    "ss",
                    "saradominsword",
                    "gmaul",
                    "granitemaul",
                    "g maul",
                    "dwh",
                    "dragonwarhammer"
                    "bp",
                    "blowpipe",
                    "toxicblowpipe"]

        itemName = ""

        if len(args) == 1:  # If the user didn't include an item to purchase
            await ctx.send('Please enter a valid item.')
        elif len(args) == 2:  # If the args was one word long
            itemName = args[1]
        elif len(args) == 3:  # If the args was two words long
            itemName == args[1] + args[2]
        else:  # If the args was more than two words long, default to two words to concatenate for the item to purchase
            itemName == args[1] + args[2]

        if itemName in itemList:
            print('We can buy that for you!')

        else:
            print("Sorry, we don't sell that.")

        def purchaseItem(item, quantity):
            sql = f"""
                    SELECT
                    gp gp
                    FROM duel_users
                    WHERE user_id = {ctx.author.id}"""

            userGP = 0
            conn = None
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)

                rows = cur.fetchAll()

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


        # Price list -- maybe use API calls?
            # Dragon claws - 55M
            # Ags - 13M
            # Sgs - 34.5M
            # Zgs - 5.1M
            # Bgs - 10M
            # SS - 700K
            # Gmaul - 500k
            # DWH - 45M
            # Bp - 5M


def setup(bot):
    bot.add_cog(StoreCommands(bot))
