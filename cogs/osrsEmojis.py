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

    class SlayerEquipment:
        faceMask = '<:Facemask:694816516989779998>'
        nosePeg = '<:Nosepeg:694816516541251595>'
        witchwoodIcon = '<:Witchwoodicon:694816516792909834>'
        leafBladedSword = '<:Leafbladedsword:694816516729864272>'
        leafBladedBattleaxe = '<:Leafbladedbattleaxe:694816516897636352> '
        slayerHelmet = '<:Slayerhelmet:694816516721475605>'
        spinyHelmet = '<:Spinyhelmet:694816516746510336>'
        mirrorShield = '<:Mirrorshield:694816516788715540>'
        rockHammer = '<:Rockhammer:694816516406902827>'
        slayerGloves = '<:Slayergloves:694816516490657823>'
        earmuffs = '<:Earmuffs:694816516381605920>'
        blackMask = '<:Blackmask:694816516620681227>'
        insulatedBoots = '<:Insulatedboots:694816516734058616>'
        fungicide = '<:Fungicidespray:694816516763287552>'
        iceCooler = '<:Icecooler:694816516759355392>'
        bagOfSalt = '<:Bagofsalt:694816516855693353>'

    class Jewelry:
        amuletOfGlory = '<:amuletofglory:688088003469770768>'
        ringOfSuffering = '<:ringofsuffering:687878177296744489>'
        amuletOfTorture = '<:amuletoftorture:687878176931577903>'
        necklaceOfAnguish = '<:necklaceofanguish:687878176969719840>'
        tormentedBracelet = '<:tormentedbracelet:687878177519042570>'
        amuletOfFury = '<:amuletoffury:687878177200406565>'

    class Potions:
        superCombat = '<:supercombat:688088003876487176>'
        prayer = '<:prayerpotion:688088003511582755>'
        superRestore = '<:superrestore:688088003402662059>'
        superAttack = '<:superattack:688088003675160616>'
        superStrength = '<:superstrength:688088003108798512>'
        superDefence = '<:superdefence:688088003092021273>'
        saradominBrew = '<:saradominbrew:688088003444342862>'
        ranging = '<:rangingpotion:688088003381428224>'
        attack = '<:attackpotion:693810045279928371>'
        strength = '<:strengthpotion:693810045309419610>'
        defence = '<:defencepotion:693810045388849172>'
        divineSuperStrength = '<:divinesuperstrength:693810045275602944>'
        divineSuperCombat = '<:divinesupercombat:693810045254893588>'

    class Prayers:
        thickSkin = '<:ThickSkin:693810076997255239>'
        burstOfStrength = '<:BurstofStrength:693810077240524891>'
        clarityOfThought = '<:ClarityofThought:693810076850323472>'
        rockSkin = '<:RockSkin:693810076846129224>'
        superhumanStrength = '<:SuperhumanStrength:693810077047717969>'
        improvedReflexes = '<:ImprovedReflexes:693810077252976640>'
        steelSkin = '<:SteelSkin:693810077181804564>'
        ultimateStrength = '<:UltimateStrength:693810077185998928>'
        incredibleReflexes = '<:IncredibleReflexes:693810077219684372>'
        chivalry = '<:Chivalry:693810076825288735>'
        piety = '<:Piety:693810076779151461>'

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

    class Misc:
        skull = '<:pkskull:689309885359194150>'
        ticket = '<:Castlewarsticket:691371392037552178>'
        clue = '<:masterclue:692775913816850492>'
        minigames = '<:Minigames:692775913942679842>'
        boss = '<:Boss_icon:690688303183429662>'
        fireCape = '<:Firecape:694263728803151952>'
        combat = '<:combat:694616668026175669>'

    class Skills:
        total = '<:totallevel:692667090540298270>'
        attack = '<:Attack_icon:690688303183167528>'
        strength = '<:Strength_icon:690688303032434739>'
        defence = '<:Defence_icon:690688303329968158>'
        ranged = '<:Ranged_icon:690696437410824224>'
        magic = '<:Magic_icon:690688303254601798>'
        prayer = '<:Prayericon:690688303258927164>'
        runecraft = '<:Runecrafticon:690688303372042240>'
        construction = '<:Construction_icon:690688303229304852>'
        hitpoints = '<:Hitpoints_icon:690688303246082069>'
        agility = '<:Agility_icon:690697402679689257>'
        herblore = '<:Herblore_icon:690688303279898695>'
        thieving = '<:Thieving_icon:690688303208333312>'
        crafting = '<:Crafting_icon:690688303128772689>'
        fletching = '<:Fletching_icon:690688303296675890>'
        slayer = '<:Slayer_icon:690688303191556196>'
        hunter = '<:Hunter_icon:690688303305064530>'
        mining = '<:Mining_icon:690688303220916314>'
        smithing = '<:Smithing_icon:690688303023915099>'
        fishing = '<:Fishing_icon:690688303279636521>'
        cooking = '<:Cooking_icon:690688302935965737>'
        firemaking = '<:Firemaking_icon:690688303262990518>' 
        woodcutting = '<:Woodcutting_icon:690688302948286535>'
        farming = '<:Farming_icon:690688303380561980>'

    class Bosses:
        gauntlet = '<:Youngllef:692820203054170212>'
        vorkath = '<:Vorki:692820203008032799>'
        vetion = '<:Vetionjr:692820202642997290>'
        venenatis = '<:Venenatisspiderling:692820203058364436>'
        fightCaves = '<:Tzrekjad:692820203054039121>'
        sarachnis = '<:Sraracha:692820202672619643>'
        zalcano = '<:Smolcano:692820202718625880>'
        skotizo = '<:Skotos:692820202806706197>'
        scorpia = '<:Scorpiasoffspring:692820202785865869>'
        kingBlackDragon = '<:Princeblackdragon:692820203016290314>'
        wintertodt = '<:Phoenix:692820202680877097>'
        commanderZilyana = '<:Petzilyana:692820203045650552>'
        zulrah = '<:Petsnakeling:692820203045650572>'
        thermonuclearSmokeDevil =' <:Petsmokedevil:692820202915758093>'
        krilTsutsaroth = '<:Petkriltsutsaroth:692820202940923906>'
        kreeArra = '<:Petkreearra:692820203024678982>'
        kraken = '<:Petkraken:692820203066621952>'
        generalGraardor = '<:Petgeneralgraardor:692820202852843652>'
        corporealBeast = '<:Petdarkcore:692820202974478358>'
        dagannothSupreme = '<:supreme:692820203343708170>'
        dagannothRex = '<:rex:692820203163222046>'
        dagannothPrime = '<:prime:692820203402297354>'
        chaosElemental = '<:chaosele:692820203326669152>'
        chaosFanatic = '<:fanatic:692831446007676979>'
        chambersOfXeric = '<:cox:692820202811031624>'
        chambersOfXericChallengeMode = '<:coxcm:692828044334989313>'
        grotesqueGuardians = '<:Noon:692820202886529126>'
        nightmare = '<:Littlenightmare:692820203066884178>'
        theaterOfBlood = '<:Lilzik:692820203008032811>'
        kalphiteQueen = '<:kq:692820203264016424>'
        inferno = '<:Jalnibrek:692820203154833448>'
        alchemicalHydra = '<:hydra:692820203272273960>'
        obor = '<:hillgiant:692820202391470132>'
        hespori = '<:Hesporiicon:692820202630676551>'
        cerberus = '<:cerberus:692820203284987935>'
        derangedArchaeologist = '<:deranged:692820202370367569>'
        crazyArchaeologist = '<:crazy:692820202689134727>'
        corruptedGauntlet = '<:Corruptedyoungllef:692820202525556847>'
        callisto = '<:Callistocub:692820203268079726>'
        bryophyta = '<:Bryophyta:692820203784110111>'
        giantMole = '<:Babymole:692820203163222056>'
        abyssalSire = '<:sire:692820203238719578>'
        barrows = '<:verac:692820202806706230>'
        mimic = '<:mimic:692843508180189244>'

    class SlayerMasters:
        turael = '<:Turael:694794552363581450>'
        mazchna = '<:Mazchna:694794552397004860>'
        vannaka = '<:Vannaka:694794552145608736>'
        konar = '<:Konar:694794552137220119>'
        nieve = '<:Nieve:694794552405524500>'
        duradel = '<:Duradel:694794552011259955>'
        chaeldar = '<:Chaeldar:694794552476696636>'

def setup(bot):
    bot.add_cog(ItemEmojis(bot))
