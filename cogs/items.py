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

class SpecItems(commands.Cog):

    # TODO List
    # Enable buying items
    # Enable selling items
    # Create store for buying items
    # Limit using special weapons unless the weapon is owned
    # Add 'dropping' weapons
    # Add 'picking up' weapons

    def __init__(self, bot):
        self.bot = bot
        
def setup(bot):
    bot.add_cog(SpecItems(bot))
