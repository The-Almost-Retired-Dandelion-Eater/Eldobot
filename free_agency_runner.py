import shared_info
exports = shared_info.serverExports
serversList = shared_info.serversList
import basics
import pull_info
import fa_commands
import discord
import copy
import random

async def offer_score(offer, serverId):

    serverExport = shared_info.serverExports[str(serverId)]
    players = serverExport['players']
    teams = serverExport['teams']
    season = serverExport['gameAttributes']['season']
    for p in players:
        
        if p['pid'] == offer['player']:

            playerOvr = p['ratings'][-1]['ovr']
            playerPos = p['ratings'][-1]['pos']
            playerAge = p['born']['year'] - season
            playerStats = p['stats'] #for loyalty calculation
            playerRequest = p['contract']['amount']
            #mood trait scores
            playerWinning = float(serversList[str(serverId)]['winning'])
            playerFame = float(serversList[str(serverId)]['fame'])
            playerLoyal = float(serversList[str(serverId)]['loyalty'])
            playerMoney = float(serversList[str(serverId)]['money'])
            
    
            if 'W' in p['moodTraits']:
                playerWinning += 1
            if 'F' in p['moodTraits']:
                playerFame += 1
            if 'L' in p['moodTraits']:
                playerLoyal += 1
            if '$' in p['moodTraits']:
                playerMoney += 1
            if playerAge > 25:
                playerWinning += (0.1*(playerAge - 25))
                playerLoyal += (0.1*(playerAge - 25))
            if playerAge < 25:
                playerFame += (0.33*(25 - playerAge))
                playerMoney += (0.33*(25 - playerAge))
            #calculate winning score (15% hype, 85% weighted win%)
            teamWinning = 0
            teamHype = -1000
            for t in teams:

                if t['tid'] == offer['team']:
                    #first step, weighted winning % over the past 5 years
                    ts = t['seasons']
                    #need this to make it expansion-team friendly
                    teamHype = 0.5
                    teamWinPercent = 0
                    if len(ts) == 0:
                        teamWinPercent = 0
                        teamHype = 0.5
                    else:
                        if len(ts) > 4:
                            lastSeasonMultiplier = 16
                            if serverExport['gameAttributes']['phase'] == 7:
                                lastSeasonMultiplier = 512
                            teamWinPercent = ((ts[-1]['won'] / (ts[-1]['won'] + ts[-1]['lost'] + 0.000000001))*lastSeasonMultiplier + (ts[-2]['won'] / (ts[-2]['won'] + ts[-2]['lost']))*8 + (ts[-3]['won'] / (ts[-3]['won'] + ts[-3]['lost']))*4 + (ts[-4]['won'] / (ts[-4]['won'] + ts[-4]['lost']))*2 + (ts[-5]['won'] / (ts[-5]['won'] + ts[-5]['lost']))*1) / (15 + lastSeasonMultiplier)
                        else:
                            teamWinPercent = (ts[-1]['won'] / (ts[-1]['won'] + ts[-1]['lost'] + 0.000000001))
                        teamHype = ts[-1]['hype']
                    teamWinning = teamWinPercent*0.85 + teamHype*0.15
            winningScore = (0.5 + teamWinning)*offer['amount']

            #calculate fame score (50% hype, 50% rotation)
            #hype variable should be made already. if it's not, we've got other errors on our hands anyway, so may as well assume it's there
            #rotation calculation
            playersBetter = 0
            for p2 in players:
                if p2['tid'] == offer['team'] and p2['ratings'][-1]['ovr'] >= playerOvr:
                    if p2['ratings'][-1]['pos'] == playerPos:
                        playersBetter += 1.5
                    else:
                        playersBetter += 0.75
            fameScore = (1.5 - playersBetter/10)
            if fameScore < 0.2:
                fameScore = 0.2
            if teamHype == -1000:
                teamHype = 0
            fameScore = (fameScore*0.5 + (teamHype + 0.5)*0.5)*offer['amount']

            #calculate money score (80% money per year, 20% total money)
            moneyScore = 0.8*offer['amount'] + 0.2*(offer['amount']*offer['years'])

            #loyalty score (15% years with team prior, 85% trade penalty)
            yearsWith = 0
            for s in playerStats:
                if 'tid' in s:
                    if s['tid'] == offer['team'] and s['playoffs'] == False:
                        yearsWith += 1
            #print(yearsWith)
            penalty = pull_info.trade_penalty(offer['team'], serverExport)
            loyalScore = ((1 + (yearsWith/10))*0.15 + ((1 - penalty)*0.85))*offer['amount']

            #combine our scores into the final offer score
            loyalScore = loyalScore*playerLoyal
            winningScore = winningScore*playerWinning
            moneyScore = moneyScore*playerMoney
            fameScore = fameScore*playerFame
            #add idiosyncratic component
            for t in teams:

                if t['tid'] == offer['team']:
                    string = t['abbrev']+t['region']+t['name']+"-----"+p['firstName']+" "+p['lastName']

            integer2 = 0
            for char in string:
                integer2 += ord(char)*ord(char)
            idiosyncratic = ((integer2 % 10000) / 10000)*((integer2 % 10000) / 10000)*offer['amount']+0.75*offer['amount']
            
            idiosyncraticweight = 0.05
            if 'idiosyncratic' in serversList[str(serverId)]:
                idiosyncraticweight = float(serversList[str(serverId)]['idiosyncratic'])
            finalScore = (loyalScore + winningScore + moneyScore + fameScore+idiosyncratic*idiosyncraticweight) / (playerLoyal + playerWinning + playerMoney + playerFame+idiosyncraticweight)
            #now for the final part... years!
            years = offer['years']
            if offer['amount'] < playerRequest/1000:
                
                if offer['option'] != None:
                    if offer['option'] == 'PO':
                        years -= 1
                    if offer['option'] == 'TO':
                        years += 1
                finalScore = finalScore*(1 + (-0.10*years))
            if offer['amount'] > playerRequest/1000:
                if offer['option'] != None:
                    if offer['option'] == 'PO':
                        years += 1
                    if offer['option'] == 'TO':
                        years -= 1
                finalScore = finalScore*(1 + (0.10*years))
            # Bugfix: options should be treated as +1 year for offers larger than asking price
            #adding later - options! 15% penalty for a TO. 15% boost for a PO.
            if offer['option'] != None:
                if offer['option'] == 'PO':
                    finalScore = finalScore*1.15
                if offer['option'] == 'TO':
                    finalScore = finalScore*0.85
                    
            #additional years boost
            if playerAge > 28:
                boost = 0.5 * (-0.75**(playerAge - 28)) + 0.5
                finalScore = finalScore*(1+boost*(offer['years']-1))


            

            finalScore = finalScore 

            return finalScore
