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


class Referrals(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def refer(self, ctx, referralUser):

        sanitizedReferral = referralUser.replace('<','').replace('>', '').replace('@', '').replace('!','')

        if referralUser not in ctx.guild.members:
            await ctx.send('Please tag an appropriate user using the @ symbol.')
            return

        if sanitizedReferral == str(ctx.author.id):
            await ctx.send('You cannot give your referral to yourself.')
            return

        async def getReferral():
            sql = f"""
            SELECT
            referral
            FROM duel_users
            WHERE user_id = {ctx.author.id}
            """

            referData = None

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                data = cur.fetchall()
                for row in data:
                    referData = row[0]
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR OVER HEERE", error)
            finally:
                if conn is not None:
                    conn.close()

            return referData

        async def giveReferral(toUserId):
            sql = f"""
            UPDATE duel_users
            SET referral = {toUserId}
            WHERE user_id = {ctx.author.id}
            """

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 342343", error)
            finally:
                if conn is not None:
                    conn.close()

                await Economy(self.bot).giveItemToUser(toUserId, 'duel_users', 'gp', 25000000)
                await Economy(self.bot).giveItemToUser(ctx.author.id, 'duel_users', 'gp', 25000000)
                await ctx.send(f'You have given your one-time referral to <@!{toUserId}> and both of you receive 25m gp')
                return

        previousReferral = await getReferral()

        if previousReferral != None:
            await ctx.send("You have already given out your one-time referral.")

        else:
            await giveReferral(sanitizedReferral)

def setup(bot):
    bot.add_cog(Referrals(bot))
