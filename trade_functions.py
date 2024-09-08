from shared_info import serverExports
from shared_info import serversList
import pull_info
import basics
import discord
from discord.utils import get
import asyncio
import math
import shared_info
from input_trade import input_trade
import re

async def scan_text(text, message):
    text = text.split('@')
    if text[0].startswith('<@&'):
        firstIndex = 0
        secondIndex = 1
    else:
        firstIndex = 1
        secondIndex = 2
    if len(text) < secondIndex+1:
        errorText = f"**{message.guild.name} Trade Confirmation Channel**" + '\n' + f"> {message.content}" + '\n' + '\n' + 'Your format seems to be invalid. Make sure that two team roles are pinged.'
        try:
            await message.delete()
        except Exception:
            firstIndex = firstIndex * 1
        await message.author.send(errorText)
    else:
        #teamOneLine = text[firstIndex].split(',')
        teamOneLine = re.split(r',\s*|\s+and\s+',text[firstIndex])
        teamOneRole = teamOneLine[0].split(' ')[0].replace('&', '').replace('>', '')
        try:
            role = get(message.guild.roles, id=int(teamOneRole))
        except ValueError:
            errorText = f"**{message.guild.name} Trade Confirmation Channel**" + '\n' + f"> {message.content}" + '\n' + '\n' + 'Your format seems to be invalid. Make sure that two team roles are pinged.'
            await message.delete()
            await message.author.send(errorText)
            return
        teamOneName = role.name.strip().replace("  "," ")
        teamOneAssets = [' '.join(teamOneLine[0].split(' ')[1:])] + teamOneLine[1:]
        #teamTwoLine = text[secondIndex].split(',')
        teamTwoLine = re.split(r',\s*|\s+and\s+', text[secondIndex])
        teamTwoRole = teamTwoLine[0].split(' ')[0].replace('&', '').replace('>', '')
        role = get(message.guild.roles, id=int(teamTwoRole))
        teamTwoName = role.name.strip().replace("  "," ")
        teamTwoAssets = [' '.join(teamTwoLine[0].split(' ')[1:])] + teamTwoLine[1:]
        #check that teams are valid
        export = shared_info.serverExports[str(message.guild.id)]
        teams = export['teams']
        players = export['players']
        foundTeams = 0
        for t in export['teams']:
            if t['region'].strip() + ' ' + t['name'].strip() in [teamOneName, teamTwoName]:
                foundTeams += 1
        if foundTeams < 2:
            errorText = f"**{message.guild.id} Trade Confirmation Channel**" + '\n' + f"> {message.content}" + '\n' + '\n' + 'One of the specified roles does not correspond to a team in the export. Check with moderators to make sure the role name matches perfectly with the full names of teams.'
            try:
                await message.delete()
            except Exception:
                foundTeams = foundTeams*1
            await message.author.send(errorText)
        else:
            #make the trade dict, pass it along to an inputting function
            for t in teams:
                if t['region'].strip() + ' ' + t['name'].strip() == teamOneName:
                    teamOneTid = t['tid']
                if t['region'].strip() + ' ' + t['name'].strip() == teamTwoName:
                    teamTwoTid = t['tid']
            tradeAssets = {
                teamOneTid: teamOneAssets,
                teamTwoTid: teamTwoAssets
            }
            errors = []
            tradeData = {
                teamOneTid: [],
                teamTwoTid: []
            }
            for team, assets in tradeAssets.items():
                for a in assets:
                    print(a)
                    #check if asset is nothing
                    if 'nothing' not in str.lower(a) and len(a)>1:
                        a = a.replace("to the","").replace(" for ","").replace(" trade","").replace(" traded","")
                        #check if a has a year in it - if so, it's a draft pick
                        draftPick = False
                        for i in range(0, 3000):
                            if str(i) in a:
                                draftPick = True
                                pickYear = i
                        if draftPick:
                            pickData = basics.find_pick_info(a, export)
                            if pickData['tid'] == None:
                                pickData['tid'] = team
                            #now find the pick in question
                            picks = export['draftPicks']
                            found = False
                            print(pickData)
                            for p in picks:
                                if p['season'] == pickData['year'] and p['round'] == pickData['round'] and p['originalTid'] == pickData['tid']:
                                    found = True
                                    #check if team in question actually owns pick
                                    ownerOfPick = p['tid']
                                    if ownerOfPick == team:
                                        if p['originalTid'] != p['tid']:
                                            for t in teams:
                                                if t['tid'] == p['originalTid']:
                                                    abbrev = t['abbrev']
                                            pickTeamText = f" ({abbrev})"
                                        else:
                                            pickTeamText = ''
                                        tradeData[team].append({
                                            "type": 'draftPick',
                                            "descrip": f"{p['season']} round {p['round']} pick{pickTeamText}",
                                            "id": p['dpid']
                                        })
                                    else:
                                        for t in teams:
                                            if t['tid'] == team:
                                                name = t['region']
                                            if t['tid'] == ownerOfPick:
                                                owner = t['region']
                                        errors.append(f"``{a}`` is not owned by {name}. It's owned by {owner}.")
                            if found == False:
                                errors.append(f"Did not find a draft pick under the name ``{a}``. Please try again.")
                        else:
                            if a != 'trade' and a != 'for':
                                #it's a player!
                                player = basics.find_match(a, export, False, True)
                                for p in export['players']:
                                    if p['pid'] == player:
                                        if p['tid'] == team:
                                            tradeData[team].append({
                                                "type": 'player',
                                                "descrip": p['firstName'] + ' ' + p['lastName'],
                                                "id": p['pid']
                                            })
                                        else:
                                            for t in teams:
                                                if t['tid'] == team:
                                                    name = t['region']
                                            errors.append(f"{p['firstName'] + ' ' + p['lastName']} is not on {name}.")
            if len(errors) > 0:
                embed = discord.Embed(title='Trade Confirmation', description=f"{message.guild.name}, {export['gameAttributes']['season']} season")
                errorText = ""
                for e in errors:
                    errorText += e + '\n'
                if len(errorText) <= 1000:
                    embed.add_field(name='Errors Detected', value=errorText)
                else:
                    errorText = errorText.split('\n')
                    split1 = len(errorText) // 4
                    split2 = split1*2
                    split3 = split1*3
                    part1 = '\n'.join(errorText[:split1])
                    part2 = '\n'.join(errorText[split1:split2])
                    part3 = '\n'.join(errorText[split2:split3])
                    part4 = '\n'.join(errorText[split3:])
                    embed.add_field(name='Errors Detected', value=part1)
                    embed.add_field(name='Continued', value=part2)
                    embed.add_field(name='Continued', value=part3)
                    embed.add_field(name='Continued', value=part4)
                await message.channel.send(embed=embed)
            else:
                #slightly reformat tradeData
                #additional validity checks
                players = export['players']
                teams = export['teams']
                events = export['events']

                #use this list to apply all checks to both teams - will be applied as tid, otherTid
                tradeTeams = [[teamOneTid, teamTwoTid], [teamTwoTid, teamOneTid]]
                
                #store violations
                errors = []

                #cap
                salaryCap = export['gameAttributes']['salaryCap']/1000
                hardCap = float(serversList[str(message.guild.id)]['hardcap'])

                #start with cap checks
                for tid, otherTid in tradeTeams:
                    startingPayroll = 0
                    for p in players:
                        if p['tid'] == tid:
                            startingPayroll += p['contract']['amount']
                    payrollOut = 0
                    for a in tradeData[tid]:
                        if a['type'] == 'player':
                            for p in players:
                                if p['pid'] == a['id']:
                                    payrollOut += p['contract']['amount']
                    payrollIn = 0
                    for a in tradeData[otherTid]:
                        if a['type'] == 'player':
                            for p in players:
                                if p['pid'] == a['id']:
                                    payrollIn += p['contract']['amount']
                    endingPayroll = ((payrollIn - payrollOut) + startingPayroll)/1000
                    if endingPayroll > hardCap:
                        for t in teams:
                            if t['tid'] == tid:
                                text = f"{t['region']} goes over the hard cap, reaching a payroll of ${endingPayroll}M, exceeding the hard cap by ${endingPayroll - hardCap}M."
                                errors.append(text)
                    #125%
                    if endingPayroll > salaryCap:
                        try: 
                            amount = (payrollIn/payrollOut)
                            amountText = round((payrollIn / payrollOut), 4)*100
                        except ZeroDivisionError:
                            amount = 100
                            amountText = 'infinity'

                        if amount > 1.25999 and payrollIn != 0:
                            for t in teams:
                                if t['tid'] == tid:
                                    text = f"{t['region']} is over the salary cap, and they take in more than 125% of the salary they send out, taking in {amountText}%."
                                    errors.append(text)
                #check validity of players being traded
                for tid, otherTid in tradeTeams:
                    assets = tradeData[tid]
                    for a in assets:
                        if a['type'] == 'player':
                            #FA check
                            for p in players:
                                if p['pid'] == a['id']:
                                    if p['gamesUntilTradable'] > 0:
                                        text = f"{p['firstName']} {p['lastName']} is a recently signed free agent, and cannot be traded."
                                        errors.append(text)
                            if serversList[str(message.guild.id)]['tradeback'] == 'off':
                                #must make sure player a['id'] was not traded away from otherTid in this season
                                for e in events:
                                    if e['season'] == export['gameAttributes']['season'] and e['type'] == 'trade':
                                        if int(otherTid) in e['tids']:
                                            if e['tids'][0] == otherTid:
                                                index = 1
                                            if e['tids'][1] == otherTid:
                                                index = 0
                                            for asset in e['teams'][index]['assets']:
                                                if 'pid' in asset:
                                                    if asset['pid'] == a['id']:
                                                        for p in players:
                                                            if p['pid'] == a['id']:
                                                                text = f"{p['firstName']} {p['lastName']} was traded away from this team earlier in the season, meaning he can not be traded back until the next."
                                                                errors.append(text)
                            #check expirings during draft time
                            if export['gameAttributes']['phase'] in [3, 4, 5, 6]:
                                #expirings cannot be dealt
                                for p in players:
                                    if p['pid'] == a['id']:
                                        if p['contract']['exp'] == export['gameAttributes']['season']:
                                            text = f"{p['firstName']} {p['lastName']} is expiring and, since the regular season had ended, cannot be traded."
                                            errors.append(text)
                #END OF CHECKS
                # ########
                #either way, we're going to put the trade on the screen, so generate that text now.
                tradeText = ""
                for team, assets in tradeData.items():
                    for t in teams:
                        if t['tid'] == team:
                            teamName = t['region'] + ' ' + t['name']
                            abbrev = t['abbrev']
                    role = basics.team_mention(message,teamName, abbrev, emoji_add = False)
                    
                    emoji = discord.utils.get(message.guild.emojis, name=str.lower(abbrev))
                    if emoji is not None:
                        teamText = role
                    else:
                        teamText = role
                    tradeText += f"{teamText} trade:" + '\n'
                    for a in assets:
                        if a['type'] == 'player':
                            for p in players:
                                if p['pid'] == a['id']:
                                    tradeText += f"{a['descrip']} ({export['gameAttributes']['season'] - p['born']['year']}yo {p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']}, ${p['contract']['amount']/1000}M/{p['contract']['exp']})" + '\n'
                    for a in assets:
                        if a['type'] == 'draftPick':
                            a['descrip'] = a['descrip'].replace('round 1', '1st round').replace('round 2', '2nd round').replace('round 3', '3rd round')
                            tradeText += a['descrip'] + '\n'
                embed = discord.Embed(title='Trade Confirmation', description=f"{message.guild.name}, {export['gameAttributes']['season']} season")
                print(len(tradeText))
                if len(tradeText) <= 1000:
                    embed.add_field(name='Trade', value=tradeText)
                else:
                    tradeText = tradeText.split('\n')
                    midpoint = len(tradeText) // 2
                    embed.add_field(name='Trade', value='\n'.join(tradeText[:midpoint]))
                    embed.add_field(name='Trade', value='\n'.join(tradeText[midpoint:]))
                #embed.add_field(name='Trade', value=tradeText)
                

                if errors != []:
                    errorText = ""
                    for e in errors:
                        errorText += e + '\n'
                    embed.add_field(name='Errors Detected', value=errorText)
                else:
                    confirmTeams = [teamOneTid, teamTwoTid]
                    try:
                        gmTid = serversList[str(message.guild.id)]['teamlist'][str(message.author.id)]
                    except KeyError:
                        gmTid = -1
                    if gmTid in confirmTeams:
                        confirmTeams.remove(gmTid)
                    teamsText = ""
                    for t in teams:
                        if t['tid'] in confirmTeams:
                            teamsText += ' ' + t['abbrev']
                    serversList[str(message.guild.id)]['openTrades'].append({
                        "tradeData": tradeData,
                        "confirmationNeeded": confirmTeams,
                        "season": export['gameAttributes']['season'],
                        "phase": export['gameAttributes']['phase']
                    })
                    embed.add_field(name='Confirmation', value=f'To confirm this trade, confirmation is required from the following team(s):{teamsText}' + '\n' + "*To confirm, simply type 'confirm' in the channel.*", inline=False)

                
                await message.channel.send(embed=embed)

