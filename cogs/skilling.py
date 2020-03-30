import asyncio
import discord
import os
import random
import math
import psycopg2
import json
import requests
import time
from cogs.osrsEmojis import ItemEmojis
from cogs.mathHelpers import RSMathHelpers
from cogs.economy import Economy
from osrsbox import items_api
from random import randint
import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']

class Skilling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def createSkillTable(self, user):
        sql = f"""
        INSERT INTO user_skills (user_id)
        VALUES
        ({user})
        ON CONFLICT (user_id) DO NOTHING
        """

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR SETTING UP TABLES", error)
        finally:
            if conn is not None:
                conn.close()

    def xpToLevel(self, experience): 
        experienceTable = [
            [1,0,0],
            [2,83,83],
            [3,174,91],
            [4,276,102],
            [5,388,112],
            [6,512,124],
            [7,650,138],
            [8,801,151],
            [9,969,168],
            [10,1154,185],
            [11,1358,204],
            [12,1584,226],
            [13,1833,249],
            [14,2107,274],
            [15,2411,304],
            [16,2746,335],
            [17,3115,369],
            [18,3523,408],
            [19,3973,450],
            [20,4470,497],
            [21,5018,548],
            [22,5624,606],
            [23,6291,667],
            [24,7028,737],
            [25,7842,814],
            [26,8740,898],
            [27,9730,990],
            [28,10824,1094],
            [29,12031,1207],
            [30,13363,1332],
            [31,14833,1470],
            [32,16456,1623],
            [33,18247,1791],
            [34,20224,1977],
            [35,22406,2182],
            [36,24815,2409],
            [37,27473,2658],
            [38,30408,2935],
            [39,33648,3240],
            [40,37224,3576],
            [41,41171,3947],
            [42,45529,4358],
            [43,50339,4810],
            [44,55649,5310],
            [45,61512,5863],
            [46,67983,6471],
            [47,75127,7144],
            [48,83014,7887],
            [49,91721,8707],
            [50,101333,9612],
            [51,111945,10612],
            [52,123660,11715],
            [53,136594,12934],
            [54,150872,14278],
            [55,166636,15764],
            [56,184040,17404],
            [57,203254,19214],
            [58,224466,21212],
            [59,247886,23420],
            [60,273742,25856],
            [61,302288,28546],
            [62,333804,31516],
            [63,368599,34795],
            [64,407015,38416],
            [65,449428,42413],
            [66,496254,46826],
            [67,547953,51699],
            [68,605032,57079],
            [69,668051,63019],
            [70,737627,69576],
            [71,814445,76818],
            [72,899257,84812],
            [73,992895,93638],
            [74,1096278,103383],
            [75,1210421,114143],
            [76,1336443,126022],
            [77,1475581,139138],
            [78,1629200,153619],
            [79,1798808,169608],
            [80,1986068,187260],
            [81,2192818,206750],
            [82,2421087,228269],
            [83,2673114,252027],
            [84,2951373,278259],
            [85,3258594,307221],
            [86,3597792,339198],
            [87,3972294,374502],
            [88,4385776,413482],
            [89,4842295,456519],
            [90,5346332,504037],
            [91,5902831,556499],
            [92,6517253,614422],
            [93,7195629,678376],
            [94,7944614,748985],
            [95,8771558,826944],
            [96,9684577,913019],
            [97,10692629,1008052],
            [98,11805606,1112977],
            [99,13034431,1228825]
        ]
        l = 0
        r = 99
        mid = None
        level = None

        if experience >= 13034431:
            level = 99
        else:
            # While the left is less than the right
            while l <= r: 

                # The mid is halfway between the left and right
                mid = l + math.ceil((r - l)/2); 

                # Check if x is present at mid 
                if experienceTable[mid][1] <= experience < experienceTable[mid+1][1]:
                    level = experienceTable[mid][0]
                    break
                    # return level
        
                # If x is greater, ignore left half 
                elif experienceTable[mid][1] < experience and experienceTable[mid+1][1] < experience: 
                    l = mid + 1
        
                # If x is smaller, ignore right half 
                else: 
                    r = mid - 1
        
        # If we reach here, then the element was not present 
        return level

    async def getLevel(self, userId, skill):
        sql = F"""SELECT
        {skill}_xp
        FROM user_skills
        WHERE user_id = {userId}
        """

        # List element containing the user's slayer experience
        level = 1
        row = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            for row in data:
                data = row
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 3", error)
        finally:
            if conn is not None:
                conn.close()

        level = self.xpToLevel(row[0])
        return level

    async def getCombatLevel(self, userId):

        #Get user's stats from SQL
        attack = await self.getLevel(userId, 'attack')
        strength = await self.getLevel(userId, 'strength')
        defence = await self.getLevel(userId, 'defence')
        hitpoints = await self.getLevel(userId, 'hitpoints')
        ranged = await self.getLevel(userId, 'ranged')
        magic = await self.getLevel(userId, 'magic')
        prayer = await self.getLevel(userId, 'prayer')

        # Calculate the combat attributed to each stat
        base = 0.25 * (defence + hitpoints + math.floor(prayer/2))
        meleeLevel = 0.325 * (attack + strength)
        rangedLevel = 0.325 * (math.floor(3*ranged/2))
        magicLevel = 0.325 * (math.floor(3*magic/2))

        # Calculate final combat level
        combatLevel = math.floor(base + max([meleeLevel, rangedLevel, magicLevel]))

        # Return combat level
        return combatLevel

    # Returns the level after adding experience to it
    async def addExperienceToStat(self, userId, skill, gainedXP):
        sql = f"""
        UPDATE user_skills
        SET {skill}_xp = {skill}_xp + {gainedXP}
        WHERE user_id = {userId}
        """

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 36", error)
        finally:
            if conn is not None:
                conn.close()

        afterLevel = await self.getLevel(userId, skill)
        return afterLevel

    @commands.command()
    async def buybones(self, ctx, amount):
        await self.createSkillTable(ctx.author.id)

        if amount == 'info':
            # Display info about prayer
            embed = discord.Embed(title="Prayer bonuses", description="Damage multiplier based on level", color=discord.Color.from_rgb(250, 250, 250))
            embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/f/f2/Prayer_icon.png?ca0dc')

            description_1 = f"""{ItemEmojis.Prayers.thickSkin} Thick skin - 1 - +0%
            {ItemEmojis.Prayers.burstOfStrength} Burst of Strength - 4 - +2%
            {ItemEmojis.Prayers.clarityOfThought} Clarity of Thought - 7 - +3.5%
            {ItemEmojis.Prayers.rockSkin} Rock Skin - 10 - +5%
            {ItemEmojis.Prayers.superhumanStrength} Superhm. Strength - 13 - +6.5%
            {ItemEmojis.Prayers.improvedReflexes} Improved Reflexes - 14 - +7%
            """
            description_2 = f"""{ItemEmojis.Prayers.steelSkin} Steel Skin - 28 - +14%
            {ItemEmojis.Prayers.ultimateStrength} Ultimate Strength - 31 - +15.5%
            {ItemEmojis.Prayers.incredibleReflexes} Incredible Reflexes - 34 - +17%
            {ItemEmojis.Prayers.chivalry} Chivalry - 60 - +30%
            {ItemEmojis.Prayers.piety} Piety - 70 - +35%
            {ItemEmojis.Skills.prayer} Mastery - 99 - 60%
            """

            description_3 = f"""Prayer experience costs **200 GP** per 1 experience
            To buy Prayer experience, use .buybones (GP amount)

            Your effective multiplier grows by ~0.5% per level, with a 10% bonus at 99.
            Even if your level is between upgrades, you will get a bonus. *(e.g. 80 prayer for +40%)*
            """

            embed.add_field(name='\u200b', value=description_1, inline=True)
            embed.add_field(name='\u200b', value=description_2, inline=True)
            embed.add_field(name='\u200b', value=description_3, inline=False)

            await ctx.send(embed=embed)
            return

        else:
            amount = RSMathHelpers(self.bot).numify(amount)
            if amount < 200:
                await ctx.send('You must purchase at least 1 xp. Each experience point costs 200 gp.')
                return

            userGP = await Economy(self.bot).getNumberOfItem(ctx.author.id, 'duel_users', 'gp')

            if amount > userGP:
                print("Here!")
                await ctx.send("You don't have that much GP.")
                return

            print("Didn't make it here")
            shortAmount = RSMathHelpers(self.bot).shortNumify(amount, 1)
            prayerXP = math.floor(amount/200)
            shortPrayerXP = RSMathHelpers(self.bot).shortNumify(prayerXP, 1)

            if type(amount) != int:

                await ctx.send("Please enter a valid amount.")
                
            else:
                userGP = await Economy(self.bot).getNumberOfItem(ctx.author.id, 'duel_users', 'gp')

                if userGP >= amount:

                    await Economy(self.bot).removeItemFromUser(ctx.author.id, 'duel_users', 'gp', amount)

                    startLevel = await self.getLevel(ctx.author.id, 'prayer')
                    await self.addExperienceToStat(ctx.author.id, 'prayer', prayerXP)
                    endLevel = await self.getLevel(ctx.author.id, 'prayer')

                    levelUpMessage = ""
                    if endLevel > startLevel:
                        levelUpMessage = f"Your prayer level is now {endLevel}."
                    
                    await ctx.send(f"{ItemEmojis.Skills.prayer} You have purchased {shortPrayerXP} prayer experience for {shortAmount} GP. {levelUpMessage}")

    @buybones.error
    async def buyBonesError(self, ctx, error):
        await ctx.send("Proper syntax is *.buybones [GP amount]*. Prayer experience can be bought for 200 GP each.")

    @commands.command()
    async def buyherb(self, ctx, amount):

        await self.createSkillTable(ctx.author.id)

        if amount == 'info':
            # Display info about prayer
            embed = discord.Embed(title="Herblore bonuses", description="Damage multiplier based on level", color=discord.Color.green())
            embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/0/03/Herblore_icon.png?ffa9e')

            description_1 = f"""{ItemEmojis.Potions.attack} Attack potions - 3 - +1%
            {ItemEmojis.Potions.strength} Strength potions - 12 - +2%
            {ItemEmojis.Potions.defence} Defence potions - 30 - +5%
            {ItemEmojis.Potions.prayer} Prayer potions - 38 - +10%
            {ItemEmojis.Potions.superAttack} Super attack potions - 45 - +20%
            {ItemEmojis.Potions.superStrength} Super strength potions - 55 - +30%
            {ItemEmojis.Potions.superRestore} Super restore potions - 63 - +40%
            """
            description_2 = f"""{ItemEmojis.Potions.superDefence} Super defence potions - 66 - +50%
            {ItemEmojis.Potions.divineSuperStrength} Divine combat potions - 70 - +60%
            {ItemEmojis.Potions.saradominBrew} Saradomin brews - 81 - +70%
            {ItemEmojis.Potions.superCombat} Super combat potion - 90 - +80%
            {ItemEmojis.Potions.divineSuperCombat} Divine super combat potions - 90 - +90%
            {ItemEmojis.Skills.herblore} Mastery - 99 - +100%
            """

            description_3 = """Herblore experience costs **350 GP** per 1 experience
            To buy Herblore experience, use .buyherb (GP amount)
            """

            embed.add_field(name='\u200b', value=description_1, inline=True)
            embed.add_field(name='\u200b', value=description_2, inline=True)
            embed.add_field(name='\u200b', value=description_3, inline=False)

            await ctx.send(embed=embed)
            return

        else:
            amount = RSMathHelpers(self.bot).numify(amount)
            if amount < 200:
                await ctx.send('You must purchase at least 1 xp. Each experience point costs 350 gp.')
                return

            userGP = await Economy(self.bot).getNumberOfItem(ctx.author.id, 'duel_users', 'gp')

            if amount > userGP:
                print("Here!")
                await ctx.send("You don't have that much GP.")
                return
            
            print("Didn't make it here herb")
            shortAmount = RSMathHelpers(self.bot).shortNumify(amount, 1)
            herbXP = math.floor(amount/350)
            shortHerbXp = RSMathHelpers(self.bot).shortNumify(herbXP, 1)

            if type(amount) != int:

                await ctx.send("Please enter a valid amount.")

            else:

                userGP = await Economy(self.bot).getNumberOfItem(ctx.author.id, 'duel_users', 'gp')

                if userGP >= amount:

                    await Economy(self.bot).removeItemFromUser(ctx.author.id, 'duel_users', 'gp', amount)

                    startLevel = await self.getLevel(ctx.author.id, 'herblore')
                    await self.addExperienceToStat(ctx.author.id, 'herblore', herbXP)
                    endLevel = await self.getLevel(ctx.author.id, 'herblore')

                    levelUpMessage = ""
                    if endLevel > startLevel:
                        levelUpMessage = f"Your herblore level is now {endLevel}."

                    await ctx.send(f"{ItemEmojis.Skills.herblore} You have purchased {shortHerbXp} herblore experience for {shortAmount} GP. {levelUpMessage}")

    @buyherb.error
    async def buyBonesError(self, ctx, error):
        print(error)
        await ctx.send("Proper syntax is *.buyherb [GP amount]*. Herblore experience can be bought for 350 GP each.")

def setup(bot):
    bot.add_cog(Skilling(bot))
