from shared_info import serverExports
from shared_info import serversList
import shared_info
import pull_info
import basics
import random
import json
import numpy as np
import discord
from sklearn.linear_model import LinearRegression
import plotly_express as px

#LEAGUE COMMANDS

    
def getabbrev(export, tid):
    for t in export['teams']:
        if t['tid'] == tid:
            return t['abbrev']
def gettname(export, tid):
    for t in export['teams']:
        if t['tid'] == tid:
            return t['region']+" "+t['name']
def gsos(export, tid):
    road = 0
    home = 0
    oppWins = 0
    oppLoses = 0
    for s in export['schedule']:
        oppTid = None
        gametype = "none"
        if s['homeTid'] == tid:
            oppTid = s['awayTid']
            home += 1
            gametype = "home"
        if s['awayTid'] == tid:
            oppTid = s['homeTid']
            road += 1
            gametype = "away"
        if oppTid != None:
            for t in export['teams']:
                if t['tid'] == oppTid:
                    oppWins += t['seasons'][-1]['won']
                    oppLoses += t['seasons'][-1]['lost']
    if home + road == 0:
        return 0.5
    
    sos = oppWins / (oppWins+oppLoses)
    homediff = (home-road)/(home+road)
    return sos-0.1*homediff
def standingspredict(embed,commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    if export['gameAttributes']['phase'] == 0:
        embed.add_field(name = "sorry, but", value = "we don't support preseason predictions yet, as team MOV plays a large part into record prediction")
        return embed
    names = []
    wins = []
    losses = []
    gp = []
    rates = []
    mov = []
    ratings = []
    confs = dict()
    abbrevs = dict()
    sos = []
    for t in export['teams']:
        
        for s in t['seasons']:
            if s['season'] == season:
                names.append(s['region']+" "+s['name'])
                confs.update({s['region']+" "+s['name']:t['cid']})
                wins.append(s['won'])
                losses.append(s['lost'])
                rates.append(min(0.999,max(0.001,s['won']/(s['won']+s['lost']))))
                gp.append(s['won']+s['lost'])
                abbrevs.update({s['region']+" "+s['name']:s['abbrev']})
        for s in t['stats']:
            if s['season'] == season and s['playoffs'] == False:
                mov.append((s['pts']-s['oppPts'])/s['gp'])
                sos.append(gsos(export, t['tid']))
        roster = []
        for p in export['players']:

            if p['tid'] == t['tid']:
                roster.append(p['ratings'][-1]['ovr'])
        if len(t['stats']) > 0:
            ratings.append(int(pull_info.team_rating(roster, False)))

    extendmov = []
    extendedrates = []
    for t in export['teams']:
        for s in t['seasons']:
            e = s['season']
            matchexists = False
            for ss in t['stats']:
                if ss['season'] == e:
                    matchexists = True
            if matchexists:
                extendedrates.append(min(0.999,max(0.001,s['won']/(s['won']+s['lost']))))
        for s in t['stats']:
            if s['playoffs'] == False:
                extendmov.append((s['pts']-s['oppPts'])/s['gp'])
        

    logrates = []
    for item in rates:
        logrates.append(np.log(item/(1-item)))
    logextrates = []
    for item in extendedrates:
        logextrates.append(np.log(item/(1-item)))
    logextrates_a = np.array(logextrates)
    extendmov_a = np.array(extendmov).reshape((-1, 1))
    model = LinearRegression()
    model.fit(extendmov_a, logextrates_a)
    

    model2 = LinearRegression()
    ratings_a = np.array(ratings).reshape((-1,1))
    mov_a = np.array(mov)
    model2.fit(ratings_a,mov_a)

    predictedmov = []
    for item in range (0, len(names)):
        predictedmov.append(model2.coef_[0]*ratings[item]+model2.intercept_)

    predictedmovweight = []
    for i in range (0, len(names)):
        predictedmovweight.append(0.9-gp[i]/export['gameAttributes']['numGames']*0.6)

    # START THE SIMULATIONS
    pdict= dict()
    for iti in names:
        pdict.update({iti:0})
    random.seed(sum(gp))
    np.random.seed(sum(gp))

    try:
        ep = export['gameAttributes']['numGamesPlayoffSeries'][-1]['value']

    except  Exception:
        ep = export['gameAttributes']['numGamesPlayoffSeries']
    b = export['gameAttributes']['numPlayoffByes']

    if not isinstance(b, int):
        b = b[-1]['value']

    playoffslotsperconf = 2**(len(ep)-1)-int(b/2+0.001)
    playoffsvector = []
    if export['gameAttributes']['playIn']:
        for i in range(0,playoffslotsperconf-2):
            playoffsvector.append(1)

        playoffsvector.append(0.75)
        playoffsvector.append(0.75)
        playoffsvector.append(0.25)
        playoffsvector.append(0.25)
    else:
        for i in range(0,playoffslotsperconf):
            playoffsvector.append(1)
    number = 2500
    for sim in range (0,number):
        
        eststandings = dict()
        for t in range (0, len(names)):
            tname = names[t]
            # first generate ros movs
            ros_mov=predictedmov[t]*predictedmovweight[t]+(1-predictedmovweight[t])*mov[t]+np.random.normal(0,np.sqrt(export['gameAttributes']['numGames']/gp[t])) # a bit of random noise
            s = sos[t]
            ros_wr = model.coef_[0]*ros_mov + model.intercept_-np.log(s/(1-s))
            ros_wr = np.exp(ros_wr)/(1+np.exp(ros_wr))

            remaininggameswin = np.random.binomial(export['gameAttributes']['numGames']-gp[t],ros_wr)
            numwins = wins[t]+remaininggameswin
            eststandings.update({tname:numwins})

        # now for deciding who makes playoffs
        
        c0standings = sorted(eststandings.keys(), key = lambda x : (1-confs[x])*eststandings[x]+np.random.normal(0,0.0001), reverse = True)
        c1standings = sorted(eststandings.keys(), key = lambda x : (confs[x])*eststandings[x]+np.random.normal(0,0.0001), reverse = True)

        for x in range (0, len(playoffsvector)):
            temp = pdict[c0standings[x]]
            pdict.update({c0standings[x]:playoffsvector[x]+temp})
            temp = pdict[c1standings[x]]
            pdict.update({c1standings[x]:playoffsvector[x]+temp})
    print(pdict)
    # final display
    confstandings = [[],[]]
    for t in range(0, len(names)):
        n = names[t]
        ros_mov=predictedmov[t]*predictedmovweight[t]+(1-predictedmovweight[t])*mov[t]
        s = sos[t]
        ros_wr = model.coef_[0]*ros_mov + model.intercept_-np.log(s/(1-s))
        ros_wr = np.exp(ros_wr)/(1+np.exp(ros_wr))
        ros_ew = (export['gameAttributes']['numGames']-gp[t])*ros_wr
        ew = wins[t]+ros_ew
        conf = confs[n]
        confstandings[conf].append((n,rates[t],wins[t],losses[t],ros_mov,ew,pdict[n]/number))
    confstandings[0] = sorted(confstandings[0], key = lambda x : x[1], reverse = True)
    confstandings[1] = sorted(confstandings[1], key = lambda x : x[1], reverse = True)
    print(confstandings)
    i = 0
    for c in confstandings:
        i += 1
        s = "Record | Pre. MOV | Pre. Wins | Playoff Prob."+"\n"
        for t in c:
            s += "**"+abbrevs[t[0]]+"**: "+str(t[2])+"-"+str(t[3])+" | "+str(round(t[4],2))+" | "+str(round(t[5],1))+" | **"+str(round(t[6]*100,2))+"**%\n"
        try:
            n = export['gameAttributes']['confs'][i-1]['name']
        except Exception:
            n = export['gameAttributes']['confs'][-1]['value'][i-1]['name']
        embed.add_field(name = n, value = s, inline = False)
        
    return embed
            
            
                
                
        
def draftorder(embed, commandInfo):
    dround = "All Rounds"
    for item in commandInfo['message'].content.split(" "):
        if len(item) == 1:
            try:
                dround = int(item)
            except ValueError:
                pass
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    if export['gameAttributes']['phase'] != 5 and export['gameAttributes']['phase'] != 6:
        embed.add_field(name = "Order! ORDER!", value= "You can't have draft order unless its draft phase")
        return embed
    ls = []
    for p in export['draftPicks']:
        if p['season'] == export['gameAttributes']['season']:
            if dround == "All Rounds" or p['round'] == dround:
                ls.append(p)
    ls = sorted(ls, key = lambda x:x['round']*100000+x['pick'])
    if len(ls) > 100:
        ls = ls[0:100]
    s = ""
    c = 1
    if len(ls) == 0:
        embed.add_field(name = "Draft Order for round "+str(dround), value= "For some reason, no draft picks for that round were detected in the export. You might want to check with your local lawn inspection agency.")
        return embed
    fround = ls[0]['round']
    s += "---**Round "+str(fround)+"**---\n"
    for p in ls:
        
        s = s + str(p['pick'])+": "+getabbrev(export,p['tid'])+"\n"
        if len(ls) > c:
            if ls[c]['round'] > ls[c-1]['round']:
                s += "---**Round "+str(ls[c]['round'])+"**---\n"
        c += 1
    embed.add_field(name = "Draft Order for round "+str(dround), value=s)
    return embed
    
def mostuniform(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]

    
    timewarp = commandInfo['message'].content.split(" ")
    year = -1000
    listofdevs = []
    if len(timewarp)>1:
        year = int(timewarp[1])
    for p in export['players']:
        rates = p['ratings']
        priorminimum = 1000
        pname = p['firstName'].strip() + " " + p['lastName'].strip()
        for rts in rates:
                
            if year == -1000 or rts.get("season") == year:
                    
                #print(rts)
                ratingslist = ["hgt","dnk","oiq","stre","ins","diq","spd","ft","drb","jmp","pss","fg","endu","tp","reb"]
                ratingslist2 = []
                totdeviation = 0
                tot = 0
                for name in ratingslist:
                    tot += rts.get(name)
                avg = tot/15
                for name in ratingslist:
                    ratingslist2.append(rts.get(name))
                    deviation = rts.get(name)-avg
                    if deviation<0:
                        deviation = -deviation
                    totdeviation += deviation
                szn = rts.get("season")
                if totdeviation<priorminimum:
                    for item1 in listofdevs:
                        if item1[0]==pname:
                            listofdevs.remove(item1)
                    listofdevs.append([pname,totdeviation,szn,avg])
                    priorminimum = totdeviation
                            
                        
                    #print(listofdevs[-1])
        #print(listofdevs)
    title = "Most Average Players: \n"
    string = ""
    tenlargest = sorted(listofdevs, key = lambda i:i[1])[0:10]
    for item in tenlargest:
        string = string+(str(item[2])+" "+item[0]+", Deviation of "+str(round(item[1],2))+" from average of "+str(round(item[3],1))+"\n")
    embed.add_field(name = title, value = string)
    return embed
def stripnames(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    for p in players:
        p.update({'firstName':p['firstName'].strip()})
        p.update({'lastName':p['lastName'].strip()})
    return embed
def reprog(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    
    if export['gameAttributes']['phase'] > 0:
        embed.add_field(name = "It's not preseason", value = "this can only be done in preseason")
        return embed
    f = open("summaries.txt")
    summaries = json.load(f)
    random.seed(export['gameAttributes']['season']) # should give deterministic ish results on reruns with the same variance
    variance = 0
    for item in commandInfo['message'].content.split(" "):
        try:
            variance = abs(int(item))
        except ValueError:
            pass
    if variance > 5:
        variance = 5
    ratingslist = ["stre","jmp","endu","spd","ins","reb","pss","fg","tp","ft","dnk","drb","oiq","diq"]
    for p in export['players']:
        if p['retiredYear'] is None:
            if p['draft']['year'] < export['gameAttributes']['season'] and len(p['ratings']) > 1:
                age = max(min(export['gameAttributes']['season'] - 1 - p['born']['year'],37),19)
                truevar = variance * 10/(age-10)
                pvar = np.random.normal(0,np.sqrt(truevar))
                pratings = p['ratings']

                base = pratings[-2]
                current = pratings[-1]
                if p['pid'] == 637:
                    print(current)
                
                sum_age = summaries[str(age)]
                
                for ratings in ratingslist:
                    
                    yboost = 0
                    if age < 29:
                        yboost = 0.25
                    if age < 25:
                       yboost = 0.5
                    if age > 27 and age < 31:
                        yboost += 0.5
                    if age == 27:
                        yboost += 0.25
                    current[ratings] = int(base[ratings]+float(sum_age[ratings])+yboost+pvar+np.random.normal(0,np.sqrt(truevar)))
                if 'ovr' in current:
                    del current['ovr']
                    del current['pot']
                    del current['skills']
                if p['pid'] == 637:
                    print(current)
    embed.add_field(name = "Progs Done with variance "+str(variance)+". BUT IMPORTANTLY", value = '''**NOTHING WILL WORK** until the following is done:\n
                    1. -updatexport is run\n
                    2. export is loaded into BBGM website\n
                    3. a NEW export link generated from within bbgm export league function\n
                    4. That new export link loaded back into this server!''')
    
    return embed
                
                
    

def mostaverage(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    if commandInfo['message'].content.__contains__("mostuniform"):
        return mostuniform(embed, commandInfo)
    
    timewarp = commandInfo['message'].content.split(" ")
    year = -1000
    listofdevs = []
    if len(timewarp)>1:
        year = int(timewarp[1])
    for p in export['players']:
        rates = p['ratings']
        priorminimum = 1000
        pname = p['firstName'].strip() + " " + p['lastName'].strip()
        for rts in rates:
                
            if year == -1000 or rts.get("season") == year:
                    
                #print(rts)
                ratingslist = ["hgt","dnk","oiq","stre","ins","diq","spd","ft","drb","jmp","pss","fg","endu","tp","reb"]
                ratingslist2 = []
                totdeviation = 0
                for name in ratingslist:
                    ratingslist2.append(rts.get(name))
                    deviation = rts.get(name)-50
                    if deviation<0:
                        deviation = -deviation
                    totdeviation += deviation
                szn = rts.get("season")
                if totdeviation<priorminimum:
                    for item1 in listofdevs:
                        if item1[0]==pname:
                            listofdevs.remove(item1)
                    listofdevs.append([pname,totdeviation,szn])
                    priorminimum = totdeviation
                            
                        
                    #print(listofdevs[-1])
        #print(listofdevs)
    title = "Most Average Players: \n"
    string = ""
    tenlargest = sorted(listofdevs, key = lambda i:i[1])[0:10]
    for item in tenlargest:
        string = string+(str(item[2])+" "+item[0]+", Deviation of "+str(item[1])+"\n")
    embed.add_field(name = title, value = string)
    return embed


def mostunbalanced(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    if commandInfo['message'].content.__contains__("mostuniform"):
        return mostuniform(embed, commandInfo)
    
    timewarp = commandInfo['message'].content.split(" ")
    year = -1000
    listofdevs = []
    if len(timewarp)>1:
        year = int(timewarp[1])
    for p in export['players']:
        rates = p['ratings']
        priorminimum = 0
        pname = p['firstName'].strip() + " " + p['lastName'].strip()
        for rts in rates:
                
            if year == -1000 or rts.get("season") == year:
                    
                #print(rts)
                ratingslist = ["hgt","dnk","oiq","stre","ins","diq","spd","ft","drb","jmp","pss","fg","endu","tp","reb"]
                ratingslist2 = []
                totdeviation = 0
                tot = 0
                for name in ratingslist:
                    tot += rts.get(name)
                avg = tot/15
                for name in ratingslist:
                    ratingslist2.append(rts.get(name))
                    deviation = rts.get(name)-avg
                    if deviation<0:
                        deviation = -deviation
                    totdeviation += deviation
                szn = rts.get("season")
                if totdeviation>priorminimum:
                    for item1 in listofdevs:
                        if item1[0]==pname:
                            listofdevs.remove(item1)
                    listofdevs.append([pname,totdeviation,szn,avg])
                    priorminimum = totdeviation
                            
                        
                    #print(listofdevs[-1])
        #print(listofdevs)
    title = "Least Balanced Players: \n"
    string = ""
    tenlargest = sorted(listofdevs, key = lambda i:i[1], reverse = True)[0:10]
    for item in tenlargest:
        string = string+(str(round(item[2],2))+" "+item[0]+", Deviation of "+str(round(item[1],2))+"\n"+" from average of "+str(round(item[3],1))+"\n")
    embed.add_field(name = title, value = string)
    return embed

def playoffs(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    playoffs = export['playoffSeries']
    teams = export['teams']
    tid_dict = dict()
    for t in teams:
        for s in t['seasons']:
            if s['season'] == commandInfo['season']:
                tid_dict.update({t['tid']:s['region']+" "+s['name']})
    found = False
    for p in playoffs:
        if p['season'] == commandInfo['season']:
            found = True
            
            series = p['series']
            for index in range(0, len(series)):
                p_round = series[index]
                s = ""
                for ind_series in p_round:
                    if 'away' in ind_series:
                        print(ind_series)

                        s = s + "("+str(ind_series['home']['seed'])+") "+tid_dict[ind_series['home']['tid']]+" **"+str(ind_series['home']['won'])+"-"+str(ind_series['away']['won'])+"** "+tid_dict[ind_series['away']['tid']]+" ("+str(ind_series['away']['seed'])+") "+"\n"
                      
                nm = "Round "+str(index+1)
                if index == len(series)-1:
                    nm = "Finals"
                print(s)
                embed.add_field(name = nm, value = s, inline = False)
    if not found:
        embed.add_field(name = "Maybe you can run the playoffs in a test sim or something,", value = "Because there sure isn't one in the current export for that season.", inline = False)
    return embed

def standings(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    teams = export['teams']
    season = commandInfo['season']
    confs = dict()
    for t in teams:
        for s in t['seasons']:
            if s['season'] == season:
                if not export['gameAttributes']['confs'][s['cid']]['name'] in confs:
                    print(export['gameAttributes']['confs'])
                    confs.update({export['gameAttributes']['confs'][s['cid']]['name']:[]})
                i = confs[export['gameAttributes']['confs'][s['cid']]['name']]
                if 'clinchedPlayoffs' in s:
                    p = s['clinchedPlayoffs']
                else:
                    p = ""
                
                i.append((t['region']+" "+t['name'],s['won'],s['lost'],p))
                confs.update({export['gameAttributes']['confs'][s['cid']]['name']:i})
    for i in confs:
        teams = sorted(confs[i], key = lambda p:p[1]/(max(p[1]+p[2],0.00001)), reverse = True)
        string = ""
        for t in teams:
            string +=t[0]+": "+str(t[1])+"-"+str(t[2])+" "+t[3]+ "\n"
        embed.add_field(name = i, value = string)

    return embed
                    
def po(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    serverSettings = serversList[str(commandInfo['serverId'])]
    if "PO" in serverSettings:
        text = ""
        todelete = []
        l = serverSettings["PO"]
        print(l)
        for i in l:

            name = "who's this, idk. "+str(i)
            teamname = None
            for p in export['players']:
                if p['pid'] == int(i):

                    name = '**'+p['firstName']+" "+p['lastName']+"**"
                    contract = str(p['contract']['amount']/1000)
                    team = p['tid']
                    if team < 0:
                        if team == -1:
                            if 'negotiations' in export:
                                for neg in export['negotiations']:

                                    if neg['pid'] == int(i):
                                        team = neg['tid']


                    ovr = p['ratings'][-1]['ovr']
                    pot = p['ratings'][-1]['pot']
                    
                    for t in export['teams']:

                        if t['tid'] == team:
                            teamname = t['abbrev']
            if teamname == None:
                todelete.append(i)
                    
            
            text += str(name) +", "+str(ovr)+"/"+str(pot)+", "+str(teamname)+ ", $"+str(l[i][0])+"M until "+str(l[i][1])+"\n"
            if len(t) > 1000:
                embed.add_field(name = "POs", value = text)
                text = ""
        for i in todelete:
            del serverSettings["PO"][i]
        print(todelete)
        embed.add_field(name = "POs", value = text)
        return embed
    else:
        embed.add_field(name = "What in the world!!!!!", value = "There's no POs in existence here. This is barren territory.")
                
def to(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    serverSettings = serversList[str(commandInfo['serverId'])]
    if "TO" in serverSettings:
        text = ""
        todelete = []
        l = serverSettings["TO"]
        print(l)
        for i in l:

            name = "who's this, idk. "+str(i)
            teamname = None
            for p in export['players']:
                if p['pid'] == int(i):

                    name = '**'+p['firstName']+" "+p['lastName']+"**"
                    contract = str(p['contract']['amount']/1000)
                    team = p['tid']
                    if team < 0:
                        if team == -1:
                            if 'negotiations' in export:
                                for neg in export['negotiations']:

                                    if neg['pid'] == int(i):
                                        team = neg['tid']



                    ovr = p['ratings'][-1]['ovr']
                    pot = p['ratings'][-1]['pot']
                    
                    for t in export['teams']:

                        if t['tid'] == team:
                            teamname = t['abbrev']
            if teamname == None:
                todelete.append(i)
                    
            
            text += str(name) +", "+str(ovr)+"/"+str(pot)+", "+str(teamname)+ ", $"+str(l[i][0])+"M until "+str(l[i][1])+"\n"
            if len(t) > 1000:
                embed.add_field(name = "TOs", value = text)
                text = ""
        for i in todelete:
            del serverSettings["TO"][i]
        print(todelete)
        embed.add_field(name = "TOs", value = text)
        return embed
    else:
        embed.add_field(name = "What in the world!!!!!", value = "There's no TOs in existence here. This is barren territory.")
                
    
def fa(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    sortBy = 'ovr'
    values = ['ovr', 'pot', 'hgt', 'stre', 'spd', 'jmp', 'endu', 'ins', 'dnk', 'ft', 'fg', 'tp', 'oiq', 'diq', 'drb', 'pss', 'reb']
    if len(commandInfo['text']) > 1:
        if str.lower(commandInfo['text'][1]) in values:
            sortBy = commandInfo['text'][1]
    freeAgents = []
    for p in players:
        if p['tid'] == -1:
            playerInfo = pull_info.pinfo(p)
            freeAgents.append(playerInfo)
    commandContent = basics.player_list_embed(freeAgents, commandInfo['pageNumber'], export['gameAttributes']['season'], sortBy)
    
    embed.add_field(name=f"Sorted by {commandContent[1]}", value=commandContent[0])
    return embed
def topall(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    t = commandInfo['message'].content.split(" ")
    pagenumber = 1
    for item in t:
        try:
            pagenumber = int(item)
        except:
            pass
    datatype = "rating"
    for item in t:
        if item.lower() == "stat" or item.lower() in ["points","assists", "rebounds","threes","minutes","turnovers","blocks","steals"]:
            datatype = "stat"
        if item.lower() == "awards":
            datatype = "award"
    correctawards = ["MVP","All League","First Team","Second Team","Third Team","All Defensive","First Team All Defensive","Second Team All Defensive","Third Team All Defensive", "Sixth Man","Most Improved",
                         "All Star","Rookie of the Year","All Rookie","Defensive Player of the Year","Finals MVP","Semifinals MVP","Won Championship","Scoring Leader","Assists Leader","Rebounds Leader","Steals Leader","Blocks Leader","Biggest Booty"]
    for item in correctawards:
        
        if item.lower() in commandInfo['message'].content.lower():
            datatype = "award"
    if datatype == "rating":
        types = ["pot","endu","tp","reb","pss","fg","jmp","spd","ft","drb","diq","oiq","dnk","ins","hgt","stre"]
        indicate = "ovr"
        for item in t:
            print(item)
            if item.lower() in types:
                indicate = item.lower()
        plist = []
        for p in players:
            peak = 0
            for r in p['ratings']:
                val = r[indicate]
                if val > peak:
                    peak = val
            plist.append((p['firstName']+" "+p['lastName'],peak))
    if datatype == "stat":
        pergame = False
        playoffs = False
        if commandInfo['message'].content.lower().__contains__("per game"):
            pergame = True
        if commandInfo['message'].content.lower().__contains__("playoffs"):
            playoffs = True
        indicate = "points"
        for item in t:
            print(item)
            if item.lower() in ["assists", "rebounds","threes","turnovers","blocks","steals", "minutes"]:
                indicate = item.lower()
        plist = []
        for player in players:
            total = 0
            gp = 0
            for s in player['stats']:
                if s['playoffs'] == playoffs:
                    gp += s['gp']
                    if indicate == "points":
                        total += s["pts"]
                    if indicate == "minutes":
                        total = round(total+s['min'],1)
                                
                    if indicate == "rebounds":
                        total += s["orb"]+s["drb"]
                    if indicate == "assists":
                        total += s["ast"]
                    if indicate == "blocks":
                        if isinstance(s["blk"], int):
                        
                            total += s["blk"]
                    if indicate == "steals":
                        if isinstance(s["stl"], int):
                            total += s["stl"]
                    if indicate == "threes":
                        total += s["tp"]
                    if indicate == "turnovers":
                        total += s["tov"]
            if pergame:
                if gp > 0:
                    total = round(total / gp, 2)
            if total > 0:
                plist.append((player['firstName']+" "+player['lastName'],total))
    if datatype == "award":
        plist = []
        indicate = "Error"
        for item in correctawards:
            if item.lower().replace(" ","") in commandInfo['message'].content.lower().replace(" ",""):
                indicate = item
        if indicate == "First Team" or indicate == "Second Team" or indicate == "Third Team":
            indicate = indicate + " All League"
        if indicate == "MVP":
            indicate = "Most Valuable Player"
        if indicate == "Error":
            embed.add_field(name = "Please specify exactly one of the following: ",value = ",".join(correctawards))
            return embed
        for player in players:
            a = player['awards']
            t = 0
            for award in a:
                if award["type"].replace("-"," ").lower().__contains__(indicate.lower()):
                    t += 1
                if indicate == "Biggest Booty":
                    if "All-Star MVP" in award["type"]:
                         t = 1
                    if "Slam Dunk" in award["type"]:
                        t += 1
                    if "Three Point" in award["type"]:
                        t += 1
                
            if t > 0:
                plist.append((player['firstName']+" "+player['lastName'],t))
            
                
                        
        
    plist = sorted(plist, key = lambda i:i[1], reverse = True)
    t = ""
    totalpages = int((len(plist)-1)/15)+1
    pagenumber = min(pagenumber, totalpages)
    ccc = 0
    for i in plist[(pagenumber-1)*15:pagenumber*15]:
        t +=str(pagenumber*15-14+ccc)+": "+ i[0]+": "+str(i[1])+"\n"
        ccc += 1
    embed.add_field(name="Best of all time for "+datatype+" "+str(indicate)+", page "+str(pagenumber)+" out of "+str(totalpages), value=t)
    return embed
def draft(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    players = export['players']
    sortBy = ['draftRound']
    values = ['ovr', 'pot', 'hgt', 'stre', 'spd', 'jmp', 'endu', 'ins', 'dnk', 'ft', 'fg', 'tp', 'oiq', 'diq', 'drb', 'pss', 'reb']
    if len(commandInfo['text']) > 1:
        if str.lower(commandInfo['text'][1]) in values:
            sortBy = commandInfo['text'][1]
    draftProspects = []
    for p in players:
        if commandInfo['season'] < season:
            if p['draft']['year'] == commandInfo['season'] and p['draft']['round'] != 0:
                playerInfo = pull_info.pinfo(p)
                draftProspects.append(playerInfo)
                draftProspects.sort(key=lambda p: p['draftPick'])
        else:
            if p['draft']['year'] == commandInfo['season'] and p['tid'] == -2:
                playerInfo = pull_info.pinfo(p)
                draftProspects.append(playerInfo)
                if sortBy == ['draftRound']:
                    sortBy = ['value']
    
    if sortBy == ['draftRound']:
        commandContent = basics.player_list_embed(draftProspects, commandInfo['pageNumber'], export['gameAttributes']['season'], sortBy, False, True)
    else:
        commandContent = basics.player_list_embed(draftProspects, commandInfo['pageNumber'], export['gameAttributes']['season'], sortBy)
    embed.add_field(name=f"Sorted by {commandContent[1]}", value=commandContent[0])
    return embed
    
def pr(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    teams = export['teams']
    season = export['gameAttributes']['season']

    powerRanking = []

    for t in teams:
        roster = []
        for p in players:
            if commandInfo['season'] == season:
                if p['tid'] == t['tid']:
                    roster.append(p['ratings'][-1]['ovr'])
            else:
                if 'stats' in p:
                    stats = p['stats']
                    lastTeam = -1
                    for s in stats:
                        if s['season'] == commandInfo['season']:
                            lastTeam = s['tid']
                    if lastTeam == t['tid']:
                        roster.append(pull_info.pinfo(p, commandInfo['season']['ovr']))
        teamInfo = pull_info.tinfo(t, commandInfo['season'])
        powerRanking.append([teamInfo['name'], teamInfo['record'], pull_info.team_rating(roster, False)])
    
    powerRanking.sort(key=lambda p: float(p[2]), reverse=True)
    lines = []
    number = 1
    for p in powerRanking:
        lines.append(f"``{number}.`` **{p[0]}** ({p[1]}) - **{p[2]}/100** TR")
        number += 1
    numDivs, rem = divmod(len(lines), 15)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*15):((i*15)+15)]
        text ='\n'.join(newLines)
        embed.add_field(name=f"Power Rankings", value=text, inline=False)
    return embed
def lgoptions(embed, commandInfo):
    listofthings2 = 'gp, min, fg, fga, fgAtRim, fgaAtRim, fgLowPost, fgaLowPost, fgMidRange, fgaMidRange, tp, tpa, ft, fta, orb, drb, ast, tov, stl, blk, pf, pts, dd, td, qd, fxf, oppFg, oppFga, oppFgAtRim, oppFgaAtRim, oppFgLowPost, oppFgaLowPost, oppFgMidRange, oppFgaMidRange, oppTp, oppTpa, oppFt, oppFta, oppOrb, oppDrb, oppAst, oppTov, oppStl, oppBlk, oppPf, oppPts, oppDd, oppTd, oppQd, oppFxf, rid, reb, wins, losses, win%, oppReb, ptsPerGame, oppPtsPerGame, rebPerGame, oppRebPerGame, astPerGame, oppAstPerGame, blkPerGame, oppBlkPerGame, stlPerGame, oppStlPerGame, tovPerGame, oppTovPerGame, pfPerGame, oppPfPerGame, fgPerGame, oppFgPerGame, tpPerGame, oppTpPerGame, ftPerGame, oppFtPerGame, tp%, oppTp%, ft%, oppFt%, fg%, oppFg%, fgAtRim%, oppFgAtRim%, fgLowPost%, oppFgLowPost%, fgMidRange%, oppFgMidRange%, ptdiff'
    embed.add_field(name = "Stats options", value = listofthings2)
    return embed
def leaguegraph(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    message = commandInfo['message']
    listofthings2 = 'gp, min, fg, fga, fgAtRim, fgaAtRim, fgLowPost, fgaLowPost, fgMidRange, fgaMidRange, tp, tpa, ft, fta, orb, drb, ast, tov, stl, blk, pf, pts, dd, td, qd, fxf, oppFg, oppFga, oppFgAtRim, oppFgaAtRim, oppFgLowPost, oppFgaLowPost, oppFgMidRange, oppFgaMidRange, oppTp, oppTpa, oppFt, oppFta, oppOrb, oppDrb, oppAst, oppTov, oppStl, oppBlk, oppPf, oppPts, oppDd, oppTd, oppQd, oppFxf, rid, reb, wins, losses, win%, oppReb, ptsPerGame, oppPtsPerGame, rebPerGame, oppRebPerGame, astPerGame, oppAstPerGame, blkPerGame, oppBlkPerGame, stlPerGame, oppStlPerGame, tovPerGame, oppTovPerGame, pfPerGame, oppPfPerGame, fgPerGame, oppFgPerGame, tpPerGame, oppTpPerGame, ftPerGame, oppFtPerGame, tp%, oppTp%, ft%, oppFt%, fg%, oppFg%, fgAtRim%, oppFgAtRim%, fgLowPost%, oppFgLowPost%, fgMidRange%, oppFgMidRange%, ptdiff'
    prefix = serversList[str(message.guild.id)]['prefix']
    if True:
        
        m=message.content.replace(prefix+'leaguegraph',"").strip()
        try:
            yr = int(message.content.split(" ")[-1])
            m=m.replace(str(yr),"").strip()
        except ValueError:
            yr = export['gameAttributes']['season']
        firststatname = "ptdiff"
        secondstatname = "win%"
        assigned = False
        secondisassigned = False
        poff = False

        t = m.split(" ")
        for item in t:
            if len(item)>1:
                if not assigned:
                    firststatname = item
                    assigned = True
                else:
                    if not secondisassigned:
                        secondstatname = item
                        secondisassigned = True


        teams = export['teams']
        seasons = list()
        stats= list()
        colors = list()
        firststat=list()
        secondstat=list()
        finalcolors = list()
        tcolors = ["#F63309","#09F621","#090FF6","#F68509","#F3F609","#09c3ba","#601A83","#83221A","#835B1A","#b1d5fb","#BB22B5","#FF13CD","#6891f8","#fcc5f4","#1d6b05","#878787","#787878","#A36B41","#87B5FF","#F5BFBD","#4E1B4B","#76190F","#41203E","#0A144A"]
        sizes=list()
        names=list()
        for t in teams:
            for season in t.get("seasons"):
                if season.get("season")==yr:
                    seasons.append(season)
                    
            for season in t.get("stats"):
                if season.get("season")==yr and not season.get("playoffs"):
                    stats.append(season)
                    colors.append(t.get("colors")[0])
        #print(seasons)
        for index in range (0,len(stats)):
            st = stats[index]
            tid = stats[index].get("tid")
            for season in teams[tid]['seasons']:
                if season['season'] == yr:
                    name = season['region']+" "+season['name']
            #print(tid)
            names.append(name)
            s = dict()
            for ss in seasons:
                if ss.get("tid")==tid:
                    s = ss
            #print(s)
            st.update({"reb":st.get("orb")+st.get("drb")})
            st.update({"wins":s.get("won")})
            st.update({"losses":s.get("lost")})
            st.update({"win%":s.get("won")/st.get("gp")})
            #print(firststatname,secondstatname)
            st.update({"oppReb":st.get("oppOrb")+st.get("oppDrb")})
            for rating in ["pts","reb","ast","blk","stl","tov","pf","fg","tp","ft"]:
                st.update({rating+"PerGame":st.get(rating)/st.get("gp")})
                rating = rating.capitalize()
                st.update({"opp"+rating+"PerGame":st.get("opp"+rating)/st.get("gp")})
            for rating in ["tp","ft", "fg","fgAtRim","fgLowPost","fgMidRange"]:
                st.update({rating+"%":st.get(rating)/st.get(rating[0:2]+"a"+rating[2:])})
                rating = rating[0:2].capitalize()+rating[2:]
                #print(rating)
                st.update({"opp"+rating+"%":st.get("opp"+rating)/st.get("opp"+rating[0:2]+"a"+rating[2:])})
            st.update({"ptdiff":(st.get("ptsPerGame")-st.get("oppPtsPerGame"))})
            if not (st.__contains__(firststatname) and st.__contains__(secondstatname)):
                t22 = ""
  
                t22 += "Something about the two variables you specified is invalid.\n"
                t22 += "To help you out: what we received from you was: "+firststatname+" and "+secondstatname+"\n"
                embed.add_field(name = "Error", value = t22)
                return embed
            firststat.append(st.get(firststatname))
            secondstat.append(st.get(secondstatname))
            sizes.append(4)
            #print(st.keys())
            finalcolors.append(teams[tid].get("colors")[0])
        #print(firststat)
        fig = px.scatter(x=firststat, y=secondstat,color=names,size = sizes, size_max = 10, color_discrete_sequence = finalcolors[0:len(secondstat)])
        fig.update_layout(
        title='The league in year '+str(yr),
        xaxis=dict(
            title=firststatname,

        ),
        yaxis=dict(
            title=secondstatname,
        ))
        #fig.show()
        fig.write_image('third_figure.png',height=750, width = 790)

        t22 = ""
        t22 += "Call "+prefix+"lgoptions to see options"
        embed.add_field(name = "Behold the worst graph you will ever see!", value = t22)
        return embed


def top(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    sortBy = 'ovr'
    if len(commandInfo['text']) > 1:
        sortBy = commandInfo['text'][1]
    activePlayers = []
    for p in players:
        if p['tid'] > -2:
            playerInfo = pull_info.pinfo(p)
            activePlayers.append(playerInfo)
    commandContent = basics.player_list_embed(activePlayers, commandInfo['pageNumber'], export['gameAttributes']['season'], sortBy)
    
    embed.add_field(name=f"Sorted by {commandContent[1]}", value=commandContent[0])
    return embed

def injuries(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']

    injuries = []
    for p in players:
        if p['injury']['type'] != 'Healthy':
            injuries.append([f"{p['ratings'][-1]['pos']} **{p['firstName']} {p['lastName']}** ({p['ratings'][-1]['ovr']}/{ p['ratings'][-1]['pot']})", p['ratings'][-1]['ovr']+p['injury']['gamesRemaining'], p['injury']])
    injuries.sort(key=lambda i: i[1], reverse=True)
    lines = []
    for i in injuries:
        lines.append(f"{i[0]} - {i[2]['type']}, {i[2]['gamesRemaining']} games")
    numDivs, rem = divmod(len(lines), 15)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*15):((i*15)+15)]
        text ='\n'.join(newLines)
        embed.add_field(name=f"Injuries", value=text, inline=False)
    
    return embed

def top(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    sortBy = 'ovr'
    if len(commandInfo['text']) > 1:
        sortBy = commandInfo['text'][1]
    activePlayers = []
    for p in players:
        if p['tid'] > -2:
            playerInfo = pull_info.pinfo(p)
            activePlayers.append(playerInfo)
    commandContent = basics.player_list_embed(activePlayers, commandInfo['pageNumber'], export['gameAttributes']['season'], sortBy)
    commandContent[0] = commandContent[0][0:1023]
    print("command_content[0]"+str(len(commandContent[0])))
    embed.add_field(name=f"Sorted by {commandContent[1]}", value=commandContent[0])
    return embed

def deaths(embed, commandInfo):
    cont = commandInfo['message'].content.split(' ')
    deathInfo = ['deathInfo', 'yearDied']
    if len(cont) > 1:
        if str.lower(cont[1]) in ['age', 'oldest']:
            deathInfo = ['deathInfo', 'ageDied']

    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    deadPlayers = []
    for p in players:
        p = pull_info.pinfo(p)
        if p['deathInfo']['died']:
            deadPlayers.append(p)
    deadPlayers.sort(key=lambda p: p['deathInfo']['yearDied'], reverse=True)
    commandContent = basics.player_list_embed(deadPlayers, commandInfo['pageNumber'], export['gameAttributes']['season'], deathInfo)
    
    embed.add_field(name=f"Sorted by {commandContent[1]}", value=commandContent[0])
    return embed

def leaders(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    statTypes = ['pts', 'reb', 'drb', 'orb', 'ast', 'stl', 'blk', 'tov', 'min', 'tov', 'pm', 'gp', 'ows', 'dws', 'ortg', 'drtg', 'pm100', 'onOff100', 'vorp', 'obpm', 'dbpm', 'ewa', 'per', 'usgp', 'dd', 'td', 'qd', 'fxf', 'fg%', 'tp%', 'ft%', 'at-rim%', 'low-post%', 'mid-range%']
    sortBy = ['stats', 'pts']
    if len(commandInfo['text']) > 1:
        if commandInfo['text'][1] in statTypes:
            sortBy = ['stats', str.lower(commandInfo['text'][1]).replace('%', '')]
        else:
            text = "These stats are supported: " + '\n' + '\n'
            for s in statTypes:
                text += f"• ``{s}``" + '\n'
            embed.add_field(name='Error', value=text)
            return embed
    playerList = []
    for p in players:
        played = False
        stats = p['stats']
        for s in stats:
            if s['season'] == commandInfo['season']:
                if s['gp'] > 0:
                    played = True
        if played:
            playerInfo = pull_info.pinfo(p, commandInfo['season'])
            playerList.append(playerInfo)
    commandContent = basics.player_list_embed(playerList, commandInfo['pageNumber'], commandInfo['season'], sortBy)
    
    embed.add_field(name=f"Sorted by {commandContent[1]}", value=commandContent[0])
    return embed

def matchups(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    teams = export['teams']
    text = commandInfo['text']
    abbrevs = []
    teamOne = None
    teamTwo = None
    for t in teams:
        abbrevs.append(str.lower(t['abbrev']))
    if len(text) < 3:
        embed.add_field(name='Error', value='Please provide two teams to search for matchups between.')
        return embed
    else:
        if str.lower(text[1]) in abbrevs:
            teamOne = str.lower(text[1])
        if str.lower(text[2]) in abbrevs:
            teamTwo = str.lower(text[2])
    if teamOne == None or teamTwo == None:
        embed.add_field(name='Team Finding Error', value='Make sure you use current team abbreviations.')
    else:
        for t in teams:
            if str.lower(t['abbrev']) == teamOne:
                teamOne = t['tid']
            if str.lower(t['abbrev']) == teamTwo:
                teamTwo = t['tid']
        #find matchups
        matchupsFound = 0
        try: games = export['games']
        except KeyError: 
            embed.add_field(name='Error', value='No boxscores in file.')
            return embed
        
        for g in games:
            if (g['teams'][0]['tid'] == teamOne and g['teams'][1]['tid'] == teamTwo) or (g['teams'][0]['tid'] == teamTwo and g['teams'][1]['tid'] == teamOne):
                matchupsFound += 1
                gameInfo = pull_info.game_info(g, export, commandInfo['message'])
                text = f"{gameInfo['fullScore']} \n \n **Top Performances:** \n {gameInfo['topPerformances'][0]} \n {gameInfo['topPerformances'][1]}"
                if g['clutchPlays'] != []:
                    for c in g['clutchPlays']:
                        text += '\n' + '***' + c.split('>')[1].replace('</a', '') + '** ' + c.split('>')[2] + '*'
                embed.add_field(name=f"Game {matchupsFound}", value=text)
        
        if matchupsFound == 0:
            embed.add_field(name='No Games Found', value='Those two teams have not yet faced, or no box scores of their game are saved.')
        
        return embed
    
def summary(embed, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    teams = export['teams']
    players = export['players']
    found = False
    for s in export['awards']:
        if s['season'] == commandInfo['season']:
            found = True
            #get champion
            playoffSettings = export['gameAttributes']['numGamesPlayoffSeries']
            for t in teams:
                t = pull_info.tinfo(t, commandInfo['season'])
                result = pull_info.playoff_result(t['roundsWon'], playoffSettings, commandInfo['season'])
                if result == '**won championship**':
                    champion = f"{basics.team_mention(commandInfo['message'], t['name'], t['abbrev'])} ({t['record']})"
                #grab FMVP team
                if t['tid'] == s['finalsMvp']['tid']:
                    fmvpTeam = t['abbrev']
            fmvp = f"{s['finalsMvp']['name']} ({fmvpTeam}) - ``{round(s['finalsMvp']['pts'], 1)} pts, {round(s['finalsMvp']['trb'], 1)} reb, {round(s['finalsMvp']['ast'], 1)} ast``"
            sfMvps = ""
            try:
                for mvp in s['sfmvp']:
                    for t in teams:
                        if t['tid'] == mvp['tid']:
                            t = pull_info.tinfo(t, commandInfo['season'])
                            abbrev = t['abbrev']
                    sfMvps += f"**{mvp['name']}** ({abbrev}) - ``{round(mvp['pts'], 1)}pts , {round(mvp['trb'], 1)} reb, {round(mvp['ast'], 1)} ast``" + '\n'
            except KeyError: sfMvps = "None"
            bestRecords = ""
            for tr in s['bestRecordConfs']:
                for t in teams:
                    if t['tid'] == tr['tid']:
                        t = pull_info.tinfo(t, commandInfo['season'])
                        bestRecords += f"{basics.team_mention(commandInfo['message'], t['name'], t['abbrev'])} ({tr['won']}-{tr['lost']})" + '\n'
            embed.add_field(name='Season Summary', value=f"**Champion:** {champion}\n Finals MVP: {fmvp} \n \n Semifinals MVPs: \n {sfMvps} \n \n Best Records: \n {bestRecords}")
            #awards
            text = ""
            awards = ['mvp', 'dpoy', 'smoy', 'roy', 'mip']
            for a in awards:
                if a in s:
                    for t in teams:
                        if t['tid'] == s[a]['tid']:
                            info = pull_info.tinfo(t, commandInfo['season'])
                            teamLine = f"{info['name']} ({info['record']}, {pull_info.playoff_result(info['roundsWon'], export['gameAttributes']['numGamesPlayoffSeries'], commandInfo['season'])})"
                    if a == 'dpoy':
                        text += f"**{str.upper(a)}: {s[a]['name']}**" + '\n' + teamLine + '\n' + f"``{round(s[a]['trb'], 1)} reb, {round(s[a]['blk'], 1)} blk, {round(s[a]['stl'], 1)} stl``" + '\n' + '\n'
                    else:
                        text += f"**{str.upper(a)}: {s[a]['name']}**" + '\n' + teamLine + '\n' + f"``{round(s[a]['pts'], 1)} pts, {round(s[a]['trb'], 1)} reb, {round(s[a]['ast'], 1)} ast``" + '\n' + '\n'
            embed.add_field(name='Awards', value=text)

            
            #retirements
            text = ""
            retiredPlayers = []
            for p in players:
                p = pull_info.pinfo(p, commandInfo['season'])
                if p['retired']:
                    if p['retiredYear'] == commandInfo['season']:
                        retiredPlayers.append([p['name'], p['peakOvr'], commandInfo['season']-p['born']])
            retiredPlayers.sort(key=lambda r: r[1], reverse=True)
            retiredPlayers = retiredPlayers[:10]
            text = ""
            for r in retiredPlayers:
                text += f"**{r[0]}** ({r[2]} yo, peaked at {r[1]} OVR) \n"

            embed.add_field(name='Retirements', value=text) 



            #all-league
            text = ""
            allLeague = s['allLeague']
            for t in allLeague:
                text += f"\n __{t['title']}__\n"
                for pl in t['players']:
                    for te in teams:
                        if te['tid'] == pl['tid']:
                            abbrev = pull_info.tinfo(te, commandInfo['season'])['abbrev']
                    text += f"{pl['name']} ({abbrev})" + '\n'
            embed.add_field(name='All-League Teams', value=text)
            
            #all-defense
            text = ""
            allDefense = s['allDefensive']
            for t in allDefense:
                text += f"\n __{t['title']}__\n"
                for pl in t['players']:
                    for te in teams:
                        if te['tid'] == pl['tid']:
                            abbrev = pull_info.tinfo(te, commandInfo['season'])['abbrev']
                    text += f"{pl['name']} ({abbrev})" + '\n'
            embed.add_field(name='All-Defensive Teams', value=text)

            #all-rookie
            text = f"\n __All-Rookie Team__\n"
            allRookie = s['allRookie']
            for pl in allRookie:
                for te in teams:
                    if te['tid'] == pl['tid']:
                        abbrev = pull_info.tinfo(te, commandInfo['season'])['abbrev']
                text += f"{pl['name']} ({abbrev})" + '\n'
            embed.add_field(name='All-Rookie Team', value=text)
        
    if found == False:
        embed.add_field(name='Error', value='No summary data for that season.')
    return embed






                

    
        
    
