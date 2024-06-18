import shared_info
from shared_info import serverExports
from shared_info import serversList
import pull_info
import basics
import discord
import free_agency_runner
import asyncio
import os
import random
import copy
async def decidepo(embed, text, commandInfo):
    export = shared_info.serverExports[commandInfo['serverId']]
    message = commandInfo['message']
    serverSettings = serversList[str(commandInfo['serverId'])]
    if serverSettings['options'] == "off":
        await message.channel.send("I'll give you an option, to turn on the options, to take on this option, just run -edit options on")
        return embed
    if not 'PO' in serverSettings:
        await message.channel.send("There were no player options. LAME")
        return embed
    todelete = []
    transChannel = shared_info.bot.get_channel(int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', '')))
    await transChannel.send("POs")
    print("weird")
    print(transChannel)
    for po in serverSettings['PO']:
        pid = int(po)
        expiration = int(serverSettings['PO'][po][1])
        amount = float(serverSettings['PO'][po][0])
        print(expiration)
        if expiration == export['gameAttributes']['season']:
            print("got here")
            todelnegs = []
            for neg in export['negotiations']:
                if neg['pid'] == pid:
                    player = None
                    for p in export['players']:
                        if p['pid'] == pid:
                            player = p
                    askingamount = player['contract']['amount']/1000
                    if askingamount < amount:
                        t = neg['tid']
                        todelnegs.append(neg)
                        team = export['teams'][t]
                        abbrev = team['abbrev']
                        tname = team['region']+" "+team['name']
                        # accepts player option
                        p = player
                        p['tid'] = team['tid']
                        p['contract'] = {
                            "amount": amount*1000,
                            "exp":expiration + 1
                        }
                        p['gamesUntilTradable'] = serversList[str(commandInfo['serverId'])]['traderesign']
                        
                        for i in range(0,1):
                            salaryInfo = dict()
                            salaryInfo['season'] = expiration + i + 1
                            salaryInfo['amount'] = amount*1000
                            p['salaries'].append(salaryInfo)
                        events = export['events']
                        newEvent = dict()
                        newEvent['text'] = 'The <a href="/l/10/roster/' + team['abbrev'] + '/' + str(expiration) + '">' + tname + '</a> re-signed <a href="/l/10/player/' + str(p['pid']) + '">' + p['firstName'] + ' ' + p['lastName'] + '</a> for $' + str(amount) + 'M/year through ' + str(1 + expiration) +' as accepted the player option.'
                        newEvent['pids'] = [p['pid']]
                        newEvent['tids'] = [team['tid']]
                        newEvent['season'] = expiration
                        newEvent['type'] = 'reSigned'
                        newEvent['eid'] = events[-1]['eid'] + 1
                        events.append(newEvent)
                                    #print(p['tid'])
                        
                        
                       
                        message2 = player['firstName']+" "+player['lastName']+ " decides to **accept** his player option for "+basics.team_mention(message, tname, abbrev)+"."
                        try:
                            transChannel = shared_info.bot.get_channel(int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', '')))
                            await transChannel.send(message2)
                        except Exception:
                            await message.channel.send(message2)
                    else:
                        t = export['teams'][neg['tid']]
                        abbrev = t['abbrev']
                        tname = t['region']+" "+t['name']
                        message2 = player['firstName']+" "+player['lastName']+ " decides to **reject** his player option for "+basics.team_mention(message, tname, abbrev)+"."

                        try:
                            transChannel = shared_info.bot.get_channel(int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', '')))
                            await transChannel.send(message2)
                        except Exception:
                            await message.channel.send(message2)

            todelete.append(po)
            for item in todelnegs:
                export['negotiations'].remove(item)
    # MUST DELETE THE PO, JUST NOT NOW, BUT AFTER IT WORKS
    for td in todelete:
        del serverSettings['PO'][td]
    current_dir = os.getcwd()
    path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
    await basics.save_db(export, path_to_file)
    await basics.save_db(serversList)
    return embed
        
    
async def match(embed, text, commandInfo):
    export = shared_info.serverExports[commandInfo['serverId']]
    if not export['gameAttributes']['phase'] == 8:
        embed.add_field(name = "Are you dumb?", value = "You are, cause you tried to run match command outside of Free Agency phase")
        return embed
    if serversList[commandInfo['serverId']]['rfa'] == 'off':
        embed.add_field(name = "Are you dumb?", value = "You are, cause you tried run match in a server that has not enabled rfa")
        return embed
    name = ' '.join(text[1:])
    offerPlayer = basics.find_match(name, export, True,settings =  shared_info.serversList[str(commandInfo['serverId'])])
    for p in export['players']:
        if p['pid'] == offerPlayer:
            offerPlayer = p
    s = offerPlayer['ratings'][-1]['skills']
    if len(s) > 1 and s[-1].__contains__('RFA'):
        #is rfa
        teamabbrev = s[-1].split(",")[1]

        for t in export['teams']:
            print(t['abbrev'])
            if t['abbrev'] == teamabbrev:
                
                tid = t['tid']
                print("ok")
        if tid == commandInfo['userTid']:
            #right team
            players = export['players']
            payroll = 0
            playersRostered = 0
            serverSettings = serversList[str(commandInfo['serverId'])]
            for player in players:
                if player['tid'] == tid:
                    payroll += player['contract']['amount']
                    if player['draft']['year'] == export['gameAttributes']['season']:
                         if serverSettings['rookiescount'] == 'on':
                            playersRostered += 1
                    else:
                        playersRostered += 1
            try:
                for rp in export['releasedPlayers']:
                    if rp['tid'] == tid:
                        payroll += rp['contract']['amount']
            except: pass
            payroll = payroll/1000
            hardCap = float(serversList[str(commandInfo['serverId'])]['hardcap'])
            if payroll + offerPlayer['contract']['amount'] <= hardCap:
            

                transaction = {
                    "season": export['gameAttributes']['season'],
                    "phase": export['gameAttributes']['phase'],
                    "tid": tid,
                    "type": "freeAgent"
                }
                try:
                    offerPlayer['transactions'].append(transaction)
                except KeyError:
                    offerPlayer['transactions'] = []
                    offerPlayer['transactions'].append(transaction)
                offerPlayer['tid'] = tid
                t = offerPlayer['ratings'][-1]['skills'][0:-1]
                offerPlayer['ratings'][-1].update({'skills':t})
                embed.add_field(name = "Restricted FA?", value = "You matched the player")
                
                transChannel = shared_info.bot.get_channel(int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', '')))

                for t in export['teams']:

                    if t['tid'] == tid:
                         name = t['region'] + ' ' + t['name']
                         abbrev = t['abbrev']
                         
                roleMention = basics.team_mention(commandInfo['message'],name, abbrev)
                pname = offerPlayer['firstName']+" "+offerPlayer['lastName']+" ("+str(offerPlayer['ratings'][-1]['ovr'])+"/"+str(offerPlayer['ratings'][-1]['pot'])+")"
                playerName = offerPlayer['firstName']+" "+offerPlayer['lastName']
                adjective = "merrily"
                d = roleMention+" "+adjective+" matched "+pname+" to a "+str(offerPlayer['contract']['amount']/1000)+"M/"+str(offerPlayer['contract']['exp']-export['gameAttributes']['season'])+"Y contract."
                await transChannel.send(d)
                #b = 1/0
                current_dir = os.getcwd()
                path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
                if True:
                    events = export['events']
                    season = export['gameAttributes']['season']
                    eventText = f'The <a href="/l/10/roster/{teamabbrev}/{season}">{name}</a> matched restricted free agent <a href="/l/10/player/{offerPlayer["pid"]}">{playerName}</a> '+" to a "+str(offerPlayer['contract']['amount']/1000)+"M/"+str(offerPlayer['contract']['exp']-export['gameAttributes']['season'])+"Y contract."       
                    #transaction
                    transaction = {
                        "season": season,
                        "phase": 8,
                        "tid": tid,
                        "type": "freeAgent"
                    }
                    try:
                        offerPlayer['transactions'].append(transaction)
                    except KeyError:
                        offerPlayer['transactions'] = []
                        offerPlayer['transactions'].append(transaction)

                    #event
                    newEvent = {
                        'text': eventText,
                        'pids': [offerPlayer['pid']],
                        'tids': [tid],
                        'season': season,
                        'type': 'freeAgent',
                        'eid': events[-1]['eid']+1
                    } 
                    events.append(newEvent)
                await basics.save_db(export, path_to_file)
                return embed
            else:
                embed.add_field(name = "Are you soft?", value = "You aren't, in fact, you were gonna exceed the hard cap if you matched this plyaer")
                return embed
        else:
            embed.add_field(name = "Are you a spy?", value = "You probably aren't, but given that you were trying to match a player whose matching rights aren't with your team, you might as well be trying to be one.")
            return embed
    else:
        embed.add_field(name = "Are you an illusionist?", value = "Cause you sure were pretending a player to be RFA when he was not.")
        return embed
            
            
            
async def qo(embed, text, commandInfo):
    offerList = serversList[commandInfo['serverId']]['offers']
    if commandInfo['message'].content.__contains__("/"):
        await commandInfo['message'].channel.send("Note: qualifying offers are always 1 year long and 1.5 times the rookie contract in value")
    export = shared_info.serverExports[commandInfo['serverId']]
    if not export['gameAttributes']['phase'] == 7:
    #not resignings
        embed.add_field(name = "Are you dumb?", value = "You are, cause you tried to run qo command outside of Resignings phase")
        return embed
    if serversList[commandInfo['serverId']]['rfa'] == 'off':
        embed.add_field(name = "Are you dumb?", value = "You are, cause you tried run qo in a server that has not enabled rfa")
        return embed
    
    validFormat = True


    name = ' '.join(text[1:])
    validFormat=True


    if validFormat:
        offerPlayer = basics.find_match(name, export, True,settings =  shared_info.serversList[str(commandInfo['serverId'])])
        #Qualifying offer conditions
        for p in export['players']:
           if int(p['pid']) == int(offerPlayer):
                offerPlayer = p

                break
        #create a list of the team's re-signings - should be useful
        resigns = export['negotiations']
        teamResigns = []
        for r in resigns:
            try:
                if r['tid'] == commandInfo['userTid'] and r['resigning'] == True:
                    for p in export['players']:
                        if p['pid'] == r['pid']:
                            playerRating = p['ratings'][-1]['ovr'] + p['ratings'][-1]['pot']
                    teamResigns.append([r['pid'], playerRating])
            except KeyError: pass
        isresigned = False
        for element in teamResigns:
            if element[0] == offerPlayer['pid']:
                isresigned = True
        #teamResigns.sort(key=lambda r: r[1], reverse=True)
        if offerPlayer['draft']['round'] == 1:
            print('A')
        if isresigned:
            print('B')
        if offerPlayer['draft']['year'] + export['gameAttributes']['rookieContractLengths'][0] == export['gameAttributes']['season']:
            print('C')
        if offerPlayer['draft']['round'] == 1 and isresigned and offerPlayer['draft']['year'] + export['gameAttributes']['rookieContractLengths'][0] == export['gameAttributes']['season']:
            amount = offerPlayer['salaries'][-1]['amount']*float(serversList[commandInfo['serverId']]['rfamultiplier'])/1000
            years = 1
            print("got here")
            legalOffer = True
            if offerPlayer['tid'] != -1:
                if offerPlayer['tid'] < -1:
                    legalOffer = False
                    embed.add_field(name='Illegal Offer', value=f"{offerPlayer['name']} isn't active, and thus you cannot offer them.")
                else:
                    embed.add_field(name='⚠️ Warning', value='This player is not currently a free agent. The offer has been recorded in case you anticipate that they will become a free agent, but it might be invalidated before FA is run.', inline=False)
            print(legalOffer)

            #now specific validity checks
            if amount > (export['gameAttributes']['maxContract']/1000) or amount < (export['gameAttributes']['minContract']/1000):
                embed.add_field(name='Illegal Offer', value=f'Your amount of ${amount}M is not within the min/max contracts for the league.' + '\n' + f"Max contract: ${export['gameAttributes']['maxContract']/1000}M" + '\n' + f"Min Contract: ${export['gameAttributes']['minContract']/1000}M", inline=False)
                legalOffer = False
            print(legalOffer)
            priority = 1
            for o in offerList:
                if o['team'] == commandInfo['userTid']:
                    priority += 1
            
            if legalOffer:
                print('got to legal offer')
                offer = {
                    "player": offerPlayer['pid'],
                    "amount": amount,
                    "years": years,
                    "team": commandInfo['userTid'],
                    "option": None,
                    "priority": priority,
                    'qo':True
                    
                }
                
                toDelete = []
                for o in offerList:
                    if o['team'] == commandInfo['userTid'] and o['player'] == offerPlayer['pid']:
                        toDelete.append(o)
                for d in toDelete:
                    offerList.remove(d)
                if toDelete != []:
                    embed.add_field(name='Offer Deleted', value='A previous offer for this player was cleared.', inline=False)


                offerList.append(offer)
                serversList[commandInfo['serverId']]['offers'] = offerList
                await basics.save_db(serversList)

                #score
                offerScore = round(await free_agency_runner.offer_score(offer, commandInfo['serverId']), 2)
                name = offerPlayer['firstName']+' '+offerPlayer['lastName']
                if export['gameAttributes']['phase'] == 7:
                    players = export['players']
                    season = export['gameAttributes']['season']
                    playerPrices = await free_agency_runner.resign_prices(offerPlayer['pid'], commandInfo['userTid'], export, commandInfo['serverId'],  getvalues(players, season, export))
                    odds = await basics.resign_odds(playerPrices, years, amount)
                    odds = str(round(odds*100, 2))
                    
                    optionText = ""
                    embed.add_field(name='✅ Qualifying Offer Submitted', value=('Review details below:' + '\n' +
                    f"**Player:** {name} ({offerPlayer['ratings'][-1]['ovr']}/{offerPlayer['ratings'][-1]['pot']})" + '\n' +
                    f"**Contract:** ${amount}M/{years} years" + optionText) + '\n' +
                    f"**Priority:** #{priority} (can be edited)" + '\n' +
                    f"**Odds to accept:** {odds}%" + '\n' +  "(**Warning:** These odds can change before re-signings are run if you make trades or other roster moves, if such moves change player asking prices.)" + '\n' +
                    f'*Offers cannot be edited (except priority). To change this offer, delete it with {serversList[commandInfo["serverId"]]["prefix"]}deloffer [player name] and re-offer.*')
                
                if serversList[str(commandInfo['serverId'])]['openmarket'] == 'on':

                    for o in offerList:
                        o['score'] = await free_agency_runner.offer_score(o, commandInfo['serverId'])
                    playerOffers = []
                    for o in offerList:
                        if int(o['player']) == int(offerPlayer['pid']):
                            if o['option'] != None:
                                optionText = f", + {o['option']}"
                            else:
                                optionText = ""
                            playerOffers.append({
                                "team": o['team'],
                                "score": o['score'],
                                "offer": f"${o['amount']}M/{o['years']}Y{optionText}"
                            })
                    print(playerOffers)
                    playerOffers = sorted(playerOffers, key=lambda o: o['score'], reverse = True)
                    text = f">>> **{name} - Top 5 Offers**" + '\n' 
                    for o in playerOffers[:5]:
                        for t in export['teams']:
                            if t['tid'] == o['team']:
                                name = t['region'] + ' ' + t['name']
                                abbrev = t['abbrev']
                        roleMention = basics.team_mention(commandInfo['message'],name, abbrev)
                        text += f"• {roleMention} - {o['offer']} (score: **{round(o['score'], 2)}**)" + '\n'

                    channelId =int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', ''))
                    channel = shared_info.bot.get_channel(channelId)
                    if isinstance(channel, discord.TextChannel):
                        print("PRINTING")
                        await channel.send(text)
                    else:
                        commandInfo['message'].channel.send('Your FA channel is invalid, so top 5 offers were not sent to it.')

            
    return embed
async def offer(embed, text, commandInfo):
    if commandInfo['userTid'] < 0:
        embed.add_field(name='Don\'t jump the gun', value='You better get a GM offer from a team first before you think of giving one.')
        return embed
    offerList = serversList[commandInfo['serverId']]['offers']
    export = shared_info.serverExports[commandInfo['serverId']]
    validFormat = False


    if len(text) <= 2:
        name = ' '.join(text[1:])
        validFormat=True
        minContract = export['gameAttributes']['minContract']/1000
        offerText = f'{minContract}/1'
    else:
        if '/' in text[2]:
            name = text[1]
            validFormat = True
            offerText = text[2]
        else:
            if len(text) >= 4:
                if '/' in text[3]:
                    validFormat = True
                    offerText = text[3]
                    name = text[1] + ' ' + text[2]
                else:
                    if len(text) >= 5:
                        if '/' in text[4]:
                            validFormat = True
                            offerText = text[4]
                            name = text[1] + ' ' + text[2] + ' ' + text[3]
                        else:
                            name = ' '.join(text[1:])
                            validFormat=True
                            minContract = export['gameAttributes']['minContract']/1000
                            offerText = f'{minContract}/1'
                    else:
                        name = ' '.join(text[1:])
                        validFormat=True
                        minContract = export['gameAttributes']['minContract']/1000
                        offerText = f'{minContract}/1'
            else:
                name = ' '.join(text[1:])
                validFormat=True
                minContract = export['gameAttributes']['minContract']/1000
                offerText = f'{minContract}/1'
    if validFormat:
        offerPlayer = basics.find_match(name, export, True,settings =  shared_info.serversList[str(commandInfo['serverId'])])
        for p in export['players']:
            if p['pid'] == offerPlayer:
                offerPlayer = pull_info.pinfo(p)
                offerPlayerAdvanced = p
        offerText = offerText.split('/')
        try: 
            amount = float(offerText[0])
            amount = round(amount, 2)
        except: validFormat = False
        try: years = int(offerText[1])
        except: validFormat = False
        if validFormat:
            #CHECK SERVER CONTRACT RULES
            if 'crules' in serversList[commandInfo['serverId']]:
                rules = serversList[commandInfo['serverId']]['crules']
            else:
                rules = []
            ovr = offerPlayerAdvanced['ratings'][-1]['ovr']
            age = export['gameAttributes']['season']-offerPlayerAdvanced['born']['year']
            legalOffer = True
            if not export['gameAttributes']['phase'] == 7:
                for r in rules:
                    if age <= r['age'] and ovr >= r['ovr']:
                        if amount < r['amount'] and years > r['years']:
                            legalOffer = False
                            embed.add_field(name="Yo! S'up Fam?", value = "You violated the contract rule "+organize(r,export))
                            return embed
                                            
                
            #check for extras
            option = None
            if len(offerPlayerAdvanced['ratings'][-1]['skills']) > 0 and 'RFA' in offerPlayerAdvanced['ratings'][-1]['skills'][-1]:
                if amount < offerPlayerAdvanced['salaries'][-1]['amount']*float(serversList[commandInfo['serverId']]['rfamultiplier'])/1000:
                    pname = offerPlayer['name']
                    embed.add_field(name = "Are you a lawyer?", value = "Cause you sure are trying to find a legal loophole.\nHowever, "+pname+" is a restricted FA. Offer at least "+str(offerPlayerAdvanced['salaries'][-1]['amount']*float(serversList[commandInfo['serverId']]['rfamultiplier'])/1000)+" million. **It's the law!**")
                    return embed
            if str.upper(text[-1]) == 'PO' or str.upper(text[-1]) == 'TO':
                if serversList[commandInfo['serverId']]['options'] == 'on':
                    option = str.upper(text[-1])
                else:
                    embed.add_field(name='⚠️ Warning', value='You attempted to offer an option, which is not turned on for this server. Therefore, that part of the offer was ignored.', inline=False)

            if offerPlayer['tid'] != -1:
                if offerPlayer['tid'] < -1:
                    legalOffer = False
                    embed.add_field(name='Illegal Offer', value=f"{offerPlayer['name']} isn't active, and thus you cannot offer them.")
                else:
                    embed.add_field(name='⚠️ Warning', value='This player is not currently a free agent. The offer has been recorded in case you anticipate that they will become a free agent, but it might be invalidated before FA is run.', inline=False)
            else:
                askingPrice = offerPlayer['contractAmount']
                holdoutLimit = float(serversList[commandInfo['serverId']]['holdout'])/100 * askingPrice
                if amount < holdoutLimit:
                    embed.add_field(name='⚠️ Warning', value=f'This server currently has holdouts enabled, and your offer of ${amount}M falls below the holdout amount for this player of ${holdoutLimit}M. Feel free to keep this offer in case that limit changes or in case the asking price decreases, but it might be invalidated before FA is run.')
                tuodlohLimit = float(serversList[commandInfo['serverId']]['tuodloh'])/100 * askingPrice
                if amount > tuodlohLimit and tuodlohLimit > 0:
                    embed.add_field(name='⚠️ Warning', value=f'This server currently has tuodloh limits enabled, and your offer of ${amount}M falls above the tuodloh amount for this player of ${tuodlohLimit}M. Feel free to keep this offer in case that limit changes or in case the asking price decreases, but it might be invalidated before FA is run.')
                    
                
                

            #now specific validity checks
            if amount > (export['gameAttributes']['maxContract']/1000) or amount < (export['gameAttributes']['minContract']/1000):
                embed.add_field(name='Illegal Offer', value=f'Your amount of ${amount}M is not within the min/max contracts for the league.' + '\n' + f"Max contract: ${export['gameAttributes']['maxContract']/1000}M" + '\n' + f"Min Contract: ${export['gameAttributes']['minContract']/1000}M", inline=False)
                legalOffer = False
            
            if option == None:
                realYears = years
            else:
                realYears = years+1
            if realYears > (export['gameAttributes']['maxContractLength']) or realYears < (export['gameAttributes']['minContractLength']):
                embed.add_field(name='Illegal Offer', value=f'Your length of {years} years (with player or team options being counted as a year) is not within the min/max years for the league.' + '\n' + f"Max years: {export['gameAttributes']['maxContractLength']}" + '\n' + f"Min years: {export['gameAttributes']['minContractLength']}", inline=False)
                legalOffer = False

            #three year rule
            if serversList[commandInfo['serverId']]['threeyearrule'] == 'on' and export['gameAttributes']['phase'] != 7:
                if years > 2 and amount < (export['gameAttributes']['minContract']/1000)*2.5:
                    min = (export['gameAttributes']['minContract']/1000)*2.5
                    legalOffer = False
                    embed.add_field(name='Illegal Offer', value=f'Offers 3 or more years must be at least ${min}M per year.')

            #figure out the priority
            priority = 1
            for o in offerList:
                if o['team'] == commandInfo['userTid']:
                    priority += 1
            
            if legalOffer:
                offer = {
                    "player": offerPlayer['pid'],
                    "amount": amount,
                    "years": years,
                    "team": commandInfo['userTid'],
                    "option": option,
                    "priority": priority,
                    'qo':False
                }

            optionText = ""
            if option != None:
                optionText = f", + {option}"
            if legalOffer:
                toDelete = []
                for o in offerList:
                    if o['team'] == commandInfo['userTid'] and o['player'] == offerPlayer['pid']:
                        toDelete.append(o)
                        priority = o['priority']
                        offer.update({'priority':priority})
                for d in toDelete:
                    offerList.remove(d)
                if toDelete != []:
                    embed.add_field(name='Offer Deleted', value='A previous offer for this player was cleared.', inline=False)


                offerList.append(offer)
                serversList[commandInfo['serverId']]['offers'] = offerList
                await basics.save_db(serversList)

                #score
                offerScore = round(await free_agency_runner.offer_score(offer, commandInfo['serverId']), 2)
                if export['gameAttributes']['phase'] == 7:
                    players = export['players']
                    season = export['gameAttributes']['season']
                    playerPrices = await free_agency_runner.resign_prices(offerPlayer['pid'], commandInfo['userTid'], export, commandInfo['serverId'], getvalues(players, season, export))
                    odds = await basics.resign_odds(playerPrices, years, amount)
                    odds = str(round(odds*100, 2))
                    embed.add_field(name='✅ Offer Submitted', value=('Review details below:' + '\n' +
                    f"**Player:** {offerPlayer['name']} ({offerPlayer['ovr']}/{offerPlayer['pot']})" + '\n' +
                    f"**Contract:** ${amount}M/{years} years" + optionText) + '\n' +
                    f"**Priority:** #{priority} (can be edited)" + '\n' +
                    f"**Odds to accept:** {odds}%" + '\n' +  "(**Warning:** These odds can change before re-signings are run if you make trades or other roster moves, if such moves change player asking prices.)" + '\n' +
                    f'*Offers cannot be edited (except priority). To change this offer, delete it with {serversList[commandInfo["serverId"]]["prefix"]}deloffer [player name] and re-offer.*')
                
                else:
                    embed.add_field(name='✅ Offer Submitted', value=('Review details below:' + '\n' +
                    f"**Player:** {offerPlayer['name']} ({offerPlayer['ovr']}/{offerPlayer['pot']})" + '\n' +
                    f"**Contract:** ${amount}M/{years} years" + optionText) + '\n' +
                    f"**Priority:** #{priority} (can be edited)" + '\n' +
                    f"**Score:** {offerScore} (what player views offer as worth)" + '\n' +
                    f'*Offers cannot be edited (except priority). To change this offer, delete it with {serversList[commandInfo["serverId"]]["prefix"]}deloffer [player name] and re-offer.*')
                

                if serversList[str(commandInfo['serverId'])]['openmarket'] == 'on':
                    for o in offerList:
                        o['score'] = await free_agency_runner.offer_score(o, commandInfo['serverId'])
                    playerOffers = []
                    for o in offerList:
                        if int(o['player']) == int(offerPlayer['pid']):
                            if o['option'] != None:
                                optionText = f", + {o['option']}"
                            else:
                                optionText = ""
                            playerOffers.append({
                                "team": o['team'],
                                "score": o['score'],
                                "offer": f"${o['amount']}M/{o['years']}Y{optionText}"
                            })
                    print(playerOffers)
                    playerOffers = sorted(playerOffers, key=lambda o: o['score'], reverse = True)
                    text = f">>> **{offerPlayer['name']} - Top 5 Offers**" + '\n' 
                    for o in playerOffers[:5]:
                        for t in export['teams']:
                            if t['tid'] == o['team']:
                                name = t['region'] + ' ' + t['name']
                                abbrev = t['abbrev']
                        roleMention = basics.team_mention(commandInfo['message'],name, abbrev)
                        text += f"• {roleMention} - {o['offer']} (score: **{round(o['score'], 2)}**)" + '\n'

                    channelId =int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', ''))
                    channel = shared_info.bot.get_channel(channelId)
                    if isinstance(channel, discord.TextChannel):
                        print("PRINTING")
                        await channel.send(text)
                    else:
                        commandInfo['message'].channel.send('Your FA channel is invalid, so top 5 offers were not sent to it.')


                
                
    return embed
async def bulkoffer(embed, text, commandInfo):
    export = shared_info.serverExports[commandInfo['serverId']]
    #print(text)
    contractinfoword = ""
    for item in text:
        if "/" in item:
            contractinfoword = item
    if contractinfoword == "":
        await commandInfo['message'].channel.send("invalid info, defaulting to min")
        contractinfoword = str(export['gameAttributes']['minContract']/1000)+"/1"
    divisions = commandInfo['message'].content.split(",")
    for t in range (0, len(divisions)):
        item = divisions[t].strip()
        if t == 0:
            item = " ".join(item.split(" ")[1:])
        for word in item.split(" "):
            if word.__contains__("/"):
                item = item.replace(word,"").strip()

        embed = await offer(embed, ("offer"+" "+item+" "+contractinfoword).split(" "),commandInfo)
    return embed
    
        
async def offers(embed, text, commandInfo):
    offerList = serversList[commandInfo['serverId']]['offers']
    export = shared_info.serverExports[commandInfo['serverId']]
    players = export['players']
    userOffers = []
    for o in offerList:
        if o['team'] == commandInfo['userTid']:
            userOffers.append(o)
    userOffers.sort(key=lambda o: o['priority'])
    textLines = []
    playerName = "Blank"
    for u in userOffers:
        playerName = "Unknown player "+str(u['player'])
        for p in players:
            if p['pid'] == u['player']:
                playerName = p['firstName'] + ' ' + p['lastName']
        if u['option'] != None:
            optionText = f', + {u["option"]}'
        else:
            optionText = ""
        text = f"Pri {u['priority']} - {playerName}, ${u['amount']}M/{u['years']}Y {optionText}"
        textLines.append(text)
    output = []
    for i in range(0, len(textLines), 20):
        output.append(textLines[i:i+20])
    for o in output:
        fieldText = ""
        for l in o:
            fieldText += l + '\n'
        embed.add_field(name='Offers', value=fieldText)
    if userOffers == []:
        embed.add_field(name='No offers!', value='Start making some by running the ``help offer`` command.', inline=False)
    
    toSign = 'Max Possible'
    toSignData = serversList[commandInfo['serverId']]['toSign']
    for t, v in toSignData.items():
        if t == str(commandInfo['userTid']) or t == commandInfo['userTid']:
            toSign = str(v)
    
    embed.add_field(name=f'Max Players to Sign: {toSign}', value='Edit this with ``-tosign [new number]``, or ``-tosign reset``', inline=False)

    
    return(embed)

async def deloffer(embed, text, commandInfo):
    offerList = serversList[commandInfo['serverId']]['offers']
    export = shared_info.serverExports[commandInfo['serverId']]
    playerToDelete = ' '.join(text[1:])
    playerToDelete = basics.find_match(playerToDelete, export,settings =  shared_info.serversList[str(commandInfo['serverId'])])
    toDelete = []
    for p in export['players']:
            if p['pid'] == playerToDelete:
                name = p['firstName'] + ' ' + p['lastName']
    for o in offerList:
        if o['team'] == commandInfo['userTid'] and o['player'] == playerToDelete:
            toClear = o
    
    try: 
        offerList.remove(toClear)
        embed.add_field(name='Success', value=f'Deleted offer for {name}.')
        await basics.save_db(serversList)
    except: 
        embed.add_field(name='Error', value=f"No offer found for {name}.")
    return embed

async def clearoffers(embed, text, commandInfo):
    offerList = serversList[commandInfo['serverId']]['offers']
    toClear = []
    for o in offerList:
        if o['team'] == commandInfo['userTid']:
            toClear.append(o)
    for t in toClear:
        offerList.remove(t)
    embed.add_field(name='Success', value='Cleared all your team\'s offers.')
    return embed
async def clearalloffers(embed, text, commandInfo):
    offerList = serversList[commandInfo['serverId']]['offers']
    toClear = []
    for o in offerList:
        toClear.append(o)
    for t in toClear:
        offerList.remove(t)
    embed.add_field(name='Success', value='Cleared all leaguewide offers.')
    return embed

async def move(embed, text, commandInfo):
    offerList = serversList[commandInfo['serverId']]['offers']
    export = shared_info.serverExports[commandInfo['serverId']]
    playerToMove = ' '.join(text[1:-1])
    print(playerToMove)
    playerToMove = basics.find_match(playerToMove, export,settings =  shared_info.serversList[str(commandInfo['serverId'])])
    newPriority = text[-1]
    try: newPriority = int(text[-1])
    except: 
        embed.add_field(name='Error', value='Please specify an integer as your new priority as the last word in the command.')
        return embed
    if isinstance(newPriority, int):
        for o in offerList:
            if o['team'] == commandInfo['userTid'] and o['player'] == playerToMove:
                currentPriority = o['priority']
                if currentPriority > newPriority:
                    o['priority'] = newPriority-0.1
                if currentPriority < newPriority:
                    o['priority'] = newPriority+0.1
                embed.add_field(name='Complete', value=f'Moved player to priority {newPriority}.')
        await basics.save_db(serversList)
        return embed
def organize(item, export):
    p = "Any player "
    if item['ovr'] > 0:
        if item['age'] >= 100:
            
            p = "Above "+str(item['ovr'])+" overall "

        else:
            p = "Above** "+str(item['ovr'])+"** overall and at most **"+str(item['age'])+"** age "
    else:
        if item['age'] < 100:
            p = "Players at most **"+str(item['age'])+"** in age "
    if item['amount'] > export['gameAttributes']['minContract']/1000:
        p += "can't sign for < **"+str(item['amount'] )+"**M/Yr"
        if item['years'] > 0:
            p += " for over **"+str(item['years'])+"** yrs."
    else:
        p += " can't sign for over **"+str(item['years'])+"** yrs."
    return p
async def viewrules(embed, text, commandInfo):
    
    if not "crules" in serversList[commandInfo['serverId']]:
        embed.add_field(name = "No rules", value = "What do you want me to say. Your server's got no contract rules! Other than the minimum contract length in the export and the maximum contract length in the export and the minimum contract amount in the export and the.......")
        return embed

    l = serversList[commandInfo['serverId']]['crules']

    finalstring = ""
    count = 1
    for item in l:
        p = organize(item,shared_info.serverExports[commandInfo['serverId']])
        finalstring += str(count)+". "+p + "\n"
        count += 1
    embed.add_field(name = "All rules", value = finalstring)
    return embed
async def deleterule(embed, text, commandInfo):
    if not "crules" in serversList[commandInfo['serverId']]:
        embed.add_field(name = "No rules", value = "What do you want me to say. Your server's got no contract rules! Other than the minimum contract length in the export and the maximum contract length in the export and the minimum contract amount in the export and the.......")
        return embed
    l = serversList[commandInfo['serverId']]['crules']
    order = -1
    for item in text:
        try:
            order = int(item)
        except ValueError:
            pass
    if order >= 1:
        if order > len(l):
            return embed
        d = l[order-1]
        l.remove(l[order-1])
        serversList[commandInfo['serverId']].update({'crules':l})
        await basics.save_db(serversList)
        embed.add_field(name = "removed rule", value = "removed the rule of "+organize(d,shared_info.serverExports[commandInfo['serverId']])+". \nNOTE: If you are trying to remove multiple rules, the deletion of this rule might have re-numbered the other rules. Please check -contractrules again to make sure you are not deleting the wrong one.")
        return embed
    else:
        return embed
        
async def addrule(embed, text, commandInfo):
    ovr = 0
    age = 100
    years = 0
    amount =  shared_info.serverExports[commandInfo['serverId']]['gameAttributes']['minContract']/1000
    print(text)
    for item in text[1:]:
        if item.count(":") == 1:
            if item.split(":")[0] == "ovr":
                try:
                    ovr = int(item.split(":")[1])
                except ValueError:
                    embed.add_field(name = "Seems like you might have had a wrong format", value = "format should be -addcontractrule ovr:50 age:23 amount:3 years:4 and that means that anyone above 50 overall and at most 23 age could not be offered a contract less than 3 million and contract length over 4 years. For disallowance for any amount of years, leave the years blank.")
                    return embed
            elif item.split(":")[0] == "age":
                try:
                    age = int(item.split(":")[1])
                except ValueError:
                    embed.add_field(name = "Seems like you might have had a wrong format", value = "format should be -addcontractrule ovr:50 age:23 amount:3 years:4 and that means that anyone above 50 overall and at most 23 age could not be offered a contract less than 3 million and contract length over 4 years. For disallowance for any amount of years, leave the years blank.")
                    return embed
            elif item.split(":")[0] == "amount":
                try:
                    amount = float(item.split(":")[1])
                except ValueError:
                    embed.add_field(name = "Seems like you might have had a wrong format", value = "format should be -addcontractrule ovr:50 age:23 amount:3 years:4 and that means that anyone above 50 overall and at most 23 age could not be offered a contract less than 3 million and contract length over 4 years. For disallowance for any amount of years, leave the years blank.")
                    return embed
            elif item.split(":")[0] == "years":
                try:
                    years = int(item.split(":")[1])
                except ValueError:
                    embed.add_field(name = "Seems like you might have had a wrong format", value = "format should be -addcontractrule ovr:50 age:23 amount:3 years:4 and that means that anyone above 50 overall and at most 23 age could not be offered a contract less than 3 million and contract length over 4 years. For disallowance for any amount of years, leave the years blank.")
                    return embed
            else:
                embed.add_field(name = "Seems like you might have had a wrong format", value = "format should be -addcontractrule ovr:50 age:23 amount:3 years:4 and that means that anyone above 50 overall and at most 23 age could not be offered a contract less than 3 million and contract length over 4 years. For disallowance for any amount of years, leave the years blank.")
                return embed
        else:
            embed.add_field(name = "Seems like you might have had a wrong format", value = "format should be -addcontractrule ovr:50 age:23 amount:3 years:4 and that means that anyone above 50 overall and at most 23 age could not be offered a contract less than 3 million and contract length over 4 years. For disallowance for any amount of years, leave the years blank.")
            return embed
        
    if years ==0 and amount == shared_info.serverExports[commandInfo['serverId']]['gameAttributes']['minContract']/1000:
        embed.add_field(name = "Seems like you might have had a wrong format", value = "format should be -addcontractrule ovr:50 age:23 amount:3 years:4 and that means that anyone above 50 overall and at most 23 age could not be offered a contract less than 3 million and contract length over 4 years. For disallowance for any amount of years, leave the years blank.")
        return embed
    else:
        if not "crules" in serversList[commandInfo['serverId']]:
            print("ok")
            serversList[commandInfo['serverId']].update({'crules':[]})
        l = serversList[commandInfo['serverId']]['crules']
        d = {"ovr":ovr,"age":age,"amount":amount,"years":years}
        if not d in l:
            l.append({"ovr":ovr,"age":age,"amount":amount,"years":years})
        else:
            print("repeated")
        serversList[commandInfo['serverId']].update({'crules':l})
        await basics.save_db(serversList)
        embed.add_field(name = "The league just got a little bit worse!", value = "Cause you just added a contract rule that said that \n"+organize(d, shared_info.serverExports[commandInfo['serverId']])+"\n If you want to delete the rule, run contractrules to see which number this rule is, and run deleterules and provide that rule number.")
        return embed
        
        
async def tosign(embed, text, commandInfo):
    toSign = None
    print(text)
    try: 
        toSign = int(text[1])
    except:
        if str.lower(text[1]) == 'reset':
            try: del serversList[commandInfo['serverId']]['toSign'][str(commandInfo['userTid'])]
            except: pass
            embed.add_field(name='Complete', value='Reset max number of players to sign to maximum.')
        else:

            embed.add_field(name='Error', value='Please set your new maximum signed players to an integer or a species of marsupials.')
    print(serversList[commandInfo['serverId']]['toSign'])
    if toSign != None:
        
        serversList[commandInfo['serverId']]['toSign'].update({str(commandInfo['userTid']): toSign})
        embed.add_field(name='Success', value=f"Set your maximum number of players to sign to {toSign}.")
    await basics.save_db(serversList)
    
    return embed

async def runfa(embed, text, commandInfo):
    export = shared_info.serverExports[commandInfo['serverId']]
    if export['gameAttributes']['phase'] == 7:
        print("detected")
        if not commandInfo['message'].content.__contains__("runfa force"):
            print("ok")
            embed.add_field(name = "It's resignings phase", value = "You should not really be able to run FA.You should call runrs if you want to do resignings. If you still want to do so, do '-runfa force'")
            return embed
    offerList = copy.deepcopy(serversList[commandInfo['serverId']]['offers'])
    
    serverSettings = serversList[str(commandInfo['serverId'])]
    players = export['players']
    teams = export['teams']
    delay = 0
    if len(text) > 1:
        if text[1] == 'delay':
            try: delay = int(text[2])
            except: pass
    
    #BACK UP THE OFFERS
    for o in offerList:
        o['score'] = await free_agency_runner.offer_score(o, commandInfo['serverId'])
    serversList[str(commandInfo['serverId'])]['backupOffers'] = copy.deepcopy(offerList)
    await basics.save_db(serversList)
    #run it
    validOffers = 1
    signings = []
    playersDone = []
    invalidations = []
    finalSignings = []

    ct = 0
    while validOffers > 0:
        ct += 1
        faData = await free_agency_runner.run_fa2(offerList, signings, playersDone, invalidations, commandInfo['serverId'])
        offerList = faData[0]
        signings += faData[1]
        playersDone = faData[2]
        invalidations += faData[3]
        validOffers = faData[5]
        finalSignings += faData[4]
        print('---')
        print(faData[4])
    signingLines = []
    for f in finalSignings:
        for p in players:
            if p['pid'] == f['player']:
                name = p['firstName'] + ' ' + p['lastName']
        for t in teams:
            if t['tid'] == f['team']:
                teamName = t['abbrev']
        text = f"{name}, {teamName} - ${f['amount']}M/{f['years']}Y"
        signingLines.append(text)
    signingLines = [signingLines[i:i+20] for i in range(0, len(signingLines), 20)]
    for s in signingLines:
        s = '\n'.join(s)
        await commandInfo['message'].author.send(s)
    invalidations = set(invalidations)
    invalidations = list(invalidations)
    await commandInfo['message'].author.send('**ERRORS**')
    for i in invalidations:
        await commandInfo['message'].author.send(i)
    confirmEmbed = discord.Embed(
    title='Confirmation',
    description=f"{export['gameAttributes']['season']} season")
    confirmEmbed.add_field(name='FA Completed', value="I've DMd you the list of signings for a last look. Press the ✅ to send signings to the server's FA channel, update the server export file with the signings, and clear all existing offers from database.")
    confirmEmbed = await commandInfo['message'].channel.send(embed=confirmEmbed)
    print("sent embed")
    await confirmEmbed.add_reaction('✅')
    def check(reaction, user):
        return str(reaction.emoji) == '✅' and user == commandInfo['message'].author and reaction.message.id == confirmEmbed.id

    try:
        reaction, user = await shared_info.bot.wait_for('reaction_add', timeout=60, check=check)
    except asyncio.TimeoutError:
        await confirmEmbed.edit(content='❌ Timed out.')
        serverSettings = serversList[str(commandInfo['serverId'])]
        for s in finalSignings:
            if s['option'] == "PO":
                del serverSettings['PO'][s['player']]
            if s['option'] == "TO":
                del serverSettings['TO'][s['player']]
        await basics.save_db(serversList)
                                   
        #serversList[commandInfo['serverId']].update({'offers':serversList[str(commandInfo['serverId'])]['backupOffers']})
        current_dir = os.getcwd()
        path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
        shared_info.serverExports[commandInfo['serverId']] = basics.load_db(path_to_file)
    else:
        await confirmEmbed.edit(content='✅ Confirmed. Sending signings to transaction channel...')
        errorSent = False
        for o in finalSignings:
            

            for p in players:
                if p['pid'] == o['player']:
                    name = p['firstName'] + ' ' + p['lastName']
                    rating = f"{p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']}"
                    age = str(export['gameAttributes']['season'] - p['born']['year'])
                    pos = p['ratings'][-1]['pos']
                    traits = ' '.join(p['moodTraits'])
            for t in teams:
                if t['tid'] == o['team']:
                    teamName = t['region'] + ' ' + t['name']
                    abbrev = t['abbrev']
            text = '>>> **FA Signing**' + '\n' + '--' + '\n'
            roleMention = basics.team_mention(commandInfo['message'],teamName, abbrev, emoji_add = False)
            emoji = discord.utils.get(commandInfo['message'].guild.emojis, name=str.lower(abbrev))
            if emoji is not None:
                teamText = f"{roleMention} {emoji}"
            else:
                teamText = roleMention
            adj = shared_info.getadjective()
            if 'qo' in o and o['qo']:
                text += f"The {teamText} {adj} signed restricted free agent **{name}** to a qualifying offer of {o['years']}-year, ${o['amount']}M contract." + '\n'
            else:
                text += f"The {teamText} {adj} signed **{name}** to a {o['years']}-year, ${o['amount']}M contract." + '\n'
            text += f"{pos} - {age} yo {rating} | *Traits: {traits}*" + '\n' + '--'

            #send message to channel
            errorSent = False
            channelId = int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', ''))
            channel = shared_info.bot.get_channel(channelId)
            if isinstance(channel, discord.TextChannel):
                # Send the message to the channel
                await channel.send(text)
            else:
                if errorSent == False:
                    commandInfo['message'].channel.send('Your FA channel is invalid, so signings were not sent. FA was still executed.')
                    errorSent = True
        await confirmEmbed.edit(content='✅ **Signings sent!** Now, saving changes to server export file...')
        current_dir = os.getcwd()
        path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
        await basics.save_db(export, path_to_file)
        await basics.save_db(serversList)
        await confirmEmbed.edit(content='✅ **Signings sent! FA Complete.** Run -updateexport for a new link. \nIf you are sure the signings were correctly done, **run -clearalloffers** to clear all the offers. They do not automatically clear.')
    
    return embed

def value(age, ovr, ws, prin = False):
    if age == 23 and ovr == 56:
        print(ws)

    if prin:
        print("VALUE")
        print(age)
        print(ovr)
    if age <= 19:
        ovr += (20-age)*8
    if age <= 20:
        ovr += 5
    if age <= 21:
        ovr += 4
    if age <= 22:
        ovr += 3
    if age <= 23:
        ovr += 2
    if age <= 24:
        ovr += 2
    if age > 25:
        ovr = ovr - (age-25)*1
    ovr = ovr + ws

    if prin:
        print(ovr)

    return ovr
def getvalues(players, season, export):
    values = dict()
    for p in players:

        if p['retiredYear'] == None:
            if p['draft']['year'] < season:
                ws = 0
                gp = 0

                age = season-p['born']['year']
                ovr = p['ratings'][-1]['ovr']
                
                for s in p['stats']:
                    if s['season'] == season and not s['playoffs']:
                        gp += s['gp']
                        ws += s['ows']+s['dws']
                if gp > 0:
                    g = export['gameAttributes']['numGames']
                    if isinstance(g, int):
                        if gp < export['gameAttributes']['numGames'] * 0.8:
                            ws = ws * (export['gameAttributes']['numGames'] * 0.8/gp)
                    else:
                        g = g[-1]['value']
                        if gp < g * 0.8:
                            ws = ws * (g * 0.8/gp)

 
                v = value(age, ovr, ws)
                values.update({p['pid']:v})
    return values

async def resignings(embed, text, commandInfo):
    if commandInfo['userTid'] < 0:
        embed.add_field(name='Resignings', value='The only resigning you\'ll get is your past resigning from whatever team you last managed.')
        return embed
    offerList = serversList[commandInfo['serverId']]['offers']
    export = shared_info.serverExports[commandInfo['serverId']]
    players = export['players']
    season = export['gameAttributes']['season']
    settings = export['gameAttributes']
    if settings['phase'] != 7:
        embed.add_field(name='Error', value='Export must be in the re-signings phase.')
        return embed

    #create a list of the team's re-signings - should be useful
    resigns = export['negotiations']
    teamResigns = []
    for r in resigns:
        
        try:
            if r['tid'] == commandInfo['userTid'] and r['resigning'] == True:
                for p in players:
                    if p['pid'] == r['pid']:
                        playerRating = p['ratings'][-1]['ovr'] + p['ratings'][-1]['pot']
                teamResigns.append([r['pid'], playerRating])
        except KeyError: pass
    teamResigns.sort(key=lambda r: r[1], reverse=True)


    lines = []
    # calculates value for all (active) players
    
    values = getvalues(players, season, export)

    if len(text) == 1:
        progressMessage = await commandInfo['message'].channel.send('Calculating re-signings prices...')
        numberAdded = 0
        for r, pr in teamResigns:
            
            for p in players:
                if p['pid'] == r:
                    numberAdded += 1
                    rating = str(p['ratings'][-1]['ovr']) + '/' + str(p['ratings'][-1]['pot'])
                    age = str(season - p['born']['year'])
                    reSignPrice = await free_agency_runner.resign_prices(p['pid'], commandInfo['userTid'], export, commandInfo['serverId'],  values)
                    lines.append(p['ratings'][-1]['pos'] + ' ' + p['firstName'] + ' ' + p['lastName'] + ' (' + age + 'yo ' + rating + ') - $' + str(reSignPrice['main'][0]/1000) + 'M / ' + str(reSignPrice['main'][1]) + 'Y')
        if lines == []:
            lines.append('None!')
        lines.append('')
        lines.append(f'Run -rs [player name] to see what each player wants over different years. Use -offer just like in free agency to offer a player. An offer at or above their asking price for the given years will always be accepted. An offer lower will be randomly accepted or declined, with the chances depending on how much lower it is.' + '\n' + 'If you have team options, you can accept them with -ao [player].')
        numDivs, rem = divmod(len(lines), 10)
        numDivs += 1
        for i in range(numDivs):
            newLines = lines[(i*10):((i*10)+10)]
            text = '\n'.join(newLines)
            if text !='':
                embed.add_field(name='Re-Signings', value=text, inline = False)
        
        #team option check
        optionsText = ""
        for r, pr in teamResigns:
            for p in players:
                if p['pid'] == r:
                    if 'note' and 'noteBool' in p:
                        if 'note' == f"Option: {season+1} TO":
                            optionAmount = p['salaries'][-1]['amount']/1000
                            optionsText += p['ratings'][-1]['pos'] + ' ' + p['firstName'] + ' ' + p['lastName'] + ' - $' + str(optionAmount) + 'M TO' + '\n'
        if optionsText != "":
            embed.add_field(name='Team Options', value=optionsText, inline=False)
        #cap space
        salaryCap = settings['salaryCap']
        hardCap = float(serversList[str(commandInfo['serverId'])]['hardcap'])*1000
        teamPayroll = 0
        for p in players:
            if p['tid'] == commandInfo['userTid']:
                teamPayroll += p['contract']['amount']
        try:
            for r in export['releasedPlayers']:
                if r['tid'] == commandInfo['userTid']:
                    teamPayroll += r['contract']['amount']
        except: pass
        #sum of offers
        offerSum = 0
        for o in offerList:
            if o['team'] == commandInfo['userTid']:
                offerSum += float(o['amount'])
        #tie it together
        capText = "Salary Cap Room: $" + str((salaryCap - teamPayroll)/1000) + 'M' + '\n' + 'Hard Cap Room: $' + str((hardCap - teamPayroll)/1000) + 'M' + '\n' + 'Sum of current offers: $' + str(round(offerSum, 2)) + 'M'
        if round(offerSum, 2)*1000 + teamPayroll > hardCap:
            capText += '\n' + '⚠️ Warning: Your offers total more than the hard cap, which means that they cannot all be accepted. Check your offers priority list to ensure you have them sorted correctly (re-signings are ran in priority order).'
        embed.add_field(name='Finances', value=capText, inline=False)
        await progressMessage.delete()


    else:
        pid = basics.find_match(' ' + ' '.join(text[1:]), export, True,settings =  shared_info.serversList[str(commandInfo['serverId'])])
        for p in players:
            if p['pid'] == pid:
                if [p['pid'], p['ratings'][-1]['ovr'] + p['ratings'][-1]['pot']] in teamResigns:
                    reSignPrice = await free_agency_runner.resign_prices(p['pid'], commandInfo['userTid'], export, commandInfo['serverId'],  getvalues(players, season, export))
                    text = ""
                    for r in reSignPrice:
                        if r != 'main':
                            if r == reSignPrice['main'][1]:
                                text += '**'
                            text += str(r) + 'Y: $' + str(reSignPrice[r]/1000) + 'M'
                            if r == reSignPrice['main'][1]:
                                text += '**'
                            text += '\n'
                    embed.add_field(name=p['firstName'] + ' ' + p['lastName'] + ' Re-Signing Prices', value=text)
                else:
                    embed.add_field(name='Error', value=p['firstName'] + ' ' + p['lastName'] + " isn't up for re-signing on your team.")
    return embed

import random
async def reset(embed, text, commandInfo):
    export = shared_info.serverExports[commandInfo['serverId']]
    players = export['players']
    for p in players:
        p.update({'gamesUntilTradable':0}) 
    current_dir = os.getcwd()
    path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
    await basics.save_db(export, path_to_file)
    embed.add_field(name='Complete', value='everyone can now be traded.')
    return embed
async def runresign(embed, text, commandInfo):
  
    offerList = serversList[commandInfo['serverId']]['offers']
    export = shared_info.serverExports[commandInfo['serverId']]
    players = export['players']
    teams = export['teams']
    season = export['gameAttributes']['season']
    print("started get value")
    values = getvalues(players, season, export)
    print("ended get value")
    settings = export['gameAttributes']
    serverSettings = serversList[str(commandInfo['serverId'])]
    todelete = []
    if 'PO' in serverSettings:
        for po in serverSettings['PO']:
            if int(serverSettings['PO'][po][1]) <= season:
                todelete.append(po)
    for po in todelete:
        del serverSettings['PO'][po]
    todelete = []
    if 'TO' in serverSettings:
        for to in serverSettings['TO']:
            if int(serverSettings['TO'][to][1]) <= season:
                todelete.append(to)
    for to in todelete:
        del serverSettings['TO'][to]
    await basics.save_db(serversList)
    print("got here 1")
    await commandInfo['message'].channel.send("Calculating prices, wait a moment.")
    if settings['phase'] == 7:
        pricesDb = {}
        for n in export['negotiations']:
            print(n)
            pricesDb[str(n['pid'])] = await free_agency_runner.resign_prices(n['pid'], n['tid'], export, commandInfo['serverId'],  values)
        print("got here 2")
        for team in teams:
            if team['disabled'] == False:
                teamOffers = []
                text = ""
                #run re-signings for each team
                for o in offerList:
                    if o['team'] == team['tid']:
                        teamOffers.append(o)
                teamOffers.sort(key=lambda t: int(t['priority']))
                for t in teamOffers:
                    for p in players:
                        if p['pid'] == t['player']:
                            valid = False
                            for n in export['negotiations']:
                                if n['pid'] == p['pid'] and n['tid'] == team['tid']:
                                    valid = True
                            payroll = 0
                            for pl in players:
                                if pl['tid'] == team['tid']:
                                    payroll += pl['contract']['amount']
                            try:
                                for rp in export['releasedPlayers']:
                                    if rp['tid'] == team['tid']:
                                        payroll += rp['contract']['amount']
                                            
                            except: pass
                            if payroll + t['amount']*1000 > settings['luxuryPayroll']:
                                valid = False
                            if valid:
                                print("ok")
                                accepted = False
                                #time for the sauce
                                playerPrices = pricesDb[str(p['pid'])]
                                probability = await basics.resign_odds(playerPrices, float(t['years']), float(t['amount']))
        
                                if random.random() <= probability:
                                    accepted = True
                                else:
                                    teamList = serversList[str(commandInfo['serverId'])]['teamlist']
                                    for tl in teamList:
                                        if teamList[tl] == team['tid']:
                                            try:
                                                toDm =shared_info.bot.get_user(int(tl))
                                                print(toDm)
                                                textToSend = p['firstName'] + ' ' + p['lastName'] + ' declines your offer (' + str(round(probability*100, 2)) + '% chance to accept).'
                                                await toDm.send(textToSend)
                                            except Exception as e:
                                                print(e)
                                    transChannel = shared_info.bot.get_channel(int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', '')))
                                    await transChannel.send(textToSend)

                                if accepted:
                                    #re-signing festivities
                                    print('got here')
                                    p['tid'] = team['tid']
                                    p['contract'] = {
                                        "amount": t['amount']*1000,
                                        "exp": season + t['years']
                                    }
                                    p['gamesUntilTradable'] = serversList[str(commandInfo['serverId'])]['traderesign']
                                    for i in range(t['years']):
                                        salaryInfo = dict()
                                        salaryInfo['season'] = season + i + 1
                                        salaryInfo['amount'] = t['amount']*1000
                                        p['salaries'].append(salaryInfo)
                                    events = export['events']
                                    newEvent = dict()
                                    newEvent['text'] = 'The <a href="/l/10/roster/' + team['abbrev'] + '/' + str(season) + '">' + team['name'] + '</a> re-signed <a href="/l/10/player/' + str(p['pid']) + '">' + p['firstName'] + ' ' + p['lastName'] + '</a> for $' + str(t['amount']) + 'M/year through ' + str(float(t['years']) + season) + '.'
                                    newEvent['pids'] = [p['pid']]
                                    newEvent['tids'] = [team['tid']]
                                    newEvent['season'] = season
                                    newEvent['type'] = 'reSigned'
                                    newEvent['eid'] = events[-1]['eid'] + 1
                                    events.append(newEvent)
                                    #print(p['tid'])
                                    text += '• **' + p['firstName'] + ' ' + p['lastName'] + '** - $' + str(t['amount']) + 'M/' + str(t['years']) + ' years' + '\n'
                                else:
                                    #label players as restricted FA
                                    
                                    if t['qo']:
                                        print(t)
                                        string = "RFA,"
                                        for tm in export['teams']:
                                            if tm['tid'] ==t['team']:
                                                string = string + tm['abbrev']
                                        for p in export['players']:
                                            if p['pid'] == t['player']:
                                                s = p['ratings'][-1]['skills']
                                                s.append(string)
                                                p['ratings'][-1].update({'skills':s})
                                                
                                    
                if text == "":
                    text = "*No players.*" + '\n'
                finalText = '>>> **Re-Signings**' + '\n' + '--' + '\n' + 'The '
                rolePing = basics.team_mention(commandInfo['message'], team['region'] + ' ' + team['name'], team['abbrev'])
                finalText += rolePing + ' re-sign:' + '\n' + text + '--'
                #print(int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', '')))
                transChannel = shared_info.bot.get_channel(int(serversList[str(commandInfo['serverId'])]['fachannel'].replace('<#', '').replace('>', '')))
                await transChannel.send(finalText)
        current_dir = os.getcwd()
        path_to_file = os.path.join(current_dir, "exports", f"{commandInfo['serverId']}-export.json")
        await basics.save_db(export, path_to_file)
        embed.add_field(name='Complete', value='Re-Signings run. Run -updateexport to get a new link.')
    else:
        print("could not")
        embed.add_field(name='Could Not Run Re-Signings', value='Make sure your export is in the re-signings phase, and that you have mod permissions.')
    return embed
