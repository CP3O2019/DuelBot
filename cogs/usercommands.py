import asyncio
import os
import discord
import psycopg2
import uuid
import random
import math
from random import randint
from cogs.osrsEmojis import ItemEmojis
from cogs.loots import PotentialItems
import globals
from globals import Duel, DuelUser
from cogs.mathHelpers import RSMathHelpers
from cogs.economy import Economy
from discord.ext import commands
from bot import duels, lastMessages

DATABASE_URL = os.environ['DATABASE_URL']

class UserCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready')

    @commands.command() 
    async def invite(self, ctx):
        await ctx.send("""
        Click the link below to add the DuelBot to your server! \n
        https://discordapp.com/api/oauth2/authorize?client_id=684592148284571670&permissions=388160&scope=bot
        """)

    @commands.command() 
    async def server(self, ctx):
        await ctx.send("""
        **Click the link below to joib our server and get an extra loot roll every kill!**
        https://discord.gg/qQPFt3
        """)

    async def createTablesForUser(self, user):

        global DATABASE_URL

        cmds = (
        f"""
        INSERT INTO duel_rares (
            user_id,
            _1038,
            _1040,
            _1042,
            _1044,
            _1046,
            _1048,
            _962,
            _1057,
            _1055,
            _1053,
            _1050,
            _1959,
            _1961) 
        VALUES 
        ({user.id}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ON CONFLICT (user_id) DO NOTHING
        """,
        f"""
        INSERT INTO duel_users (user_id, nick, wins, losses, gp) 
        VALUES 
        ({user.id}, '{user.nick}', 0, 0, 0)
        ON CONFLICT (user_id) DO NOTHING
        """
        )

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            for command in cmds:
                cur.execute(command)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("TABLE CREATION ERROR", error)
        finally:
            if conn is not None:
                conn.close()

    # begin a duel command
    @commands.command()
    async def fight(self, message, *args):

        await self.createDuel(message, args)

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            return

    @commands.command(name='commands')
    async def cmds(self, message):
        embed = discord.Embed(title="Duel bot commands", color = discord.Color.orange())
        embed.add_field(name="Server commands", value="**.server**: Links to our server. Members get +1 loot roll for pking and fighting!\n"
        "**.invite**: Gives an invite link to add the DuelBot to your server.", inline=False)
        embed.add_field(name="General commands", value="**.fight**: Begins a duel \n"
        "**.kd**: View your kill/death ratio \n"
        "**.rares**: See all of the rares you've won \n"
        "**.gp**: See how much GP you have", inline = False)
        embed.add_field(name="Fighting commands", value="**.dds**: Hits twice, max of **18** each hit, uses 25% special, 25% chance to poison \n"
        "**.whip**: Hits once, max of **27** \n"
        "**.ags**: Hits once, max of **46**, uses 50% of special \n"
        "**.sgs**: Hits once, max of **39**, uses 50% of special, heals for 50% of damage \n"
        "**.zgs**: Hits once, max of **36**, uses 50% of special, has a 25% chance to freeze enemy \n"
        "**.dclaws**: Hits four times, max of **21** on any hit, each consecutive hit does 50% damage \n"
        "**.dwh**: Hits once, max of **39**, uses 50% special \n"
        "**.ss**: Hits twice, max of **27** each hit, uses 100% special \n"
        "**.gmaul**: Hits three times, max of **24** each hit, uses 100% special \n"
        "**.bp**: Hits once, max of **27**, uses 50% special, heals for 50% of damage, 25% chance to poison \n"
        "**.ice**: Hits once, max of **30**, has a 12.5% chance to freeze enemy\n"
        "**.blood**: Hits once, max of **28**, heals for 25% of damage \n"
        "**.smoke**: Hits once, max of **27**, 25% chance to poison"
        , inline=False)
        await message.send(embed=embed)

    @commands.command()
    async def rares(self, message):

        await self.createTablesForUser(message.author)

        cmds = f"""
        SELECT 
            _1038 red_partyhat,
            _1040 yellow_partyhat,
            _1042 blue_partyhat,
            _1044 green_partyhat,
            _1046 purple_partyhat,
            _1048 white_partyhat,
            _962 christmas_cracker,
            _1057 red_hween_mask,
            _1055 blue_hween_mask,
            _1053 green_hween_mask,
            _1050 santa_hat,
            _1959 pumpkin,
            _1961 easter_egg

        FROM duel_rares
        WHERE user_id = {message.author.id}"""

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(cmds)

            rows = cur.fetchall()

            for row in rows:
                embed = discord.Embed(title=f"{message.author.nick}'s rares", color = discord.Color.blurple())
                embed.add_field(name=f"**Red partyhat** {ItemEmojis.Rares.redPartyhat}", value=row[0])
                embed.add_field(name=f"**Yellow partyhat** {ItemEmojis.Rares.yellowPartyhat}", value=row[1])
                embed.add_field(name=f"**Blue partyhat** {ItemEmojis.Rares.bluePartyhat}", value=row[2])
                embed.add_field(name=f"**Green partyhat** {ItemEmojis.Rares.greenPartyhat}", value=row[3])
                embed.add_field(name=f"**Purple partyhat** {ItemEmojis.Rares.purplePartyhat}", value=row[4])
                embed.add_field(name=f"**White partyhat** {ItemEmojis.Rares.whitePartyhat}", value=row[5])
                embed.add_field(name=f"**Christmas cracker** {ItemEmojis.Rares.christmasCracker}", value=row[6])
                embed.add_field(name=f"**Red h'ween mask** {ItemEmojis.Rares.redHween}", value=row[7])
                embed.add_field(name=f"**Blue h'ween mask** {ItemEmojis.Rares.blueHween}", value=row[8])
                embed.add_field(name=f"**Green h'ween mask** {ItemEmojis.Rares.greenHween}", value=row[9])
                embed.add_field(name=f"**Santa hat** {ItemEmojis.Rares.santaHat}", value=row[10])
                embed.add_field(name=f"**Pumpkin** {ItemEmojis.Rares.pumpkin}", value=row[11])
                embed.add_field(name=f"**Easter egg** {ItemEmojis.Rares.easterEgg}", value=row[12])

                await message.send(embed=embed)

            cur.close()
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print("RARES ERROR", error)
        finally:
            if conn is not None:
                conn.close()

    @commands.command()
    async def kd(self, message):
        await self.createTablesForUser(message.author)

        sql = f"""
        SELECT
        nick nick,
        wins wins,
        losses losses

        FROM duel_users
        WHERE user_id = {message.author.id}"""

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()

            cur.execute(sql)

            rows = cur.fetchall()

            for row in rows:

                embed = discord.Embed(title=f"K/D for {message.author.nick}", color = discord.Color.green())
                embed.add_field(name="**Wins**", value=row[1])
                embed.add_field(name="**Losses**", value=row[2])
                embed.add_field(name="**KDA**", value=round((row[1]/row[2]), 2))

                await message.send(embed=embed)

            cur.close()
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print("KD ERROR", error)
            return
        finally:
            if conn is not None:
                conn.close()

    @commands.command()
    async def gp(self, message):
        await self.createTablesForUser(message.author)

        sql = f"""
        SELECT
        gp gp
        FROM duel_users
        WHERE user_id = {message.author.id}
        """

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

            for row in rows:
                commaMoney = "{:,d}".format(row[0])
                await message.send(f'{ItemEmojis.Coins.coins} You have {commaMoney} GP {ItemEmojis.Coins.coins}')

            cur.close()
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print("GP ERROR", error)
            return
        finally:
            if conn is not None:
                conn.close()

    @commands.command()
    async def dice(self, message, *args):
        diceAmount = 0
        helper = RSMathHelpers(self.bot)
        winStatus = ""
        try:
            helper = RSMathHelpers(self.bot)
            diceAmount = helper.numify(args[0])

            if diceAmount <= 0:
                await message.send("You can't dice less than 1 GP.")
                return
            elif diceAmount > 2000000000:
                await message.send("You can only dice up to 2B at once.")
                return

            diceAmountString = helper.shortNumify(diceAmount, 1)

            hasMoney = await helper.removeGPFromUser(message, message.author.id, diceAmount)

            if hasMoney == False:
                return

            rand = randint(1, 100)
            diceDescription = ''

            if rand >= 55:
                await helper.giveGPToUser(message, message.author.id, diceAmount * 2)
                diceDescription = f'You rolled a **{rand}** and won {diceAmountString} GP'
                winStatus = "won"
            else:
                diceDescription = f'You rolled a **{rand}** and lost {diceAmountString} GP.'
                winStatus = "lost"

            embed = discord.Embed(title='**Dice Roll**', description=diceDescription, color = discord.Color.orange())
            embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/runescape2/images/f/f2/Dice_bag_detail.png/revision/latest?cb=20111120013858')
            await message.send(embed=embed)
        except:
            await message.send('You must dice a valid amount.')

        # If over 100M is diced, send it to the global notifications channel
        if diceAmount >= 500000000:
                notifChannel = self.bot.get_channel(689313376286802026)
                await notifChannel.send(f"{ItemEmojis.Coins.coins} {message.author.nick} has just diced **{helper.shortNumify(diceAmount, 1)}** and **{winStatus}**.")

    async def createDuel(self, message, *args):

        async def convertArgsToItemString(args):

            itemName = ""
            itemQuantity = 0
            try:
                try:
                    # Test if the argument is an integer
                    itemQuantity = int(args[0])
                except:
                    # Test if the argument is a string
                    try:
                        placeholderQuantity = int(RSMathHelpers.numify(self, args[0]))
                        if type(placeholderQuantity) == int:
                            itemQuantity = placeholderQuantity
                    except:
                        itemQuantity = None
                #If the first argument is an integer, 
                if type(itemQuantity) != int:
                    await message.send('Please enter a valid quantity.')
                    return None            
            except:
                await message.send('Please enter a quantity to stake.')
                return None

            if len(args) == 1:  # If the user didn't include an item to purchase, but did include a quantity (is staking GP)
                itemName = "GP"
            elif len(args) == 2:  # If the args was two values long, including an integer 
                itemName = args[1]
            else:  # If the args was more than two words long, concatenate
                for n in range(1, len(args)):
                    itemName += args[n]

            # Cast the itemName to its lowercase version
            itemName = itemName.lower()
            # Return [name of item, quantity to stake]
            return [itemName, itemQuantity]

        def get_key(val, itemDict):
            for key, value in itemDict.items():
                if val == value:
                    return key
            return None

        async def getStakeType():
            stakeType = ""
            arguments = args[0]
            itemLongName = ""
            itemId = None

            if len(arguments) == 0:
                return None
            # If there is only one argument
            if len(arguments) == 1:
                # Try to convert the argument into a number, because the stake should be GP
                value = RSMathHelpers.numify(self, arguments[0])
                try:
                    # If the number did not successfully convert to a number, this will throw an exception when int(value) is called
                    # If it is successful, it will return "gp" to indicate a monetary stake
                    intValue = int(value)
                    stakeType = "gp"
                    return [stakeType, arguments[0]]
                except:
                    return None
            
            # If there are two arguments (could be "[quantity] [text]" or "[text] [text]")
            if len(arguments) == 2 or len(arguments) == 3:
                try:
                    # Try to convert the arguments into a a [name, quantity] array
                    # This will fail if the 
                    stakeVals = await convertArgsToItemString(arguments)
                    if stakeVals == None:
                        return

                    # Check to see if the name of the item is in either of the item dictionaries
                    if stakeVals[0] in Economy(self.bot).rareIDs.keys():
                        stakeType = "rares"
                        itemLongName = Economy(self.bot).rareIDs[stakeVals[0]][2]
                        itemId = Economy(self.bot).rareIDs[stakeVals[0]][0]
                        return [stakeType, itemLongName, itemId]
                    elif stakeVals[0] in Economy(self.bot).itemList.values():
                        stakeType = "items"
                        itemId = get_key(stakeVals[0], Economy(self.bot).itemList)
                        itemLongName = Economy(self.bot).getItemName(itemId)
                        return [stakeType, itemLongName, itemId]
                    else:
                        await message.send("Couldn't find that item, please try again.")
                        return
                except:
                    await message.send("Couldn't find that item, please try again.")
                    return
            else:
                await message.send("Something went wrong.")
                return None

        # Returns [stake type, full name, itemId]
            # Stake type can be 'items', 'rares', or 'gp'
            # i.e. ['rares', 'Christmas cracker', 962]
        stakeType = await getStakeType()

        # Get the item quantity and itemName for the stake
        # Returned as [itemName, itemQuantity]
        # i.e. ['christmasCracker', 1]
        stakeParams = None
        if stakeType == None:
            #If the duel is just a regular old duel
            stakeParams = [None, None]
        else:
            stakeParams = await convertArgsToItemString(args[0])

        # Get the global duel
        channelDuel = globals.duels.get(message.channel.id, None)

        # Determine if the user has enough of the item
        async def checkUsersItemQuantity(user):

            if channelDuel != None and stakeParams[1] == None:
                if channelDuel.stakeItem == 'gp':
                    await message.send(f"You don't have {channelDuel.shortQuantity} GP to stake.")
                else:
                    if len(args[0]) == 0:
                        return True
                    else:
                        if stakeParams[0] != channelDuel.itemLongName.replace(' ', '').lower():
                            await message.send(f'Please type **.fight {channelDuel.shortQuantity} {channelDuel.itemLongName}** to enter this duel.')
                        elif stakeParams[0] == channelDuel.itemLongName.replace(' ', '').lower():
                            await message.send(f"You don't have {channelDuel.shortQuantity} {channelDuel.itemLongName} to stake.")
                return False

            # Sort out values
            _itemType = stakeType[0]
            _fullItemName = stakeType[1]
            _itemId = None
            _shortItemName = stakeParams[0]
            _itemQuantity = stakeParams[1]
            _table = None

            if _itemType == 'gp':
                _table = 'duel_users'
                _itemId = 'gp'
            elif _itemType == 'rares':
                _table = 'duel_rares'
                _itemId = f"_{stakeType[2]}"
            elif _itemType == 'items':
                _table = 'pking_items'
                _itemId = f"_{stakeType[2]}"

            _userQuantity = await Economy(self.bot).getNumberOfItem(user.id, _table, f"{_itemId}")

            if _userQuantity < _itemQuantity:
                if _itemType == 'gp':
                    if message.author.id == user.id:
                        await message.send(f"You don't have {_shortItemName} to stake.")
                    else:
                        await message.send(f"{user.nick} does not {_shortItemName} to stake.")
                else:
                    shortQuantity = RSMathHelpers(self.bot).shortNumify(_itemQuantity, 1)

                    if message.author.id == user.id:
                        await message.send(f"You don't have {shortQuantity} {_fullItemName} to stake.")
                    else:
                        await message.send(f"{user.nick} does not have {shortQuantity} {_fullItemName} to stake")
                return False
            elif _userQuantity >= _itemQuantity:
                return True



        if len(args[0]) != 0:
            user1HasItem = await checkUsersItemQuantity(message.author)

            if user1HasItem == False:
                return

        # Returns an array that details 
        # where the user should have their info pulled to/written to
        # i.e. ['gp', 'duel_users'] or ['_1040', 'duel_rares']
        def returnTableColumn():
            # Sort out values
            _itemType = None
            if stakeType != None:
                _itemType = stakeType[0]
            _itemId = None
            _table = None

            if _itemType == 'gp':
                _table = 'duel_users'
                _itemId = 'gp'
            elif _itemType == 'rares':
                _table = 'duel_rares'
                _itemId = f"_{stakeType[2]}"
            elif _itemType == 'items':
                _table = 'pking_items'
                _itemId = f"_{stakeType[2]}"


            return [_itemId, _table]

        if channelDuel != None:
            if len(args[0]) > 0:
                if str(args[0][0]).lower() != str(channelDuel.shortQuantity).lower() and channelDuel.stakeItem == 'gp':
                    await message.send(f'Please type **.fight {channelDuel.shortQuantity}** to enter this duel.')
                    return
                elif str(args[0][0]).lower() != str(channelDuel.shortQuantity).lower() and channelDuel.stakeItem != 'gp' and stakeParams[0] != channelDuel.itemLongName.replace(' ', '').lower():
                    await message.send(f'Please type **.fight {channelDuel.shortQuantity} {channelDuel.itemLongName}** to enter this duel.')
                    return
                else:
                    pass

            if channelDuel.stakeItem != None:
                userHasQuantity = await checkUsersItemQuantity(message.author)

                if userHasQuantity == False:
                    return

        # Check to see if a duel exists in the channel
        if channelDuel == None:
            if len(args[0]) == 0:
                # If the duel is not for any particular amount of money
                globals.duels[message.channel.id] = globals.Duel(globals.DuelUser(message.author), uuid.uuid4(), message.channel.id, None, None, None, None, None)
                channelDuel = globals.duels.get(message.channel.id, None)
                globals.lastMessages[message.channel.id] = await message.send(f"{message.author.nick} has started a duel. Type **.fight** to duel them.")
                await self.startCancelCountdown(message, channelDuel.uuid)
                return
            elif args != None:
                # If the stake has a value attached to it
                table = returnTableColumn()

                if stakeParams[1] < 0:
                    await message.send("You cannot stake less than 1 of an item.")
                    return

                globals.duels[message.channel.id] = globals.Duel(globals.DuelUser(message.author), uuid.uuid4(), message.channel.id, table[0], stakeParams[1], table[1], stakeType[1], RSMathHelpers(self.bot).shortNumify(stakeParams[1], 1))  
                channelDuel = globals.duels.get(message.channel.id, None)
                if stakeType[0] == 'gp':
                    globals.lastMessages[message.channel.id] = await message.send(f"**{message.author.nick}** has started a duel for **{args[0][0]} GP**. Type **.fight {args[0][0]}** to duel them.")
                else:
                    globals.lastMessages[message.channel.id] = await message.send(f"**{message.author.nick}** has started a duel for **{args[0][0]} {stakeType[1]}**. Type **.fight {RSMathHelpers(self.bot).shortNumify(stakeParams[1], 1)} {stakeType[1]}** to duel them.")

                await self.startCancelCountdown(message, channelDuel.uuid)
                return
        else:
            if channelDuel.stakeItem != None:
                userHasQuantity = await checkUsersItemQuantity(message.author)

                if userHasQuantity == False:
                    return

        # Check to see if the person is dueling themselves
        if self.check(message.author, message.channel.id) == False:
            await message.send("You cannot duel yourself.")
            return

        # Check to see if a duel already exists between two people
        if channelDuel.user_1 != None and channelDuel.user_2 != None:
            await message.send("There are already two people dueling.")
            return

        # Check to see if player 2 has the required items to participate in the stake
        player2HasQuantity = await checkUsersItemQuantity(message.author)
        if player2HasQuantity == False:
            return

        # # If it passed the other checks, add duel user 2 to the fight
        # channelDuel.user_2 = globals.DuelUser(message.author)

        if channelDuel.stakeItem != None and channelDuel.stakeQuantity != None:
            tableValues = returnTableColumn()

            if len(args[0]) == 0:
                await message.send(f'Please type **.fight {channelDuel.shortQuantity} {channelDuel.itemLongName}** to enter this duel.')
                return
            if stakeType[1].replace(' ', '').lower() == channelDuel.itemLongName.replace(' ', '').lower():
                player1HasQuantityStill = await checkUsersItemQuantity(channelDuel.user_1.user)
                if player1HasQuantityStill == False:
                    await message.send(f"Cancelling the duel because {channelDuel.user_1.user.nick} no longer has {RSMathHelpers(self.bot).shortNumify(stakeParams[1], 1)} {stakeType[1]}.")
                    del globals.duels[message.channel.id]
                    return
            elif stakeType[1].replace(' ', '').lower() != channelDuel.itemLongName.replace(' ', '').lower():
                await message.send(f"The current duel is not for {stakeType[1]}.")
                return

             # If it passed the other checks, add duel user 2 to the fight
            channelDuel.user_2 = globals.DuelUser(message.author)

            await Economy(self.bot).removeItemFromUser(channelDuel.user_1.user.id, channelDuel.table, channelDuel.stakeItem, channelDuel.stakeQuantity)
            await Economy(self.bot).removeItemFromUser(channelDuel.user_2.user.id, channelDuel.table, channelDuel.stakeItem, channelDuel.stakeQuantity)
        elif channelDuel.stakeItem == None:
            channelDuel.user_2 = globals.DuelUser(message.author)

        # Randomly pick a starting user
        startingUserBool = bool(random.getrandbits(1))
        startingUser = None
        if startingUserBool == True:
            startingUser = channelDuel.user_1
            channelDuel.turn = channelDuel.user_1
        else:
            startingUser = channelDuel.user_2
            channelDuel.turn = channelDuel.user_2

        try:
            del globals.lastMessages[message.channel.id]
        except:
            pass

        await message.send(f"Beginning duel between {channelDuel.user_1.user.nick} and {channelDuel.user_2.user.nick} \n**{startingUser.user.nick}** goes first.")

        if channelDuel.user_1 != None and channelDuel.user_2 != None:
            await self.beginFightTurnChecker(message, channelDuel)

    async def beginFightTurnChecker(self, message, duel):

        channelDuel = globals.duels.get(message.channel.id, None)

        # switches who's turn it is
        savedTurn = channelDuel.turn

        attackTypes = [".dds",
                       ".ags",
                       ".sgs",
                       ".claws",
                       ".whip",
                       ".zgs",
                       ".dlong",
                       ".dmace",
                       ".dwh",
                       ".ss",
                       ".gmaul",
                       ".ice",
                       ".blood",
                       ".smoke",
                       ".bp"]

        def checkParameters(message):
            channelDuel = globals.duels.get(message.channel.id, None)
            attackTypes = [".dds",
                       ".ags",
                       ".sgs",
                       ".claws",
                       ".whip",
                       ".zgs",
                       ".dlong",
                       ".dmace",
                       ".dwh",
                       ".ss",
                       ".gmaul",
                       ".ice",
                       ".blood",
                       ".smoke",
                       ".bp"]

            attackTypeCheck = None

            if message.content in attackTypes:
                attackTypeCheck = True
            else:
                attackTypeCheck = False

            return channelDuel != None and message.author.id == savedTurn.user.id and attackTypeCheck == True and duel.turnCount == globals.duels[message.channel.id].turnCount
        
        try:
            msg = await self.bot.wait_for('message', check=checkParameters, timeout=90)

        except asyncio.TimeoutError:
            # called when it times out

            turnUser = None
            notTurn = None

            channelDuel = globals.duels.get(message.channel.id, None)

            if channelDuel == None:
                return

            if channelDuel.turn.user.id == channelDuel.user_1.user.id and channelDuel.uuid == duel.uuid:
                turnUser = channelDuel.user_1
                notTurn = channelDuel.user_2
            elif channelDuel.uuid == duel.uuid and channelDuel.turnCount == duel.turnCount:
                turnUser = channelDuel.user_2
                notTurn = channelDuel.user_1
            await message.channel.send(f'{turnUser.user.nick} took too long to take their turn. {notTurn.user.nick} wins the duel.')
            await self.updateDB(notTurn.user, turnUser.user)
            globals.duels[message.channel.id] = None

    def check(self, user, channelId):
        channelDuel = globals.duels.get(channelId, None)

        if channelDuel == None:
            print("This shouldn't ever call from check")

        return user != channelDuel.user_1.user

    async def updateDB(self, winner, loser):

        commands = (
            f"""
        INSERT INTO duel_users (user_id, wins, losses, gp) 
        VALUES 
        ({winner.id}, 1, 0, 0) 
        ON CONFLICT (user_id) DO UPDATE 
        SET wins = duel_users.wins + 1 
        """,

            f"""
        INSERT INTO duel_users (user_id, wins, losses, gp) 
        VALUES 
        ({loser.id}, 0, 1, 0) 
        ON CONFLICT (user_id) DO UPDATE 
        SET losses = duel_users.losses + 1 
        """
        )

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()

            for command in commands:
                cur.execute(command)

            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 4", error)
        finally:
            if conn is not None:
                conn.close()

    async def startCancelCountdown(self, message, saved_uuid):

        await asyncio.sleep(30.0)

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            return

        if channelDuel.user_2 == None and channelDuel.uuid == saved_uuid:
            del globals.duels[message.channel.id]
            await message.send("Nobody accepted the duel.")

        elif channelDuel.user_2 != None:
            return

    @commands.is_owner()
    @commands.command()
    async def test(self, message):
        await PotentialItems.generateLoot(self, message)

    @commands.command()
    async def hs(self, ctx):
        placeholderEmbed = discord.Embed(title="Wins highscores", description = "Checking the highscores...", color=discord.Color.gold())
        msg = await ctx.send(embed=placeholderEmbed)

        async def getWinsHighscores(ctx):
            sql = f"""
            SELECT nick, wins, losses
            FROM duel_users
            ORDER BY wins DESC
            """

            conn = None
            leaderboard = []

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)

                rows = cur.fetchall()

                counter = 0
                for row in rows:
                    leaderboard.append(row)
                    counter += 1
                    if counter == 10:
                        return leaderboard

                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 4", error)
                return leaderboard
            finally:
                if conn is not None:
                    conn.close()
                return leaderboard

        # For when we have different high scores
        # if args == None:
        frontPage = await getWinsHighscores(ctx)

        description = ""

        if len(frontPage) == 0:
            errorEmbed = discord.Embed(title="Wins highscores", description="Something went wrong.", color=discord.Color.dark_red())
            await msg.edit(embed=errorEmbed)

        for n in range(0, len(frontPage)):
            description += f"{n + 1} - **{frontPage[n][0]}**: {frontPage[n][1]} wins | {frontPage[n][2]} losses | {round((frontPage[n][1]/frontPage[n][2]), 2)} KDA \n"

        frontPageEmbed = discord.Embed(title="Wins highscores", description=description, color=discord.Color.gold())
        await msg.edit(embed=frontPageEmbed)

    @commands.command()
    @commands.is_owner()
    async def givegp(self, ctx, *args):
        quantity = args[1]
        quantity = RSMathHelpers(self.bot).numify(args[1])

        shortQuant = RSMathHelpers(self.bot).shortNumify(quantity, 1)

        if type(quantity) != int:
            await ctx.send('Please enter a valid number.')
            return

        person = args[0].replace('@', '').replace('>','').replace('<','').replace('!', '')

        await Economy(self.bot).giveItemToUser(person, 'duel_users', 'gp', quantity)
        await ctx.send(f"You gave {shortQuant} to <@!{person}>")
        return
    
    @commands.command()
    async def pay(self, ctx, *args):
        quantity = args[1]
        quantity = RSMathHelpers(self.bot).numify(args[1])

        shortQuant = RSMathHelpers(self.bot).shortNumify(quantity, 1)

        if type(quantity) != int:
            await ctx.send('Please enter a valid number.')
            return

        usersQuantity = await Economy(self.bot).getNumberOfItem(ctx.author.id, 'duel_users', 'gp')

        if usersQuantity < quantity:
            await ctx.send('You do not have enough gp to do that.')
            return

        person = args[0].replace('@', '').replace('>','').replace('<','').replace('!', '')

        await Economy(self.bot).removeItemFromUser(ctx.author.id, 'duel_users', 'gp', quantity)
        await Economy(self.bot).giveItemToUser(person, 'duel_users', 'gp', quantity)
        await ctx.send(f"You give {shortQuant} to <@!{person}>")
        return

def setup(bot):
    bot.add_cog(UserCommands(bot))