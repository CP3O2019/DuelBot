import asyncio
import discord
import os
import random
import math
import psycopg2
import json
import requests
import time
from datetime import datetime, timedelta
from cogs.osrsEmojis import ItemEmojis
from cogs.mathHelpers import RSMathHelpers
from osrsbox import items_api
from cogs.economy import Economy
from random import randint
import threading
import schedule
import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']
 
class Lottery(commands.Cog):

    async def pickWinner(self):

        print('attempting to pick winner!')
        totalTickets = 0
        ticketArray = []

        def pickWinnerFromArray():
            if len(ticketArray) > 0:
                return random.choice(ticketArray)
            else:
                return None

        sql = """
        SELECT
        user_id,
        nick,
        numTickets
        FROM lottery
        """
        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:
                print(row)
                totalTickets += row[2]
                for n in range(1, row[2]):
                    ticketArray.append([row[0], row[1], row[2]])
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return
        finally:
            if conn is not None:
                conn.close()

        def clearWinnerDB():

            sql = "DELETE FROM lottery"
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

        # Pick a winner
        winnerList = pickWinnerFromArray()

        # Calculate the prize money
        totalPrize = RSMathHelpers(self.bot).shortNumify(totalTickets * 9000000, 1)

        # Log that someone won the lottery
        print(f"Lottery winner chosen! {winnerList[0]} wins {totalPrize}")

        # Give the winner their prize money
        await Economy(self.bot).giveItemToUser(winnerList[0], 'duel_users', 'gp', totalTickets * 9000000)

        # Send notification to the #notifications channel of the lottery winner
        notifChannel = self.bot.get_channel(689313376286802026)
        await notifChannel.send(f"**{winnerList[1]}** has won the lottery worth **{totalPrize}**! \n The next lottery will be in 12 hours. Use *.lottery buy (quantity)* to buy tickets for 10m each.")

        # Empty the lottery DB
        clearWinnerDB()

    def runPickWinnerThread(self):
        asyncio.run_coroutine_threadsafe(self.pickWinner(), self.bot.loop)

    def __init__(self, bot):
        self.bot = bot

        schedstop = threading.Event()
        def timer():
            while not schedstop.is_set():
                schedule.run_pending()
                time.sleep(3)

        schedthread = threading.Thread(target=timer)
        schedthread.start()

        # Works off of UTC --> 5PM PST is 0:00,  7PM is 02:00
        schedule.every().day.at("01:00").do(bot.loop.call_soon_threadsafe, self.runPickWinnerThread)
        schedule.every().day.at("13:00").do(bot.loop.call_soon_threadsafe, self.runPickWinnerThread)

    @commands.command()
    async def lottery(self, ctx, *args):

        quantity = None
        print(args)
        if len(args) > 0:
            if args[0] == 'buy':
                quantity = int(args[1])


        async def getNumTickets():

            def timeUntilNoon():
                now = datetime.now()
                today = datetime.now()
                lottoEndPM = datetime(year=today.year, month=today.month, day=today.day, hour=1, minute=0, second=0)
                                    
                lottoEndAM = datetime(year=today.year, month=today.month, day=today.day, hour=13, minute=0, second=0)

                delta = None

                pmDelta = lottoEndPM - now
                amDelta = lottoEndAM - now

                if pmDelta.seconds < amDelta.seconds:
                    delta = pmDelta
                else:
                    delta = amDelta

                seconds = delta.seconds
                hours = math.floor(seconds / 3600)
                minutes = math.floor((seconds / 60) % 60)
                timeSeconds = math.ceil(seconds - (hours * 3600) - (minutes * 60))

                return [hours, minutes, timeSeconds]

            sql = """
            SELECT
            numTickets
            FROM lottery
            """
            conn = None
            totalTickets = 0

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall()
                for row in rows:
                    totalTickets += row[0]
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()

            totalPrize = RSMathHelpers(self.bot).shortNumify(totalTickets * 9000000, 1)
            timeLeft = timeUntilNoon()


            sql2 = f"""
            SELECT
            numTickets
            FROM lottery
            WHERE user_id = {ctx.author.id}
            """
            conn = None
            userTickets = 0

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql2)
                rows = cur.fetchall()
                for row in rows:
                    userTickets += row[0]
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()

                description = f"""You have purchased **{userTickets}** tickets 
                Total tickets in lottery: **{totalTickets}**
                Total lottery prize: **{totalPrize}**
                Lottery ends in {timeLeft[0]} hours, {timeLeft[1]} minutes, and {timeLeft[2]} seconds."""

                embed = discord.Embed(title="DuelBot lottery", description=description, color = discord.Color.gold())
                embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/5/52/Castle_wars_ticket.png?190d3')
                await ctx.send(embed=embed)

        async def purchaseTicket(numTicks):

            # Check to see if the quantity is an integer
            try:
                quantity = int(numTicks)
            except:
                await ctx.send('You must purchase a whole number of tickets.')
                return False

            # SQL query
            sql = f"""
            INSERT INTO lottery (user_id, nick, numTickets) 
            VALUES 
            ({ctx.author.id}, '{ctx.author.nick}', {numTicks}) 
            ON CONFLICT (user_id) DO UPDATE 
            SET numTickets = lottery.numTickets + {numTicks}
            """
            conn = None

            # Count the number of tickets purchased
            totalTickets = 0

            # Execute sql
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                await ctx.send('Your tickets could not be purchased.')
                return False
            finally:
                if conn is not None:
                    conn.close()
            await Economy(self.bot).removeItemFromUser(ctx.author.id, 'duel_users', 'gp', numTicks * 10000000)
            cost = RSMathHelpers(self.bot).shortNumify(numTicks * 10000000, 1)
            await ctx.send(f'You have purchased {numTicks} lottery tickets {ItemEmojis.Misc.ticket} for {cost} gp')
            return True

        if len(args) == 0:
            await getNumTickets()
        # If the comand is to buy a ticket and there is a valid quantity being purchased
        elif args[0] == 'buy' and type(quantity) == int:

            # Get the user's current FP
            userGP = await Economy(self.bot).getNumberOfItem(ctx.author.id, 'duel_users', 'gp')

            # Verify the user has enough gp to make the purchase
            if userGP >= quantity * 10000000:
                # Attempt to purchase the ticket if the user has enough gp
                success = await purchaseTicket(quantity)
                if success == False:
                    return
            else:
                # Return a message saying the user doesn't have enough gp
                cost = RSMathHelpers(self.bot).shortNumify(quantity * 10000000, 1)
                await ctx.send(f"You need {cost} gp to purchase {quantity} lottery tickets.")
                return
            
        # If the command is to get info about the lottery
        elif args[0] == 'info':
            await getNumTickets()

        # User wants more info about the lottery
        elif args[0] == 'help':
            message = """
            ```Lottery commands
            .lottery buy (number) - buys lottery tickets for 10m gp each
            .lottery or .lottery info - shows information about the current lottery```
            """

            await ctx.send(message)
           
    @commands.command()
    async def pickwinner(self, ctx):
        await self.pickWinner()


def setup(bot):
    bot.add_cog(Lottery(bot))
