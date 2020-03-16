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

class ItemEmojis(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    class Rares:
        redPartyhat = '<:redpartyhat:687877056368869409>'
        yellowPartyhat = '<:yellowpartyhat:687877070994276433>'
        bluePartyhat = '<:bluepartyhat:687877007039791380>'
        greenPartyhat = '<:greenpartyhat:687876980682522624>'
        whitePartyhat = '<:whitepartyhat:687877084403859478>'
        purplePartyhat = '<:purplepartyhat:687877097884221485>'

        christmasCracker = '<:christmascracker:687877155253911555>'

        greenHween = '<:greenhalloweenmask:687877031727464516>'
        redHween = '<:redhalloweenmask:687877056301891727>'
        blueHween = '<:bluehalloweenmask:687877007085666304>'

        santaHat = '<:santahat:687877228507168788>'

        easterEgg = '<:easteregg:687877187164307467>'
        pumpkin = '<:pumpkin:687877207846027265>'

    class Barrows:
        ahrimsHood = '<:ahrimshood:687939117358645291>'
        ahrimsRobeskirt = '<:ahrimsrobeskirt:687939117459439653>'
        ahrimsRobetop = '<:ahrimsrobetop:687939117622886430>'
        ahrimsStaff = '<:ahrimsstaff:687939117673086997>'

        guthansHelm = '<:guthanshelm:687939118583513142>'
        guthansWarpear = '<:guthanswarspear:687939118151237653>'
        guthansPlatebody = '<:guthansplatebody:687939117665091586>'
        guthansChainskirt = '<:guthanschainskirt:687939117648183306>'

        toragsPlatelegs = '<:toragsplatelegs:687939118050705454>'
        toragsPlatebody = '<:toragsplatebody:687939117530873882>'
        toragsHammers = '<:toragshammers:687939117371490319>'
        toragsHelm = '<:toragshelm:687939117593395351>'

        dharoksHelm = '<:dharokshelm:687939117543456805>'
        dharoksGreataxe = '<:dharoksgreataxe:687939117480148993>'
        dharoksPlatebody = '<:dharoksplatebody:687939117627342858>'
        dharoksPlatelegs = '<:dharoksplatelegs:687939117605978134>'

        veracsPlateskirt = '<:veracsplateskirt:687939525468618762>'
        veracsHelm = '<:veracshelm:687939117471891456>'
        veracsBrassard = '<:veracsbrassard:687939117375684611>'
        veracsFlail = '<:veracsflail:687939117392068630>'

        karilsLeathertop = '<:karilsleathertop:687939117551845404>'
        karilsLeatherskirt = '<:karilsleatherskirt:687939117387874367>'
        karilsCrossbow = '<:karilscrossbow:687939117530480640>'
        karilsCoif = '<:karilscoif:687939117492731977>'

    class DragonItems:
        dragonBoots = '<:dragonboots:688083206490030098>'
        dragonPlatelegs = '<:dragonplatelegs:688083206645350452>'
        dragonPlateskirt = '<:dragonplatelegs:688083206645350452>'
        dragonChainbody = '<:dragonplatelegs:688083206645350452>'
        dragonScimitar = '<:dragonscimitar:688083206742081587>'
        dragonLongsword = '<:dragonlongsword:688083206498418768>'
        dragonMace = '<:dragonmace:688083206557138962>'
        dragonDagger = '<:dragondagger:688083206490423348>'
        dragonBattleaxe = '<:dragonbattleaxe:688083206469058579>'
        dragonSqShield = '<:dragonsqshield:688083206490030154>'
        dragonWarhammer = '<:dragonwarhammer:689046155333730341>'

    class RuneItems:
        runeFullHelm = '<:runefullhelm:688105227374952512>'
        runePlatelegs = '<:runeplatelegs:688105227345199145>'
        runePlateskirt = '<:runeplateskirt:688105226997071944>'
        runePlatebody = '<:runeplatebody:688105227383210072>'
        runeScimitar = '<:runescimitar:688105227353850013>'


    class Food:
        shark = '<:rsshark:688084604049031171>'
        mantaRay = '<:mantaray:688084603939979331>'
        anglerFish = '<:anglerfish:688084603889778738>'
        monkFish = '<:monkfish:688084603764080739>'

    class DragonhideArmor:
        blackDhideBody = '<:blackdhidebody:688084603952693258>'
        blackDhideChaps = '<:blackdhidechaps:688084603940110391>'
        blackDhideVamb = '<:blackdhidevamb:688084603528937533>'

    class MysticArmor:
        mysticRobeTop = '<:mysticrobetop:688084603986378759>'
        mysticRobeBottom = '<:mysticrobebottom:688084603889516599>'
        mysticHat = '<:mystichat:688084603923333138>'

    class SlayerItems:
        abyssalWhip = '<:abyssalwhip:687878177397145611>'
        graniteMaul = '<:granitemaul:688087564581863453>'
        darkBow = '<:darkbow:688096972665913366>'

    class Jewelry:
        amuletOfGlory = '<:amuletofglory:688088003469770768>'
        ringOfSuffering = '<:ringofsuffering:687878177296744489>'
        amuletOfTorture = '<:amuletoftorture:687878176931577903>'
        necklaceOfAnguish = '<:necklaceofanguish:687878176969719840>'
        tormentedBracelet = '<:tormentedbracelet:687878177519042570>'
        amuletOfFury = '<:amuletoffury:687878177200406565>'

    class Potions:
        superCombat = '<:supercombat:688088003876487176>'
        prayer = '<:supercombat:688088003876487176>'
        superRestore = '<:superrestore:688088003402662059>'
        superAttack = '<:superattack:688088003675160616>'
        superStrength = '<:superstrength:688088003108798512>'
        superDefence = '<:superdefence:688088003092021273>'
        saradominBrew = '<:saradominbrew:688088003444342862>'
        ranging = '<:rangingpotion:688088003381428224>'

    class RawMaterials:
        uncutOnyx = '<:uncutonyx:688088003469639728>'

    class RangedWeapons:
        magicShortbow = '<:magicshortbow:688088003528359998>'

    class ZulrahItems:
        serpentineHelm = '<:serpentinehelm:688093963671961686>'
        toxicBlowpipe = '<:toxicblowpipe:689047304161722470>'

    class Infinity:
        infinityGloves = '<:infinitygloves:687878177590214674>'
        infinityTop = '<:infinitytop:687878177468841994>'
        infinityBottoms = '<:infinitybottoms:687878177934278666>'
        infinityHat = '<:infinitybottoms:687878177934278666>'
        infinityBoots = '<:infinityboots:688094756479565829>'

    class Armadyl:
        armadylHelm = '<:armadylhelmet:687878177141686303>'
        armadylChestplate = '<:armadylchestplate:687878177179303966>'
        armadylChainskirt = '<:armadylchainskirt:687878177355333655>'
        armadylGodsword = '<:armadylgodsword:687878177510522895>'


    class Bandos:
        bandosBoots = '<:bandosboots:687878177338556425>'
        bandosChestplate = '<:bandoschestplate:687878177162526838>'
        bandosTassets = '<:bandostassets:687878177170784338>'
        bandosGodsword = '<:bandosgodsword:687878177535951002>'

    class Zamorak:
        zamorakianSpear = '<:zamorakianspear:687878177015857229>'
        toxicStaff = '<:toxicstaff:687878176965263486>'
        zamorakGodsword = '<:zamorakgodsword:687878177468842025>'

    class Saradomin:
        saradominSword = '<:saradominsword:687878177468842002>'
        saradominGodsword = '<:saradomingodsword:687878177410121745>'

    class EliteClues:
        rangersTights = '<:rangerstights:687878177284161617>'
        rangerGloves = '<:rangergloves:687878177431093269>'
        rangersTunic = '<:rangerstunic:687878177443545088>'

    class HardClues:
        robinHoodHat = '<:robinhoodhat:687878177502134309>'

    class MediumClues:
        rangerBoots = '<:rangerboots:687878177443414086>'

    class CerberusItems:
        pegasianBoots = '<:pegasianboots:687878177372110855>'
        primordialBoots = '<:primordialboots:687878176944160780>'
        eternalBoots = '<:eternalboots:687878177346945072>'

    class RaidsItems:
        ancestralHat = '<:ancestralhat:687878177468842016>'
        ancestralRobeTop = '<:ancestralrobetop:687878177321910292>'
        ancestralRobeBottom = '<:ancestralrobebottom:687878177145487361>'
        dragonClaws = '<:dragonclaws:687878177296744468>'
        kodaiWand = '<:kodaiwand:687878177330167825>'
        elderMaul = '<:eldermaul:687878177108131902>'

    class Coins:
        coins = '<:coins:688107815365378051>'



def setup(bot):
    bot.add_cog(ItemEmojis(bot))