async def validitytest(o,p,players,season,invalidations,signings,export,serverSettings,hardCap, playerName,teamName,serverId):
        settings = export['gameAttributes']
        salaryCap = settings['salaryCap']/1000

        minContract = settings['minContract']/1000
        
        valid = True

        #ROSTER
        maxRoster = serverSettings['maxroster']
        rostered = 0
        for player in players:
            if player['tid'] == o['team']:
                if player['draft']['year'] == season:
                    if serverSettings['rookiescount'] == 'on':
                        rostered += 1
                else:
                    rostered += 1
        if rostered > int(maxRoster):
            valid = False
            message = f"{playerName}'s offer from the {teamName} invalid due to max roster limit."
            if len(invalidations) < 50:
                invalidations.append(message)

        #PLAYER
        if p['tid'] > -1:
            valid = False
            message = f"{playerName}'s offer from the {teamName} invalidated due to player not being a free agent."
            if len(invalidations) < 50:
                invalidations.append(message)

        #TOSIGN
        totalSignings = signings.count(o['team'])
        #print(serversList[str(serverId)]['toSign'])
        try: toSign = int(serversList[str(serverId)]['toSign'][str(o['team'])])
        except:
            try:toSign = int(serversList[str(serverId)]['toSign'][o['team']])
            except:toSign = 100000000
        if totalSignings == toSign:
            valid = False
            message = f"{playerName}'s offer from the {teamName} invalidated due to team hitting their max signing number."
            if len(invalidations) < 50:
                invalidations.append(message)
        
        #SALARY CAP
        ##team payroll
        payroll = 0
        
        for player in players:
            if player['tid'] == o['team']:
                payroll += player['contract']['amount']
        try:
            releasedPlayers = export['releasedPlayers']
            for r in releasedPlayers:
                if r['tid'] == o['team']:
                    payroll += r['contract']['amount']
        except: pass
        payroll = payroll/1000
        birdPlayer = False
        if len(p['stats']) >= 1:
            if p['stats'][-1]['tid'] == o['team'] and serverSettings['birdrights'] == 'on':
                birdPlayer = True
        if o['amount'] == minContract or birdPlayer:
            #hardcap
            if payroll + o['amount']  > hardCap:
                valid = False
                message = f"{playerName}'s min offer from the {teamName} invalidated due to hard cap."
                if len(invalidations) < 50:
                    invalidations.append(message)
        else:
            if payroll + o['amount'] > salaryCap:
                valid = False
                message = f"{playerName}'s offer from the {teamName} invalidated due to going over the salary cap."
                if len(invalidations) < 50:
                    invalidations.append(message)
        o['bird'] = birdPlayer
        
        #HOLDOUTS
        holdoutMultiplier = float(serverSettings['holdout'])/100
        holdoutAmount = holdoutMultiplier*p['contract']['amount']
        tuodlohMultiplier = float(serverSettings['tuodloh'])/100
        tuodlohAmount = tuodlohMultiplier*p['contract']['amount']

        if o['amount'] < holdoutAmount*0.001:
            valid = False
            message = f"{playerName}'s offer from the {teamName} invalidated due to holdout threshold."
            if len(invalidations) < 50:
                invalidations.append(message)
        if o['amount'] > tuodlohAmount*0.001 and not tuodlohAmount < 0.00001:
            valid = False
            message = f"{playerName}'s offer from the {teamName} invalidated due to tuodloh threshold."
            if len(invalidations) < 50:
                invalidations.append(message)
        return [valid, invalidations]
