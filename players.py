import shared_info
exports = shared_info.serverExports
import basics
import pull_info
from pull_info import pinfo
from pull_info import tinfo
import discord
import player_commands as pc
from shared_info import triviabl
import asyncio
##PLAYER COMMANDS

commandFuncs = {
    'stats': pc.stats,
    'progspredict':pc.progspredict,
    'pratings':pc.pratings,
    'pcompare':pc.pcompare,
    'bio': pc.bio,
    'padv': pc.adv,
    'ratings': pc.ratings,
    'pshots':pc.shots,
    'shots':pc.shots,
    'adv': pc.adv,
    'progs': pc.progs,
    'hstats': pc.hstats,
    'cstats': pc.stats,
    'pstats': pc.stats,
    'awards': pc.awards,
    'pgamelog': pc.pgamelog,
    'compare': pc.compare,
    'nbacompare': 'players',
    'proggraph':pc.progschart,
    'trivia':pc.trivia,
    'hint':pc.hint
}


async def process_text(text, message):
    export =shared_info.serverExports[str(message.guild.id)]
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
    
    playerToFind = ' '.join(text[1:])
    playerPid = basics.find_match(playerToFind, export,settings =  shared_info.serversList[str(message.guild.id)])
    for player in players:
        if player['pid'] == playerPid:
            p = player
    if commandSeason == season:
        p = pinfo(p)
    else:
        p = pinfo(p, commandSeason)
    t = None
    for team in teams:
        if team['tid'] == p['tid']:
            if commandSeason == season:
                t = tinfo(team)
            else:
                t = tinfo(team, commandSeason)
    if t == None:
        t = pull_info.tgeneric(p['tid'], p)
    
    descriptionLine = f"{p['position']}, {p['ovr']}/{p['pot']}, {commandSeason - p['born']} years | #{p['jerseyNumber']}, {t['name']} ({t['record']})"
    if p['skills'] != '': descriptionLine += '\n' + f"*Skills: {p['skills']}*"
    embed = discord.Embed(title=p['name'], description=descriptionLine, color=t['color'])

    #pull together some essential command info to pass along to the command funcs
    commandInfo = {"id": message.guild.id,
                   "season": commandSeason,
                   "commandName": command,
                   "message": message}
    #uncomment to get a full error message in console
    #print(commandFuncs)
    if (commandInfo['message'].author.id in triviabl or message.channel in triviabl.values()) and not command == 'hint':
        embed = discord.Embed(title="Trivia", description="You're not allowed to run any player commands within 30 seconds of starting a trivia.")
        embed.set_footer(text=shared_info.embedFooter)
        await message.channel.send(embed=embed)
    else:
        embed = commandFuncs[command](embed, p, commandInfo) 
        #try: embed = commandFuncs[command](embed, p, commandInfo) #fill the embed with the specified function
        #except Exception as e:
         #   print(e) 
         #   embed.add_field(name='Error', value="An error occured. Command may not be specified.", inline=False)
        
        #add the bottom parts
        if command == 'trivia':
            triviabl.update({message.author.id:message.channel})

        if not command=="trivia" and not command == 'hint':
            if commandSeason == season:
                if p['retired']:
                    titles = 0
                    for a in p['awards']:
                        if a['type'] == 'Won Championship':
                            titles += 1
                    embed.add_field(name=f'Championships: {titles}', value='', inline=False)
                else:
                    contract = f"${p['contractAmount']}M/{p['contractExp']}"
                    injury = p['injury'][0]
                    if p['injury'][0] != "Healthy":
                        injury += f" (out {p['injury'][1]} more games)"
                    embed.add_field(name=f"Contract: {contract}", value=injury, inline=False)
            else:
                embed.add_field(name=f"Playoffs: {pull_info.playoff_result(t['roundsWon'], export['gameAttributes']['numGamesPlayoffSeries'], commandSeason)}", value=p['awards'], inline=False)
        
        embed.set_footer(text=shared_info.embedFooter)
        
        gc = ["proggraph","progspredict"]
        if command in gc:
            do = True
            for fi in embed.fields:
                if fi.name.startswith("Error"):
                    do = False
            if do:
                if command == "progspredict":
                    embed.set_footer(text="Based on a sample of over 220 years worth of player progressions")
                f = open("first_figure.png",'rb')
                await message.channel.send("Your graph", file = discord.File(f))
                f.close()
        await message.channel.send(embed=embed)
        if command == 'trivia':
            del(season)
            del(players)
            del(teams)
            del(export)
            
            shared_info.iscrowded = False
            print("reached end trivia")
            
            await asyncio.sleep(30)
            if message.author.id in triviabl:
                del triviabl[message.author.id]



