import shared_info
exports = shared_info.serverExports
serversList = shared_info.serversList
import basics
import pull_info
import roster_commands as rc
import discord


#ROSTER COMMANDS

commandFuncs = {
    'lmove': rc.lmove,
    'pt': rc.pt,
    'autosort': rc.autosort,
    'resetpt': rc.resetpt,
    'changepos': rc.changepos,
    'release': rc.release,
    'autocut': rc.autocut,
    'acceptto': rc.acceptto
}

async def process_text(text, message):

    export = shared_info.serverExports[str(message.guild.id)]

    season = export['gameAttributes']['season']
    teams = export['teams']
    
    userTid = serversList[str(message.guild.id)]['teamlist'][str(message.author.id)]

    t = None
    for team in teams:
        if team['tid'] == userTid:
            t = pull_info.tinfo(team)
    if t == None:
        t = pull_info.tgeneric(-1)

    command = str.lower(text[0])
    embed = discord.Embed(title=t['name'] + ' Roster Management', description=f"{season} season", color=t['color'])
    
    #see if user is affiliated with a team
    teamList = serversList[str(message.guild.id)]['teamlist']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:

        commandInfo = {
            "userTid": userTid,
            "serverId": str(message.guild.id),
            "userId": str(message.author.id),
            "userTid": userTeam,
            "message": message
        }
        #uncomment to get full error message in console
        #embed = await commandFuncs[command](embed, text, commandInfo) #fill the embed with the specified function
        try: embed = await commandFuncs[command](embed, text, commandInfo) #fill the embed with the specified function
        except Exception as e:
            print(e) 
            embed.add_field(name='Error', value="An error occured. Command may not be specified.", inline=False)

    if embed != None:
        embed.set_footer(text=shared_info.embedFooter)
        await message.channel.send(embed=embed)
