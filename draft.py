##DRAFT COMMANDS

import shared_info
from shared_info import serverExports
from shared_info import serversList
import pull_info
import basics
import discord
import draft_commands as dc

commandFuncs = {
    'board': dc.board,
    'add': dc.add,
    'remove': dc.remove,
    'dmove': dc.move,
    'clearboard': dc.clear,
    'auto': dc.auto,
    'pick': dc.pick,
    'pausedraft': dc.pause,
    'bulkadd': dc.bulkadd
}


async def process_text(text, message):
    export = shared_info.serverExports[str(message.guild.id)]
    season = export['gameAttributes']['season']
    players = export['players']
    teams = export['teams']
    commandSeason = season
    command = str.lower(text[0])
    for m in text:
        try:
            m = int(m)
            commandSeason = m
            text.remove(str(commandSeason))
        except:
            pass
    
    embed = discord.Embed(title='Draft Preparation', description=f"{season} season")

    #pull together some essential command info to pass along to the command funcs
    #uncomment to get a full error message in console
    # embed = await commandFuncs[command](embed, message) 
    try:
        embed = await commandFuncs[command](embed, message) #fill the embed with the specified function
    except Exception as e:
        print(e) 
        embed.add_field(name='Error', value="An error occured. Command may not be specified.", inline=False)
    
    embed.set_footer(text=shared_info.embedFooter)
    await message.channel.send(embed=embed)
