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
import globals
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']

class PotentialItems(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.all_db_items = globals.all_db_items
        #Formatted {id: [name, price, stringprice, quantity]}
        self.lootArray = {995: [0, ItemEmojis.Coins.coins]}
        self.totalPrice = 0

    async def generateLoot(self, message):
        lastmsg = await message.send('*Checking the loot pile...*')
        loot = await PotentialItems(self.bot).rollLoot(message)

        sql = f"""
        UPDATE duel_users 
        SET gp = gp + {loot[995][1]} 
        WHERE user_id = {message.author.id}
        """
        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 3", error)
        finally:
            if conn is not None:
                conn.close()

            lootMessage = ""

            for item in loot.values():
                if item[0] != 'Coins':
                    
                    each = ''

                    if item[3] > 1 and type(item[2]) != int:
                        each = ' each' 

                    lootMessage += f"*{item[3]}x {item[4]} {item[0]} worth {item[2]} GP{each}* \n"
                    
            commaMoney = "{:,d}".format(loot[995][1])
            lootMessage += f"Total loot value: **{commaMoney} GP** {ItemEmojis.Coins.coins}"

            embed = discord.Embed(title=f"**{message.author.nick} received some loot from their kill:**", color=discord.Color.dark_teal())
            embed.add_field(name="Loot", value=lootMessage)
            await lastmsg.edit(embed=embed)


    #Returns dict of loot
    async def rollLoot(self, ctx):

        lootDict = self.rollForLoot(ctx)

        lootValueDict = {}

        for itemKey in lootDict.keys():
            url = f'http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={itemKey}'

            jsonResponse = None

            if itemKey != 995:
                response = requests.get(url)
                jsonResponse = response.json()
            elif itemKey == 995:
                jsonResponse = {'item':
                                    {'name': 'Coins',
                                    'current':
                                        {'price': 1}
                                    }
                                }

            #Get current price of item
            # Can beformatted as x,xxx,xxx or x.xxxM/K/B
            itemPrice = 0

            itemPrice = jsonResponse['item']['current']['price']

            # Remove commas

            value = 0

            # If the item is a string (not an int, basically) 
            if type(itemPrice) == str:

                if ',' in itemPrice:
                    itemPrice = itemPrice.replace(',', '')
                    value = int(itemPrice)
                else:
                    priceMultiplier = float(itemPrice[0: -1])
                    priceSuffix = itemPrice[-1]
                    
                    if priceSuffix == 'k':
                        value = math.floor(priceMultiplier * 1000)
                    elif priceSuffix == 'm':
                        value = math.floor(priceMultiplier * 1000000)
                    elif priceSuffix == 'b':
                        value = math.floor(priceMultiplier * 1000000000)


            if type(itemPrice) == int:
                value = int(itemPrice)

            print('LOOT VALUES:', lootDict[itemKey])
            # 0 is the name of the item, 1 is the GP (int) value of the item, 2 is the item price shortened, 3 is the number of the item, 4 is the emoji
            self.lootArray[itemKey] = [jsonResponse['item']['name'], value, itemPrice, lootDict[itemKey][0], lootDict[itemKey][1]]
        
        # Add the coin value of each item to the the total coins in the drop
        for item in self.lootArray.values():
            self.lootArray[995][1] = self.lootArray[995][1] + (item[1] * item[3])

        return self.lootArray

    def rollForLoot(self, ctx):
        def pickTable():
            # Pick a random number and assign it to the table
            rng = randint(0, 599)

            table = None

            # Roll for table
            if rng <= 5:
                table = self.superRareItems
            elif rng <= 35:
                table = self.rareItems
            elif rng <= 135:
                table = self.uncommonItems
            elif rng <= 599:
                table = self.commonItems

            # Roll for random value in table -- loot is a dictionary key
            loot = random.choice(list(table.keys()))

            # Roll for random loot quantity from min/max in value for key [loot]
            lootQuantity = randint(table[loot][1], table[loot][2])

            if self.lootArray.get(loot, None) != None:
                self.lootArray[loot][0] = self.lootArray[loot][0] + lootQuantity
            elif self.lootArray.get(loot, None) == None:
                self.lootArray[loot] = [lootQuantity, table[loot][3]] #Stores the quantity and emoji for the item

        # Roll between 3 and 6 drops
        # Gives an additional roll to people that are a member of the main discord guild
        bonusRolls = 0
        duelArenaGuild = self.bot.get_guild(663113372580970509)
        if duelArenaGuild.get_member(ctx.author.id) != None:
            bonusRolls = 1


        rollNum = randint(3, 6)

        for _ in range(0, rollNum):
            pickTable()

        if bonusRolls == 1:
            pickTable()
            
        return self.lootArray

    superRareItems = {
                   2577: ["Ranger boots", 1, 1, ItemEmojis.MediumClues.rangerBoots],
                   2581: ["Robin hood hat", 1, 1, ItemEmojis.HardClues.robinHoodHat],
                   19994: ["Ranger gloves", 1, 1, ItemEmojis.EliteClues.rangerGloves],
                   23249: ["Rangers' tights ", 1, 1, ItemEmojis.EliteClues.rangersTights],
                   12569: ["Ranger's tunic", 1, 1, ItemEmojis.EliteClues.rangersTunic],
                   6916: ["Infinity top", 1, 1, ItemEmojis.Infinity.infinityTop],
                   6924: ["Infinity bottoms", 1, 1, ItemEmojis.Infinity.infinityBottoms],
                   6922: ["Infinity boots", 1, 1, ItemEmojis.Infinity.infinityBoots],
                   6922: ["Infinity gloves", 1, 1, ItemEmojis.Infinity.infinityGloves],
                   6918: ["Infinity hat", 1, 1, ItemEmojis.Infinity.infinityHat],
                   11802: ["Armadyl godsword", 1, 1, ItemEmojis.Armadyl.armadylGodsword],
                   11806: ["Saradomin godsword", 1, 1, ItemEmojis.Saradomin.saradominGodsword],
                   11808: ["Zamorak godsword", 1, 1, ItemEmojis.Zamorak.zamorakGodsword],
                   11804: ["Bandos godsword", 1, 1, ItemEmojis.Bandos.bandosGodsword],
                   11826: ["Armadyl helmet", 1, 1, ItemEmojis.Armadyl.armadylHelm],
                   11828: ["Armadyl chestplate", 1, 1, ItemEmojis.Armadyl.armadylChestplate],
                   11830: ["Armadyl chainskirt", 1, 1, ItemEmojis.Armadyl.armadylChainskirt],
                   11832: ["Bandos chestplate", 1, 1, ItemEmojis.Bandos.bandosChestplate],
                   11834: ["Bandos tassets", 1, 1, ItemEmojis.Bandos.bandosTassets],
                   11836: ["Bandos boots", 1, 1, ItemEmojis.Bandos.bandosBoots],
                   11838: ["Saradomin sword", 1, 1, ItemEmojis.Saradomin.saradominSword],
                   11824: ["Zamorakian spear", 1, 1, ItemEmojis.Zamorak.zamorakianSpear],
                   12902: ["Toxic staff of the dead", 1, 1, ItemEmojis.Zamorak.toxicStaff],
                   13235: ["Eternal boots", 1, 1, ItemEmojis.CerberusItems.eternalBoots],
                   13237: ["Pegasian boots", 1, 1, ItemEmojis.CerberusItems.pegasianBoots],
                   13239: ["Primordial boots", 1, 1, ItemEmojis.CerberusItems.primordialBoots],
                   19544: ["Tormented bracelet", 1, 1, ItemEmojis.Jewelry.tormentedBracelet],
                   19547: ["Necklace of anguish", 1, 1, ItemEmojis.Jewelry.necklaceOfAnguish],
                   19550: ["Ring of suffering", 1, 1, ItemEmojis.Jewelry.ringOfSuffering],
                   19553: ["Amulet of torture", 1, 1, ItemEmojis.Jewelry.amuletOfTorture],
                   21018: ["Ancestral hat", 1, 1, ItemEmojis.RaidsItems.ancestralHat],
                   21021: ["Ancestral robe bottom", 1, 1, ItemEmojis.RaidsItems.ancestralRobeBottom],
                   21024: ["Ancestral rbe top", 1, 1, ItemEmojis.RaidsItems.ancestralRobeTop],
                   13652: ["Dragon claws", 1, 1, ItemEmojis.RaidsItems.dragonClaws],
                   21006: ["Kodai wand", 1, 1, ItemEmojis.RaidsItems.kodaiWand],
                   21003: ["Elder maul", 1, 1, ItemEmojis.RaidsItems.elderMaul]
                  }
    
    rareItems = {
                4151: ["Abyssal whip", 1, 1, ItemEmojis.SlayerItems.abyssalWhip],
                6585: ["Amulet of fury", 1, 1, ItemEmojis.Jewelry.amuletOfFury],
                6571: ["Uncut onyx", 1, 1, ItemEmojis.RawMaterials.uncutOnyx],
                11235: ["Dark bow", 1, 1, ItemEmojis.SlayerItems.darkBow],
                12929: ["Serpentine helm", 1, 1, ItemEmojis.ZulrahItems.serpentineHelm],
                995: ["Coins", 500000, 1000000, ItemEmojis.Coins.coins],
              }           
    
    uncommonItems = {
                    1187: ["Dragon sq shield", 1, 1, ItemEmojis.DragonItems.dragonSqShield],
                    4087: ["Dragon platelegs", 1, 1, ItemEmojis.DragonItems.dragonPlatelegs],
                    3140: ["Dragon chainbody", 1, 1, ItemEmojis.DragonItems.dragonChainbody],
                    4585: ["Dragon plateskirt", 1, 1, ItemEmojis.DragonItems.dragonPlateskirt],
                    11840: ["Dragon boots", 1, 1, ItemEmojis.DragonItems.dragonBoots],
                    4708: ["Ahrim's hood", 1, 1, ItemEmojis.Barrows.ahrimsHood],
                    4710: ["Ahrim's staff", 1, 1, ItemEmojis.Barrows.ahrimsStaff],
                    4712: ["Ahrim's robetop", 1, 1, ItemEmojis.Barrows.ahrimsRobetop],
                    4714: ["Ahrim' robeskirt", 1, 1, ItemEmojis.Barrows.ahrimsRobeskirt],
                    4716: ["Dharok's helm", 1, 1, ItemEmojis.Barrows.dharoksHelm],
                    4718: ["Dharok's greataxe", 1, 1, ItemEmojis.Barrows.dharoksGreataxe],
                    4720: ["Dharok's platelegs", 1, 1, ItemEmojis.Barrows.dharoksPlatelegs],
                    4722: ["Dharok's platebody", 1, 1, ItemEmojis.Barrows.dharoksPlatebody],
                    4724: ["Guthan's helm", 1, 1, ItemEmojis.Barrows.guthansHelm],
                    4726: ["Guthan's spear", 1, 1, ItemEmojis.Barrows.guthansWarpear],
                    4728: ["Guthan's platebody", 1, 1, ItemEmojis.Barrows.guthansPlatebody],
                    4730: ["Guthan's chainskirt", 1, 1, ItemEmojis.Barrows.guthansChainskirt],
                    4732: ["Karil's coif", 1, 1, ItemEmojis.Barrows.karilsCoif],
                    4734: ["Karil's crossbow", 1, 1, ItemEmojis.Barrows.karilsCrossbow],
                    4736: ["Karil's leathertop", 1, 1, ItemEmojis.Barrows.karilsLeathertop],
                    4738: ["Karil's leatherskirt", 1, 1, ItemEmojis.Barrows.karilsLeatherskirt],
                    4745: ["Torag's helm", 1, 1, ItemEmojis.Barrows.toragsHelm],
                    4747: ["Torag's hammers", 1, 1, ItemEmojis.Barrows.toragsHammers],
                    4749: ["Torag's platebody", 1, 1, ItemEmojis.Barrows.toragsPlatebody],
                    4751: ["Torag's platelegs", 1, 1, ItemEmojis.Barrows.toragsPlatelegs],
                    4753: ["Verac's helm", 1, 1, ItemEmojis.Barrows.veracsHelm],
                    4755: ["Verac's flail", 1, 1, ItemEmojis.Barrows.veracsFlail],
                    4757: ["Verac's brassard", 1, 1, ItemEmojis.Barrows.veracsBrassard],
                    4759: ["Verac's plateskirt", 1, 1, ItemEmojis.Barrows.veracsPlateskirt],
                    995: ["Coins", 250000, 499999, ItemEmojis.Coins.coins]
                    }

    commonItems = {
                385: ["Shark", 1, 16, ItemEmojis.Food.shark],
                391: ["Manta ray", 1, 16, ItemEmojis.Food.mantaRay],
                7946: ["Monkfish", 1, 16, ItemEmojis.Food.monkFish],
                13441: ["Anglerfish", 1, 16, ItemEmojis.Food.anglerFish],
                861: ["Magic shortbow", 1, 1, ItemEmojis.RangedWeapons.magicShortbow],
                1079: ["Rune platelegs", 1, 1, ItemEmojis.RuneItems.runePlatelegs],
                1093: ["Rune plateskirt", 1, 1, ItemEmojis.RuneItems.runePlateskirt],
                1163: ["Rune full helm", 1, 1, ItemEmojis.RuneItems.runeFullHelm],
                1333: ["Rune scimitar", 1, 1, ItemEmojis.RuneItems.runeScimitar],
                1127: ["Rune platebody", 1, 1, ItemEmojis.RuneItems.runePlatebody],
                1305: ["Dragon longsword", 1, 1, ItemEmojis.DragonItems.dragonLongsword],
                1377: ["Dragon battleaxe", 1, 1, ItemEmojis.DragonItems.dragonBattleaxe],
                5698: ["Dragon dagger(p++)", 1, 1, ItemEmojis.DragonItems.dragonDagger],
                1434: ["Dragon mace", 1, 1, ItemEmojis.DragonItems.dragonMace],
                4587: ["Dragon scimitar", 1, 1, ItemEmojis.DragonItems.dragonScimitar],
                4153: ["Granite maul", 1, 1, ItemEmojis.SlayerItems.graniteMaul],
                4089: ["Mystic hat", 1, 1, ItemEmojis.MysticArmor.mysticHat],
                4091: ["Mystic robe top", 1, 1, ItemEmojis.MysticArmor.mysticRobeTop],
                4093: ["Mystic robe bottom", 1, 1, ItemEmojis.MysticArmor.mysticRobeBottom],
                2503: ["Black d'hide body", 1, 1, ItemEmojis.DragonhideArmor.blackDhideBody],
                2497: ["Black d'hide chaps", 1, 1, ItemEmojis.DragonhideArmor.blackDhideChaps],
                2491: ["Black d'hide vamb", 1, 1, ItemEmojis.DragonhideArmor.blackDhideVamb],
                1712: ["Amulet of glory(4)", 1, 1, ItemEmojis.Jewelry.amuletOfGlory],
                2434: ["Prayer potion(4)", 2, 6, ItemEmojis.Potions.prayer],
                3024: ["Super restore(4)", 2, 6, ItemEmojis.Potions.superRestore],
                6685: ["Saradomin brew(4)", 2, 6, ItemEmojis.Potions.saradominBrew],
                2440: ["Super strength(4)", 1, 2, ItemEmojis.Potions.superStrength],
                2442: ["Super defence(4)", 1, 2, ItemEmojis.Potions.superDefence],
                2436: ["Super attack(4)", 1, 2, ItemEmojis.Potions.superAttack],
                12695: ["Super combat potion(4)", 1, 2, ItemEmojis.Potions.superCombat],
                2444: ["Ranging potion(4)", 1, 2, ItemEmojis.Potions.ranging],
                995: ["Coins", 30000, 249999, ItemEmojis.Coins.coins]
                }

    def randQuantity(min, max):
        return randint(min, max)

def setup(bot):
    bot.add_cog(PotentialItems(bot))