async def run_fa2(offerList, signings, playersDone, invalidations, serverId):
    print('NEW FA2 RUN!!!')
    
    #print(len(playersDone))
    shared_info.is_Crowded = False
    export = shared_info.serverExports[str(serverId)]
    players = export['players']
    teams = export['teams']
    events = export['events']
    settings = export['gameAttributes']
    season = settings['season']
    salaryCap = settings['salaryCap']/1000
    hardCap = float(serversList[str(serverId)]['hardcap'])
    minContract = settings['minContract']/1000
    serverSettings = serversList[str(serverId)]
    if not "PO" in serverSettings:
        serverSettings.update({'PO':dict()})
    if not "TO" in serverSettings:
        serverSettings.update({'TO':dict()})
    finalSignings = []
    playersDone = []
    validOffers = 0
    #populating RFA offers
    setofpids = set()
    for o in offerList:
        setofpids.add(o['player'])
    maxscore = 0
    maxoffer = None
    while(len(offerList)>0):
        somethingwasvalid = False
        hso= dict() #highest score offers
        for o in offerList:
            #need to take highest score for every player
            s = o['score']
            pid = o['player']
            if not pid in hso:
                hso.update({pid:o})
            else:
                if hso[pid]['score'] < s:
                    hso.update({pid:o})
        scoredict = dict()
        scoredictp = dict()
        for pid, o in hso.items():
            pid = o['player']
            p = None
            for pl in players:
                if pl['pid'] == pid:
                    p = pl
            if p is None:
                print("there was no p found")
                print(pid)
                print(o)
                offerList.remove(o)
            else:
                playerName = p['firstName'] + ' ' + p['lastName']
                teamName = "not found"
                for t in teams:
                    if t['tid'] == o['team']:
                        teamName = t['region'] + ' ' + t['name']
                if teamName == "not found":
                    valid = False
                else:
                    valid, invalidations =await validitytest(o,p,players,season,invalidations,signings,export,serverSettings,hardCap, playerName,teamName,serverId)
                if valid:
                    validOffers += 1
                    somethingwasvalid = True
                    goThru = True
                    #highest score remaining is guaranteed to be winning offer for that player
                   
                    
                    if goThru:
                        lowestprior = True
                        for offer in offerList:
                            if offer['team'] == o['team'] and offer['priority'] < o['priority']:
                                lowestprior = False
                        if lowestprior == False:
                            goThru = False
                             # start of info gathering, the one case where not lowest priority but offer goes through
                            sumOfAbove = 0
                            playersAbove = 0
                            for offer in offerList:
                                if offer['team'] == o['team'] and offer['priority'] < o['priority']:
                                    sumOfAbove += offer['amount']
                                    playersAbove += 1
                            payroll = 0
                            playersRostered = 0
                            for player in players:
                                if player['tid'] == o['team']:
                                    payroll += player['contract']['amount']
                                    if player['draft']['year'] == season:
                                        if serverSettings['rookiescount'] == 'on':
                                            playersRostered += 1
                                    else:
                                        playersRostered += 1
                            try:
                                for rp in export['releasedPlayers']:
                                    if rp['tid'] == o['team']:
                                        payroll += rp['contract']['amount']
                            except: pass
                            payroll = payroll/1000
                            capNumber = salaryCap

                            capRoom = capNumber - payroll
                            rosterRoom = int(serverSettings['maxroster']) - playersRostered
                            #end of info gathering
                            try: toSign = int(serversList[str(serverId)]['toSign'][str(o['team'])])
                            except:
                                try:toSign = int(serversList[str(serverId)]['toSign'][o['team']])
                                except:toSign = 100000000
                            if (sumOfAbove+o['amount'] <= capRoom or sumOfAbove == 0) and playersAbove+1 <= rosterRoom and  playersAbove+1 <=( toSign - signings.count(o['team'])):
                                goThru = True
                                #print('got here on'+str(o))
                            #print(rosterRoom)
                            if rosterRoom == 0:
                                offerList.remove(o)
                                #why can't remove the offer
                            toRemove = []
                        #SELECT BEST OFFER
                        score = o['score']
                        if not goThru:
                            score = score - 100
                            #This makes it such that if offers get stuck in priority deadlock, something goes through
                        scoredict.update({p['pid']:score})
                        scoredictp.update({playerName:score})
                else:
                    offerList.remove(o)    
            
        if somethingwasvalid:
            #print(scoredict)
           
            moffer = None
            m = -100000000
            #print(scoredict)
            for a, b in scoredict.items():
                if b > m:
                    m = b
                    moffer = hso[a]
            o = moffer
            pid = o['player']
            for t in teams:
                if t['tid'] == o['team']:
                    teamName = t['region'] + ' ' + t['name']
            for pl in players:
                if pl['pid'] == pid:
                    p = pl
            #print(p['firstName'])
            #print(moffer)
            #print("gothru")
            toRemove = []
            for offer in offerList:
                if offer['player'] == o['player']:
                    toRemove.append(offer)
            signings.append(o['team'])
            p['tid'] = o['team']
            playersDone.append(p)
            p['contract']['amount'] = o['amount']*1000
            p['gamesUntilTradable'] = int(serverSettings['tradefa'])
            if settings['phase'] == 8:
                expDate = season + o['years']
                var = 1
            else:
                expDate = season + o['years'] - 1
                var = 0
            p['contract']['exp'] = expDate
            for i in range(o['years']):
                salaryInfo = {
                    'season': season + var + i,
                    'amount': o['amount']*1000
                }
            #option
            for t in teams:
                if t['tid'] == o['team']:
                    teamAbbrev = t['abbrev']
                    teamName2 =  t['region'] + ' ' + t['name']
            adj = shared_info.getadjective()
            playerName = p['firstName'] + ' ' + p['lastName']
            eventText = f'The <a href="/l/10/roster/{teamAbbrev}/{season}">{teamName2}</a> {adj} signed <a href="/l/10/player/{p["pid"]}">{playerName}</a> for ${o["amount"]}M/year through {expDate}'
            if o['option'] != None:
                optionText = f"Option: {expDate+1} {o['option']}"
                p['note'] = optionText
                p['noteBool'] = 1
                eventText += f", plus a {o['option']}."
            else:
                eventText += '.'
            
            
            #transaction
            transaction = {
                "season": season,
                "phase": settings['phase'],
                "tid": o['team'],
                "type": "freeAgent"
            }
            try:
                p['transactions'].append(transaction)
            except KeyError:
                p['transactions'] = []
                p['transactions'].append(transaction)

            #event
            newEvent = {
                'text': eventText,
                'pids': [p['pid']],
                'tids': [o['team']],
                'season': season,
                'type': 'freeAgent',
                'eid': events[-1]['eid']+1
            } 
            events.append(newEvent)
            finalSignings.append(o)# marker
            if o['option'] == "PO":
                if p['pid'] in serverSettings['PO']:
                    del serverSettings['PO'][p['pid']]
                if str(p['pid']) in serverSettings['PO']:
                    del serverSettings['PO'][str(p['pid'])]
                if p['pid'] in serverSettings['TO']:
                    del serverSettings['TO'][p['pid']]
                if str(p['pid']) in serverSettings['TO']:
                    del serverSettings['TO'][str(p['pid'])]
                serverSettings['PO'].update({p['pid']:(o['amount'],expDate)})
            if o['option'] == "TO":
                if p['pid'] in serverSettings['PO']:
                    del serverSettings['PO'][p['pid']]
                if str(p['pid']) in serverSettings['PO']:
                    del serverSettings['PO'][str(p['pid'])]
                if p['pid'] in serverSettings['TO']:
                    del serverSettings['TO'][p['pid']]
                if str(p['pid']) in serverSettings['TO']:
                    del serverSettings['TO'][str(p['pid'])]
                print(o)
                serverSettings['TO'].update({p['pid']:(o['amount'],expDate)})
            for o in toRemove:
                offerList.remove(o)
    
    for p in players:
        if len(p['ratings'][-1]['skills'])> 0:
            if 'RFA' in p['ratings'][-1]['skills'][-1]:

                for t in teams:

                    if t['abbrev'] == p['ratings'][-1]['skills'][-1].split(",")[-1]:

                        tid = t['tid']
                        teamName = t['region'] + ' ' + t['name']
                
                if p['tid'] == -1:
                    s = p['ratings'][-1]['skills'][0:-1]
                    p['ratings'][-1].update({'skills':s})
                    
                    o = {
                        "player": p['pid'],
                        "amount": p['salaries'][-1]['amount']*float(serversList[serverId]['rfamultiplier'])/1000,
                        "years": 1,
                        "team": tid,
                        "option": None,
                        "priority": 1,
                        'qo':True
                    }
                    signings.append(o['team'])
                    p['tid'] = o['team']
                    playerName = p['firstName'] + ' ' + p['lastName']
                    p['contract']['amount'] = o['amount']*1000
                    p['gamesUntilTradable'] = int(serverSettings['tradefa'])
                    if settings['phase'] == 8:
                        expDate = season + o['years']
                        var = 1
                    else:
                        expDate = season + o['years'] - 1
                        var = 0
                    p['contract']['exp'] = expDate
                    for i in range(o['years']):
                        salaryInfo = {
                            'season': season + var + i,
                            'amount': o['amount']*1000
                        }
                    #option
                    for t in teams:
                        if t['tid'] == o['team']:
                            teamAbbrev = t['abbrev']
                            teamName2 =  t['region'] + ' ' + t['name']
                    adj = shared_info.getadjective()
                    eventText = f'The <a href="/l/10/roster/{teamAbbrev}/{season}">{teamName2}</a> {adj} signed <a href="/l/10/player/{p["pid"]}">{playerName}</a> to a **qualifying offer** of ${o["amount"]}M/year through {expDate}'
                    if o['option'] != None:
                        optionText = f"Option: {expDate+1} {o['option']}"
                        p['note'] = optionText
                        p['noteBool'] = 1
                        eventText += f", plus a {o['option']}."
                    else:
                        eventText += '.'
                    
                    
                    #transaction
                    transaction = {
                        "season": season,
                        "phase": settings['phase'],
                        "tid": o['team'],
                        "type": "freeAgent"
                    }
                    try:
                        p['transactions'].append(transaction)
                    except KeyError:
                        p['transactions'] = []
                        p['transactions'].append(transaction)

                    #event
                    newEvent = {
                        'text': eventText,
                        'pids': [p['pid']],
                        'tids': [o['team']],
                        'season': season,
                        'type': 'freeAgent',
                        'eid': events[-1]['eid']+1
                    } 
                    events.append(newEvent)
                    finalSignings.append(o)
    await basics.save_db(serversList)
    return (offerList, signings, playersDone, invalidations, finalSignings, validOffers)
        