async def confirm_message(message):
    export = shared_info.serverExports[str(message.guild.id)]
    players = export['players']
    teams = export['teams']
    events = export['events']
    openTrades = serversList[str(message.guild.id)]['openTrades']
    #find the most recent open trade concerning the user who sent it
    confirmedTrade = None
    for o in openTrades:
        try:
            authorTid = serversList[str(message.guild.id)]['teamlist'][str(message.author.id)]
        except KeyError:
            authorTid = -1
        if authorTid in o['confirmationNeeded']:
            confirmedTrade = o
    if confirmedTrade == None:
        text = f"**{message.guild.name} Trade Confirmation Channel**" + '\n' + 'You attempted to confirm a trade, but no trade awaiting your confirmation was found.'
        await message.author.send(text)
        await message.delete()
    else:
        confirmedTrade['confirmationNeeded'].remove(authorTid)
        if confirmedTrade['confirmationNeeded'] != []:
            for t in teams:
                if t['tid'] == confirmedTrade['confirmationNeeded'][0]:
                    teamName = t['abbrev']
            text = f"✅ **Confirmed.** Trade is still awaiting confirmation from {teamName}."
            await message.channel.send(text)
            basics.save_db(serversList)
        else:
            #trade has been confirmed. time to put it through
            text = '✅ Trade confirmation received. Waiting on database save. Until you see the words trade finalized, it has not gone through'
            waitingMessage = await message.channel.send(text)
            await input_trade(export, confirmedTrade['tradeData'], message)
            await waitingMessage.edit(content='**Trade finalized.**')


