import asyncio
import discord
import os
import random
import math
import psycopg2
from cogs.loots import PotentialItems
from cogs.osrsEmojis import ItemEmojis
from random import randint
import globals
from discord.ext import commands
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

DATABASE_URL = os.environ['DATABASE_URL']

class AttackCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Weapon commands
    # All non-freezing spells pull from 'useAttack()'
    # Freezing spells pull from 'freezeAttack()'
    # Dragon claws are currently an owner-only command
    @commands.command()
    async def dds(self, message):
        await self.useAttack(message, "DDS", 25, 2, 18, 0, True)

    @commands.command()
    async def whip(self, message):
        await self.useAttack(message, "Abyssal whip", 0, 1, 27, 0, False)

    @commands.command()
    async def ags(self, message):
        await self.useAttack(message, "Armadyl godsword", 50, 1, 46, 0, False)

    @commands.command()
    async def zgs(self, message):
        await self.freezeAttack(message, "Zamorak godsword", 50, 1, 36, 25)

    @commands.command()
    async def dlong(self, message):
        await self.useAttack(message, "Dragon longsword", 25, 1, 26, 0, False)

    @commands.command()
    async def dmace(self, message):
        await self.useAttack(message, "Dragon mace", 25, 1, 30, 0, False)

    @commands.command()
    async def dwh(self, message):
        await self.useAttack(message, "Dragon warhammer", 50, 1, 39, 0, False)

    @commands.command()
    async def ss(self, message):
        await self.useAttack(message, "Saradomin sword", 100, 2, 27, 0, False)

    @commands.command()
    async def gmaul(self, message):
        await self.useAttack(message, "Granite maul", 100, 3, 24, 0, False)

    @commands.command()
    async def ice(self, message):
        await self.freezeAttack(message, "Ice barrage", 0, 1, 30, 12.5)

    @commands.command()
    async def sgs(self, message):
        await self.useAttack(message, "Saradomin godsword", 50, 1, 37, 50, False)

    @commands.command()
    @commands.is_owner()
    async def dclaws(self, message):

        sendingUser = None
        receivingUser = None

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            return

        if message.author.id == channelDuel.user_1.user.id:
            sendingUser = channelDuel.user_1
            receivingUser = channelDuel.user_2

        if message.author.id == channelDuel.user_2.user.id:
            sendingUser = channelDuel.user_2
            receivingUser = channelDuel.user_1

        if sendingUser == None:
            return

        # if the wrong user is trying to go
        if sendingUser.user.id != channelDuel.turn.user.id:
            await message.send("It's not your turn.")
            return

        # records last attack to prevent using spamming
        if sendingUser.lastAttack == "claws":
            await message.send("You cannot use that type of attack twice in a row.")
            return
        else:
            sendingUser.lastAttack = "claws"

        # if the user does not have enough special attack
        if sendingUser.special < 50:
            await message.send(f"Using the Dragon claws requires 50% special attack energy.")
            return

        hitArray = []

        # calculate each damage roll
        hit = randint(0, 21)

        # if first hit 10 or higher, keep it. If it's lower, scrap it.
        if hit >= 10:
            hitArray.append(hit)  # First hit does full
            # Second hit does half of the first hit
            hitArray.append(math.floor(hit/2))
            # Third and fourth hits do a quarter of the first hit
            hitArray.append(math.floor(hit/4))
            hitArray.append(math.floor(hit/4))

        else:
            hitArray.append(0)  # First hit is a 0
            secondHit = randint(0, 21)
            if secondHit >= 4:
                hitArray.append(secondHit)  # Second hit rolls for max
                # Third and fourth hits are half of second
                hitArray.append(math.floor(secondHit/2))
                hitArray.append(math.floor(secondHit/2))
            else:
                hitArray.append(0)  # Second hit is 0
                thirdHit = randint(0, 21)
                if thirdHit >= 4:
                    # Third and fourth hits do 75% of max
                    hitArray.append(thirdHit)
                    hitArray.append(thirdHit - 1)
                else:
                    hitArray.append(0)  # Third hit is a 0
                    fourthHit = randint(0, 21)
                    if fourthHit >= 4:
                        hitArray.append(31)  # Fourth hit is a 0
                    else:
                        hitArray[2] = 1
                        hitArray.append(1)

        # calculate poison
        poisonRoll = randint(0, 3)

        if receivingUser.poisoned == True:
            # if the user is already poisoned and the poison roll succeeded, apply damage.
            if poisonRoll == 0:
                receivingUser.hitpoints -= 6

        # calculate damage dealt
        leftoverHitpoints = receivingUser.hitpoints - sum(hitArray)
        receivingUser.hitpoints = leftoverHitpoints

        # calculate special remaining
        sendingUser.special -= 50

        # create the image for the remaining hitpoints
        if leftoverHitpoints > 0:
            if receivingUser.poisoned == True:
                self.makeImage(leftoverHitpoints, False, True)
            else:
                self.makeImage(leftoverHitpoints, False, False)
        else:
            self.makeImage(0, False, False)

        sending = ""

        sending += f'{message.author.nick} uses their **Dragon claws** and hits **{hitArray[0]}-{hitArray[1]}-{hitArray[2]}-{hitArray[3]}** on {receivingUser.user.nick}.'

        if poisonRoll == 0 and receivingUser.poisoned == True:
            sending += f' {receivingUser.user.nick} is hit for **6** poison damage.'

        # winning message
        if leftoverHitpoints <= 0:
            await message.send(content=f'{sending} \n{message.author.nick} has won the duel with **{sendingUser.hitpoints}** HP left!', file=discord.File('./hpbar.png'))
            await self.updateDB(sendingUser.user, receivingUser.user)
            await self.rollForRares(message, sendingUser.user)
            del globals.duels[message.channel.id]
            await PotentialItems.generateLoot(message)
            return

        # calculates special energy remaining and adds to message
        sending += f' {message.author.nick} has {sendingUser.special}% special attack energy left.'

        # send message and add image below
        await message.send(content=sending, file=discord.File('./hpbar.png'))

        # remove image from local file
        os.remove('./hpbar.png')
        channelDuel.turnCount += 1
        await self.turnChecker(message, channelDuel)

    @commands.command()
    async def bp(self, message):
        await self.useAttack(message, "Toxic blowpipe", 50, 1, 27, 50, False)

    @commands.command()
    async def blood(self, message):
        await self.useAttack(message, "Blood barrage", 0, 1, 29, 25, False)

    @commands.command()
    async def smoke(self, message):
        await self.useAttack(message, "Smoke barrage", 0, 1, 27, 0, True)

    # OWner command to test loot generation. Useful for generating statistics or giving myself money :-)
    @commands.command()
    @commands.is_owner()
    async def randomLoot(self, message):
        await PotentialItems.generateLoot(message)

    # freezeAttack() causes the attacking user to use an attack that has potential to use the enemy
    # Inputs:
        # message - discord context - context of the discord bot
        # weapon - string - the weapon name
        # special - int - the amount of special attack the weapon uses
        # rolls - int - number of hits the weapon has
        # max - int - max hit of the weapon
        # freezeChance - int - % chance to freeze the enemy
    async def freezeAttack(self, message, weapon, special, rolls, max, freezeChance):

        # Internal vars used for reference
        sendingUser = None # User ending the attack
        receivingUser = None # User taking damage

        # Retrieve the channel's duel from the global duel dict
        channelDuel = globals.duels.get(message.channel.id, None)

        #If the duel doesn't exist, just return
        if channelDuel == None:
            return

        # Sets the attacker and defender (sendingUser and receivingUser, respectively)
        # If the attacker is player one
        if message.author.id == channelDuel.user_1.user.id:
            sendingUser = channelDuel.user_1
            receivingUser = channelDuel.user_2

        # If the attacker is player two
        if message.author.id == channelDuel.user_2.user.id:
            sendingUser = channelDuel.user_2
            receivingUser = channelDuel.user_1

        # If the user was not part of the duel
        if sendingUser == None:
            return

        # If the sender is part of the duel, but it is not their turn
        # Sends a message to the discord channel stating that it is not the player's turn
        if sendingUser.user.id != channelDuel.turn.user.id:
            await message.send("It's not your turn.")
            return

        # Records last attack to prevent using spamming
        # Notable exceptions include the DDS and Abyssal whip
        # TODO: Might be a good idea to just convert this into a bool parameter
        if weapon == "DDS" or weapon == "Abyssal whip": # Exceptions
            sendingUser.lastAttack = weapon
        elif sendingUser.lastAttack == weapon: # Weapon being used is the same as last time
            # Send a message to the channel that the weapon cannot be used twice in a row
            await message.send("You cannot use that type of attack twice in a row.")
            return
        else:
            sendingUser.lastAttack = weapon

        # Array to hold the hits rolled
        hitArray = []

        # Roll a RNG hit (rolls) times and append [hitArray]
        for n in range(0, rolls):
            hit = randint(0, max)
            hitArray.append(hit)

        # Calculate poison (25% chance of 6 damage)
        # This is outside of the below code because it's used to append the final message
        poisonRoll = randint(0, 3)

        #If the receiver is already poisoned...
        if receivingUser.poisoned == True:
            # If the user is already poisoned and the poison roll succeeded, apply damage
            if poisonRoll == 0:
                receivingUser.hitpoints -= 6

        # Calculate damage dealt and subtract it from receivingUser hitpoints
        leftoverHitpoints = receivingUser.hitpoints - sum(hitArray)
        receivingUser.hitpoints = leftoverHitpoints

        # Calculate special remaining
        sendingUser.special -= special

        # Roll to freeze, rounds down
        rand = randint(0, math.floor((100/freezeChance))-1)

        # Creates the appropriate image to display hitpoints
        if leftoverHitpoints > 0:

            if receivingUser.poisoned == True and rand == 0: # If the receivingUser is poisoned, and the freeze roll hit
                self.makeImage(leftoverHitpoints, True, True)
            elif receivingUser.poisoned == True and rand != 0: # If the receivingUser is poisoned and the freeze roll did not hit
                self.makeImage(leftoverHitpoints, False, True)
            elif receivingUser.poisoned == False and rand == 0: # If the receivingUser is not poisoned and the freeze roll hit
                self.makeImage(leftoverHitpoints, True, False)
            elif receivingUser.poisoned == False and rand != 0: # If the receivingUser is not poisoned and the freeze roll did not hit
                self.makeImage(leftoverHitpoints, False, False)    
        else:
            # If the receivingUser has 0 hitpoints left
            self.makeImage(0, False, False)

        # Holds the message to send to the channel containing information about the hit, spec percentage, freeze, or death
        sending = ""

        # If the weapon only hit once (no freeze attacks currently hit more than once)
        if len(hitArray) == 1:
            sending += f'{message.author.nick} uses **{weapon}** and hits a **{hitArray[0]}** on {receivingUser.user.nick}.'

        # If the receivingUser is dead
        if leftoverHitpoints <= 0:

            # Send message with info about winning, attach image of HP
            await message.send(content=f'{sending} \n{message.author.nick} has won the duel with **{sendingUser.hitpoints}** HP left!', file=discord.File('./hpbar.png'))
            
            # Update database with winner and loser
            await self.updateDB(sendingUser.user, receivingUser.user)

            # Roll for a chance on the rares table
            await self.rollForRares(message, sendingUser.user)

            # Delete the duel from the duel dict
            del globals.duels[message.channel.id]

            # Generate loot and send the message to the channel
            # Purposefully after deleting the duel because it can throw errors from the G/E API
            await PotentialItems.generateLoot(message)

            return

        # Calculates special energy remaining and adds to message
        if special != 0:
            sending += f' {message.author.nick} has {sendingUser.special}% special attack energy left.'

        # If the user got hit by poison and they're poisoned (both will be true if the user was poisoned this turn) append the message to send
        if poisonRoll == 0 and receivingUser.poisoned == True:
            sending += f' {receivingUser.user.nick} is hit for **6** poison damage.'

        # If the user is frozen, send the message and return early to avoid switching who the turnChecker is looking for
        if rand == 0:
            sending += f' {receivingUser.user.nick} is **frozen** and loses their turn.'
            channelDuel.turnCount += 1
            await message.send(sending)
            await message.send(file=discord.File('./hpbar.png'))
            return

        # Send the attack message and image
        await message.send(content=sending, file=discord.File('./hpbar.png'))
        
        os.remove('./hpbar.png')
        channelDuel.turnCount += 1
        await self.turnChecker(message, channelDuel)

    async def useAttack(self, message, weapon, special, rolls, max, healpercent, poison):

        sendingUser = None
        receivingUser = None

        channelDuel = globals.duels.get(message.channel.id, None)

        if channelDuel == None:
            return

        if message.author.id == channelDuel.user_1.user.id:
            sendingUser = channelDuel.user_1
            receivingUser = channelDuel.user_2

        if message.author.id == channelDuel.user_2.user.id:
            sendingUser = channelDuel.user_2
            receivingUser = channelDuel.user_1

        if sendingUser == None:
            return

        # if the wrong user is trying to go

        if sendingUser.user.id != channelDuel.turn.user.id:
            await message.send("It's not your turn.")
            return

        # records last attack to prevent using spamming
        if weapon == "DDS" or weapon == "Abyssal whip":
            sendingUser.lastAttack = weapon
        elif sendingUser.lastAttack == weapon:
            await message.send("You cannot use that type of attack twice in a row.")
            return
        else:
            sendingUser.lastAttack = weapon

        # if the user does not have enough special attack
        if special == 0:
            pass
        elif sendingUser.special < special:
            await message.send(f"Using the {weapon} requires {special}% special attack energy.")
            return

        hitArray = []

        # calculate each damage roll
        for n in range(0, rolls):
            hit = randint(0, max)
            hitArray.append(hit)

        # calculate poison
        poisonRoll = randint(0, 3)

        if poison == True and receivingUser.poisoned == False:
            if poisonRoll == 0:  # checks roll to see if the user is now poisoned. If yes, apply damage.
                receivingUser.poisoned = True
                receivingUser.hitpoints -= 6
        elif receivingUser.poisoned == True:
            # if the user is already poisoned and the poison roll succeeded, apply damage.
            if poisonRoll == 0:
                receivingUser.hitpoints -= 6

        # calculate damage dealt
        leftoverHitpoints = receivingUser.hitpoints - sum(hitArray)
        receivingUser.hitpoints = leftoverHitpoints

        # calculate special remaining
        sendingUser.special -= special

        # calculate any healing
        healAmount = math.floor(healpercent/100 * hitArray[0])

        # sets lowest possible heal for SGS
        if weapon == "Saradomin godsword" and healAmount < 10:
            healAmount = 10

        # prevents healing over 99 HP
        if sendingUser.hitpoints + healAmount < 99:
            sendingUser.hitpoints += healAmount
        else:
            sendingUser.hitpoints = 99

        # create the image for the remaining hitpoints
        if leftoverHitpoints > 0:
            if receivingUser.poisoned == True:
                self.makeImage(leftoverHitpoints, False, True)
            else:
                self.makeImage(leftoverHitpoints, False, False)
        else:
            self.makeImage(0, False, False)

        sending = ""

        # 1 attack roll
        if len(hitArray) == 1:
            sending += f'{message.author.nick} uses their **{weapon}** and hits **{hitArray[0]}** on {receivingUser.user.nick}.'

        # 2 attack rolls
        if len(hitArray) == 2:
            sending += f'{message.author.nick} uses their **{weapon}** and hits **{hitArray[0]}-{hitArray[1]}** on {receivingUser.user.nick}.'

        # 3 attack rolls
        if len(hitArray) == 3:
            sending += f'{message.author.nick} uses their **{weapon}** and hits **{hitArray[0]}-{hitArray[1]}-{hitArray[2]}** on {receivingUser.user.nick}.'

        if poisonRoll == 0 and receivingUser.poisoned == True:
            sending += f' {receivingUser.user.nick} is hit for **6** poison damage.'

        # healing message
        if healpercent > 0:
            sending = f'{message.author.nick} uses their **{weapon}** and hits **{hitArray[0]}**, healing for **{healAmount}**. {sendingUser.user.nick} now has **{sendingUser.hitpoints}** HP.'

        # winning message
        if leftoverHitpoints <= 0:
            await message.send(content=f'{sending} \n{message.author.nick} has won the duel with **{sendingUser.hitpoints}** HP left!', file=discord.File('./hpbar.png'))
            await self.updateDB(sendingUser.user, receivingUser.user)
            await self.rollForRares(message, sendingUser.user)
            del globals.duels[message.channel.id]
            await PotentialItems.generateLoot(message)
            return

        # calculates special energy remaining and adds to message
        if special != 0:
            sending += f' {message.author.nick} has {sendingUser.special}% special attack energy left.'

        # send message and add image below
        await message.send(content=sending, file=discord.File('./hpbar.png'))

        # Remove image from local file
        os.remove('./hpbar.png')

        # Tick up the turn counter
        channelDuel.turnCount += 1

        # Start the timer to check if another turn is taken
        await self.turnChecker(message, channelDuel)

    # Checker function to see if a turn is taken in a set amount of time
    async def turnChecker(self, message, duel):

        # Retrieve the duel for the channel
        channelDuel = globals.duels.get(message.channel.id, None)

        # Switches who's turn it is
        savedTurn = channelDuel.turn
        savedTurnCount = channelDuel.turnCount
        if channelDuel.turn == channelDuel.user_1:
            channelDuel.turn = channelDuel.user_2
        else:
            channelDuel.turn = channelDuel.user_1

        # Array of attack command strings
        attackTypes = [".dds",
                       ".ags",
                       ".sgs",
                       ".dlaws",
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

        # Nested discord 'check' function for checking to see if the duel has been altered
        def checkParameters(message):

            # Retrieve the duel for the channel
            channelDuel = globals.duels.get(message.channel.id, None)

            # Array of attack command strings
            attackTypes = [".dds",
                           ".ags",
                           ".sgs",
                           ".dclaws",
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

            # Does the content of the message pass the attack type check?
            # Sets attackTypeCheck to BOOL
            if message.content in attackTypes:
                attackTypeCheck = True
            else:
                attackTypeCheck = False

            # If there is no duel found, return
            if globals.duels.get(message.channel.id, None) == None:
                return

            # Return this executable to test if the duel has changed
            # If the duel exists (is not None) AND
            # If the author of the message sent is the same as the person who's turn it is AND
            # If the command used is one of the attack commands AND
            # If the duel has the same turn count as when initially called
            return channelDuel != None and message.author.id == savedTurn.user.id and attackTypeCheck == True and savedTurnCount == globals.duels[message.channel.id].turnCount
        
        try:
            # Wait for the person who's turn it is to send a messsage that matches the parameters in checkParameters(), executes after 90 seconds
            msg = await self.bot.wait_for('message', check=checkParameters, timeout=90)

        except asyncio.TimeoutError:
            # Called when it times out

            # Placeholders for determining the user of the turn
            turnUser = None
            notTurn = None

            # Retrieve the duel for the channel
            channelDuel = globals.duels.get(message.channel.id, None)

            # If no duel exists, return ELSE IF
            # The turncount hasn't changed and the duel is the same duel from before (same uuid) THEN
            # Store the turnUser/notTurn variables for the last message
            if channelDuel == None:
                return
            elif channelDuel != None and channelDuel.turnCount == duel.turnCount and channelDuel.uuid == duel.uuid:
                if channelDuel.turn.user.id == channelDuel.user_1.user.id:
                    turnUser = channelDuel.user_1
                    notTurn = channelDuel.user_2
                else:
                    turnUser = channelDuel.user_2
                    notTurn = channelDuel.user_1

                # Send a message to the discord channel stating the winner and loser based on their nicknames in the channel
                await message.channel.send(f'{turnUser.user.nick} took too long to take their turn. {notTurn.user.nick} wins the duel.')

                # Log the timeout to the console, useful for debugging
                print(f'Duel in channel {message.channel.id} timed out.')

                # Delete the duel from the duels dict
                globals.duels[message.channel.id] = None

    # Update the winne and loser's kill/death in the database
    async def updateDB(self, winner, loser):
        # 1st command for the winner
        # 2nd command for the loser
        # gp included in case user has never had row created for them
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
                cur.execute(command) # Do the SQL shit

            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 1", error)
        finally:
            if conn is not None:
                conn.close()

    # Roll for a chance to receive a rare/holiday item
    # If the rares table is hit, the user will receive a message
    async def rollForRares(self, message, winner):

        item = None
        itemText = None
        itemEmoji = None

        tableRoll = randint(0, 99)

        # Winner hits the rares table
        # Effective rates are as follows:
            # Christmas cracker - 0.01% or 1/10,000
            # Partyhat table - 0.18% or 18/10,000
                # Red partyhat - 0.03% or 3/10,000
                # Blue partyhat - 0.03% or 3/10,000
                # Yellow partyhat - 0.03% or 3/10,000
                # Green partyhat - 0.03% or 3/10,000
                # Purple partyhat - 0.03% or 3/10,000
                # White partyhat - 0.03% or 3/10,000
            # Halloween mask table - 0.21% or 21/10,000
                # Red halloween mask - 0.07% or 7/10,000
                # Blue halloween mask - 0.07% or 7/10,000
                # Green halloween mask - 0.07% or 7/10,000
            # Santa hat - 0.10% or 10/10,000
            # Pumpkin - 0.25% or 25/10,000
            # Easter egg - 0.25% or 25/10,000

        if tableRoll == 0:
            raresRoll = randint(0, 99)
            if raresRoll == 0:  # hit table for cracker
                item = "christmas_cracker"
                itemText = "Christmas cracker"
                itemEmoji = ItemEmojis.Rares.christmasCracker
            elif raresRoll <= 17:  # hit table for a partyhat
                phatRoll = randint(0, 5)
                if phatRoll == 0:
                    item = "red_partyhat"
                    itemText = "a Red partyhat"
                    itemEmoji = ItemEmojis.Rares.redPartyhat
                elif phatRoll == 1:
                    item = "blue_partyhat"
                    itemText = "a Blue partyhat"
                    itemEmoji = ItemEmojis.Rares.bluePartyhat
                elif phatRoll == 2:
                    item = "yellow_partyhat"
                    itemText = "a Yellow partyhat"
                    itemEmoji = ItemEmojis.Rares.yellowPartyhat
                elif phatRoll == 3:
                    item = "green_partyhat"
                    itemText = "a Green partyhat"
                    itemEmoji = ItemEmojis.Rares.greenPartyhat
                elif phatRoll == 4:
                    item = "purple_partyhat"
                    itemText = "a Purple partyhat"
                    itemEmoji = ItemEmojis.Rares.purplePartyhat
                elif phatRoll == 5:
                    item = "white_partyhat"
                    itemText = "a White partyhat"
                    itemEmoji = ItemEmojis.Rares.whitePartyhat
            elif raresRoll <= 38:  # hit table for a mask
                maskRoll = randint(0, 2)
                if maskRoll == 0:
                    item = "red_hween_mask"
                    itemText = "a Red h'ween mask"
                    itemEmoji = ItemEmojis.Rares.redHween
                elif maskRoll == 1:
                    item = "blue_hween_mask"
                    itemText = "a Blue h'ween mask"
                    itemEmoji = ItemEmojis.Rares.blueHween
                elif maskRoll == 2:
                    item = "green_hween_mask"
                    itemText = "a Green h'ween mask"
                    itemEmoji = ItemEmojis.Rares.greenHween
            elif raresRoll <= 49:  # hit table for a santa hat
                item = "santa_hat"
                itemText = "a Santa hat"
                itemEmoji = ItemEmojis.Rares.santaHat
            elif raresRoll <= 74:  # hit table for a pumpkin
                item = "pumpkin"
                itemText = "a Pumpkin"
                itemEmoji = ItemEmojis.Rares.pumpkin
            elif raresRoll <= 99:  # hit table for an easter egg
                item = "easter_egg"
                itemText = "an Easter egg"
                itemEmoji = ItemEmojis.Rares.easterEgg

        sql = None

        if tableRoll == 0:
            print(f"{message.author.nick} hit the rares table")
            sql = f"""
            INSERT INTO duel_rares (
            user_id,
            red_partyhat,
            blue_partyhat,
            yellow_partyhat,
            green_partyhat,
            purple_partyhat,
            white_partyhat,
            christmas_cracker,
            red_hween_mask,
            blue_hween_mask,
            green_hween_mask,
            santa_hat,
            pumpkin,
            easter_egg) 
            VALUES 
            ({winner.id}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) 
            ON CONFLICT (user_id) DO UPDATE 
            SET {item} = duel_rares.{item} + 1 
            """
        else:
            print(f"{message.author.nick} did not hit the rares table")
            return

        conn = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 2", error)
            return
        finally:
            if conn is not None:
                conn.close()

        # Send the message with info about hitting the rares table to the winner
        await message.send(f"*{message.author.nick} received {itemText} {itemEmoji} for winning!*")

    # Creates the hitpoints image
    # Parameters:
        # Hipoints - int - how many hitpoints are left
        # Freeze - bool - is the user frozen
        # Poison - bool - is the user poisoned
    def makeImage(self, hitpoints, freeze, poison):
       
        # Red background
        primary = (252, 3, 3)

        #Green hitpoints bar
        secondary = (0, 255, 26)

        if poison == True:
            #Lighter green
            primary = (44, 156, 55)

            #Darker green
            secondary = (112, 219, 123)

        if freeze == True:
            #Lighter blue
            primary = (69, 155, 217)

            #Darker blue
            secondary = (130, 203, 255)

        # Creates the image with width of 40 x 198 (99 x 2), with a background color of the primary var
        img = Image.new('RGB', (198, 40), primary)

        # Adds the remaining HP on top of the background, with 2 * the number of hitpoints remaining as the width
        img.paste(secondary, (0, 0, 2 * hitpoints, 40))

        # Draw the image
        draw = ImageDraw.Draw(img)

        # Load the Runescape font
        font = ImageFont.truetype(r'./runescape_uf.ttf', 16)

        # Add text containing info about the remaining HP to the image
        draw.text((80, 10), f"{hitpoints}/99", (0, 0, 0), font=font)

        # Save the image locally
        # Note: this file is created and immediately deleted after the image has been posted to discord
        img.save('./hpbar.png')

def setup(bot):
    bot.add_cog(AttackCommands(bot))
