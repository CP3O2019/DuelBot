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

def setup(bot):
    bot.add_cog(StoreCommands(bot))
