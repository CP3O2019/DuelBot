
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
# import globals
from discord.ext import commands

# DATABASE_URL = os.environ['DATABASE_URL']

class PotentialItems(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.all_db_items = items_api.load()
        
        #Formatted {id: [name, price, stringprice, quantity]}
        self.lootArray = {995: 0}
        self.totalPrice = 0

    async def rollLoot(self):

        lootDict = self.rollForLoot()

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

            # 0 is the name of the item, 1 is the integer value of the item, 2 is the item price shortened, 3 is the number of the item
            self.lootArray[itemKey] = [jsonResponse['item']['name'], value, itemPrice, lootDict[itemKey]]
        
        # Add the coin value of each item to the the total coins in the drop
        for item in self.lootArray.values():
            self.lootArray[995][1] = self.lootArray[995][1] + item[1]

        return self.lootArray

    def rollForLoot(self):
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
                self.lootArray[loot] = self.lootArray[loot] + lootQuantity
            elif self.lootArray.get(loot, None) == None:
                self.lootArray[loot] = lootQuantity

        # Roll between 3 and 6 drops
        rollNum = randint(3, 6)

        for _ in range(0, rollNum):
            pickTable()
            
        return self.lootArray

    superRareItems = {
                   2577: ["Ranger boots", 1, 1],
                   2581: ["Robin hood hat", 1, 1],
                   19994: ["Ranger gloves", 1, 1],
                   23249: ["Rangers' tights ", 1, 1],
                   12569: ["Ranger's tunic", 1, 1],
                   6916: ["Infinity top", 1, 1],
                   6924: ["Infinity bottoms", 1, 1],
                   6922: ["Infinity boots", 1, 1],
                   6922: ["Infinity gloves", 1, 1],
                   6918: ["Infinity hat", 1, 1],
                   11802: ["Armadyl godsword", 1, 1],
                   11806: ["Saradomin godsword", 1, 1],
                   11808: ["Zamorak godsword", 1, 1],
                   11804: ["Bandos godsword", 1, 1],
                   11826: ["Armadyl helmet", 1, 1],
                   11828: ["Armadyl chestplate", 1, 1],
                   11830: ["Armadyl chainskirt", 1, 1],
                   11832: ["Bandos chestplate", 1, 1],
                   11834: ["Bandos tassets", 1, 1],
                   11836: ["Bandos boots", 1, 1],
                   11838: ["Saradomin sword", 1, 1],
                   11824: ["Zamorakian spear", 1, 1],
                   12902: ["Toxic staff of the dead", 1, 1],
                   13235: ["Eternal boots", 1, 1],
                   13237: ["Pegasian boots", 1, 1],
                   13239: ["Primordial boots", 1, 1],
                   19544: ["Tormented bracelet", 1, 1],
                   19547: ["Necklace of anguish", 1, 1],
                   19550: ["Ring of suffering", 1, 1],
                   19553: ["Amulet of torture", 1, 1],
                   21018: ["Ancestral hat", 1, 1],
                   21021: ["Ancestral robe bottom", 1, 1],
                   21024: ["Ancestral rbe top", 1, 1],
                   13652: ["Dragon claws", 1, 1],
                   21006: ["Kodai wand", 1, 1],
                   21003: ["Elder maul", 1, 1]
                  }
    
    rareItems = {
                4151: ["Abyssal whip", 1, 1],
                6585: ["Amulet of fury", 1, 1],
                6571: ["Uncut onyx", 1, 1],
                11235: ["Dark bow", 1, 1],
                12929: ["Serpentine helm", 1, 1],
                995: ["Coins", 500000, 1000000],
              }           
    
    uncommonItems = {
                    1187: ["Dragon sq shield", 1, 1],
                    4087: ["Dragon platelegs", 1, 1],
                    3140: ["Dragon chainbody", 1, 1],
                    4585: ["Dragon plateskirt", 1, 1],
                    11840: ["Dragon boots", 1, 1],
                    4708: ["Ahrim's hood", 1, 1],
                    4710: ["Ahrim's staff", 1, 1],
                    4712: ["Ahrim's robetop", 1, 1],
                    4714: ["Ahrim' robeskirt", 1, 1],
                    4716: ["Dharok's helm", 1, 1],
                    4718: ["Dharok's greataxe", 1, 1],
                    4720: ["Dharok's platelegs", 1, 1],
                    4722: ["Dharok's platebody", 1, 1],
                    4724: ["Guthan's helm", 1, 1],
                    4726: ["Guthan's spear", 1, 1],
                    4728: ["Guthan's platebody", 1, 1],
                    4730: ["Guthan's chainskirt", 1, 1],
                    4732: ["Karil's coif", 1, 1],
                    4734: ["Karil's crossbow", 1, 1],
                    4736: ["Karil's leathertop", 1, 1],
                    4738: ["Karil's leatherskirt", 1, 1],
                    4745: ["Torag's helm", 1, 1],
                    4747: ["Torag's hammers", 1, 1],
                    4749: ["Torag's platebody", 1, 1],
                    4751: ["Torag's platelegs", 1, 1],
                    4753: ["Verac's helm", 1, 1],
                    4755: ["Verac's flail", 1, 1],
                    4757: ["Verac's brassard", 1, 1],
                    995: ["Coins", 250000, 499999]
                    }

    commonItems = {
                385: ["Shark", 1, 16],
                391: ["Manta ray", 1, 16],
                7946: ["Monkfish", 1, 16],
                13441: ["Anglerfish", 1, 16],
                861: ["Magic shortbow", 1, 1],
                1079: ["Rune platelegs", 1, 1],
                1093: ["Rune plateskirt", 1, 1],
                1163: ["Rune full helm", 1, 1],
                1333: ["Rune scimitar", 1, 1],
                1127: ["Rune platebody", 1, 1],
                1305: ["Dragon longsword", 1, 1],
                1377: ["Dragon battleaxe", 1, 1],
                5698: ["Dragon dagger(p++)", 1, 1],
                1434: ["Dragon mace", 1, 1],
                4587: ["Dragon scimitar", 1, 1],
                4153: ["Granite maul", 1, 1],
                4089: ["Mystic hat", 1, 1],
                4091: ["Mystic robe top", 1, 1],
                4093: ["Mystic robe bottom", 1, 1],
                2503: ["Black d'hide body", 1, 1],
                2497: ["Black d'hide chaps", 1, 1],
                2491: ["Black d'hide vamb", 1, 1],
                1712: ["Amulet of glory(4)", 1, 1],
                2434: ["Prayer potion(4)", 2, 6],
                3024: ["Super restore(4)", 2, 6],
                6685: ["Saradomin brew(4)", 2, 6],
                2440: ["Super strength(4)", 1, 2],
                2442: ["Super defence(4)", 1, 2],
                2436: ["Super attack(4)", 1, 2],
                12695: ["Super combat potion(4)", 1, 2],
                2444: ["Ranging potion(4)", 1, 2],
                995: ["Coins", 30000, 249999]
                }

    def randQuantity(min, max):
        return randint(min, max)

def setup(bot):
    bot.add_cog(PotentialItems(bot))
