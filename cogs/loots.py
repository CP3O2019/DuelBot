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

# Hosts the loot generator with all potential items on loot tables
class PotentialItems(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.all_db_items = items_api.load() #Load the RS ItemDB
        
        self.lootArray = {995: [0, ItemEmojis.Coins.coins]} # Default category is coins to prevent glitches
        self.totalPrice = 0 #K eeps track of price of loot

    # Generates loot and sends a message to the discord channel of the duel that details loot and value
    async def generateLoot(self, message):
        # Writes a placeholder message BEFORE making OSRS GE API calls.
        # This prevents other messages from coming between them, and looks cleaner
        lastmsg = await message.send('*Checking the loot pile...*') 


        # Generate the loot for whoever won the duel
        loot = await PotentialItems(self.bot).rollLoot()

        # Database calls to add the appropriate amount of GP from the loot rolls to the winning user's coffers
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

                # Bot sends a message to the channel that shows their loot.
                # The first and last lines are standard, with loot rolls in the middle for each item that was rolled.
                # Displays:
                    # item[0] = string item name 
                    # item[1] = the long int value of the item rolled
                    # item[2] = value of the item rolled
                    # item[3] = value of the item rolled
                    # item[4] = the discord emoji for the item
                lootMessage = f"__**{message.author.nick} received some loot from their kill:**__ \n"

                # Adds a message for each item in the loot dict
                for item in loot.values():
                    if item[0] != 'Coins':
                        
                        each = ''

                        # If the quantity if greater than one, add 'each' to the string
                        if item[3] > 1 and type(item[2]) != int:
                            each = ' each' 

                        # e.g. '2x <abyssalwhip:12345678> Abyssal whip worth 2.5m GP each'
                        lootMessage += f"*{item[3]}x {item[4]} {item[0]} worth {item[2]} GP{each}* \n"
                        
                # Adds commas to the integer value of the loot (e.g. 1234567 --> 1,234,567) 
                commaMoney = "{:,d}".format(loot[995][1])

                # Appends the message to send with the total GP won
                lootMessage += f"Total loot value: **{commaMoney} GP** {ItemEmojis.Coins.coins}"

                # Edits the placeholder 'Checking the loot pile...' message
                await lastmsg.edit(content=lootMessage)

    # Grabs prices of items and makes API calls to find the price, and convert them 
    # Returns: dictionary of loot to use for the message 
    async def rollLoot(self):

        # Creates a dictionary of loot 
        lootDict = self.rollForLoot()

        # For each item in the loot dictionary, make a call to the OSRS GE API to retrieve the object
        for itemKey in lootDict.keys():
            url = f'http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={itemKey}'

            # Hosts the json response of the API call
            # Pre-written to accept the coins API call for coins, which doesn't return anything
            jsonResponse = None

            # If the item rolled is not coins
            if itemKey != 995:
                response = requests.get(url)
                jsonResponse = response.json() # Parse

            # If the item rolled is coins, use this default object with the necessary parameters to continue that matches the API structure
            elif itemKey == 995:
                jsonResponse = {'item':
                                    {'name': 'Coins',
                                    'current':
                                        {'price': 1}
                                    }
                                }

            # Get current price of item
            # Can beformatted as x,xxx,xxx or x.xxxM/K/B
            # Defaults to 0 
            itemPrice = 0
            itemPrice = jsonResponse['item']['current']['price']

            value = 0

            # If the item is a string (not an int, basically), do some finagling to convert it to an int and set the value as the int
            if type(itemPrice) == str:

                # Remove commas, if there are any
                if ',' in itemPrice:
                    itemPrice = itemPrice.replace(',', '')
                    value = int(itemPrice)
                else:
                    # Convert the item to a float (minus the last character, which should be K/M/B)
                    priceMultiplier = float(itemPrice[0: -1])

                    # The last character, which should be K/M/B
                    priceSuffix = itemPrice[-1]
                    
                    if priceSuffix == 'k': # Thousands 
                        value = math.floor(priceMultiplier * 1000)
                    elif priceSuffix == 'm': # Millions
                        value = math.floor(priceMultiplier * 1000000)
                    elif priceSuffix == 'b': # Billions
                        value = math.floor(priceMultiplier * 1000000000)

            # If the itemPrice is an int, set the value to the int
            if type(itemPrice) == int:
                value = int(itemPrice)

            # Prints the loot to the console
            # Really useful for debugging if an item crashes the loot system, since it tends to be the last item used for an GE API call
            print('LOOT VALUES:', lootDict[itemKey])

            # 0 is the name of the item, 1 is the integer value of the item, 2 is the item price shortened, 3 is the number of the item, 4 is the emoji
            self.lootArray[itemKey] = [jsonResponse['item']['name'], value, itemPrice, lootDict[itemKey][0], lootDict[itemKey][1]]
        
        # Add the coin value of each item to the the total coins in the drop
        for item in self.lootArray.values():
            self.lootArray[995][1] = self.lootArray[995][1] + item[1]

        # Returns the loot array
        return self.lootArray

    # Internal function for rolling for loot (should probavly nest within rollLoot() but whatever, fuck it)
    def rollForLoot(self):

        # Nested function used for randomly selecting a loot table based on RNG, then selecting a loot from that table.
            # Common table 86.66%
            # Uncommon table - 10.00%
            # Rare table - 2.66%
            # Superrare table - 0.66%
        def pickTable():

            # Pick a random number and assign it to the table
            rng = randint(0, 599)

            table = None

            # Roll for table
            if rng <= 3:
                table = self.superRareItems
            elif rng <= 20:
                table = self.rareItems
            elif rng <= 80:
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
        # TO-DO: add additional rolls for being in the duel arena server
        rollNum = randint(3, 6)

        # Picks a table, 
        for _ in range(0, rollNum):
            pickTable()
            
        return self.lootArray

    # Dictionary loot tables
    # Structured as {itemID: minPossible, maxPossible, CustomEmoji}
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
                   11808: ["Zamorak godsword", 1, 1, ItemEmojis.Zamorak.zamorakGodword],
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
                }

def setup(bot):
    bot.add_cog(PotentialItems(bot))
