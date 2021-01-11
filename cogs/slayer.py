import asyncio
import discord
import os
import random
import math
import psycopg2
import json
import requests
import time
import datetime
from datetime import datetime, timedelta
from cogs.osrsEmojis import ItemEmojis
from cogs.mathHelpers import RSMathHelpers
from cogs.skilling import Skilling
from osrsbox import monsters_api
from random import randint
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']

# Todo
# Add items


class Slayer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    slayerMasters = {
        "turael": {
            "req": 1,
            "tasks": {
                "Banshees": {"min": 15, "max": 50, "req": 15, "weight": 8, "id": 414 },
                "Bats": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 2827},
                "Birds": {"min": 15, "max": 50, "req": 1, "weight": 6, "id": 1173},
                "Bears": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 2839},
                "Cave Bugs": {"min": 10, "max": 20, "req": 7, "weight": 8, "id": 481},
                "Cave Crawlers": {"min": 15, "max": 50, "req": 10, "weight": 8, "id": 406},
                "Cave Slimes": {"min": 10, "max": 20, "req": 17, "weight": 8, "id": 480},
                "Cows": {"min": 15, "max": 50, "req": 1, "weight": 8, "id":2790  },
                "Crawling Hands": {"min": 15, "max": 50, "req": 5, "weight": 8, "id": 448},
                "Dogs": {"min": 15, "max": 50, "req": 30, "weight": 7, "id": 114  },
                "Dwarves": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 290  },
                "Ghosts": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 85  },
                "Goblins": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 655  },
                "Icefiends": {"min": 15, "max": 50, "req": 1, "weight": 8, "id": 3140  },
                "Kalphites": {"min": 15, "max": 50, "req": 25, "weight": 6, "id": 95  },
                "Lizards": {"min": 15, "max": 50, "req": 22, "weight": 8, "id": 458  },
                "Minotaurs": {"min": 10, "max": 20, "req": 1, "weight": 7, "id": 2481  },
                "Monkeys": {"min": 15, "max": 50, "req": 1, "weight": 6, "id": 1038  },
                "Rats": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 2492  },
                "Scorpions": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 2479  },
                "Skeletons": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 70  },
                "Spiders": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 2478  },
                "Wolves": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 2490  },
                "Zombies": {"min": 15, "max": 50, "req": 1, "weight": 7, "id": 26  }
            },
            "points": 0
        },
        "mazchna": {
            "req": 20,
            "tasks": {
                "Banshees": {"min": 40, "max": 70, "req": 15, "weight": 8, "id": 414},
                "Bats": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 2827 },
                "Bears": {"min": 40, "max": 70, "req": 1, "weight": 6, "id": 2839 },
                "Catablepons": {"min": 20, "max": 30, "req": 18, "weight": 8, "id": 2474 },
                "Cave Bugs": {"min": 10, "max": 20, "req": 7, "weight": 8, "id": 481 },
                "Cave Crawlers": {"min": 40, "max": 70, "req": 10, "weight": 8, "id": 406 },
                "Cave Slimes": {"min": 10, "max": 20, "req": 17, "weight": 8, "id": 480 },
                "Cockatrice": {"min": 40, "max": 70, "req": 25, "weight": 8, "id": 419 },
                "Crawling Hands": {"min": 40, "max": 70, "req": 5, "weight": 8, "id": 448 },
                "Lizards": {"min": 40, "max": 70, "req": 22, "weight": 8, "id": 458 },
                "Dogs": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 114 },
                "Earth Warriors": {"min": 40, "max": 70, "req": 1, "weight": 6, "id": 2840 },
                "Flesh Clawers": {"min": 15, "max": 25, "req": 1, "weight": 7, "id": 2498 },
                "Ghosts": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 85 },
                "Ghouls": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 289 },
                "Hill Giants": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 2098 },
                "Hobgoblins": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 132 },
                "Ice Warriors": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 2841 },
                "Kalphites": {"min": 40, "max": 70, "req": 1, "weight": 6, "id": 955 },
                "Killerwatts": {"min": 30, "max": 80, "req": 37, "weight": 6, "id": 469 },
                "Mogres": {"min": 40, "max": 70, "req": 32, "weight": 8, "id": 2592 },
                "Rockslugs": {"min": 40, "max": 70, "req": 20, "weight": 8, "id": 421 },
                "Scorpions": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 2479 },
                "Shades": {"min": 40, "max": 70, "req": 1, "weight": 8, "id": 5633 },
                "Skeletons": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 70 },
                "Vampyres": {"min": 10, "max": 20, "req": 1, "weight": 6, "id": 3692 },
                "Wall Beasts": {"min": 10, "max": 20, "req": 35, "weight": 7, "id": 476 },
                "Wolves": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 106 },
                "Zombies": {"min": 40, "max": 70, "req": 1, "weight": 7, "id": 26 }
            },
            "points": 2
        },
        "vannaka": {
            "req": 40,
            "tasks": {
                'Aberrantspectre': {'min':40, 'max':80, 'req':60, 'weight':7, 'id': 2},
                'Abyssaldemon': {'min':60, 'max':120, 'req':85, 'weight':8, 'id': 415},
                'Ankou': {'min':60, 'max':120, 'req':5, 'weight':5, 'id': 2514},
                'Banshee': {'min':25, 'max':35, 'req':15, 'weight':7, 'id': 414},
                'Basiliskknight': {'min':60, 'max':120, 'req':60, 'weight':6, 'id': 9293},
                'Bloodveld': {'min':60, 'max':120, 'req':60, 'weight':8, 'id': 484},
                'Bluedragon': {'min':60, 'max':120, 'req':50, 'weight':8, 'id': 265},
                'Brinerat': {'min':60, 'max':120, 'req':7, 'weight':7, 'id': 4501},
                'Bronzedragon': {'min':60, 'max':120, 'req':60, 'weight':7, 'id': 270},
                'Cavebug': {'min':10, 'max':20, 'req':1, 'weight':7, 'id': 481},
                'Cavecrawler': {'min':10, 'max':20, 'req':5, 'weight':7, 'id': 406},
                'Caveslime': {'min':60, 'max':120, 'req':10, 'weight':7, 'id': 480},
                'Cockatrice': {'min':10, 'max':20, 'req':40, 'weight':7, 'id': 419},
                'CrawlingHand': {'min':60, 'max':120, 'req':5, 'weight':8, 'id': 448},
                'Crocodile': {'min':60, 'max':120, 'req':6, 'weight':6, 'id': 4184},
                'Dagannoth': {'min':60, 'max':120, 'req':40, 'weight':6, 'id': 970},
                'Dustdevil': {'min':60, 'max':120, 'req':65, 'weight':7, 'id': 423},
                'Earthwarrior': {'min':60, 'max':120, 'req':1, 'weight':8, 'id': 2840},
                'Elfwarrior': {'min':40, 'max':80, 'req':1, 'weight':6, 'id': 5293},
                'Feverspider': {'min':40, 'max':100, 'req':40, 'weight':7, 'id': 626},
                'Firegiant': {'min':60, 'max':120, 'req':1, 'weight':7, 'id': 2075},
                'Gargoyle': {'min':60, 'max':120, 'req':75, 'weight':7, 'id': 412},
                'Ghoul': {'min':60, 'max':120, 'req':5, 'weight':5, 'id': 289},
                'Greendragon': {'min':10, 'max':40, 'req':1, 'weight':7, 'id': 260},
                'HarpieBugSwarm': {'min':40, 'max':80, 'req':33, 'weight':6, 'id': 464},
                'Hellhound': {'min':60, 'max':120, 'req':1, 'weight':8, 'id': 104},
                'HillGiant': {'min':40, 'max':80, 'req':1, 'weight':7, 'id': 2098},
                'Hobgoblin': {'min':60, 'max':120, 'req':1, 'weight':7, 'id': 2241},
                'Icegiant': {'min':60, 'max':120, 'req':1, 'weight':7, 'id': 2085},
                'Icewarrior': {'min':40, 'max':80, 'req':1, 'weight':7, 'id': 2841},
                'InfernalMage': {'min':60, 'max':120, 'req':55, 'weight':7, 'id': 443},
                'Jelly': {'min':60, 'max':120, 'req':8, 'weight':62, 'id': 437},
                'Junglehorror': {'min':60, 'max':120, 'req':53, 'weight':8, 'id': 1042},
                'KalphiteGuardian': {'min':60, 'max':120, 'req':1, 'weight':8, 'id': 959},
                'Killerwatt': {'min':60, 'max':120, 'req':7, 'weight':7, 'id': 469},
                'Kurask': {'min':30, 'max':80, 'req':70, 'weight':6, 'id': 410},
                'Lizard': {'min':60, 'max':120, 'req':20, 'weight':7, 'id': 458},
                'Lesserdemon': {'min':60, 'max':120, 'req':1, 'weight':7, 'id': 2005},
                'Mogre': {'min':60, 'max':120, 'req':1, 'weight':7, 'id': 2592},
                'Molanisk': {'min':60, 'max':120, 'req':30, 'weight':7, 'id': 1},
                'Mossgiant': {'min':39, 'max':50, 'req':1, 'weight':7, 'id': 2090},
                'Nechryael': {'min':60, 'max':120, 'req':80, 'weight':7, 'id': 8},
                'Ogre': {'min':60, 'max':120, 'req':1, 'weight':5, 'id': 136},
                'Otherworldlybeing': {'min':60, 'max':120, 'req':1, 'weight':7, 'id': 2843},
                'Pyrefiend': {'min':60, 'max':120, 'req':1, 'weight':8, 'id': 433},
                'Rockslug': {'min':60, 'max':120, 'req':20, 'weight':8, 'id': 421},
                'Shade': {'min':60, 'max':120, 'req':1, 'weight':7, 'id': 5633},
                'Seasnakeyoung': {'min':60, 'max':120, 'req':1, 'weight':8, 'id': 1097},
                'Shadowwarrior': {'min':60, 'max':120, 'req':1, 'weight':6, 'id': 2853},
                'spiritualmage': {'min':40, 'max':80, 'req':83, 'weight':8, 'id': 2212},
                'Terrordog': {'min':60, 'max':120, 'req':42, 'weight':8, 'id': 6473},
                'Icetroll': {'min':20, 'max':45, 'req':1, 'weight':6, 'id': 648},
                'Turoth': {'min':60, 'max':120, 'req':60, 'weight':7, 'id': 426},
                'Vampyrejuvenile': {'min':60, 'max':120, 'req':8, 'weight':8, 'id': 3692}
            },
            "points": 4
        },
        "chaeldar": {
            "req": 70,
            "tasks": {
                'Aberrantspectre': {'min':60, 'max':120, 'req':60, 'weight':6, 'id': 2},
                'Abyssaldemon': {'min':110, 'max':170, 'req':85, 'weight':8, 'id': 415},
                'Aviansie': {'min':110, 'max':170, 'req':1, 'weight':12, 'id': 3169},
                'Banshee': {'min':110, 'max':170, 'req':9, 'weight':9, 'id': 414},
                'Basiliskknight': {'min':110, 'max':170, 'req':60, 'weight':5, 'id': 9293},
                'Blackdemon': {'min':110, 'max':170, 'req':50, 'weight':7, 'id': 240},
                'Bloodveld': {'min':110, 'max':170, 'req':55, 'weight':10, 'id': 484},
                'Bluedragon': {'min':110, 'max':170, 'req':20, 'weight':8, 'id': 265},
                'Brinerat': {'min':110, 'max':170, 'req':1, 'weight':8, 'id': 4501},
                'Bronzedragon': {'min':110, 'max':170, 'req':60, 'weight':7, 'id': 270},
                'Cavecrawler': {'min':10, 'max':20, 'req':10, 'weight':11, 'id': 406},
                'Cavehorror': {'min':110, 'max':170, 'req':58, 'weight':5, 'id': 1047},
                'Cavekraken': {'min':110, 'max':170, 'req':87, 'weight':10, 'id': 492},
                'Caveslime': {'min':30, 'max':50, 'req':10, 'weight':12, 'id': 480},
                'Cockatrice': {'min':10, 'max':20, 'req':40, 'weight':6, 'id': 419},
                'Dagannoth': {'min':110, 'max':170, 'req':30, 'weight':6, 'id': 970},
                'Dustdevil': {'min':110, 'max':170, 'req':65, 'weight':11, 'id': 423},
                'Elfwarrior': {'min':110, 'max':170, 'req':40, 'weight':9, 'id': 5293},
                'Feverspider': {'min':110, 'max':170, 'req':40, 'weight':8, 'id': 626},
                'Firegiant': {'min':110, 'max':170, 'req':40, 'weight':7, 'id': 2075},
                'Talonedwyvern': {'min':110, 'max':170, 'req':70, 'weight':12, 'id': 7793},
                'Gargoyle': {'min':10, 'max':20, 'req':7, 'weight':75, 'id': 412},
                'Greaterdemon': {'min':110, 'max':170, 'req':20, 'weight':11, 'id': 2025},
                'HarpieBugSwarm': {'min':110, 'max':170, 'req':33, 'weight':9, 'id': 464},
                'Hellhound': {'min':110, 'max':170, 'req':50, 'weight':6, 'id': 104},
                'InfernalMage': {'min':110, 'max':170, 'req':55, 'weight':9, 'id': 443},
                'Irondragon': {'min':110, 'max':170, 'req':60, 'weight':7, 'id': 272},
                'Jelly': {'min':25, 'max':45, 'req':12, 'weight':40, 'id': 437},
                'Junglehorror': {'min':110, 'max':170, 'req':53, 'weight':10, 'id': 1042},
                'Kalphitesoldier': {'min':110, 'max':170, 'req':30, 'weight':10, 'id': 957},
                'Kurask': {'min':110, 'max':170, 'req':11, 'weight':70, 'id': 410},
                'Lesserdemon': {'min':110, 'max':170, 'req':20, 'weight':12, 'id': 2005},
                'LizardmanShaman': {'min':110, 'max':170, 'req':1, 'weight':9, 'id': 6766},
                'Lizard': {'min':70, 'max':90, 'req':10, 'weight':20, 'id': 458},
                'Mogre': {'min':110, 'max':170, 'req':1, 'weight':1, 'id': 2592},
                'Molanisk': {'min':110, 'max':170, 'req':30, 'weight':30, 'id': 1},
                'Zygomite': {'min':39, 'max':50, 'req':50, 'weight':57, 'id': 537},
                'Nechryael': {'min':8, 'max':15, 'req':80, 'weight':80, 'id': 8},
                'Pyrefiend': {'min':110, 'max':170, 'req':10, 'weight':12, 'id': 433},
                'Rockslug': {'min':110, 'max':170, 'req':5, 'weight':6, 'id': 421},
                'Shadowwarrior': {'min':110, 'max':170, 'req':1, 'weight':5, 'id': 2853},
                'SkeletalWyvern': {'min':110, 'max':170, 'req':77, 'weight':8, 'id': 465},
                'Spiritualwarrior': {'min':10, 'max':20, 'req':63, 'weight':7, 'id': 2210},
                'Steeldragon': {'min':110, 'max':170, 'req':65, 'weight':12, 'id': 274},
                'Icetroll': {'min':10, 'max':20, 'req':1, 'weight':9, 'id': 648},
                'Turoth': {'min':110, 'max':170, 'req':60, 'weight':11, 'id': 426},
                'TzHaar-ket': {'min':110, 'max':170, 'req':40, 'weight':10, 'id': 2173},
                'Wallbeast': {'min':90, 'max':150, 'req':25, 'weight':8, 'id': 476},
                'Wyrm': {'min':10, 'max':20, 'req':60, 'weight':6, 'id': 8610}
            },
            "points": 10
        },
        "konar": {
            "req": 75,
            "tasks": {
                "Aberrant Spectres": {"min": 120, "max": 170, "req": 60, "weight": 6, "id":2 },
                "Abyssal Demons": {"min": 120, "max": 170, "req": 85, "weight": 9, "id":415 },
                "Adamant Dragons": {"min": 3, "max": 6, "req": 1, "weight": 5, "id":8030 },
                "Ankou": {"min": 50, "max": 50, "req": 1, "weight": 5, "id":2514 },
                "Aviansie": {"min": 120, "max": 175, "req": 1, "weight": 6, "id":3169 },
                "Basilisk": {"min": 110, "max": 170, "req": 40, "weight": 5, "id":9293 },
                "Black Demons": {"min": 120, "max": 170, "req": 1, "weight": 9, "id":240 },
                "Black Dragons": {"min": 10, "max": 15, "req": 1, "weight": 6, "id":252 },
                "Bloodvelds": {"min": 120, "max": 170, "req": 50, "weight": 9, "id":484 },
                "Blue Dragons": {"min": 120, "max": 170, "req": 1, "weight": 4, "id":265 },
                "Brine Rats": {"min": 120, "max": 170, "req": 47, "weight": 2, "id":4501 },
                "Bronze Dragons": {"min": 30, "max": 50, "req": 1, "weight": 5, "id":270 },
                "Cave Kraken": {"min": 80, "max": 100, "req": 87, "weight": 9, "id":492 },
                "Dagannoth": {"min": 120, "max": 170, "req": 1, "weight": 8, "id":140 },
                "Dark Beats": {"min": 10, "max": 15, "req": 90, "weight": 5, "id":4005 },
                "Drakes": {"min": 75, "max": 122, "req": 84, "weight": 10, "id":8612 },
                "Dust Devils": {"min": 120, "max": 170, "req": 65, "weight": 6, "id":423 },
                "Fire Giants": {"min": 120, "max": 175, "req": 1, "weight": 9, "id":2075 },
                "Fossil Island Wyverns": {"min": 15, "max": 30, "req": 66, "weight": 5, "id":7793 },
                "Gargoyles": {"min": 120, "max": 170, "req": 75, "weight": 6, "id":412 },
                "Greater Demons": {"min": 120, "max": 170, "req": 1, "weight": 7, "id":2025 },
                "Hellhounds": {"min": 120, "max": 170, "req": 1, "weight": 8, "id":104 },
                "Hydras": {"min": 125, "max": 190, "req": 95, "weight": 10, "id":8609 },
                "Iron Dragons": {"min": 30, "max": 50, "req": 1, "weight": 5, "id":272 },
                "Jellies": {"min": 120, "max": 170, "req": 52, "weight": 6, "id":437 },
                "Kalphites": {"min": 120, "max": 170, "req": 1, "weight": 9, "id":138 },
                "Kurasks": {"min": 120, "max": 170, "req": 1, "weight": 9, "id":410 },
                "Lizardmen": {"min": 90, "max": 110, "req": 1, "weight": 8, "id":6766 },
                "Mithril Dragons": {"min": 3, "max": 6, "req": 1, "weight": 5, "id":2919 },
                "Mutated Zygomite": {"min": 10, "max": 25, "req": 57, "weight": 2, "id":537 },
                "Nechryaels": {"min": 110, "max": 110, "req": 80, "weight": 7, "id":7278 },
                "Red Dragons": {"min": 30, "max": 50, "req": 1, "weight": 5, "id":247 },
                "Rune Dragons": {"min": 3, "max": 6, "req": 1, "weight": 5, "id":8031 },
                "Skeletal Wyverns": {"min": 5, "max": 12, "req": 72, "weight": 5, "id":465 },
                "Smoke Devils": {"min": 120, "max": 170, "req": 93, "weight": 7, "id":498 },
                "Steel Dragons": {"min": 30, "max": 50, "req": 1, "weight": 5, "id":274 },
                "Trolls": {"min": 120, "max": 175, "req": 1, "weight": 6, "id":648 },
                "Turoths": {"min": 120, "max": 170, "req": 55, "weight": 3, "id":426 },
                "Waterfiends": {"min": 120, "max": 170, "req": 1, "weight": 2, "id":2916 },
                "Wyrms": {"min": 125, "max": 190, "req": 62, "weight": 10, "id":8610 }
            },
            "points": 18
        },
        "nieve": {
            "req": 85,
            "tasks": {
                "Aberrant Spectres": {"min": 120, "max": 185, "req": 60, "weight": 6, "id": 2},
                "Abyssal Demons": {"min": 120, "max": 185, "req": 85, "weight": 9, "id": 415},
                "Adamant Dragons": {"min": 3, "max": 7, "req": 1, "weight": 2, "id": 8030 },
                "Ankous": {"min": 50, "max": 90, "req": 1, "weight": 5, "id": 2514 },
                "Aviansies": {"min": 120, "max": 185, "req": 1, "weight": 6, "id": 3169 }, # (Requires Watch The Birdy for 80 slayer points)
                "Basilisks": {"min": 120, "max": 180, "req": 40, "weight": 6, "id": 9293 }, # (Requires Basilocked for 80 slayer points)
                "Black Demons": {"min": 120, "max": 185, "req": 1, "weight": 9, "id": 240 },
                "Black Dragons": {"min": 10, "max": 20, "req": 1, "weight": 6, "id": 252 },
                "Bloodvelds": {"min": 120, "max": 185, "req": 50, "weight": 9, "id": 484 },
                "Blue Dragons": {"min": 120, "max": 185, "req": 1, "weight": 4, "id": 265 },
                "Brine Rat": {"min": 120, "max": 185, "req": 47, "weight": 3, "id": 4501 },
                "Cave Horror": {"min": 120, "max": 180, "req": 58, "weight": 5, "id": 1047 },
                "Cave Kraken": {"min": 100, "max": 120, "req": 87, "weight": 6, "id": 492 },
                "Dagannoth": {"min": 120, "max": 185, "req": 1, "weight": 8, "id": 140 },
                "Dark Beast": {"min": 10, "max": 20, "req": 90, "weight": 5, "id": 4005 },
                "Drakes": {"min": 30, "max": 95, "req": 84, "weight": 7, "id": 8612 },
                "Elves": {"min": 60, "max": 90, "req": 1, "weight": 4, "id": 5293 },
                "Fire Giants": {"min": 120, "max": 185, "req": 1, "weight": 9, "id": 2075 },
                "Fossil Island Wyverns": {"min": 20, "max": 60, "req": 60, "weight": 5, "id": 7794 },
                "Gargoyles": {"min": 120, "max": 185, "req": 75, "weight": 6, "id": 412 },
                "Greater Demons": {"min": 120, "max": 185, "req": 1, "weight": 7, "id": 2025 },
                "Hellhounds": {"min": 120, "max": 185, "req": 1, "weight": 8, "id": 104 },
                "Iron Dragons": {"min": 30, "max": 60, "req": 1, "weight": 5, "id": 272 },
                "Kalphites": {"min": 120, "max": 185, "req": 1, "weight": 9, "id": 138 },
                "Kurasks": {"min": 120, "max": 185, "req": 70, "weight": 3, "id": 410 },
                "Lizardmen": {"min": 90, "max": 120, "req": 1, "weight": 8, "id": 6766 }, # (Requires Got Ripped for 75 slayer points)
                "Minions of Scabaras ": {"min": 30, "max": 60, "req": 1, "weight": 4, "id": 794 },
                "Mithril Dragons": {"min": 4, "max": 9, "req": 1, "weight": 4, "id": 2919 },  # (Requires I Hope you mith me for 80 slayer points)
                "Mutated Zygomites": {"min": 10, "max": 25, "req": 57, "weight": 2, "id": 537 },
                "Nechryael": {"min": 110, "max":170, "req": 80, "weight": 7, "id": 8 },
                "Red Dragons": {"min": 30, "max": 80, "req": 1, "weight": 5, "id": 247 }, # ( Requires seeing red for 50 slayer points)
                "Rune Dragons": {"min": 3, "max": 6, "req": 1, "weight": 2, "id": 8031 },
                "Skeletal Wyverns": {"min": 5, "max": 15, "req": 72, "weight": 5, "id": 465 },
                "Smoke Devils": {"min": 120, "max": 185, "req": 93, "weight": 7, "id": 498 },
                "Spiritual Creatures": {"min": 120, "max": 185, "req": 63, "weight": 6, "id": 2212 },
                "Steel Dragons": {"min": 30, "max": 60, "req": 1, "weight": 5, "id": 274 },
                "Suqah": {"min": 120, "max": 185, "req": 1, "weight": 8, "id": 787 },
                "Trolls": {"min": 120, "max": 185, "req": 1, "weight": 6, "id": 648 },
                "Turoths": {"min": 120, "max": 185, "req": 55, "weight": 3, "id": 426 },
                "Tzhaar": {"min": 110, "max": 180, "req": 1, "weight": 10, "id": 2173 }, # (Requires Hot Stuff for 100 slayer points)
                "Wyrms": {"min": 80, "max": 145, "req": 62, "weight": 7, "id": 8610 }
            },
            "points": 12
        },
        "duradel": {
            "req": 100,
            "tasks": {
                "Aberrant Spectres": {"min": 130, "max": 200, "req": 60, "weight": 7, "id": 2 },
                "Abyssal Demons": {"min": 130, "max": 200, "req": 85, "weight": 12, "id": 415 },
                "Adamant Dragons": {"min": 4, "max": 9, "req": 1, "weight": 2, "id": 8030 },
                "Ankou": {"min": 50, "max": 80, "req": 1, "weight": 5, "id": 2514 },
                "Aviansies": {"min": 120, "max": 200, "req": 1, "weight": 8, "id": 3169 },
                "Basilisk": {"min": 130, "max": 200, "req": 40, "weight": 7, "id": 9293 },
                "Black Demons": {"min": 130, "max": 200, "req": 1, "weight": 8, "id": 240 },
                "Black Dragons": {"min": 10, "max": 20, "req": 1, "weight": 9, "id": 252 },
                "Bloodvelds": {"min": 130, "max": 200, "req": 50, "weight": 8, "id": 484 },
                "Blue Dragons": {"min": 110, "max": 170, "req": 1, "weight": 4, "id": 265 },
                "Cave Horrors": {"min": 130, "max": 200, "req": 58, "weight": 4, "id": 1047 },
                "Cave Kraken": {"min": 120, "max": 150, "req": 87, "weight": 9, "id": 492 },
                "Dagannoth": {"min": 130, "max": 200, "req": 1, "weight": 9, "id": 970 },
                "Dark Beats": {"min": 10, "max": 20, "req": 90, "weight": 11, "id": 4005 },
                "Drakes": {"min": 50, "max": 110, "req": 84, "weight": 8, "id": 8612 },
                "Dust Devils": {"min": 130, "max": 200, "req": 65, "weight": 5, "id": 423 },
                "Elves": {"min": 100, "max": 170, "req": 1, "weight": 4, "id": 5293 },
                "Fire Giants": {"min": 130, "max": 200, "req": 1, "weight": 7, "id": 2075 },
                "Fossil Island Wyverns": {"min": 20, "max": 60, "req": 66, "weight": 5, "id": 7794 },
                "Gargoyles": {"min": 130, "max": 200, "req": 1, "weight": 8, "id": 412 },
                "Greater Demons": {"min": 130, "max": 200, "req": 1, "weight": 9, "id": 2025 },
                "Hellhounds": {"min": 130, "max": 200, "req": 1, "weight": 10, "id": 104 },
                "Iron Dragons": {"min": 40, "max": 60, "req": 1, "weight": 5, "id": 272 },
                "Kalphites": {"min": 130, "max": 200, "req": 1, "weight": 9, "id": 959 },
                "Kurask": {"min":  130, "max": 200, "req": 70, "weight": 4, "id": 410 },
                "Lizardman": {"min": 130, "max": 210, "req": 1, "weight": 10, "id": 6766 },
                "Mithril Dragons": {"min": 5, "max": 10, "req": 1, "weight": 9, "id": 2919 },
                "Mutated Zygomites": {"min": 20, "max": 30, "req": 57, "weight": 2, "id": 537 },
                "Nechryael": {"min": 130, "max": 250, "req": 8, "weight": 9, "id": 8 },
                "Red Dragons": {"min": 30, "max": 60, "req": 1, "weight": 8, "id": 247 },
                "Rune Dragons": {"min":3, "max": 8, "req": 1, "weight": 2, "id": 8031 },
                "Skeletal Wyverns": {"min": 20, "max": 40, "req": 72, "weight": 7, "id": 465 },
                "Smoke Devils": {"min": 130, "max": 200, "req": 93, "weight": 9, "id": 498 },
                "Spiritual Creatures": {"min": 130, "max": 200, "req": 63, "weight": 7, "id": 2212 },
                "Steel Dragons": {"min": 10, "max": 20, "req": 1, "weight": 7, "id": 274 },
                "Suqah": {"min": 60, "max": 90, "req": 1, "weight": 8, "id": 787 },
                "Trolls": {"min": 130, "max": 200, "req": 1, "weight": 6, "id": 648 },
                "TzHaar": {"min": 130, "max": 199, "req": 1, "weight": 10, "id": 2173 },
                "Waterfiends": {"min": 130, "max": 200, "req": 1, "weight": 2, "id": 2916 },
                "Wyrms": {"min": 100, "max": 160, "req": 62, "weight": 8, "id": 8610 }
            },
            "points": 15
        },
        "krystilia": {
            "req": 1,
            "tasks": { # https://www.osrsbox.com/tools/npc-search/
                "Ankou": {"min": 50, "max": 80, "req": 1, "weight": 6, "id": 2514 },
                "Aviansies": {"min": 120, "max": 200, "req": 1, "weight": 7, "id": 3169 },
                "Bandits": {"min": 75, "max": 125, "req": 1, "weight": 4, "id": 526 },
                "Bear": {"min": 50, "max": 100, "req": 1, "weight": 6, "id": 2838 },
                "Black Demons": {"min": 100, "max": 150, "req": 1, "weight": 7, "id": 240 },
                "Black Dragons": {"min": 5, "max": 20, "req": 1, "weight": 4, "id": 252 },
                "Chaos Druid": {"min": 50, "max": 85, "req": 1, "weight": 5, "id": 2878 },
                "Dark Warrior": {"min": 70, "max": 145, "req": 1, "weight": 4, "id": 6606 },
                "Earth Warrior": {"min": 75, "max": 130, "req": 1, "weight": 6, "id": 2840 },
                "Ent": {"min": 35, "max": 60, "req": 1, "weight": 5, "id": 7234 },
                "Fire Giants": {"min": 100, "max": 150, "req": 1, "weight": 7, "id": 2075 },
                "Greater Demons": {"min": 100, "max": 150, "req": 1, "weight": 8, "id": 2025 },
                "Green Dragons": {"min": 60, "max": 100, "req": 1, "weight": 4, "id": 260 },
                "Hellhounds": {"min": 70, "max": 123, "req": 1, "weight": 7, "id": 104 },
                "Ice Giant": {"min": 100, "max": 160, "req": 1, "weight": 6, "id": 2085 },
                "Ice Warrior": {"min": 100, "max": 150, "req": 1, "weight": 7, "id": 2841 },
                "Lava Dragon": {"min": 35, "max": 60, "req": 1, "weight": 3, "id": 6593 },
                "Lesser Demon": {"min": 80, "max": 120, "req": 1, "weight": 6, "id": 2005 },
                "Magic Axe": {"min": 70, "max": 125, "req": 1, "weight": 7, "id": 2844 },
                "Mammoth": {"min": 75, "max": 125, "req": 1, "weight": 6, "id": 2850 },
                "Revenant": {"min": 40, "max": 100, "req": 1, "weight": 5, "id": 7881 },
                "Rogue": {"min": 75, "max": 125, "req": 1, "weight": 5, "id": 2884 },
                "Scorpion": {"min": 60, "max": 100, "req": 1, "weight": 6, "id": 2479 },
                "Skeleton": {"min": 60, "max": 100, "req": 1, "weight": 5, "id": 70 },
                "Spider": {"min": 60, "max": 100, "req": 1, "weight": 6, "id": 2478 },
                "Spirital Creatures": {"min": 100, "max": 150, "req": 1, "weight": 6, "id": 2212 }
            },
            "points": 25
        }
    }

    all_db_monsters = monsters_api.load()

    async def getCurrentSlayerMaster(self, userId):
        sql = F"""SELECT
        slayer_master
        FROM user_skills
        WHERE user_id = {userId}
        """
        # List element containing the user's slayer experience
        master = None

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
            print("SOME ERROR 34567", error)
        finally:
            if conn is not None:
                conn.close()

        master = row[0]
        return master

    # Returns a list object for [monsterID, count]
    async def getCurrentSlayerTask(self, userId):
        sql = F"""SELECT
        slayer_task,
        slayer_monster_count
        FROM user_skills
        WHERE user_id = {userId}
        """

        # List element containing the user's slayer experience
        task = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            for row in data:
                task = row
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 311", error)
        finally:
            if conn is not None:
                conn.close()
        return task

    async def setSlayerMaster(self, ctx, master):

        masterName = master.lower().capitalize()
        currentTask = await self.getCurrentSlayerTask(ctx.author.id)
        if currentTask[1] != 0:
            await ctx.send("You cannot switch slayer masters in the middle of a task.")
            return
        else:
            sql = F"""
            UPDATE user_skills
            SET slayer_master = '{master.lower()}'
            WHERE user_id = {ctx.author.id}
            """

            # List element containing the user's slayer experience
            master = None

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 69", error)
            finally:
                if conn is not None:
                    conn.close()
                await ctx.send(f"You are now receiving tasks from {masterName}.")

    async def getNewTask(self, userId):

        # Get current master and slayer level
        currentMaster = await self.getCurrentSlayerMaster(userId)
        currentLevel = await Skilling(self.bot).getLevel(userId, 'slayer')

        taskId = None
        count = None

        # Roll to find a task that the user has the slayer level for
        ticker = 0
        while taskId == None and ticker < 1000:
            ticker = ticker + 1

            rolledTask = random.choice(list(self.slayerMasters[currentMaster]["tasks"]))

            if currentLevel >= self.slayerMasters[currentMaster]["tasks"][rolledTask]["req"]:
                taskId = self.slayerMasters[currentMaster]["tasks"][rolledTask]["id"]
                taskInfo = self.slayerMasters[currentMaster]["tasks"][rolledTask]
                count = randint(self.slayerMasters[currentMaster]["tasks"][rolledTask]["min"],self.slayerMasters[currentMaster]["tasks"][rolledTask]["max"])
                break

        sql = f"""
        UPDATE user_skills
        SET slayer_task = {taskId}, slayer_monster_count = {count}
        WHERE user_id = {userId}
        """

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error beginning task", error)
        finally:
            if conn is not None:
                conn.close()

        return [taskId, count]

    async def killMonsters(self, ctx, monsterId, amountLeft):

        taskMonster = None
        for monster in self.all_db_monsters:
            if monster.id == monsterId:
                taskMonster = monster
                break

        # Returns an [item, rate] list that can be rolled to receive an item.
        def rollForItem(monsterId, numRolls):

            roll = None
            if monsterId == 423 or monsterId == 498: # Dust devils and smoke devils
                roll = ['face_mask', 1/256, '1%']
            elif monsterId == 2: # Aberrant spectres
                roll = ['nose_peg', 1/256, '1%']
            elif monsterId == 476: # Wall beasts
                roll = ['spiny_helm', 1/256, '1%']
            elif monsterId == 414: # Banshees
                roll = ['earmuffs', 1/256, '1%']
            elif monsterId == 458: # Lizards
                roll = ['ice_cooler', 1/256, '1%']
            elif monsterId == 421: # Rockslugs
                roll = ['bag_of_salt', 1/256, '1%']
            elif monsterId == 1047: # Cave horrors
                # Roll up to 6. If greater than 1, roll for witchwood icon. If less than 1, roll for black mask
                rand = randint(0, 5)
                if rand > 1:
                    roll = ['witchwood_icon', 4/512, '1%'] # Multiply 2/512 by 2 since it's 2/3 up above
                else:
                    roll = ['black_mask', 3/512, '10%'] # Multiply by 1/512 by 3 since it's 1/3 up above
            elif monsterId == 2478: # Spiders
                roll = ['slayer_gloves', 1/256, '1%']
            elif monsterId == 469: # Killerwatts
                roll = ['insulated_boots', 1/256, '1%']
            elif monsterId == 537: # Zygomites
                roll = ['fungicide', 1/256, '1%']
            elif monsterId == 426 or monsterId == 410: # Turoths and kurasks
                if monsterId == 426:
                    roll = ['leaf_bladed_sword', 1/442, '2.5%']
                elif monsterId == 410:
                    rand = randint(0, 5)
                    if rand > 1:
                        roll = ['leaf_bladed_sword', 2/442, '2.5%']
                    else:
                        roll = ['leaf_bladed_battleaxe', 3/1026, '2.5%']
            elif monsterId == 412: # Gargoyles
                roll = ['rock_hammer', 1/256, '2.5%']
            elif monsterId == 419 or monsterId == 9293: # Cockatrices, Basilisks
                roll = ['mirror_shield', 1/256, '2.5%']
            elif monsterId == 415: # Abyssal demons
                roll = ['abyssal_whip', 1/512, '5%']

            success = False
            if roll != None:
                for n in range(0, numRolls):
                    lootRoll = randint(0, math.floor(1/roll[1]))
                    if lootRoll == 0:
                        success = True
                        break

                return [roll[0], success, roll[2]]
            else:
                return None

        async def addTripTime(ctx, partTime):

            sql = f"""
            UPDATE user_skills
            SET finishtime = {time.time() + partTime}, currently_slaying = TRUE
            WHERE user_id = {ctx.author.id}
            """
            conn = None
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 90", error)
            finally:
                if conn is not None:
                    conn.close()

        async def getAttackStyle(userId):
            sql = f"""
            SELECT
            attack_style
            FROM user_skills
            WHERE user_id = {userId}
            """

            attack_style = 1
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                data = cur.fetchall()
                for row in data:
                    attack_style = row[0]
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 90", error)
            finally:
                if conn is not None:
                    conn.close()

            return attack_style

        # Calculate the DPS for the task based on user levels and monster defence
        async def calculateDPS(userId, monsterId):
            attack = await Skilling(self.bot).getLevel(userId, 'attack')
            strength = await Skilling(self.bot).getLevel(userId, 'strength')
            defence = await Skilling(self.bot).getLevel(userId, 'defence')
            hitpoints = await Skilling(self.bot).getLevel(userId, 'hitpoints')
            ranged = await Skilling(self.bot).getLevel(userId, 'ranged')
            magic = await Skilling(self.bot).getLevel(userId, 'magic')
            prayer = await Skilling(self.bot).getLevel(userId, 'prayer')

            taskMonster = None
            for monster in self.all_db_monsters:
                if monster.id == monsterId:
                    taskMonster = monster

            # Give an equipment bonus depending on the attack level of the player
            # Uses scimitars for reference
            equipment_bonus = 0
            if attack < 5:
                equipment_bonus = 9
            elif attack < 10:
                equipment_bonus = 14
            elif attack < 20:
                equipment_bonus = 14
            elif attack < 30:
                equipment_bonus = 20
            elif attack < 40:
                equipment_bonus = 28
            elif attack < 60:
                equipment_bonus = 44
            elif attack >= 60:
                equipment_bonus = 66

            effective_strength_level = strength + 8

            max_hit = 0.5 + effective_strength_level * (equipment_bonus + 64) / 640

            # Calculate attack bonus depending on attack level
            # Uses scimitars for reference
            attack_bonus = 0
            if attack < 5:
                equipment_bonus = 10
            elif attack < 10:
                equipment_bonus = 15
            elif attack < 20:
                equipment_bonus = 19
            elif attack < 30:
                equipment_bonus = 21
            elif attack < 40:
                equipment_bonus = 29
            elif attack < 60:
                equipment_bonus = 45
            elif attack >= 60:
                equipment_bonus = 67

            effective_attack_level = attack + 8

            max_attack_roll = effective_attack_level * (attack_bonus + 64)

            effective_monster_defence = taskMonster.defence_level + 9

            effective_monster_equipment_bonus = taskMonster.defence_slash

            max_defence_roll = effective_monster_defence * (effective_monster_equipment_bonus + 64)

            hit_chance = 0

            if max_attack_roll > max_defence_roll:
                hit_chance = 1 - (max_defence_roll + 2) / (2 * (max_attack_roll + 1))
            else:
                hit_chance = max_attack_roll / (2 * max_defence_roll + 1)

            currentStyle = await getAttackStyle(userId)

            if currentStyle == 'attack' or currentStyle == 'strength' or currentStyle == 'defence':
                # Give an equipment bonus depending on the attack level of the player
                # Uses scimitars for reference
                equipment_bonus = 0
                if attack < 5:
                    equipment_bonus = 9
                elif attack < 10:
                    equipment_bonus = 14
                elif attack < 20:
                    equipment_bonus = 14
                elif attack < 30:
                    equipment_bonus = 20
                elif attack < 40:
                    equipment_bonus = 28
                elif attack < 60:
                    equipment_bonus = 44
                elif attack >= 60:
                    equipment_bonus = 66

                effective_strength_level = strength + 8

                max_hit = 0.5 + effective_strength_level * (equipment_bonus + 64) / 640

                # Calculate attack bonus depending on attack level
                # Uses scimitars for reference
                attack_bonus = 0
                if attack < 5:
                    equipment_bonus = 10
                elif attack < 10:
                    equipment_bonus = 15
                elif attack < 20:
                    equipment_bonus = 19
                elif attack < 30:
                    equipment_bonus = 21
                elif attack < 40:
                    equipment_bonus = 29
                elif attack < 60:
                    equipment_bonus = 45
                elif attack >= 60:
                    equipment_bonus = 67

                effective_attack_level = attack + 8

                max_attack_roll = effective_attack_level * (attack_bonus + 64)

                effective_monster_defence = taskMonster.defence_level + 9

                effective_monster_equipment_bonus = taskMonster.defence_slash

                max_defence_roll = effective_monster_defence * (effective_monster_equipment_bonus + 64)

                hit_chance = 0

                if max_attack_roll > max_defence_roll:
                    hit_chance = 1 - (max_defence_roll + 2) / (2 * (max_attack_roll + 1))
                else:
                    hit_chance = max_attack_roll / (2 * max_defence_roll + 1)

                dps = hit_chance * (max_hit/2) / 2.4

                return dps

            elif currentStyle == 'ranged':

                rangedStrength = 4
                equipment = 0
                interval = 1.2

                if ranged < 5: # Iron knives
                    rangedStrength = 4
                    equipment = 30
                elif ranged < 10: # Steel knives
                    rangedStrength = 7
                    equipment = 35
                elif ranged < 20: # Black knives
                    rangedStrength = 8
                    equipment = 40
                elif ranged < 30: # Mithril knives
                    rangedStrength = 10
                    equipment = 45
                elif ranged < 40: # Adamant knives
                    rangedStrength = 14
                    equipment = 50
                elif ranged < 50: # Rune knives
                    rangedStrength = 24
                    equipment = 70
                elif ranged < 60: # Magic shortbow, blue d'hide
                    rangedStrength = 49
                    equipment = 124
                    interval = 2.4
                elif ranged < 70: # Magic shortbow, red d'hide
                    rangedStrength = 49
                    equipment = 129
                    interval = 2.4
                elif ranged < 75: # Magic shortbow, black d'hide
                    rangedStrength = 49
                    equipment = 134
                    interval = 2.4
                elif ranged < 85: # Blowpipe with adamant darts
                    rangedStrength = 50
                    equipment = 145
                    interval = 1.2
                elif ranged < 91: # Blowpipe with rune darts
                    rangedStrength = 54
                    equipment = 149
                    interval = 1.2
                elif ranged < 97: # Blowpipe with dragon darts
                    rangedStrength = 60
                    equipment = 153
                    interval = 1.2


                max_hit = 1.3 + (ranged/10) + (rangedStrength/80) + ((ranged * rangedStrength)/640)

                average_hit = max_hit/2
                max_attack_roll = ranged * (equipment + 64)
                max_defence_roll = (taskMonster.defence_level + 9) * (taskMonster.defence_ranged + 64)

                hit_chance = 0

                if max_attack_roll > max_defence_roll:
                    hit_chance = 1 - (defence + 2) / (2 * (ranged + 1))
                else:
                    hit_chance = ranged / (2 * defence + 1)

                dps = hit_chance * average_hit / interval

                if dps < 0.25:
                    dps = dps + 0.125

                return dps

        # Calculate the user's damage % modifier
        async def calculateModifier(userId):
            sql = f"""
            SELECT
            face_mask,
            nose_peg,
            spiny_helm,
            earmuffs,
            ice_cooler,
            bag_of_salt,
            witchwood_icon,
            insulated_boots,
            fungicide,
            slayer_gloves,
            leaf_bladed_sword,
            leaf_bladed_battleaxe,
            rock_hammer,
            mirror_shield,
            fire_cape,
            abyssal_whip,
            black_mask,
            slayer_helmet
            FROM user_skills
            WHERE user_id = {userId}
            """

            boostData = None

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                data = cur.fetchall()
                for row in data:
                    boostData = row
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error fetching slayer items", error)
            finally:
                if conn is not None:
                    conn.close()

            multiplier = 1
            # Low items (spiny helm, ear muffs, etc)
            for n in range(0, 10):
                if boostData[n] == True:
                    multiplier = multiplier * 1.01

            # Leaf bladed sword, battleaxe, rock hammer, and mirror shield
            for n in range(10, 14):
                if boostData[n] == True:
                    multiplier = multiplier * 1.025

            # Fire cape and abyssal whip
            for n in range(14, 16):
                if boostData[n] == True:
                    multiplier = multiplier * 1.05

            # Black mask and slayer helmet
            for n in range(16, 18):
                if boostData[n] == True:
                    multiplier = multiplier * 1.05

            async def calculatePrayerModifier(userId):
                prayer_level = await Skilling(self.bot).getLevel(userId, 'prayer')

                modifier = 1 + (prayer_level/198)

                if prayer_level == 99:
                    modifier = modifier + 0.1

                return modifier

            async def calculateHerbloreModifier(userId):
                herblore_level = await Skilling(self.bot).getLevel(userId, 'herblore')


                modifier = 1

                if herblore_level < 3: # None
                    modifier = 1
                elif herblore_level < 12: # Attack
                    modifier = 1.01
                elif herblore_level < 30: # Strength
                    modifier = 1.02
                elif herblore_level < 38: # Defence
                    modifier = 1.05
                elif herblore_level < 45: # Prayer
                    modifier = 1.1
                elif herblore_level < 55: # Super attack
                    modifier = 1.2
                elif herblore_level < 63: # Super strength
                    modifier = 1.3
                elif herblore_level < 66: # Super restore
                    modifier = 1.4
                elif herblore_level < 70: # Super def
                    modifier = 1.5
                elif herblore_level < 81: # Divine combat
                    modifier = 1.6
                elif herblore_level < 90: # Brew
                    modifier = 1.7
                elif herblore_level < 97: # Super combat
                    modifier = 1.8
                elif herblore_level < 99: # Divine super combat
                    modifier = 1.9
                elif herblore_level == 99: # User has 99
                    modifier = 2.0

                return modifier

            prayerMultiplier = await calculatePrayerModifier(ctx.author.id)
            herbloreMultiplier = await calculateHerbloreModifier(ctx.author.id)

            return multiplier * prayerMultiplier * herbloreMultiplier

        async def removeFromTask(userId, numberKilled):

            sql = f"""
            UPDATE user_skills
            SET slayer_monster_count = slayer_monster_count - {numberKilled}
            WHERE user_id = {userId}
            """

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 90", error)
            finally:
                if conn is not None:
                    conn.close()

            return

        async def giveSlayerPoints(userId, points):
            sql = f"""
            UPDATE user_skills
            SET slayer_points = slayer_points + {points}, slayer_task_total = slayer_task_total + 1
            WHERE user_id = {userId}
            """
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 90", error)
            finally:
                if conn is not None:
                    conn.close()

        # Grab the attack style
        attackStyle = await getAttackStyle(ctx.author.id)

        # Calculate beginning level for the style being used, hitpoints, and slayer
        startCombat = await Skilling(self.bot).getLevel(ctx.author.id, attackStyle)
        startHitpoints = await Skilling(self.bot).getLevel(ctx.author.id, 'hitpoints')
        startSlayer = await Skilling(self.bot).getLevel(ctx.author.id, 'slayer')

        dps = await calculateDPS(ctx.author.id, monsterId)

        # Equiment modifier
        modifier = await calculateModifier(ctx.author.id)

        # Total damage dealt for the session
        totalDamage = dps * 1800 * modifier * 1.33

        # Maximum possible kills
        maxKills = math.floor(totalDamage/taskMonster.hitpoints)

        # Default to max kills...
        numberKilled = maxKills

        if numberKilled < 3:
            numberKilled = 3
            maxKills = 3

        taskMessage = f"You have **{amountLeft - numberKilled} {taskMonster.name}** left on your task."

        # But if the max amount of kills is greater than the amount left, just make it the amount left
        if maxKills > amountLeft:
            numberKilled = amountLeft

            # Get the current slayer master
            master = await self.getCurrentSlayerMaster(ctx.author.id)

            # Read the number of points they'll get
            points = self.slayerMasters[master]["points"]

            # Give slayer points
            await giveSlayerPoints(ctx.author.id, points)

            # If the user is getting points for their task, add it into the message.
            pointMessage = ""
            if points != 0:
                pointMessage = f"and gained **{points}** slayer points"

            taskMessage = f"You have finished your task {pointMessage}. Type *=slay task* to get a new one."
        print("Num", numberKilled/maxKills, 1800 * (numberKilled/maxKills))
        await addTripTime(ctx, math.floor(1800 * (numberKilled/maxKills)))

        # HERE BEGINS THE DATABASE WRITING STUFF

        await ctx.send(f"You begin slaying {taskMonster.name}s. You should return in about {math.ceil(30 * (numberKilled/maxKills))} minutes.")

        await asyncio.sleep(math.floor(1800 * (numberKilled/maxKills)))

        # Remove the monsters from the task monster count
        await removeFromTask(ctx.author.id, numberKilled)

        timeModifier = math.floor(amountLeft/maxKills * 1800)

        # Calculate experience for the player
        combatXP = numberKilled * taskMonster.hitpoints * 4
        commaCombatXP = "{:,d}".format(int(combatXP))
        hitpointsXP = numberKilled * taskMonster.hitpoints * 1.33
        commaHitpointsXP = "{:,d}".format(int(hitpointsXP))
        slayerXP = numberKilled * taskMonster.slayer_xp
        commaSlayerXP = "{:,d}".format(int(slayerXP))

        # End combat levels
        endCombat = await Skilling(self.bot).addExperienceToStat(ctx.author.id, attackStyle, combatXP)
        endHitpoints = await Skilling(self.bot).addExperienceToStat(ctx.author.id, 'hitpoints', hitpointsXP)
        endSlayer = await Skilling(self.bot).addExperienceToStat(ctx.author.id, 'slayer', slayerXP)

        # Level up message placeholders
        combatLevelUp = ""
        hitpointsLevelUp = ""
        slayerLevelUp = ""
        attackStyleCap = attackStyle.capitalize()

        # If the user levels up
        if endCombat > startCombat:
            combatLevelUp = f"You are now level {endCombat} {attackStyleCap}."
        if endHitpoints > startHitpoints:
            hitpointsLevelUp = f"You are now level {endHitpoints} Hitpoints."
        if endSlayer > startSlayer:
            slayerLevelUp = f"You are now level {endSlayer} Slayer."

        # The emoji corresponding to the attack style being used
        styleEmoji = None
        if attackStyle == 'attack':
            styleEmoji = ItemEmojis.Skills.attack
        elif attackStyle == 'strength':
            styleEmoji = ItemEmojis.Skills.strength
        elif attackStyle == 'defence':
            styleEmoji = ItemEmojis.Skills.defence
        elif attackStyle == 'ranged':
            styleEmoji = ItemEmojis.Skills.ranged

        itemMessage = ""

        # Roll to see if the user receives a unique slayer drop
        itemRoll = rollForItem(taskMonster.id, numberKilled)
        if itemRoll != None:
            if itemRoll[1] == True:
                async def checkForItem(item):
                    sql = f"""
                    SELECT
                    {item}
                    FROM user_skills
                    WHERE user_id = {ctx.author.id}
                    """
                    itemData = False
                    try:
                        conn = psycopg2.connect(DATABASE_URL)
                        cur = conn.cursor()
                        cur.execute(sql)
                        data = cur.fetchall()
                        for row in data:
                            itemData = row[0]
                        cur.close()
                        conn.commit()
                    except (Exception, psycopg2.DatabaseError) as error:
                        print("Error fetching slayer items", error)
                    finally:
                        if conn is not None:
                            conn.close()
                        return itemData

                async def giveItem(item):
                    sql = f"""
                    UPDATE user_skills
                    SET {item} = TRUE
                    WHERE user_id = {ctx.author.id}
                    """
                    itemData = False
                    try:
                        conn = psycopg2.connect(DATABASE_URL)
                        cur = conn.cursor()
                        cur.execute(sql)
                        cur.close()
                        conn.commit()
                    except (Exception, psycopg2.DatabaseError) as error:
                        print("Error fetching slayer items", error)
                    finally:
                        if conn is not None:
                            conn.close()

                # Check to see if the user has the item
                hasItem = await checkForItem(itemRoll[0])
                if hasItem == False:
                    itemName = itemRoll[0].capitalize().replace('_', ' ')
                    sqlColumn = itemRoll[0]

                    # Give the user the item
                    await giveItem(sqlColumn)

                    # Update the item message
                    itemMessage = f"You have received **{itemName}** as a drop, granting a permanent **{itemRoll[2]}** boost to damage."


        message = f"{ItemEmojis.Skills.slayer} {ctx.author.mention} you have killed **{numberKilled} {taskMonster.name}**.{taskMessage}\nYou have gained:\n{commaCombatXP} {attackStyle.capitalize()} XP {styleEmoji} {combatLevelUp}\n{commaHitpointsXP} Hitpoints XP {ItemEmojis.Skills.hitpoints} {hitpointsLevelUp}\n{commaSlayerXP} Slayer XP {ItemEmojis.Skills.slayer} {slayerLevelUp}\n\n{itemMessage}"

        # Send a message with task info
        await ctx.send(message)

        async def endTrip(ctx):
            sql = f"""
            UPDATE user_skills
            SET currently_slaying = FALSE
            WHERE user_id = {ctx.author.id}
            """
            conn = None
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 76", error)
            finally:
                if conn is not None:
                    conn.close()

        await endTrip(ctx)

    async def getSlayerPoints(self, ctx):
        sql = f"""
        SELECT
        slayer_points
        FROM user_skills
        WHERE user_id = {ctx.author.id}
        """

        points = None

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            for row in data:
                points = row[0]
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 34567", error)
        finally:
            if conn is not None:
                conn.close()
            return points

    async def cancelTask(self, ctx):
        sql = f"""
        UPDATE user_skills
        SET slayer_task = 0, slayer_monster_count = 0, currently_slaying = false, slayer_points = slayer_points - 30
        WHERE user_id = {ctx.author.id}
        """

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(sql)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("SOME ERROR 1923", error)
            return
        finally:
            if conn is not None:
                conn.close()
            await ctx.send("You have cancelled your slayer task. Type `=slay task` to get a new one")
            return

    @commands.command()
    async def slay(self, ctx, *args):

        async def calculateModifier(userId):
            sql = f"""
            SELECT
            face_mask,
            nose_peg,
            spiny_helm,
            earmuffs,
            ice_cooler,
            bag_of_salt,
            witchwood_icon,
            insulated_boots,
            fungicide,
            slayer_gloves,
            leaf_bladed_sword,
            leaf_bladed_battleaxe,
            rock_hammer,
            mirror_shield,
            fire_cape,
            abyssal_whip,
            black_mask,
            slayer_helmet
            FROM user_skills
            WHERE user_id = {userId}
            """

            boostData = None

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                data = cur.fetchall()
                for row in data:
                    boostData = row
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error fetching slayer items", error)
            finally:
                if conn is not None:
                    conn.close()

            multiplier = 1
            # Low items (spiny helm, ear muffs, etc)
            for n in range(0, 10):
                if boostData[n] == True:
                    multiplier = multiplier + 0.01

            # Leaf bladed sword, battleaxe, rock hammer, and mirror shield
            for n in range(10, 14):
                if boostData[n] == True:
                    multiplier = multiplier + 0.025

            # Fire cape and abyssal whip
            for n in range(14, 16):
                if boostData[n] == True:
                    multiplier = multiplier + 0.05

            # Black mask and slayer helmet
            for n in range(16, 18):
                if boostData[n] == True:
                    multiplier = multiplier + 0.10

            return [boostData, multiplier]

        async def checkIfActive(ctx):
            sql = f"""
            SELECT
            currently_slaying
            FROM user_skills
            WHERE user_id = {ctx.author.id}
            """

            status = None
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                data = cur.fetchall()
                for item in data:
                    status = item[0]
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 9001", error)
            finally:
                if conn is not None:
                    conn.close()
                return status

        async def checkTripTime(ctx):

            sql = f"""
            SELECT
            finishtime
            FROM user_skills
            WHERE user_id = {ctx.author.id}
            """

            conn = None
            activityInfo = None

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall()
                for row in rows:
                    activityInfo = row
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("SOME ERROR 90", error)
            finally:
                if conn is not None:
                    conn.close()
            if row[0] == None:
                return time.time()
            else:
                return row[0]

        await Skilling(self.bot).createSkillTable(ctx.author.id)

        if len(args) == 0:
            # Kill monster on task
            task = await self.getCurrentSlayerTask(ctx.author.id)

            # User does not have a task currently/has finished their last task
            if task[1] <= 0:
                await ctx.send("You do not have a task. Type *=slay task* to get a new task.")
                return
            else:

                status = await checkIfActive(ctx)

                if status == None:
                    await ctx.send("Something went wrong, please try again.")
                    return
                elif status == True:
                    finishTime = await checkTripTime(ctx)
                    timeDiff = finishTime - math.floor(time.time())
                    minutes = math.floor(timeDiff/60)
                    if minutes > 0:

                        await ctx.send(f"You are currently slaying. You will be done in about {minutes} minutes.")
                        return
                    else:
                        # Number of monsters
                        numLeft = task[1]

                        await self.killMonsters(ctx, task[0], task[1])

                elif status == False:
                    # Number of monsters
                    numLeft = task[1]

                    await self.killMonsters(ctx, task[0], task[1])

        elif args[0] == 'master':

            # If there was nothing else provided
            if len(args) == 1:
                currentMaster = await self.getCurrentSlayerMaster(ctx.author.id)
                await ctx.send(f"""Your current slayer master is **{currentMaster.capitalize()}**.\nTo switch masters, type *=slay master [name]*\nAvailable slayer masters:\n{ItemEmojis.SlayerMasters.turael} *Turael - 3+ combat\n{ItemEmojis.SlayerMasters.mazchna} Mazchna - 20+ combat\n{ItemEmojis.SlayerMasters.vannaka} Vannaka - 40+ combat\n{ItemEmojis.SlayerMasters.chaeldar} Chaeldar - 70+ combat\n{ItemEmojis.SlayerMasters.konar} Konar - 75+ combat\n{ItemEmojis.SlayerMasters.nieve} Nieve - 85+ combat\n{ItemEmojis.SlayerMasters.duradel} Duradel - 100+ combat*""")
                return

            #Translate the argument into key for slayerMasters dictionary
            choice = args[1].lower()

            # User has entered a valid slayer master
            if choice in self.slayerMasters:

                #Get the player's combat level
                combatLevel = await Skilling(self.bot).getCombatLevel(ctx.author.id)

                # If the user's combat level is not high enough
                if combatLevel < self.slayerMasters[choice]["req"]:
                    requirement = self.slayerMasters[choice]["req"]
                    choice = choice.capitalize()
                    await ctx.send(f"You need at least **{requirement} combat** to use {choice} as a slayer master. \nYou are currently **{combatLevel} combat**.")
                    return
                else:
                    # User has the combat requirement
                    choice = choice.capitalize()
                    await self.setSlayerMaster(ctx, choice)
                    return

            # If the user did not enter a valid slayer master
            else:
                # User did not enter a valid slayer master
                currentTask = await self.getCurrentSlayerTask(ctx.author.id)
                if currentTask[1] == 0:
                    currentMaster = await self.getCurrentSlayerMaster(ctx.author.id)

                    await ctx.send(f"""Please choose a valid slayer master.
                    {ItemEmojis.SlayerMasters.turael} *Turael - 3+ combat
                    {ItemEmojis.SlayerMasters.mazchna} Mazchna - 20+ combat
                    {ItemEmojis.SlayerMasters.vannaka} Vannaka - 40+ combat
                    {ItemEmojis.SlayerMasters.chaeldar} Chaeldar - 70+ combat
                    {ItemEmojis.SlayerMasters.konar} Konar - 75+ combat
                    {ItemEmojis.SlayerMasters.nieve} Nieve - 85+ combat
                    {ItemEmojis.SlayerMasters.duradel} Duradel - 100+ combat

                    Your current slayer master is **{currentMaster}**""")
                    return
                else:
                    # Prevent switching masters in the middle of a task
                    await ctx.send("You cannot switch slayer masters in the middle of a task.")
                    return

        elif args[0] == 'task':
            task = await self.getCurrentSlayerTask(ctx.author.id)

            # If the player has nothing left in their current task, give em' a new one
            if task[1] <= 0:
                newTask = await self.getNewTask(ctx.author.id)
                name = None

                for monster in self.all_db_monsters:
                    if monster.id == newTask[0]:
                        name = monster.name
                        break

                await ctx.send(f"You have been assigned to kill **{newTask[1]} {name}**. Type *=slay* to begin your task.")


            # If they already have a task
            else:
                name = None
                for monster in self.all_db_monsters:

                    if monster.id == task[0]:
                        name = monster.name
                        break

                await ctx.send(f"You already have a task. You have **{task[1]} {name}** left.")

        elif args[0] == 'info':
            embed = discord.Embed(title=f"Slayer information", color=discord.Color.dark_red())
            embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/2/28/Slayer_icon.png?cd34f')

            description = f"""**=slay task** - pick up a new slayer task
            **=slay** - kill monsters in current task
            **=slay cancel** - cancels current task, (cannot cancel once task is accepted via =slay)
            **=slay points** - displays users current points
            **=slay master** - view current slayer master
            **=slay master (new master)** - switch to a new slayer master. Requires appropriate combat level.
            **=switch (attack/strength/defence/ranged/magic)** - switch to training a different skill
            **=mystats** - view current stats
            **=buyherb** (GP amount) - buy {ItemEmojis.Skills.herblore} Herblore XP for 350 gp/xp
            **=buyherb info** - shows bonuses from Herblore
            **=buybones** (GP amount) - buy {ItemEmojis.Skills.prayer} Prayer XP for 200 gp/xp
            **=buybones info** - shows bonuses from Prayer
            """

            embed.add_field(name='\u200b', value="**Slayer - Get tasks, train stats**\n-Monsters will randomly drop items that upgrade your kills per hour\n-Training Herblore and Prayer increases kills per hour\n-Increasing your combat stats increases your kills per hour", inline=False)
            embed.add_field(name="Commands",value=description, inline=False)

            await ctx.send(embed=embed)

        elif args[0] == 'points':
            points = await self.getSlayerPoints(ctx)
            await ctx.send(f"{ItemEmojis.Skills.slayer} You have {points} slayer points.")
            return

        elif args[0] == 'cancel':
            points = await self.getSlayerPoints(ctx)

            status = await checkIfActive(ctx)

            if status == None:
                await ctx.send("Something went wrong, please try again.")
                return
            elif status == True:
                finishTime = await checkTripTime(ctx)
                timeDiff = finishTime - math.floor(time.time())
                minutes = math.floor(timeDiff/60)
                if minutes > 0:

                    await ctx.send(f"You cannot cancel a task while you are currently slaying. You will be done in about {minutes} minutes.")
                    return


        elif args[0] == 'items':

            boostInfo = await calculateModifier(ctx.author.id)

            modifier = boostInfo[1] - 1

            modifier = modifier * 100

            boostPercent = "{0:.2f}".format(modifier)

            ownedList = []

            for item in boostInfo[0]:
                if item == True:
                    ownedList.append('**')
                elif item == False:
                    ownedList.append('')

            one_percent = f"""{ItemEmojis.SlayerEquipment.faceMask} {ownedList[0]}Face mask{ownedList[0]}
            {ItemEmojis.SlayerEquipment.nosePeg} {ownedList[1]}Nose peg{ownedList[1]}
            {ItemEmojis.SlayerEquipment.spinyHelmet} {ownedList[2]}Spiny helmet{ownedList[2]}
            {ItemEmojis.SlayerEquipment.earmuffs} {ownedList[3]}Earmuffs{ownedList[3]}
            {ItemEmojis.SlayerEquipment.iceCooler} {ownedList[4]}Ice cooler{ownedList[4]}
            {ItemEmojis.SlayerEquipment.bagOfSalt} {ownedList[5]}Bag of salt{ownedList[5]}
            {ItemEmojis.SlayerEquipment.witchwoodIcon} {ownedList[6]}Witchwood icon{ownedList[6]}
            {ItemEmojis.SlayerEquipment.insulatedBoots} {ownedList[7]}Insulated boots{ownedList[7]}
            {ItemEmojis.SlayerEquipment.fungicide} {ownedList[8]}Fungicide{ownedList[8]}
            {ItemEmojis.SlayerEquipment.slayerGloves} {ownedList[9]}Slayer gloves{ownedList[9]}"""

            two_point_five_percent = f"""{ItemEmojis.SlayerEquipment.leafBladedSword} {ownedList[10]}Lead-bladed sword{ownedList[10]}
            {ItemEmojis.SlayerEquipment.leafBladedBattleaxe} {ownedList[11]}Leaf-bladed battleaxe{ownedList[11]}
            {ItemEmojis.SlayerEquipment.rockHammer} {ownedList[12]}Rock hammer{ownedList[12]}
            {ItemEmojis.SlayerEquipment.mirrorShield} {ownedList[13]}Mirror shield{ownedList[13]}"""

            five_percent = f"""{ItemEmojis.Misc.fireCape} {ownedList[14]}Fire cape{ownedList[14]}
            {ItemEmojis.SlayerItems.abyssalWhip} {ownedList[15]}Abyssal whip{ownedList[15]}"""

            ten_percent = f"""{ItemEmojis.SlayerEquipment.blackMask} {ownedList[16]}Black mask{ownedList[16]}
            {ItemEmojis.SlayerEquipment.slayerHelmet} {ownedList[17]}Slayer helmet{ownedList[17]}"""

            embed = discord.Embed(title="Slayer items", description=f"Total modifier: +{boostPercent}%", color=discord.Color.dark_red())
            embed.add_field(name='1% boost', value=one_percent, inline=True)
            embed.add_field(name='2.5% boost', value=two_point_five_percent, inline=True)
            embed.add_field(name = '\u200b', value = '\u200b', inline=True)
            embed.add_field(name='5% boost', value=five_percent, inline=True)
            embed.add_field(name='10% boost', value=ten_percent, inline=True)
            embed.add_field(name = '\u200b', value = '\u200b', inline=True)

            await ctx.send(embed=embed)
            return

    @commands.command()
    async def switch(self, ctx, style):

        await Skilling(self.bot).createSkillTable(ctx.author.id)

        styles = ["attack", "strength", "defence", "ranged", "magic"]

        if style in styles:
            sql = f"""
            UPDATE user_skills
            SET attack_style = '{style}'
            WHERE user_id = {ctx.author.id}
            """

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error beginning task", error)
            finally:
                if conn is not None:
                    conn.close()

                await ctx.send(f"You are now gaining {style.lower().capitalize()} xp.")
                return
        else:
            await ctx.send("You can only train Attack, Strength, Defence, Ranged and magic. ")
            return

    @switch.error
    async def switchError(self, ctx):
        await ctx.send("Proper syntax is *=switch [style]* \nYou can currently train Attack, Strength, Defence, Ranged and Magic.")

    @commands.command()
    async def mystats(self, ctx):

        await Skilling(self.bot).createSkillTable(ctx.author.id)

        
        combat = await Skilling(self.bot).getCombatLevel(ctx.author.id)
        attack = await Skilling(self.bot).getLevel(ctx.author.id, 'attack')
        strength = await Skilling(self.bot).getLevel(ctx.author.id, 'strength')
        defence = await Skilling(self.bot).getLevel(ctx.author.id, 'defence')
        hitpoints = await Skilling(self.bot).getLevel(ctx.author.id, 'hitpoints')
        ranged = await Skilling(self.bot).getLevel(ctx.author.id, 'ranged')
        magic = await Skilling(self.bot).getLevel(ctx.author.id, 'magic')
        herblore = await Skilling(self.bot).getLevel(ctx.author.id, 'herblore')
        prayer = await Skilling(self.bot).getLevel(ctx.author.id, 'prayer')
        slayer = await Skilling(self.bot).getLevel(ctx.author.id, 'slayer')

        skills_column_1 = f"""{ItemEmojis.Skills.hitpoints} {hitpoints}
        {ItemEmojis.Misc.combat} {combat}
        {ItemEmojis.Skills.attack} {attack}
        {ItemEmojis.Skills.strength} {strength}
        {ItemEmojis.Skills.defence} {defence}
        {ItemEmojis.Skills.ranged} {ranged}
        {ItemEmojis.Skills.magic} {magic}
        {ItemEmojis.Skills.prayer} {prayer}
        {ItemEmojis.Skills.herblore} {herblore}
        {ItemEmojis.Skills.slayer} {slayer}
        """

        embed = discord.Embed(title=f"DuelBot stats for {ctx.author.mention}", color=discord.Color.blurple())
        embed.set_thumbnail(url='https://oldschool.runescape.wiki/images/8/8c/HiScores_icon.png?99743')
        embed.add_field(name="\u200b", value=skills_column_1)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 60*120, commands.BucketType.user)
    async def fc(self, ctx):

        async def hasFirecape(ctx):
            sql = f"""
            SELECT
            fire_cape
            FROM user_skills
            WHERE user_id = {ctx.author.id}
            """

            # Defaults to true to stop the user from getting one
            hasFirecape = True

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                hasFirecape = cur.fetchall()
                for item in hasFirecape:
                    hasFirecape = item[0]
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error beginning task", error)
            finally:
                if conn is not None:
                    conn.close()

                return hasFirecape


        fc = await hasFirecape(ctx)

        if fc == True:
            await ctx.send(f"You already have a Fire cape {ItemEmojis.Misc.fireCape}")
            return

        hitpoints = await Skilling(self.bot).getLevel(ctx.author.id, 'hitpoints')
        prayer = await Skilling(self.bot).getLevel(ctx.author.id, 'prayer')
        herblore = await Skilling(self.bot).getLevel(ctx.author.id, 'herblore')
        ranged = await Skilling(self.bot).getLevel(ctx.author.id, 'ranged')

        cavesTime = 120

        await ctx.send(f"You step into the fight caves to take on the TzTok-Jad {ItemEmojis.Bosses.fightCaves} You should be done in about 120 minutes.")


        # Wait 2 hours
        await asyncio.sleep(60 * cavesTime)

        if hitpoints >= 70 and prayer >= 43 and herblore >= 72 and ranged >= 70:

            sql = f"""
            UPDATE user_skills
            SET fire_cape = TRUE
            WHERE user_id = {ctx.author.id}
            """

            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(sql)
                cur.close()
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error beginning task", error)
            finally:
                if conn is not None:
                    conn.close()

            # Only give them one firecape, lol. Don't want to spam them if they used .fc a bunch of times
            hasFCmidTrip = await hasFirecape(ctx)

            if hasFCmidTrip == False:
                await ctx.send(f"Congratulations {ctx.author.mention}, you have received a Fire cape {ItemEmojis.Misc.fireCape} giving you a permanent **10%** boost to DPS.")
                return

        else:
            await ctx.send(f"{ctx.author.mention} Oh no! You died to the TzTok-Jad {ItemEmojis.Bosses.fightCaves}. You NEED get 70 Ranged {ItemEmojis.Skills.ranged}, 70 Hitpoints {ItemEmojis.Skills.hitpoints}, 72 Herblore {ItemEmojis.Skills.herblore}, and 43 Prayer {ItemEmojis.Skills.prayer} if you want to complete the Fight Caves.")
            return

    @fc.error
    async def fcError(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You are already in the Fight Caves. There are {math.ceil(error.retry_after / 60)} minutes left in your attempt.")



def setup(bot):
    bot.add_cog(Slayer(bot))