async def run_fa(offerList, signings, playersDone, invalidations, serverId):
    print('NEW FA2 RUN!!!')
    #print(len(playersDone))
    shared_info.is_Crowded = False
    export = shared_info.serverExports[str(serverId)]
    players = export['players']
    teams = export['teams']
    events = export['events']
    settings = export['gameAttributes']
    season = settings['season']
    salaryCap = settings['salaryCap']/1000
    hardCap = float(serversList[str(serverId)]['hardcap'])
    minContract = settings['minContract']/1000
    serverSettings = serversList[str(serverId)]
    finalSignings = []
    validOffers = 0
    #populating RFA offers
    setofpids = set()
    for o in offerList:
        setofpids.add(o['player'])
    for p in players:
        if p['pid'] in playersDone or not p['pid']  in setofpids:
            continue
        else:
            playersDone.append(p['pid'])
            #print('on ', p['firstName'], p['lastName'])
            playerName = p['firstName'] + ' ' + p['lastName']
            winningOffer = None
            toRemove = []
            #print(len(offerList))
            for o in offerList:
                for t in teams:
                    if t['tid'] == o['team']:
                        teamName = t['region'] + ' ' + t['name']
                if o['player'] == p['pid']:
 
                    #validity
                    valid, invalidations = valid(o,players,season,invalidations,signings,export,serverSettings)
                   

                    #FINAL
                    
                    if valid:
                        validOffers += 1
                        if winningOffer == None:
                            winningOffer = o
                        else:
                            if o['score'] > winningOffer['score']:
                                winningOffer = o
                    else:
                        #delete offer
                        toRemove.append(o)
            #print(winningOffer)
            #NEXT STEPS
            for o in toRemove:
                offerList.remove(o)
            if winningOffer != None:
                o = winningOffer
                #validity checks are done. Now we have to get into the more complicated priority handling. I'm not gonna annotate this part since it's pretty much black magic, but it works
                goThru = True
                if o['priority'] > 1:

                    goThru = False
                    sumOfAbove = 0
                    playersAbove = 0
                    for offer in offerList:
                        if offer['team'] == o['team'] and offer['priority'] < o['priority']:
                            sumOfAbove += offer['amount']
                            playersAbove += 1
                    payroll = 0
                    playersRostered = 0
                    for player in players:
                        if player['tid'] == o['team']:
                            payroll += player['contract']['amount']
                            if player['draft']['year'] == season:
                                if serverSettings['rookiescount'] == 'on':
                                    playersRostered += 1
                            else:
                                playersRostered += 1
                    try:
                        for rp in export['releasedPlayers']:
                            if rp['tid'] == o['team']:
                                payroll += rp['contract']['amount']
                    except: pass
                    payroll = payroll/1000
                    capNumber = salaryCap
                    if o['bird']:
                        capNumber = hardCap
                    capRoom = capNumber - payroll
                    rosterRoom = int(serverSettings['maxroster']) - playersRostered
                    #print(sumOfAbove, o['amount'], capRoom, playersAbove, rosterRoom)
                    if (sumOfAbove+o['amount'] <= capRoom or sumOfAbove == 0) and playersAbove+1 <= rosterRoom:
                        goThru = True
                        #print('got here')
                    #print(rosterRoom)
                    if rosterRoom == 0:
                        o['score'] = 0
                
                if goThru == False:
                    #print("didntgothru")
                    scoreDock = (1.1**(o['priority'] - 50))/(1.1**(o['priority'] - 50) + 1)
                    if scoreDock > 0.9:
                        scoreDock = 0.9
                    if scoreDock < 0.3:
                        scoreDock = 0.3
                    o['score'] = float(o['score'])*(1-scoreDock)
                    #print(o['score'])
                    #print(o)


                #back to rational living!
                toRemove = []
                if goThru:
                    #print("gothru")
                    for offer in offerList:
                        if offer['player'] == o['player']:
                            toRemove.append(offer)
                    signings.append(o['team'])
                    p['tid'] = o['team']
                    p['contract']['amount'] = o['amount']*1000
                    p['gamesUntilTradable'] = int(serverSettings['tradefa'])
                    if settings['phase'] == 8:
                        expDate = season + o['years']
                        var = 1
                    else:
                        expDate = season + o['years'] - 1
                        var = 0
                    p['contract']['exp'] = expDate
                    for i in range(o['years']):
                        salaryInfo = {
                            'season': season + var + i,
                            'amount': o['amount']*1000
                        }
                    #option
                    for t in teams:
                        if t['tid'] == o['team']:
                            teamAbbrev = t['abbrev']
                            teamName2 =  t['region'] + ' ' + t['name']
                    adj = shared_info.getadjective()
                    eventText = f'The <a href="/l/10/roster/{teamAbbrev}/{season}">{teamName2}</a> {adj} signed <a href="/l/10/player/{p["pid"]}">{playerName}</a> for ${o["amount"]}M/year through {expDate}'
                    if o['option'] != None:
                        optionText = f"Option: {expDate+1} {o['option']}"
                        p['note'] = optionText
                        p['noteBool'] = 1
                        eventText += f", plus a {o['option']}."
                    else:
                        eventText += '.'
                    
                    
                    #transaction
                    transaction = {
                        "season": season,
                        "phase": settings['phase'],
                        "tid": o['team'],
                        "type": "freeAgent"
                    }
                    try:
                        p['transactions'].append(transaction)
                    except KeyError:
                        p['transactions'] = []
                        p['transactions'].append(transaction)

                    #event
                    newEvent = {
                        'text': eventText,
                        'pids': [p['pid']],
                        'tids': [o['team']],
                        'season': season,
                        'type': 'freeAgent',
                        'eid': events[-1]['eid']+1
                    } 
                    events.append(newEvent)
                    finalSignings.append(o)
                
                else:
                    playersDone.remove(p['pid'])
                for o in toRemove:
                    offerList.remove(o)
    
    for p in players:
        if len(p['ratings'][-1]['skills'])> 0:
            if 'RFA' in p['ratings'][-1]['skills'][-1]:

                for t in teams:

                    if t['abbrev'] == p['ratings'][-1]['skills'][-1].split(",")[-1]:

                        tid = t['tid']
                        teamName = t['region'] + ' ' + t['name']
                
                if p['tid'] == -1:
                    s = p['ratings'][-1]['skills'][0:-1]
                    p['ratings'][-1].update({'skills':s})
                    
                    o = {
                        "player": p['pid'],
                        "amount": p['salaries'][-1]['amount']*float(serversList[serverId]['rfamultiplier'])/1000,
                        "years": 1,
                        "team": tid,
                        "option": None,
                        "priority": 1,
                        'qo':True
                    }
                    signings.append(o['team'])
                    p['tid'] = o['team']
                    p['contract']['amount'] = o['amount']*1000
                    p['gamesUntilTradable'] = int(serverSettings['tradefa'])
                    if settings['phase'] == 8:
                        expDate = season + o['years']
                        var = 1
                    else:
                        expDate = season + o['years'] - 1
                        var = 0
                    p['contract']['exp'] = expDate
                    for i in range(o['years']):
                        salaryInfo = {
                            'season': season + var + i,
                            'amount': o['amount']*1000
                        }
                    #option
                    for t in teams:
                        if t['tid'] == o['team']:
                            teamAbbrev = t['abbrev']
                            teamName2 =  t['region'] + ' ' + t['name']
                    adj = shared_info.getadjective()
                    eventText = f'The <a href="/l/10/roster/{teamAbbrev}/{season}">{teamName2}</a> {adj} signed <a href="/l/10/player/{p["pid"]}">{playerName}</a> to a **qualifying offer** of ${o["amount"]}M/year through {expDate}'
                    if o['option'] != None:
                        optionText = f"Option: {expDate+1} {o['option']}"
                        p['note'] = optionText
                        p['noteBool'] = 1
                        eventText += f", plus a {o['option']}."
                    else:
                        eventText += '.'
                    
                    
                    #transaction
                    transaction = {
                        "season": season,
                        "phase": settings['phase'],
                        "tid": o['team'],
                        "type": "freeAgent"
                    }
                    try:
                        p['transactions'].append(transaction)
                    except KeyError:
                        p['transactions'] = []
                        p['transactions'].append(transaction)

                    #event
                    newEvent = {
                        'text': eventText,
                        'pids': [p['pid']],
                        'tids': [o['team']],
                        'season': season,
                        'type': 'freeAgent',
                        'eid': events[-1]['eid']+1
                    } 
                    events.append(newEvent)
                    finalSignings.append(o)
                
    await basics.save_db(serversList)
    return (offerList, signings, playersDone, invalidations, finalSignings, validOffers)

