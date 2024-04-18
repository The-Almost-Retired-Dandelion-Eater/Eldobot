import shared_info
exports = shared_info.serverExports
import basics
import os
import pull_info
from pull_info import pinfo
from pull_info import tinfo
from shared_info import triviabl
import discord
import league_commands

##LEAGUE COMMANDS

commandFuncs = {
    'fa': league_commands.fa,
    'draftorder':league_commands.draftorder,
    'po':league_commands.po,
    'playoffpredict':league_commands.standingspredict,
    'draft': league_commands.draft,
    'pr': league_commands.pr,
    'matchups': league_commands.matchups,
    'top': league_commands.top,
    'injuries': league_commands.injuries,
    'deaths': league_commands.deaths,
    'leaders': league_commands.leaders,
    'summary': league_commands.summary,
    'leaguegraph':league_commands.leaguegraph,
    'lgoptions':league_commands.lgoptions,
    'topall':league_commands.topall,
    'standings':league_commands.standings,
    'playoffs':league_commands.playoffs,
    'to':league_commands.to,
    'mostaverage':league_commands.mostaverage,
    'reprog':league_commands.reprog,
    'stripnames':league_commands.stripnames
}
    
async def process_text(text, message):
    export = shared_info.serverExports[str(message.guild.id)]
    season = export['gameAttributes']['season']
    players = export['players']
    teams = export['teams']
    commandSeason = season
    pageNumber = 1
    command = str.lower(text[0])
    for m in text:
        try:
            m = int(m)
            if m > 1500:
                commandSeason = m
            else:
                pageNumber = m
            text.remove(str(commandSeason))
        except:
            pass
    descripLine = str(commandSeason) + ' season'
    if command == 'fa' and season != commandSeason:
        descripLine = f"Page {commandSeason}"
    embed = discord.Embed(title=message.guild.name, description=descripLine)
    commandInfo = {
        'serverId': message.guild.id,
        'message': message,
        'season': commandSeason,
        'pageNumber': pageNumber,
        'text': text
    }
    if commandInfo['message'].author.id in triviabl or message.channel in triviabl.values():
        embed = discord.Embed(title="Trivia", description="You're not allowed to run any league commands within 30 seconds of starting a trivia.")
        embed.set_footer(text=shared_info.embedFooter)
        await message.channel.send(embed=embed)
    else:
    #embed = commandFuncs[command](embed, commandInfo)
        embed = commandFuncs[command](embed, commandInfo) #fill the embed with the specified function
        
        embed.set_footer(text=shared_info.embedFooter)
        gc = ["leaguegraph"]
        if command in gc:
            waswrong = False
            for field in embed.fields:
                if field.name == "Error":
                    waswrong = True
            if not waswrong:
                try:
                    f = open("third_figure.png",'rb')
                    await message.channel.send("Roster graph", file = discord.File(f))
                    f.close()
                except Exception:
                     await message.channel.send("There was some kind of mistake")
        if command == "reprog" or command == 'stripnames':
            current_dir = os.getcwd()
            path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
            await basics.save_db(export, path_to_file)
        await message.channel.send(embed=embed)
