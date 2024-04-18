import shared_info
from shared_info import serverExports
from shared_info import serversList
import pull_info
import basics
import discord

async def add_gm(embed, text, message):
    if len(text) != 3:
        embed.add_field(name='Invalid Format', value='Please set a new GM using this format:' + '\n' + '``-setgm [team abbreviation] [new GM, ping the user or provide their user ID number]``')
    else:
        teamToEdit = str.upper(text[1])
        gm = text[2]
        toReplace = ['<@!', '<@', '>']
        for to in toReplace:
            gm = gm.replace(to, '')
        try: gm = int(gm)
        except: embed.add_field(name='Error', value='Invalid GM. Ping the user, or provide only the numbers of their user ID.')
        teamId = None
        teams = shared_info.serverExports[str(message.guild.id)]['teams']
        for t in teams:
            if t['abbrev'] == teamToEdit:
                teamId = t['tid']
                teamName = t['region'] + ' ' + t['name']
        if teamId == None:
            embed.add_field(name='Error', value='Could not find that team. Use their abbreviation.')
        else:
            if isinstance(gm, int):
                teamList = serversList[str(message.guild.id)]['teamlist']
                teamList[str(gm)] = teamId
                await basics.save_db(serversList)
                embed.add_field(name='GM Set', value=f"Set <@!{gm}> as the {teamName} GM.")
    return(embed)

async def removegm(embed, text, message):
    teamList = serversList[str(message.guild.id)]['teamlist']
    if len(text) > 2:
 
        for word in text:
            teams = shared_info.serverExports[str(message.guild.id)]['teams']
            teamAbbrevs = []
            for t in teams:
                teamAbbrevs.append([t['abbrev'], t['tid']])
            removeUser = True

            for t in teamAbbrevs:
                if t[0] == str.upper(word):

                    usersToClear = []
                    #remove a team
                    for user, team in teamList.items():
                        if team == t[1]:
                            usersToClear.append(user)
                    removeUser = False
                    for u in usersToClear:
                        del teamList[u]
                    await basics.save_db(serversList)
                    embed.add_field(name='Team Cleared', value=f'Cleared all GMs from team {t[0]}')
        return embed
            
            
    else:
        #first check for a team
        teams = shared_info.serverExports[str(message.guild.id)]['teams']
        teamAbbrevs = []
        for t in teams:
            teamAbbrevs.append([t['abbrev'], t['tid']])
        removeUser = True
        
        for t in teamAbbrevs:
            if t[0] == str.upper(text[1]):
                usersToClear = []
                #remove a team
                for user, team in teamList.items():
                    if team == t[1]:
                        usersToClear.append(user)
                removeUser = False
                for u in usersToClear:
                    del teamList[u]
                await basics.save_db(serversList)
                embed.add_field(name='Team Cleared', value=f'Cleared all GMs from team {t[0]}')
        if removeUser:
            gm = text[1]
            toReplace = ['<@!', '<@', '>']
            for to in toReplace:
                gm = gm.replace(to, '')
            try: gm = int(gm)
            except: embed.add_field(name='Error', value='Invalid GM. Ping the user, or provide only the numbers of their user ID.')
            try:
                del teamList[str(gm)]
                embed.add_field(name='GM Removed', value=f"Removed GM <@!{gm}> from the team list.")
            except:
                embed.add_field(name='Error', value='That GM may not be on the team list.')
    return embed




async def autoassigngm(embed, text, message):
    print("CALLED ASSIGN GM")
    gid = message.guild.id
    ss = "Stuff done"
    teams = shared_info.serverExports[str(message.guild.id)]['teams']
    for member in message.guild.members:
        rolenames = [role.name for role in member.roles]
        for r in rolenames:

            for t in teams:


                if t['region'].strip().lower() in r.lower() or t['abbrev'] in r:

                    if t['name'].strip().lower() in r.lower():
                        toassign = t['tid']
                        teamList = serversList[str(message.guild.id)]['teamlist']
                        teamList[str(member.id)] = toassign
                        if len(ss) < 800:
                            ss = ss + "\n<@"+str(member.id)+"> got assigned to team "+t['region'].lower()+" "+t['name'].lower()
                        else:
                            if not "and more" in ss:
                                ss = ss + "and more\n"
    await basics.save_db(serversList)
    embed.add_field(name='GM Set', value=ss+"\nPLEASE DOUBLE CHECK USING TEAMLIST THAT IT IS CORRECT AND CORRECT ANY ERRORS MANUALLY USING -addgm OR -removegm. OR ELSE GOD WILL GEORGE YOU.")
    return embed
async def teamlist(embed, text, message):
    gid = message.guild.id
    export = shared_info.serverExports[str(gid)]
    teams = export['teams']
    teamsList = []
    for t in teams:
        if not t['disabled']:
            teamsList.append([t['tid'], t['abbrev']])
    teamsList = sorted(teamsList, key=lambda t: t[1])
    textLines = []
    serverGmList = shared_info.serversList[str(gid)]['teamlist']
    for t in teamsList:
        gmText = ""
        for gm, team in serverGmList.items():
            if team == t[0]:
                gmText += '<@!' + gm + '>, '
        gmText = gmText[:-2]
        text = f"**{t[1]}** - {gmText}"
        textLines.append(text)
    output = []
    for i in range(0, len(textLines), 18):
        output.append(textLines[i:i+18])
    for o in output:
        text = ""
        for l in o:
            text += l + '\n'
        embed.add_field(name='Team List', value=text)
    return(embed)