async def resign_prices(playerId, teamId, serverExport, serverId, values):
    players = serverExport['players']
    season = serverExport['gameAttributes']['season']
    teams = serverExport['teams']
    settings = serverExport['gameAttributes']

    for p in players:
        if p['pid'] == playerId:
            basePrice = p['contract']['amount']
            ## BUT we regenerate base prices based off of something
            ct = 0

            if playerId in values:
                criticalvalue = values[playerId]
            else:
                criticalvalue = 0

            for v in values.values():
                if v < criticalvalue:
                    ct += 1
            fraction = ct/len(values)

            small = serverExport['gameAttributes']['minContract']
            big = serverExport['gameAttributes']['maxContract']
            if fraction > 0.97:
                basePricePre = big
            elif fraction < 0.45:
                basePricePre = small
            else:
                baseratio = (fraction-0.45)/0.52
                ratio = baseratio ** 3
                basePricePre = ratio*big+(1-ratio)*small
                basePricePre = round(round(basePricePre/1000,2)*1000,1)
            if basePricePre < basePrice:
                print("adjusted")
                basePrice = basePricePre

            
            baseYears = p['contract']['exp'] - season
            if basePrice == serverExport['gameAttributes']['minContract']:
                reSignFinal = [basePrice, baseYears]
            else:
                #mood calc
                offer = {
                    "player": playerId,
                    "team": teamId,
                    "amount": basePrice/1000,
                    "years": baseYears,
                    "option": None,
                    "priority": 1
                }
                score = await offer_score(offer, serverId)
                #average
                total = 0
                num = 0
                for t in teams:
                    if t['disabled'] == False:
                        num += 1
                        offer = {
                        "player": playerId,
                        "team": t['tid'],
                        "amount": basePrice/1000,
                        "years": baseYears,
                        "option": None,
                        "priority": 1
                    }
                        total += await offer_score(offer, serverId)
                scoreMultiplier = score / (total/num)
                newScoreMulti = 2 - scoreMultiplier
                if newScoreMulti <= 1:
                    reSignFinal = [basePrice, baseYears]
                else:
                    finalPrice = round(basePrice*(newScoreMulti + ((newScoreMulti - 1)*1.35)), -1)
                    if finalPrice > settings['maxContract']:
                        finalPrice = settings['maxContract']
                    reSignFinal = [finalPrice, baseYears]
            reSignPrices = {}
            for i in range(settings['maxContractLength']):
                i = i+1
                price = round(reSignFinal[0] + 0.15*(abs(i - reSignFinal[1]))*reSignFinal[0], -1)
                if price <= settings['maxContract'] and price >= settings['minContract']:
                    reSignPrices[i] = price
    reSignPrices['main'] = reSignFinal
    return(reSignPrices)




                    



                    



                    


