import asyncio
import discord
import os
import random
import math
import psycopg2
import json
import requests
from cogs.osrsEmojis import ItemEmojis
from osrsbox import items_api
from random import randint
# import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']

class Dailies(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.triviaQuestions = {
            1: ["How much strength bonus do godswords have?", "132"],
            2: ["What is the magic level requirement for the elite wilderness diary?", "96"],
            3: ["What hunter level is required to hunt black chinchompas?", "73"],
            4: ["What level is the revenant dragon?", "135"],
            5: ["How much slayer xp does killing a revenant ork give?", "115"],
            6: ["Name one of the items on the revenant unique table.", ["craws bow", "thammarons sceptre", "viggoras chainmace", "amulet of avarice"]],
            7: ["How much GP does the emblem trader buy an ancient medallion for?", ["4m", "4000k", "4000000"]],
            8: ["What percent is the duel arena tax?", ["1%", "1", "1 percent"]],
            9: ["How many times do you need to casting a god spell in the Mage Arena before using it outside of the arena?", "100"],
            10: ["How many different wilderness team capes are there?", "50"],
            11: ["How many different clue scroll team capes are there?", "3"],
            12: ["What prayer is unlocked at level 25?", "protect item"],
            13: ["What hunter level is required to hunt black salamanders?", "67"],
            14: ["What thieving level is required to loot the rogues' chest?", "84"],
            15: ["What is the base amount of points you earn for completing a wilderness slayer task?", "25"],
            16: ["What is the combat level of Callisto?", "450"],
            17: ["What is the combat level of Scorpia?", "225"],
            18: ["What is the combat level of Vet'ion?", "454"],
            19: ["What is the combat level of Venenatis?", "464"],
            20: ["What is the combat level of the Chaos Elemental?", "305"],
            21: ["What is the combat level of the King Black Dragon?", "276"],
            22: ["What is the combat level of the Crazy Archaeologist?", "204"],
            23: ["Which weapon has a special attack called *'The Judgement'*", ["ags", "armadyl godsword"]],
            24: ["Which weapon has a special attack called *'Slice and Dice'*", ["dclaws", "dragon claws", "d claws"]]
        }

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(1, 60*60*12, commands.BucketType.user)
    async def daily(self, ctx):
        def triviaNum():
            randQuestion = randint(1, len(self.triviaQuestions))
            return randQuestion

        daily = self.triviaQuestions[triviaNum()]
        print('Trivia question:', daily[0], daily[1])

        def timeoutCheck(ctx):
            message = ctx.content.replace("'", '')
            return message.lower() in daily[1] and ctx.author == message.author

        await ctx.send(daily[0])

        try: 
            await self.bot.wait_for('message', check=timeoutCheck, timeout=15)
            await self.giveDailyMoney(ctx, True)
        except asyncio.TimeoutError:
            await self.giveDailyMoney(ctx, False)

    @daily.error
    async def daily_error(self, ctx, error):
        def getTime(seconds):

            seconds = int(seconds)
            hours = math.floor(seconds / 3600)
            minutes = math.floor((seconds / 60) % 60)
            timeSeconds = math.ceil(seconds - (hours * 3600) - (minutes * 60))
            
            return [hours, minutes, timeSeconds]

        if isinstance(error, commands.CommandOnCooldown):


            timeValues = getTime(error.retry_after)

            msg = f'You can claim your next daily reward in {timeValues[0]} hours, {timeValues[1]} minutes, and {timeValues[2]} seconds.'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    async def giveDailyMoney(self, ctx, correct):

        winnings = randint(2500000, 5000000)
        correctString = "You did not get the correct answer in time."

        if correct == True:
            winnings = winnings * 2
            correctString = "You got the answer correct!"

        duelArenaGuild = self.bot.get_guild(663113372580970509)

        # Attempt to retrieve the member, if they don't exist, ignore
        if duelArenaGuild.get_member(ctx.author.id) != None:
            winnings = math.floor(winnings * 1.5)

        sql = f"""
        UPDATE duel_users 
        SET gp = gp + {winnings} 
        WHERE user_id = {ctx.author.id}
        """

        commaMoney = "{:,d}".format(int(winnings))
        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 1", error)
        finally:
            if conn is not None:
                conn.close()
            await ctx.send(f"{correctString}\n{ItemEmojis.Coins.coins} {ctx.author.nick} received {commaMoney} GP from their daily!")

        
def setup(bot):
    bot.add_cog(Dailies(bot))