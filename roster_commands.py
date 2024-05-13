import shared_info
from shared_info import serverExports
from shared_info import serversList
import pull_info
import basics
import discord
import free_agency_runner
import asyncio
import os
import copy

#-lineup will fall under team commands.

async def lmove(embed, text, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    teams = export['teams']
    #findPlayer
    player = ' '.join(text[1:-1])
    player = basics.find_match(player, export, False, True,settings =  shared_info.serversList[str(commandInfo['serverId'])])
    #moveTo
    try:
        moveTo = int(text[-1])
    except:
        embed.add_field(name='Error', value='Please provide a valid integer as the last word of your command, to move the player to.')
    
    #see if player is valid
    valid = False
    for p in players:
        if p['pid'] == player:
            if p['tid'] != commandInfo['userTid']:
                embed.add_field(name='Error', value=f"{p['firstName']} {p['lastName']} is not on your team.")
            else:
                if moveTo < 1:
                    embed.add_field(name='Error', value='Please provide a positive number.')
                else:
                    #move the player
                    valid = True
    #create team lineup as a list
    teamLineup = []
    for p in players:
        if p['tid'] == commandInfo['userTid']:
            teamLineup.append([p['pid'], p['rosterOrder']])
    teamLineup.sort(key=lambda l: l[1])
    spot = 1
    newLineup = []
    for t in teamLineup:
        if t[0] == player:
            teamLineup.remove(t)
    for pl in teamLineup:
        if spot == moveTo:
            newLineup.append(player)
        newLineup.append(pl[0])
        spot+=1
    #check the validity of this new lineup with tank rules
    starters = newLineup[:5]
    lowStarterOvr = 101
    for s in starters:
        for p in players:
            if p['pid'] == s:
                if p['ratings'][-1]['ovr'] < lowStarterOvr:
                    lowStarterOvr = p['ratings'][-1]['ovr']
    bench = newLineup[5:]
    highBenchOvr = -1
    for b in bench:
        for p in players:
            if p['pid'] == b:
                if p['ratings'][-1]['ovr'] > highBenchOvr:
                    highBenchOvr = p['ratings'][-1]['ovr']
    limit = serversList[str(commandInfo['serverId'])]['lineupovrlimit']
    if highBenchOvr - lowStarterOvr > int(limit):
        embed.add_field(name='Error', value=f"Your lineup fails anti-tank rules. A bench player can not be more than {limit} OVR higher than a starter.")
    else:
        #set the lineup
        spot = 0
        for n in newLineup:
            for p in players:
                if p['pid'] == n:
                    p['rosterOrder'] = spot
                    spot += 1
        
        embed.add_field(name='Success', value='Lineup adjusted.')
        current_dir = os.getcwd()
        path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
        await basics.save_db(export, path_to_file)
    return embed
async def nickname(embed, text, commandInfo):
    embed = discord.Embed(title='Nicknames', description="The second dumbest feature in the bot (trailing only -mostaverage)")
   
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    teams = export['teams']
    settings = shared_info.serversList[str(commandInfo['serverId'])]
    if "nickname" not in settings:
        nicks = dict()
    else:
        nicks = settings['nickname']
    tid = commandInfo['userTid']
    if len(commandInfo['message'].content.split(" ")) == 1:
        embed.add_field(name = "Please say one of the following", value = "View\nAdd\nRemove")
        return embed
    if commandInfo['message'].content.split(" ")[1] == "add":
        
        if not commandInfo['message'].content.__contains__(":"):
            embed.add_field(name = "Please do -nickname add Kobe Bryant: The Black Mamba", value = "Well, now that there's space for it, let's do another example....how about: \n-nickname add LeBron James: LeMickey")
            return embed
        print("got here once")
        pname = " ".join(commandInfo['message'].content.split(":")[0].split(" ")[2:])
        nname =commandInfo['message'].content.split(":")[1].strip()
        player = basics.find_match(pname, export, False, True)
        print(player)
        for p in players:
            if p['pid'] == player:
                if p['tid'] == -2 or p['tid'] == tid:
                    print("got here")
                    if len(nname) == 0: 
                        embed.add_field(name = "The emptyness of my soul...", value = "can still not yet be compared to the emptiness of the nickname you provided.")

                    else:
                        
                        isunique = True
                        for item, value in nicks.items():
                            if value.lower().strip() == nname.lower().strip() and item != str(p['pid']):
                                isunique = False
                                for p2 in players:
                                    if p2['pid'] == int(item):
                                        embed.add_field(name = "non unique", value = "for player "+p2['firstName']+" "+p2['lastName'])
                        if isunique:
                            nicks.update({str(p['pid']):nname})
                            settings.update({"nickname":nicks})
                            embed.add_field(name = "Nicknames", value = "Added nickname "+nname+" for player "+p['firstName']+" "+p['lastName'])
                            await basics.save_db(serversList)
                else:
                    embed.add_field(name = "Can't add a nickname for a guy not on your team", value = "for player "+p['firstName']+" "+p['lastName'])
    elif commandInfo['message'].content.split(" ")[1] == "view":
        s = ""
        for p in players:
            if str(p['pid']) in nicks:
                s = s + "**"+p['firstName']+" "+p['lastName']+"**: "+nicks[str(p['pid'])]+"\n"
        embed.add_field(name = "Nicknames", value = s)
    elif commandInfo['message'].content.split(" ")[1] == "remove":
        pname = " .".join(commandInfo['message'].content.split(" ")[2:])
        player = basics.find_match(pname, export, False, True)
        for p in players:
            if p['pid'] == player:
                if p['tid'] == -2 or p['tid'] == tid:
                    has =  False
                    for n in nicks:
                        if n == str(p['pid']):
                            has = True
                    if has:
                        del nicks[str(p['pid'])]
                        embed.add_field(name = "Removed nickname for "+p['firstName']+" "+p['lastName'], value = "their nickname is now gone.")
                        await basics.save_db(serversList)
                else:
                     embed.add_field(name = "Can't remove nickname for a guy not on your team", value = "for player "+p['firstName']+" "+p['lastName'])
                    
    else:
        embed.add_field(name = "Please say one of the following", value = "View\nAdd\nRemove")
    
    return embed

async def pt(embed, text, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    teams = export['teams']
    #findPlayer
    player = ' '.join(text[1:-1])
    player = basics.find_match(player, export, False, True, settings =  shared_info.serversList[str(commandInfo['serverId'])])
    #the ptMod
    ptMods = ['+', '++', '-', '0', 'none', 'default']
    commandPt = text[-1]
    if commandPt in ptMods:
        if commandPt == '+':
            commandPt = 1.25
        if commandPt == '++':
            commandPt = 1.75
        if commandPt == '-':
            commandPt = 0.75
        if commandPt == '0':
            commandPt = 0
        if commandPt == 'none':
            commandPt = 1
        if commandPt == 'default':
            commandPt = 1
    else:
        try: commandPt = float(commandPt)
        except: embed.add_field(name='Error', value='Please provide 0, -, +, ++, or a positive number as the playing time modifier.')
    #check if player is on team
    valid = False
    for p in players:
        if p['pid'] == player:
            if p['tid'] == commandInfo['userTid']:
                valid = True
    if valid:
        if isinstance(commandPt, (int, float)):
            #if it's not a well known value, apply it as a PT OVR
            if commandPt not in [0, 0.75, 1, 1.25, 1.75]:
                for p in players:
                    if p['pid'] == player:
                        ovr = p['ratings'][-1]['ovr']
                        commandPt = commandPt/ovr
            #check limits
            serverSettings = serversList[str(commandInfo['serverId'])]
            if commandPt > float(serverSettings['maxptlimit']) or commandPt < float(serverSettings['minptlimit']):
                valid = False
                #one exception
                for p in players:
                    if p['pid'] == player:
                        if p['ratings'][-1]['ovr'] <= float(serverSettings['allowzero']):
                            if commandPt == 0:
                                valid = True

                if valid == False:            
                    embed.add_field(name='Violation', value=f'You tried applying a modifier of {round(commandPt, 2)}, which falls outside the server minimum/maximum limits.')
            if valid:
                #apply
                for p in players:
                    if p['pid'] == player:
                        p['ptModifier'] = commandPt
                        name = p['firstName'] + ' ' + p['lastName']
                        embed.add_field(name='Success', value=f"Adjusted {name}'s playing time modifier to {round(commandPt, 2)}.")
                        current_dir = os.getcwd()
                        path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
                        await basics.save_db(export, path_to_file)
    else:
        embed.add_field(name='Error', value='That player is not on your team.')

    return embed

async def autosort(embed, text, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    #just auto the roster
    lineup = []
    for p in players:
        if p['tid'] == commandInfo['userTid']:
            lineup.append([p['pid'], p['valueNoPot']])
    lineup.sort(key=lambda l: l[1], reverse=True)
    position = 0
    for l in lineup:
        for p in players:
            if p['pid'] == l[0]:
                p['rosterOrder'] = position
                position += 1
    embed.add_field(name='Success', value='Lineup autosorted.')
    current_dir = os.getcwd()
    path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
    await basics.save_db(export, path_to_file)
    return embed

async def resetpt(embed, text, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    for p in players:
        if p['tid'] == commandInfo['userTid']:
            p['ptModifier'] = 1
    embed.add_field(name='Success', value='Reset your playing time settings.')
    current_dir = os.getcwd()
    path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
    await basics.save_db(export, path_to_file)
    return embed

async def changepos(embed, text, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]

    players = export['players']
    teams = export['teams']
    #findPlayer
    player = ' '.join(text[1:-1])
    player = basics.find_match(player, export, False, True,settings =  shared_info.serversList[str(commandInfo['serverId'])])
    #position
    positions = ['PG', 'G', 'SG', 'GF', 'SF', 'F', 'PF', 'FC', 'C']
    if str.upper(text[-1]) in positions:
        for p in players:
            if p['pid'] == player:
                if p['tid'] != commandInfo['userTid']:
                    embed.add_field(name='Violation', value='That player is not on your team.')
                else:
                    p['ratings'][-1]['pos'] = str.upper(text[-1])
                    current_dir = os.getcwd()
                    path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
                    await basics.save_db(export, path_to_file)
                    embed.add_field(name='Success', value=f"{p['firstName']} {p['lastName']}'s position has been changed to {str.upper(text[-1])}.")
    else:
        embed.add_field(name='Error', value='Please move to a valid position.')
    
    return embed

async def acceptto(embed, text, commandInfo):
    message = commandInfo['message']
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    teams = export['teams']
    serverSettings = shared_info.serversList[str(commandInfo['serverId'])]
    #findPlayer
    player = ' '.join(text[1:])
    player = basics.find_match(player, export, False, True,settings =  shared_info.serversList[str(commandInfo['serverId'])])
    for p in players:
        if p['pid'] == player:
            name = f"{p['firstName']} {p['lastName']}"
            rating = f"{p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']}"
            # CHECKS
            valid = True
            # -1. the options is on
            if serverSettings['options'] == 'off':
                valid = False
            # 0. the TO exists, for this season
            amount = 0
            if 'TO' in serverSettings:
                print(player)
                print(serverSettings['TO'])
                if not (player in serverSettings['TO'] or str(player) in serverSettings['TO']):
                    print("hence")
                    valid = False
                else:
                    print("kinda nice")
                    
                    if player in serverSettings['TO']:
                        print("either here")
                        if not int(serverSettings['TO'][player][1]) == export['gameAttributes']['season']:
                            valid = False
                        else:
                            print("aha2")
                            amount =1000* float(serverSettings['TO'][player][0])
                    if str(player) in serverSettings['TO']:
                        print("or  here")
 
                        if not int(serverSettings['TO'][str(player)][1]) == export['gameAttributes']['season']:
                            valid = False
                        else:
                            print("aha")
                            amount =1000* float(serverSettings['TO'][str(player)][0])

            # 1. there is such a negotiation
            print("intermediate")
            print(valid)
            if valid:
                tid = commandInfo['userTid']
                if not 'negotiations' in export:
                    valid = False
                else:
                    valid = False
                    for n in export['negotiations']:
                        if n['tid'] == tid and n['pid'] == player:
                            print("found negotiation")
                            valid = True
            #2. hard cap
            if valid:
                teamPayroll = 0
                for p2 in players:
                    if p2['tid'] == commandInfo['userTid']:
                        teamPayroll += p2['contract']['amount']
                try:
                    for r in export['releasedPlayers']:
                        if r['tid'] == commandInfo['userTid']:
                            teamPayroll += r['contract']['amount']
                except: pass
                if teamPayroll + amount > float(serverSettings['hardcap'])*1000:
                    print("violated hardcap")
                    print(teamPayroll)
                    print(amount)
                    print(serverSettings['hardcap'])
                    valid = False
            #3. player currently has no team on him
            if p['tid'] >= 0:
                valid = False
            if not valid:
                embed.add_field(name = "This player is NOT available to sign to a 1 year TO.", value = "At least one of 5 things is true: \n1. options settings is off. \n2. Player is currently on a team. \n3. hard cap is violated if you sign this guy to the requested TO. \n4. the player is not negotiating with that team actively. \n5. There is no contract with a team option for this player.")
            if valid:
                #confirmation
                text = f'Are you sure you sign the player {name} ({rating}) to a 1 year team option at ${amount/1000} million? This action can not be reversed. Click the ✅ to confirm.'
                
                confirmMessage = await commandInfo['message'].channel.send(text)
                await confirmMessage.add_reaction('✅')
                def check(reaction, user):
                    return reaction.message == confirmMessage and user == commandInfo['message'].author and str(reaction.emoji) == '✅'
                try:
                    reaction, user = await shared_info.bot.wait_for('reaction_add', timeout=10, check=check)
                except asyncio.TimeoutError:
                    await confirmMessage.edit(content='❌Timed out.')
                else:
                    await confirmMessage.edit(content='Signing player...')
                    # LOGISTICAL STUFF
                    t = None
                    team = export['teams'][tid]
                    for n in export['negotiations']:
                        if n['pid'] == player:
                            t = n
                    export['negotiations'].remove(t)
                    if True:
                        x = serverSettings['TO']
                        if str(player) in x:
                            del serverSettings['TO'][str(player)]
                        else:
                            del serverSettings['TO'][player]
                    
                    p['tid'] = team['tid']
                    abbrev = team['abbrev']
                    tname = team['region']+" "+team['name']
                    p['contract'] = {
                        "amount": amount,
                        "exp": export['gameAttributes']['season']+1
                    }
                    p['gamesUntilTradable'] = serversList[str(commandInfo['serverId'])]['traderesign']
                    for i in range(0,1):
                        salaryInfo = dict()
                        salaryInfo['season'] = export['gameAttributes']['season'] + i + 1
                        salaryInfo['amount'] = amount
                        p['salaries'].append(salaryInfo)
                    events = export['events']
                    newEvent = dict()
                    newEvent['text'] = 'The <a href="/l/10/roster/' + team['abbrev'] + '/' + str( export['gameAttributes']['season']) + '">' + team['name'] + '</a> re-signed <a href="/l/10/player/' + str(p['pid']) + '">' + p['firstName'] + ' ' + p['lastName'] + '</a> for $' + str(amount/1000) + 'M/year through ' + str(1 + export['gameAttributes']['season']) + '.'
                    newEvent['pids'] = [p['pid']]
                    newEvent['tids'] = [team['tid']]
                    newEvent['season'] = export['gameAttributes']['season']
                    newEvent['type'] = 'reSigned'
                    newEvent['eid'] = events[-1]['eid'] + 1
                    events.append(newEvent)
                    message2 = p['firstName']+" "+p['lastName']+ " gets resigned on a 1 year team option by "+basics.team_mention(message, tname, abbrev)+"."
                    try:
                            transChannel = shared_info.bot.get_channel(int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', '')))
                            await transChannel.send(message2)
                    except Exception:
                            await message.channel.send(message2)
                    await basics.save_db(serversList)
                    current_dir = os.getcwd()
                    path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
                    await basics.save_db(export, path_to_file)
                    await confirmMessage.edit(content='**Complete.**')
                    embed = None
    return embed
            
                
            

async def release(embed, text, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    teams = export['teams']
    serverSettings = shared_info.serversList[str(commandInfo['serverId'])]
    #findPlayer
    player = ' '.join(text[1:])
    player = basics.find_match(player, export, False, True,settings =  shared_info.serversList[str(commandInfo['serverId'])])
    for p in players:
        if p['pid'] == player:
            name = f"{p['firstName']} {p['lastName']}"
            rating = f"{p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']}"
            #validity checks!
            valid = True
            #OVR
            maxOvrRelease = int(serverSettings['maxovrrelease'])
            if p['ratings'][-1]['ovr'] > maxOvrRelease:
                embed.add_field(name='Illegal', value=f'{name} is too highly rated to be released.')
                valid = False
            #team
            if p['tid'] != commandInfo['userTid']:
                embed.add_field(name='Illegal', value=f"{name} is not on your team.")
                valid = False
            if valid:
                #confirmation
                text = f'Are you sure you want to release {name} ({rating})? This action can not be reversed. Click the ✅ to confirm.'
                confirmMessage = await commandInfo['message'].channel.send(text)
                await confirmMessage.add_reaction('✅')
                def check(reaction, user):
                    return reaction.message == confirmMessage and user == commandInfo['message'].author and str(reaction.emoji) == '✅'
                try:
                    reaction, user = await shared_info.bot.wait_for('reaction_add', timeout=60, check=check)
                except asyncio.TimeoutError:
                    await confirmMessage.edit(content='❌ Release timed out.')
                else:
                    await confirmMessage.edit(content='Releasing player...')
                    await basics.release_player(p['pid'], commandInfo['message'], commandInfo)
                    await confirmMessage.edit(content='**Complete.**')
                    embed = None
    return embed

async def autocut(embed, text, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    teams = export['teams']
    season = export['gameAttributes']['season']

    maxRoster = export['gameAttributes']['maxRosterSize']

    for t in teams:
        roster = []
        for p in players:
            if p['tid'] == t['tid']:
                autocutFormula = (p['ratings'][-1]['ovr'] + p['ratings'][-1]['pot'])
                if p['contract']['exp'] == season:
                    autocutFormula+=0.3
                if p['draft']['year'] == season or (p['draft']['year'] == season-1 and export['gameAttributes']['phase'] == 0):
                    autocutFormula += 0.5
                roster.append([p['pid'], autocutFormula])
        roster.sort(key=lambda r: r[1], reverse=True)
        toCut = len(roster) - maxRoster
        if toCut > 0:
            releasePlayers = roster[-toCut:]
            for r in releasePlayers:
                print(r[0])
                export = await basics.release_player(r[0], commandInfo['message'], commandInfo, updateexport=False, export=export)
    current_dir = os.getcwd()
    path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
    await basics.save_db(export, path_to_file)
    embed.add_field(name='Complete', value='Autocuts done.')
    return embed





