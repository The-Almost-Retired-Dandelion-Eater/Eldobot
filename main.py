from re import L
import discord
from shared_info import iscrowded
from discord.ext import commands
import json
import urllib.request
import csv
import asyncio
import checks
import basics
import commands
import shared_info
import os
import math
import trade_functions
import bible
import gc
from unidecode import unidecode

points = shared_info.points
#move commands to a shared place for access across the bot
shared_info.commandsRaw = commands.commandsRaw

#intents for DMing bawds
intents = discord.Intents.all()
intents.members = True
#intents.message_content = True
client = discord.Client(intents=intents)
shared_info.bot = client
async def process(path, g):
    f = open(path)
    print("ended to load")
    yu =  json.load(f)
    f.close()
    if not str(g.id) in shared_info.serverExports:
                                        
        shared_info.serverExports.update({str(g.id): yu})
        print("set the db")
    else:
        print("already had it")
        del(yu)
    #return yu

#load settings db
serversList = shared_info.serversList


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='SolarBalls'))
    print('Bot connected')
    for g in client.guilds:

        serversList = checks.server_check(g.id, g.name)
        for item in serversList:
            #print(serversList[item])
            if 'draftStatus' in serversList[item]:
                if serversList[item]['draftStatus']['draftRunning']:
                    serversList[item]['draftStatus'].update({'draftRunning':False})

        await basics.save_db(serversList)
        

@client.event
async def on_guild_join(g):
    print('Joined', g.name)
    serversList = checks.server_check(g.id, g.name)
    await basics.save_db(serversList)

commandAliases = {
    "r": "ratings",
    "s": "stats",
    "b": "bio",
    "setgm": "addgm",
    "ts": "tstats",
    "tsp": 'ptstats',
    "rs": "resignings",
    "runrs": "runresignings",
    "ppr":"playoffpredict",
    "cs": "cstats",
    "hs": "hstats",
    'updateexport': 'updatexport',
    "balance":"bal",
    "gl":"globalleaders",
    "l":"pleaders",
    'lp':'lotterypool',
    'mostuniform':'mostaverage'
}

#set up bible commands quickly

