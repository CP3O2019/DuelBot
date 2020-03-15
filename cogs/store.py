
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

    def __init__(self, bot):
        self.bot = bot
        createStoreDatabase()

        def createStoreDatabase():
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
                blowpipe integer NOT NULL,
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

        # @commands.command()
        # async def buy(self, ctx, *args):
        #     print(args[0])
        #     print(args[1])



        # Price list -- maybe use API calls?
            # Dragon claws- 55M
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