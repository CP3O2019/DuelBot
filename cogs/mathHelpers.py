import asyncio
import discord
import os
import random
import math
import psycopg2
import json
import requests
from osrsbox import items_api
from random import randint
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']

class RSMathHelpers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def numify(self, num):
        if type(num) == int or type(num) == float:
            return int(math.floor(num))
        elif type(num) == str:
            # Remove any commas
            cleanNum = num.replace(',', '')

            try:
                cleanNum = int(cleanNum)
                return cleanNum
            except ValueError:
                pass

            multiplier = 1

            if cleanNum[-1:] == 'k' or cleanNum[-1:] == 'K':  # Thousands
                multiplier = 1000
            elif cleanNum[-1:] == 'm' or cleanNum[-1:] == 'M':  # Millions
                multiplier = 1000 * 1000
            elif cleanNum[-1:] == 'b' or cleanNum[-1:] == 'B':  # Billions
                multiplier = 1000 * 1000 * 1000

            try:
                baseNum = float(cleanNum[0:-1])
                finalQuantity = int(math.floor(baseNum * multiplier))
                commaMoney = "{:,d}".format(finalQuantity)
                return finalQuantity
            except ValueError:
                return "couldn't multiply"

    def shortNumify(self, num, multiplier):

        def removeLastCharForRound(string):
            shortened = string
            if shortened[-1:] == '0':
                shortened = shortened[0:-1]
                if shortened[-1:] == '.':
                    shortened = shortened[0:-1]
                    return shortened
                else:
                    return removeLastCharForRound(shortened)
            else:
                return shortened


        try:
            rawNumber = self.numify(num) * multiplier

            shortened = ''
            if rawNumber >= 1000 * 1000 * 1000:
                output = rawNumber/(1000 * 1000 * 1000)
                shortened = "{0:.2f}".format(output)
                shortened = removeLastCharForRound(shortened)
                return f"{shortened}B"
            elif rawNumber >= 1000 * 1000:
                output = rawNumber/(1000 * 1000)
                shortened = "{0:.2f}".format(output)
                shortened = removeLastCharForRound(shortened)
                return f"{shortened}M"
            elif rawNumber > 1000:
                output = rawNumber/(1000)
                shortened = "{0:.2f}".format(output)
                shortened = removeLastCharForRound(shortened) 
                return f"{shortened}K"
            else:
                return rawNumber
        except:
            pass

    def tidy_float(s):
        """Return tidied float representation.
        Remove superflous leading/trailing zero digits.
        Remove '.' if value is an integer.
        Return '****' if float(s) fails.
        """
        # float?
        try:
            f = float(s)
        except ValueError:
            return '****'
        # int?
        try:
            i = int(s)
            return str(i)
        except ValueError:
            pass
        # scientific notation?
        if 'e' in s or 'E' in s:
            t = s.lstrip('0')
            if t.startswith('.'): t = '0' + t
            return t
        # float with integral value (includes zero)?
        i = int(f)
        if i == f:
            return str(i)
        assert '.' in s
        t = s.strip('0')
        if t.startswith('.'): t = '0' + t
        if t.endswith('.'): t += '0'
        return t
    
    async def checkUserGP(self, userId):
        sql = f"""
        SELECT
         gp gp
        FROM duel_users
        where user_id = {userId}
        """
        conn = None
        userGP = 0
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:
                userGP = row[0]
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("READING GP ERROR", error)
            return
        finally:
            if conn is not None:
                conn.close()
            print(f'user has {userGP} GP')
            return userGP

    async def removeGPFromUser(self, message, userId, amount):

        if amount <= await self.checkUserGP(userId):
            sql = f"""
            UPDATE duel_users 
            SET gp = gp - {amount} 
            WHERE user_id = {userId}
            """
            conn = None

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("REMOVING GP ERROR", error)
                return
            finally:
                if conn is not None:
                    conn.close()
                return True
        else:
            await message.send("You don't have that much GP.")
            return False

    async def giveGPToUser(self, message, userId, amount):

        sql = f"""
        UPDATE duel_users 
        SET gp = gp + {amount} 
        WHERE user_id = {userId}
        """
        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("REMOVING GP ERROR", error)
        finally:
            if conn is not None:
                conn.close()
        
def setup(bot):
    bot.add_cog(RSMathHelpers(bot))