bookNames = ['Joshua', '1 Samuel', '2 Samuel', '1 Chronicles', '2 Chronicles', 'Ezra', "Tobit", "1 Maccabees", "2 Maccabees", 'Revelation', 'Nehemiah', 'Psalm', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Ezekiel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Micah', 'Jonah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi']
for book in shared_info.bibleBooks:
    bookNames.append(str.lower(book['shortname']))

#mod only
modOnlyCommands = ['clearalloffers','edit', 'load', 'addgm', 'removegm', 'runfa', 'startdraft', 'runresignings', 'autocut', 'pausedraft']


@client.event
async def on_message(message):
    
    try: prefix = serversList[str(message.guild.id)]['prefix']
    except: prefix = '-'
    if message.content.startswith(prefix):
        print("============")
        print(message.guild.name)
        print(message.channel.name)
        print(message.author.name)
        print(message.content)
        print("-------------------")
    
    
    if not str(message.author.id) in points:
        points.update({str(message.author.id):0})
    if not message.content.startswith(str(prefix)):
        increment = math.sqrt(len(message.content))*0.01
        points.update({str(message.author.id):points[str(message.author.id)]+increment})
        if str(points[str(message.author.id)]) == "nan":
            points.update({str(message.author.id):0})
    
    
    
    #
    #trade scanning - if in trade channel, just pass it along to the proper functions
    if message.guild is not None:
        if f"<#{message.channel.id}>" == serversList[str(message.guild.id)]['tradechannel'] and message.author.id != client.user.id:
            if serversList[str(message.guild.id)]['draftStatus']['draftRunning']:
                await message.channel.send("No trades during draft!")
                return
            print("here")
            g = message.guild
            todelete = set()
            for item in shared_info.serverExports:
                if not serversList[item]['draftStatus']['draftRunning'] == True or item == str(g.id):
                     todelete.add(item)
                else:
                    print(item)
            for thing in todelete:
                del shared_info.serverExports[thing]
            if not str(g.id) in shared_info.serverExports:
                current_dir = os.getcwd()
                path_to_file = os.path.join(current_dir, "exports", f'{g.id}-export.json')
                t = basics.load_db(path_to_file)
                if not str(g.id) in shared_info.serverExports:
                    shared_info.serverExports.update({str(g.id):t})
                else:
                    print("welp, guess we already here")
                    del(t)
                          
                          
            print(len(shared_info.serverExports))
            if str.lower(message.content) == 'confirm':
                if not serversList[str(message.guild.id)]['draftStatus']['draftRunning']:
                
                    await trade_functions.confirm_message(message)
                else:
                    await message.channel.send("No trades during draft!")
            else:
                if not serversList[str(message.guild.id)]['draftStatus']['draftRunning'] == True:
                    await trade_functions.scan_text(message.content, message)
                else:
                    await message.channel.send("No trades during draft!")
        else:
            #print(str(prefix))
            
            if message.author.nick is not None:
                if message.author.nick.__contains__("Eldo") and message.content.lower().__contains__("bored"):
                    await message.channel.send(message.author.mention+", then you should think about this: What do you put in a barrel to make it lighter?")
            if message.content.startswith(str(prefix)):
                
                if message.author.guild_permissions.manage_messages and message.content == prefix+"forcestopdraft":
                    serversList[str(message.guild.id)]['draftStatus'].update({'draftRunning':False})
                    await message.channel.send("OK. Dont blame me if something went wrong though, as this is more like the equivalent of Danger Zone in the BBGM game.")

                text = message.content[1:].split(' ')
                command = text[0]
                
                command = str.lower(command)
                if command in commandAliases:
                    text[0] = commandAliases[command]
                    command = commandAliases[command]
                if command in commands.commands:

                    #check for mod command
                    valid = False
                    if command in modOnlyCommands:

                        if message.author.guild_permissions.manage_messages or message.author.id == 625806545610997762:
                            valid = True
                    else:
                        valid = True
                    if valid:
                        #UPDATE EXPORT
                        if shared_info.iscrowded and (not command == 'pick') and (not commands.commandsRaw[command] in ['points','settings']):
                            await message.channel.send("your command is queued, please wait")
                            t = 0
                            while shared_info.iscrowded:
                                
                                await asyncio.sleep(1)
                                t += 1
                                if t == 10:
                                    await message.channel.send("the wait was too long, you fell out of queue")
                                    return
                        print("got to command")

                        if not commands.commandsRaw[command] in ['points','settings']:
                            shared_info.iscrowded = True
                            try:
                                g = message.guild
                                todelete = set()
                                for item in shared_info.serverExports:
                                    if not (serversList[item]['draftStatus']['draftRunning'] == True or item == str(g.id)):
                                        todelete.add(item)
                                    else:
                                        print('not deleting '+str(item))
                                for thing in todelete:
                                    del shared_info.serverExports[thing]
                                if not str(g.id) in shared_info.serverExports:
                                    if not command == 'load': #if command is load specifically, you don't need to read an export
                                        current_dir = os.getcwd()
                                        path_to_file = os.path.join("exports", f'{g.id}-export.json')
                                        print("Starting to load")
                                        await process(path_to_file,g)
                                        
                                        
                                    gc.collect()
                                #print(len(shared_info.serverExports))
                                
                            except Exception as e:
                                print(e)
                                await message.channel.send("You need an export to do this, but you don't have one.")

                        
                        await commands.commands[command](text, message)
                        
      
                        
                        
                        shared_info.iscrowded = False
                        

                    else:
                        try:
                            await message.channel.send("You aren't authorized to run that command.")
                        except Exception as e:
                            print(e)
            
            #bible command
            else:
                if message.channel in shared_info.trivias and not len(message.content) > 30:
                    if unidecode(shared_info.trivias[message.channel].lower()) in message.content.lower():
                        todelete = set()
                        for item, value in shared_info.triviabl.items():
                            if value == message.channel:
                                todelete.add(item)
                        for item in todelete:

                            del shared_info.triviabl[item]
                        del shared_info.trivias[message.channel]
                        await message.channel.send(message.author.mention+" correct, and you gain 5 points")
                        p = points[str(message.author.id)]
                        points.update({str(message.author.id):p+5})
            for b in bookNames:
                if str.lower(message.content).startswith(str.lower(b)):
                    await bible.get_verse(message.content, message, b)
f = open("token.txt","r")
for line in f:
    tk = line.replace("\n","")
f.close()
client.run(tk)
