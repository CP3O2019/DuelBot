import asyncio
import discord
import os
import random
import math
import psycopg2
import json
import requests
import time
from osrs_highscores import Highscores
from cogs.osrsEmojis import ItemEmojis
from cogs.mathHelpers import RSMathHelpers
from osrsbox import items_api
from random import randint
import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']


class Highscores(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    class HighscoresUser:

        class Skills:
            total = {}
            attack = {}
            defence = {}
            strength = {}
            hitpoints = {}
            ranged = {}
            prayer = {}
            magic = {}
            cooking = {}
            woodcutting = {}
            fletching = {}
            fishing = {}
            firemaking = {}
            crafting = {}
            smithing = {}
            mining = {}
            herblore = {}
            agility = {}
            thieving = {}
            slayer = {}
            farming = {}
            runecraft = {}
            hunter = {}
            construction = {}

        class Bosses:
            sire = {}
            hydra = {}
            barrows = {}
            bryophyta = {}
            cerberus = {}
            callisto = {}
            cox = {}
            coxcm = {}
            chaosele = {}
            chaosfan = {}
            zilyana = {}
            corp = {}
            crazyArchaeologist = {}
            prime = {}
            rex = {}
            supreme = {}
            derangedArchaeologist = {}
            graardor = {}
            mole = {}
            grotesqueGuardians = {}
            hespori = {}
            kq = {}
            kbd = {}
            kraken = {}
            kreearra = {}
            kril = {}
            mimic = {}
            nightmare = {}
            obor = {}
            sarachnis = {}
            scorpia = {}
            skotizo = {}
            gauntlet = {}
            corrgauntlet = {}
            thermonuclear = {}
            zuk = {}
            jad = {}
            tob = {}
            venenatis = {}
            vetion = {}
            vorkath = {}
            wintertodt = {}
            zalcano = {}
            zulrah = {}

        class Clues:
            total = {}
            beginner = {}
            easy = {}
            medium = {}
            hard = {}
            elite = {}
            master = {}

        class Minigames:
            bh = {}
            rogue = {}
            lms = {}

    async def getUserData(self, username):
        url = f'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={username}'

        hsObject = self.HighscoresUser()

        def mapSkill(skill, data):
            skill['rank'] = data[0]
            skill['level'] = data[1]
            skill['experience'] = data[2]

        def mapCategory(category, data):

            if data[0] == '-1':
                category['rank'] = '-'
            else:
                category['rank'] = data[0]

            if data[1] == '-1':
                category['score'] = '-'
            else:
                category['score'] = data[1]

        try:
            response = requests.get(url)
            content = response.content.decode().split()
            skillsArray = [hsObject.Skills.total,
                           hsObject.Skills.attack,
                           hsObject.Skills.defence,
                           hsObject.Skills.strength,
                           hsObject.Skills.hitpoints,
                           hsObject.Skills.ranged,
                           hsObject.Skills.prayer,
                           hsObject.Skills.magic,
                           hsObject.Skills.cooking,
                           hsObject.Skills.woodcutting,
                           hsObject.Skills.fletching,
                           hsObject.Skills.fishing,
                           hsObject.Skills.firemaking,
                           hsObject.Skills.crafting,
                           hsObject.Skills.smithing,
                           hsObject.Skills.mining,
                           hsObject.Skills.herblore,
                           hsObject.Skills.agility,
                           hsObject.Skills.thieving,
                           hsObject.Skills.slayer,
                           hsObject.Skills.farming,
                           hsObject.Skills.runecraft,
                           hsObject.Skills.hunter,
                           hsObject.Skills.construction
                           ]

            cluesArray = [hsObject.Clues.total,
                          hsObject.Clues.beginner,
                          hsObject.Clues.easy,
                          hsObject.Clues.medium,
                          hsObject.Clues.hard,
                          hsObject.Clues.elite,
                          hsObject.Clues.master]

            minigameArray = [hsObject.Minigames.bh,
                             hsObject.Minigames.rogue, hsObject.Minigames.lms]

            bossArray = [
                hsObject.Bosses.sire,
                hsObject.Bosses.hydra,
                hsObject.Bosses.barrows,
                hsObject.Bosses.bryophyta,
                hsObject.Bosses.callisto,
                hsObject.Bosses.cerberus,
                hsObject.Bosses.cox,
                hsObject.Bosses.coxcm,
                hsObject.Bosses.chaosele,
                hsObject.Bosses.chaosfan,
                hsObject.Bosses.zilyana,
                hsObject.Bosses.corp,
                hsObject.Bosses.crazyArchaeologist,
                hsObject.Bosses.prime,
                hsObject.Bosses.rex,
                hsObject.Bosses.supreme,
                hsObject.Bosses.derangedArchaeologist,
                hsObject.Bosses.graardor,
                hsObject.Bosses.mole,
                hsObject.Bosses.grotesqueGuardians,
                hsObject.Bosses.hespori,
                hsObject.Bosses.kq,
                hsObject.Bosses.kbd,
                hsObject.Bosses.kraken,
                hsObject.Bosses.kreearra,
                hsObject.Bosses.kril,
                hsObject.Bosses.mimic,
                hsObject.Bosses.nightmare,
                hsObject.Bosses.obor,
                hsObject.Bosses.sarachnis,
                hsObject.Bosses.scorpia,
                hsObject.Bosses.skotizo,
                hsObject.Bosses.gauntlet,
                hsObject.Bosses.corrgauntlet,
                hsObject.Bosses.tob,
                hsObject.Bosses.thermonuclear,
                hsObject.Bosses.zuk,
                hsObject.Bosses.jad,
                hsObject.Bosses.venenatis,
                hsObject.Bosses.vetion,
                hsObject.Bosses.vorkath,
                hsObject.Bosses.wintertodt,
                hsObject.Bosses.zalcano,
                hsObject.Bosses.zulrah
            ]

            for n in range(0, 24):
                mapSkill(skillsArray[n], content[n].split(','))
            for n in range(0, 7):
                mapCategory(cluesArray[n], content[n + 27].split(','))
            for n in range(0, 3):
                mapCategory(minigameArray[n], content[n + 32].split(','))
            for n in range(0, 44):
                mapCategory(bossArray[n], content[n + 35].split(','))

        except:
            print(f"Err fetching item {username} from Database.")
            return None

        return hsObject

    @commands.command()
    async def lookup(self, ctx, user):

        placeholderEmbed = discord.Embed(title="Searching for player...", color=discord.Color.gold())
        placeholderEmbed.set_thumbnail(url='https://oldschool.runescape.wiki/images/8/8c/HiScores_icon.png?99743')
        message = await ctx.send(embed=placeholderEmbed)

        userData = await self.getUserData(user)
        

        embed = discord.Embed(title=f"**{user.capitalize()}**", description="Stats", color=discord.Color.gold())
        embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/8/8c/HiScores_icon.png?99743')

        skills_column_1 = f"""{ItemEmojis.Skills.attack}: {userData.Skills.attack['level']}
        {ItemEmojis.Skills.strength} {userData.Skills.strength['level']}
        {ItemEmojis.Skills.defence} {userData.Skills.defence['level']}
        {ItemEmojis.Skills.ranged} {userData.Skills.ranged['level']}
        {ItemEmojis.Skills.prayer} {userData.Skills.prayer['level']}
        {ItemEmojis.Skills.magic} {userData.Skills.magic['level']}s
        {ItemEmojis.Skills.runecraft} {userData.Skills.runecraft['level']}
        {ItemEmojis.Skills.construction} {userData.Skills.construction['level']}
        """

        skills_column_2 = f"""{ItemEmojis.Skills.hitpoints}: {userData.Skills.hitpoints['level']}
        {ItemEmojis.Skills.agility} {userData.Skills.agility['level']}
        {ItemEmojis.Skills.herblore} {userData.Skills.herblore['level']}
        {ItemEmojis.Skills.thieving} {userData.Skills.thieving['level']}
        {ItemEmojis.Skills.crafting} {userData.Skills.crafting['level']}
        {ItemEmojis.Skills.fletching} {userData.Skills.fletching['level']}
        {ItemEmojis.Skills.slayer} {userData.Skills.slayer['level']}
        {ItemEmojis.Skills.hunter} {userData.Skills.hunter['level']}
        """

        skills_column_3 = f"""{ItemEmojis.Skills.mining}: {userData.Skills.mining['level']}
        {ItemEmojis.Skills.smithing}: {userData.Skills.smithing['level']}
        {ItemEmojis.Skills.fishing}: {userData.Skills.fishing['level']}
        {ItemEmojis.Skills.cooking}: {userData.Skills.cooking['level']}
        {ItemEmojis.Skills.firemaking}: {userData.Skills.firemaking['level']}
        {ItemEmojis.Skills.woodcutting}: {userData.Skills.woodcutting['level']}
        {ItemEmojis.Skills.farming}: {userData.Skills.farming['level']}
        {ItemEmojis.Skills.total}: {userData.Skills.total['level']}
        """

        def calculateCombatLevel():
            combatsList = [int(userData.Skills.attack['level']),
                           int(userData.Skills.strength['level']),
                           int(userData.Skills.defence['level']),
                           int(userData.Skills.hitpoints['level']),
                           int(userData.Skills.ranged['level']),
                           int(userData.Skills.magic['level']),
                           int(userData.Skills.prayer['level'])]
            for value in combatsList:
                if value == -1:
                    value = 1
                else:
                    value = int(value)

            base = 0.25 * (combatsList[2] + combatsList[3] + math.floor(combatsList[6]/2))

            melee = 0.325 * (combatsList[0] + combatsList[1])

            ranged = 0.325 * (math.floor(3*combatsList[4]/2))

            mage = 0.325 * (math.floor(3*combatsList[5]/2))

            final = math.floor(base + max([melee, ranged, mage]))

            return final

        overall_column = f"""{ItemEmojis.Skills.total} Overall
        **Rank:** {userData.Skills.total['rank']}
        **Level:** {userData.Skills.total['level']}
        **XP:** {userData.Skills.total['experience']}
        **Combat:** {calculateCombatLevel()}
        """

        minigames_column = f"""{ItemEmojis.Misc.minigames} Minigames
        **BH:** {userData.Minigames.bh['score']}
        **BH Rogue:** {userData.Minigames.rogue['score']}
        **LMS:** {userData.Minigames.lms['score']}
        """

        clues_column = f"""{ItemEmojis.Misc.clue} Scores
        **Beginner:** {userData.Clues.beginner['score']}
        **Easy:** {userData.Clues.easy['score']}
        **Medium:** {userData.Clues.medium['score']}
        **Hard:** {userData.Clues.hard['score']}
        **Elite:** {userData.Clues.elite['score']}
        **Master:** {userData.Clues.master['score']}
        **Total:** {userData.Clues.total['score']}
        """

        embed.add_field(name='\u200b', value=skills_column_1, inline=True)
        embed.add_field(name='\u200b', value=skills_column_2, inline=True)
        embed.add_field(name='\u200b', value=skills_column_3, inline=True)
        embed.add_field(name='\u200b', value=overall_column, inline=True)
        embed.add_field(name='\u200b', value=minigames_column, inline=True)
        embed.add_field(name='\u200b', value=clues_column, inline=True)

        await message.edit(embed=embed)
        await message.add_reaction(ItemEmojis.Skills.total)
        await message.add_reaction(ItemEmojis.Misc.boss)

        # Boss KC Embed

        bossEmbed = discord.Embed(title=f"**{user.capitalize()}**", description="Boss KCs", color=discord.Color.gold())
        bossEmbed.set_thumbnail(url='https://oldschool.runescape.wiki/images/8/8c/HiScores_icon.png?99743')

        boss_column_1 = f"""{ItemEmojis.Bosses.abyssalSire} {userData.Bosses.sire['score']}
        {ItemEmojis.Bosses.alchemicalHydra} {userData.Bosses.hydra['score']}
        {ItemEmojis.Bosses.barrows} {userData.Bosses.barrows['score']}
        {ItemEmojis.Bosses.bryophyta} {userData.Bosses.bryophyta['score']}
        {ItemEmojis.Bosses.callisto} {userData.Bosses.callisto['score']}
        {ItemEmojis.Bosses.cerberus} {userData.Bosses.cerberus['score']}
        {ItemEmojis.Bosses.chambersOfXeric} {userData.Bosses.cox['score']}
        {ItemEmojis.Bosses.chambersOfXericChallengeMode} {userData.Bosses.coxcm['score']}
        {ItemEmojis.Bosses.chaosElemental} {userData.Bosses.chaosele['score']}
        {ItemEmojis.Bosses.chaosFanatic} {userData.Bosses.chaosfan['score']}
        {ItemEmojis.Bosses.commanderZilyana} {userData.Bosses.zilyana['score']}
        {ItemEmojis.Bosses.crazyArchaeologist} {userData.Bosses.crazyArchaeologist['score']}
        {ItemEmojis.Bosses.dagannothPrime} {userData.Bosses.prime['score']}
        {ItemEmojis.Bosses.dagannothRex} {userData.Bosses.rex['score']}
        {ItemEmojis.Bosses.dagannothSupreme} {userData.Bosses.supreme['score']}
        """

        boss_column_2 = f"""{ItemEmojis.Bosses.corporealBeast} {userData.Bosses.corp['score']}
        {ItemEmojis.Bosses.derangedArchaeologist} {userData.Bosses.derangedArchaeologist['score']}
        {ItemEmojis.Bosses.generalGraardor} {userData.Bosses.graardor['score']}
        {ItemEmojis.Bosses.giantMole} {userData.Bosses.mole['score']}
        {ItemEmojis.Bosses.grotesqueGuardians} {userData.Bosses.grotesqueGuardians['score']}
        {ItemEmojis.Bosses.hespori} {userData.Bosses.hespori['score']}
        {ItemEmojis.Bosses.kalphiteQueen} {userData.Bosses.kq['score']}
        {ItemEmojis.Bosses.kingBlackDragon} {userData.Bosses.kbd['score']}
        {ItemEmojis.Bosses.kraken} {userData.Bosses.kraken['score']}
        {ItemEmojis.Bosses.kreeArra} {userData.Bosses.kreearra['score']}
        {ItemEmojis.Bosses.krilTsutsaroth} {userData.Bosses.kril['score']}
        {ItemEmojis.Bosses.mimic} {userData.Bosses.mimic['score']}
        {ItemEmojis.Bosses.nightmare} {userData.Bosses.nightmare['score']}
        {ItemEmojis.Bosses.obor} {userData.Bosses.obor['score']}
        {ItemEmojis.Bosses.sarachnis} {userData.Bosses.sarachnis['score']}
        """

        boss_column_3 = f"""{ItemEmojis.Bosses.scorpia} {userData.Bosses.scorpia['score']}
        {ItemEmojis.Bosses.skotizo} {userData.Bosses.skotizo['score']}
        {ItemEmojis.Bosses.gauntlet} {userData.Bosses.gauntlet['score']}
        {ItemEmojis.Bosses.corruptedGauntlet} {userData.Bosses.corrgauntlet['score']}
        {ItemEmojis.Bosses.theaterOfBlood} {userData.Bosses.tob['score']}
        {ItemEmojis.Bosses.thermonuclearSmokeDevil} {userData.Bosses.thermonuclear['score']}
        {ItemEmojis.Bosses.inferno} {userData.Bosses.zuk['score']}
        {ItemEmojis.Bosses.fightCaves} {userData.Bosses.jad['score']}
        {ItemEmojis.Bosses.venenatis} {userData.Bosses.venenatis['score']}
        {ItemEmojis.Bosses.vetion} {userData.Bosses.vetion['score']}
        {ItemEmojis.Bosses.vorkath} {userData.Bosses.vorkath['score']}
        {ItemEmojis.Bosses.wintertodt} {userData.Bosses.wintertodt['score']}
        {ItemEmojis.Bosses.zalcano} {userData.Bosses.zalcano['score']}
        {ItemEmojis.Bosses.zulrah} {userData.Bosses.zulrah['score']}
        """

        bossEmbed.add_field(name='\u200b', value=boss_column_1, inline=True)
        bossEmbed.add_field(name='\u200b', value=boss_column_2, inline=True)
        bossEmbed.add_field(name='\u200b', value=boss_column_3, inline=True)

        async def waitForReaction():
            def bosscheck(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == f'{ItemEmojis.Misc.boss}' or str(reaction.emoji) == f'{ItemEmojis.Skills.total}')

            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=bosscheck, timeout=60.0)

                if str(reaction) == f'{ItemEmojis.Misc.boss}':
                    await message.remove_reaction(reaction, ctx.author)
                    await message.edit(embed=bossEmbed)
                elif str(reaction) == f'{ItemEmojis.Skills.total}':
                    await message.remove_reaction(reaction, ctx.author)
                    await message.edit(embed=embed)
                await waitForReaction()
            except asyncio.TimeoutError:
                await message.remove_reaction(ItemEmojis.Misc.boss, ctx.author)
                await message.clear_reaction(ItemEmojis.Misc.boss)
                await message.clear_reaction(ItemEmojis.Skills.total)

        await waitForReaction()


def setup(bot):
    bot.add_cog(Highscores(bot))
