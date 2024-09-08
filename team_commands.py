from shared_info import serverExports
from shared_info import serversList
import shared_info
import pull_info
import basics
import discord
import random
import plotly_express as px
def penalties(embed, t, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    teams = export['teams']
    pens = []
    for t in teams:
        tp = pull_info.trade_penalty(t['tid'], export)
        name = t['region']+" "+t['name']
        pens.append((name,tp))
    s = ""
    pens = sorted(pens, key = lambda x: x[1], reverse = True)
    count = 0
    for item in pens:
        count += 1
        s = s + "**"+item[0]+"**: "+str(round(item[1],3))+"\n"
        if count % 10 == 0:
            embed.add_field(name = "trade penalties", value = s)
            s = ""
    if len(s) > 0:
        embed.add_field(name = "trade penalties", value = s)
    return embed
def penalty(embed, t, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    tp = pull_info.trade_penalty(t['tid'], export)
    embed.add_field(name = str(tp), value = "This team's trade penalty is "+str(tp))
    return embed
def capspace(embed, t, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    l = []
    salaryCap = export['gameAttributes']['salaryCap']
    for tid in export['teams']:
        if not tid['disabled']:
            payroll = 0
            for p in players:
                if p['tid'] == tid['tid']:
                    payroll += p['contract']['amount']
            if 'releasedPlayers' in export:
                for rp in export['releasedPlayers']:
                    if rp['tid'] == tid['tid']:
                        payroll += rp['contract']['amount']
            name = tid['region']+" "+tid['name']
            l.append([name, (salaryCap-payroll)/1000])
    l = sorted(l, key = lambda a: a[1], reverse = True)
    text = ""
    for i in l[0:min(len(l),20)]:
        text = text + i[0] + ": " + str(i[1])+"\n"

    embed.add_field(name = "What am I supposed to write for the name of the embed", value = text)
    return embed
def rgoptions(embed, team, commandInfo):
    listofthings = "season, tid, yearsWithTeam, per, ewa, astp, blkp, drbp, orbp, stlp, trbp, usgp, drtg, ortg, dws, ows, obpm, dbpm, vorp, gp, gs, min, minAvailable, fg, fga, fgAtRim, fgaAtRim, fgLowPost, fgaLowPost, fgMidRange, fgaMidRange, tp, tpa, ft, fta, pm, orb, drb, ast, tov, stl, blk, ba, pf, pts, dd, td, qd, fxf, jerseyNumber, mpg, ppg, reb, rpg, apg, bpg, spg, tpg, fpg, fg%, ft%, tp%, ws, bpm, ast/tov, fg%AtRim, fg%LowPost, fg%MidRange"

    embed.add_field(name = "Stats options", value = listofthings)
    return embed

def rostergraph(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    players = export['players']
    message = commandInfo['message']
    m=commandInfo['message'].content.replace('rostergraph',"")[1:].strip()
        #print(m+"hi")
        
    try:
        yr = int(message.content.split(" ")[-1])
        m=m.replace(str(yr),"").strip()
    except ValueError:
        yr = export['gameAttributes']['season']
    if yr:
        t = m.split(" ")
        
        tid = team['tid'] # default, team is the user team
        
        firststatname = "ortg"
        secondstatname = "drtg"
        assigned = False
        secondisassigned = False
        poff = False
        listofthings = "season, tid, yearsWithTeam, per, ewa, astp, blkp, drbp, orbp, stlp, trbp, usgp, drtg, ortg, dws, ows, obpm, dbpm, vorp, gp, gs, min, minAvailable, fg, fga, fgAtRim, fgaAtRim, fgLowPost, fgaLowPost, fgMidRange, fgaMidRange, tp, tpa, ft, fta, pm, orb, drb, ast, tov, stl, blk, ba, pf, pts, dd, td, qd, fxf, jerseyNumber, mpg, ppg, reb, rpg, apg, bpg, spg, tpg, fpg, fg%, ft%, tp%, ws, bpm, ast/tov, fg%AtRim, fg%LowPost, fg%MidRange"


        for item in t:
            if item.__contains__("layoff"):
                poff = True
            elif len(item)>1:

                if not assigned:
                    if item in listofthings:
                        firststatname = item
                        assigned = True
                else:
                    if not secondisassigned:
                        if item in listofthings:
                            secondstatname = item
                            secondisassigned = True


        
        roster = []
        statentries = []
        for player in players:
            t = False
            if player['retiredYear'] is None:
                t = True
            else:
                if  player['retiredYear'] >= yr:
                    t = True
            if t:

                if yr == export['gameAttributes']['season'] and len(player.get("stats"))>0 and player.get("stats")[-1].get("tid")==tid:

                    
                    if not poff:
                        if player.get("stats")[-1].get("playoffs")==False:
                            roster.append(player)
                            statentries.append(player.get("stats")[-1])
                        else:
                            if player.get("stats")[-2].get("playoffs")==False and player.get("stats")[-2].get("tid")==tid and player.get("stats")[-2].get("season")==yr:
                                roster.append(player)
                                statentries.append(player.get("stats")[-2])
                    else:
                        if player.get("stats")[-1].get("playoffs")==True:
                            roster.append(player)
                            statentries.append(player.get("stats")[-1])
                if yr<export['gameAttributes']['season']:
                    for item in player.get("stats"):
                        if item.get("season")==yr and item.get("tid")==tid and item.get("playoffs")==poff:
                            roster.append(player)
                            statentries.append(item)

        names = []
        firststat = []
        secondstat = []
        sizes = []
        colors = ["#F63309","#09F621","#090FF6","#F68509","#F3F609","#09c3ba","#601A83","#83221A","#835B1A","#b1d5fb","#BB22B5","#FF13CD","#6891f8","#fcc5f4","#1d6b05","#878787","#787878","#A36B41","#87B5FF","#F5BFBD","#4E1B4B","#76190F","#41203E","#0A144A"]
        t = ""
        
        for item in listofthings.split(" "):
            if item.replace(",","").lower()==firststatname.lower():
                firststatname=item.replace(",","")
            if item.replace(",","").lower()==secondstatname.lower():
                secondstatname=item.replace(",","")
        #print("oh "+firststatname+" oh")
        for index in range (0,len(roster)):
            s = statentries[index]
            pid = roster[index].get("pid")
            if s['season'] == yr:
            
                #calculate secondary stats
                if s.get("min")>100 or (poff == True and s.get("min")>10):
                    
                    names.append(roster[index]['firstName'] + " " + roster[index]['lastName'])
                    #print(s)
                    s.update({"mpg":s.get("min")/s.get("gp")})
                    s.update({"ppg":s.get("pts")/s.get("gp")})
                    s.update({"reb":s.get("orb")+s.get("drb")})
                    s.update({"rpg":s.get("reb")/s.get("gp")})
                    s.update({"apg":s.get("ast")/s.get("gp")})
                    s.update({"bpg":s.get("blk")/s.get("gp")})
                    s.update({"spg":s.get("stl")/s.get("gp")})
                    s.update({"tpg":s.get("tov")/s.get("gp")})
                    s.update({"fpg":s.get("pf")/s.get("gp")})
                    s.update({"fg%":100*s.get("fg")/(s.get("fga")+0.000001)})
                    s.update({"jerseyNumber":int(s.get("jerseyNumber"))})
                    s.update({"ft%":100*s.get("ft")/(s.get("fta")+0.00001)})
                    s.update({"tp%":100*s.get("tp")/(s.get("tpa")+0.00001)})
                    s.update({"ws":s.get("ows")/s.get("dws")})
                    s.update({"bpm":s.get("obpm")/s.get("dbpm")})
                    
                    s.update({"ast/tov":s.get("ast")/(s.get("tov")+0.0000001)})
                    s.update({"fg%AtRim":100*s.get("fgAtRim")/(s.get("fgaAtRim")+0.0000001)})
                    s.update({"fg%LowPost":100*s.get("fgLowPost")/(s.get("fgaLowPost")+0.0000001)})
                    s.update({"fg%MidRange":100*s.get("fgMidRange")/(s.get("fgaMidRange")+0.0000001)})
                    #print(s.keys())

                    #print(firststatname)
                    if not (s.__contains__(firststatname) and s.__contains__(secondstatname)):
                        t += "Something about the two variables you specified is invalid.\n"
                        t += "To help you out: what we received from you was: "+firststatname+" and "+secondstatname+"\n"
                        embed.add_field(name = "Error", value = t)

                        return embed
                    firststat.append(s.get(firststatname))
                    secondstat.append(s.get(secondstatname))
                    sizes.append(s.get("min"))
                    r = lambda: random.randint(0,255)
                    colors.append('#%02X%02X%02X' % (r(),r(),r()))
                    #print(list(s.keys()))
        if len(sizes) == 0:
            t += "No player was found matching the criteria you have given. Note that team abbreviation may overlap with stats specified. If so, then append the full name of the team you want at the very end"
            embed.add_field(name = "Error", value = t)
            return embed
        a = max(sizes)
        team_name = team['name']
        for i in range (0,len(sizes)):
            sizes[i] = 0.1+(sizes[i]/a)
        tt = "Regular season roster graph, "+team_name+" "+str(yr)
        if poff:
            tt = "Playoffs roster graph, "+team_name+" "+str(yr)
        fig = px.scatter(x=firststat, y=secondstat,color=names,size=sizes, color_discrete_sequence = colors[0:len(firststat)])
        fig.update_layout(
        title=tt,
        xaxis=dict(
            title=firststatname,

        ),
        yaxis=dict(
            title=secondstatname,
        ))
        #fig.show()
        fig.write_image('second_figure.png',height=630)
        prefix = serversList[str(message.guild.id)]['prefix']
        t += "Circle size corresponds to minutes played.\ncall "+prefix+"rgoptions to see options"
        embed.add_field(name = "Behold the least useful graph you will ever see!", value = t)
        return embed


def roster(embed, t, commandInfo):
    #need drastically different versions depending on whether or not this is the current roster
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    print("huh")
    season = export['gameAttributes']['season']
    players = export['players']
    #we can deal with formatting later - for now, form the list of players depending on whether or not this is current
    #CURRENT - grab by TID and sort by rosterPosition
    #PAST - grab by final stats TID and sort by OVR
    playerRatings = [] #for TR calc
    if commandInfo['season'] == season:
        #CURRENT
        rosterList = []
        for p in players:
            if p['tid'] == t['tid']:

                rosterList.append([p['pid'], p['rosterOrder'], pull_info.pinfo(p)])
                playerRatings.append(p['ratings'][-1]['ovr'])

        rosterList.sort(key=lambda r: r[1])
    else:
        #PAST
        rosterList = []
        for p in players:
            if 'stats' in p:
                stats = p['stats']
                endTeam = -1
                for s in stats:
                    if s['season'] == commandInfo['season']:
                        endTeam = s['tid']
                if endTeam == t['tid']:
                    ratings = p['ratings']
                    ovr = ratings[-1]['ovr']
                    for r in ratings:
                        if r['season'] == commandInfo['season']:
                            ovr = r['ovr']
                    rosterList.append([p['pid'], ovr])
                    playerRatings.append(ovr)
        rosterList.sort(key=lambda r: r[1], reverse = True)
    #rosterList now contains our sorted roster. all that's left is to put it in the embed. but first, we need to do the top parts
    #note that there will be the stats roster if this is -sroster or if it is a past season, the regular roster otherwise
    embed.add_field(name=f"Team Rating: {pull_info.team_rating(playerRatings, False)}/100", value=f"Playoffs: {pull_info.team_rating(playerRatings, True)}/100", inline=True)
    text = ""
    overflow = ""
    print(commandInfo)
    if commandInfo['command'] == 'roster' and commandInfo['season'] == season:
        #add the payroll
        payroll = 0
        for p in players:
            if p['tid'] == t['tid']:
                payroll += p['contract']['amount']
        if 'releasedPlayers' in export:
            for rp in export['releasedPlayers']:
                if rp['tid'] == t['tid']:
                    payroll += rp['contract']['amount']
        salaryCap = export['gameAttributes']['salaryCap']
        hardCap = serversList[str(commandInfo['serverId'])]['hardcap']

        embed.add_field(name=f"Payroll: ${payroll/1000}M/${salaryCap/1000}M", value=f"Hard Cap: ${hardCap}M", inline=True)
        embed.add_field(name=f"Roster Spots: {export['gameAttributes']['maxRosterSize']-len(rosterList)}", value=f"PTI: {t['pti'][0]} regular season, {t['pti'][1]} playoffs", inline=True)
        #now make the standard roster
        added = 0
        for player in rosterList:
            pid = player[0]
            for p in players:
                if p['pid'] == pid:
                    #print("got here")
                    p = pull_info.pinfo(p)
                    added += 1
                    
                    playerLine = f"{p['position']} **{p['name']}** - {commandInfo['season'] - p['born']} yo {p['ovr']}/{p['pot']} | ${p['contractAmount']}M/{p['contractExp']}" + '\n'
                    if added <= 15:
                        text += playerLine
                    else:
                        overflow += playerLine
    else:
        if commandInfo['command'] == 'psroster' or commandInfo['command'] == 'sroster' or commandInfo['command'] == 'roster':
            if commandInfo['command'] == 'psroster':
                playoffs = True
            else:
                playoffs = False
            #stats roster
            added = 0
            for player in rosterList:
                pid = player[0]
                for p in players:
                    if p['pid'] == pid:
                        added += 1
                        stats = pull_info.pstats(p, commandInfo['season'], playoffs)
                        p = pull_info.pinfo(p, commandInfo['season'])
                        if stats == None:
                            statLine = '``No stats available.``'
                        else:
                            statLine = f"``{stats['pts']} pts, {stats['orb'] + stats['drb']} reb, {stats['ast']} ast, {stats['per']} PER``"

                        playerLine = f"{p['position']} **{p['name']}** - {commandInfo['season'] - p['born']} yo {p['ovr']}/{p['pot']} | {statLine}" +'\n'
                        if added <= 13 and len(text) < 930:
                            text += playerLine
                        else:
                            overflow += playerLine
        if commandInfo['command'] == 'progster' or commandInfo['command'] == 'proster':
            added = 0
            for player in rosterList:
                pid = player[0]
                for p in players:
                    if p['pid'] == pid:
                        added += 1
                        p2 = pull_info.pinfo(p)
                        pastrating = p2['ovr']
                        for item in p['ratings']:

                            if item['season'] == season - 1:
                                pastrating = item['ovr']
                                pastpot = item['pot']
                                pastage = item['season'] - p2['born']
                        prog = p2['ovr'] - pastrating
                        if prog > 0:
                            prog = "+"+str(prog)
                        elif prog == 0:
                            prog = "0"
                        elif prog < 0:
                            prog = str(prog)
                        playerLine = f"{p2['position']} **{p2['name']}** - {commandInfo['season'] - p2['born']} yo {p2['ovr']}/{p2['pot']} "+" **("+prog+ ')** (was '+str(pastage)+" yo "+str(pastrating)+"/"+str(pastpot)+')\n'
                        if added <= 13:
                            text += playerLine
                        else:
                            overflow += playerLine
                            
                                    
            
        
    embed.add_field(name='Roster', value=text, inline=False)
    if overflow != "":
        embed.add_field(name='Continued', value=overflow, inline=False)
    
    return embed

def lineup(embed, t, commandInfo):
    #simply grab current lineup
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    players = export['players']
    if commandInfo['season'] != season:
        embed.add_field(name='No Support for Past Seasons', value="Basketball GM doesn't store lineup data for past seasons, so this command is only good for current lineups. You can access past teams with the roster command.")
    else:
        lineup = []
        for p in players:
            if p['tid'] == t['tid']:
                lineup.append([p['pid'], p['rosterOrder']])
        lineup.sort(key=lambda l: l[1])
        text = ""
        overflow = ""
        added = 0
        for l in lineup:
            added += 1
            for p in players:
                if p['pid'] == l[0]:
                    p = pull_info.pinfo(p)

                    ptText = None
                    #get the PT info
                    if p['ptModifier'] == 1:
                        ptText = ""
                    if p['ptModifier'] == 1.25:
                        ptText = "(**+** minutes)"
                    if p['ptModifier'] == 0.75:
                        ptText = "(**-** minutes)"
                    if p['ptModifier'] == 1.5:
                        ptText = "(**++** minutes)"
                    if p['ptModifier'] == 0:
                        ptText = "(**0** minutes)"
                    if ptText == None:
                        ptText = f"(custom playing time: **{round(p['ptModifier']*p['ovr'], 2)}** OVR)"
                    
                    line = f"{added}. {p['position']} **{p['name']}** - {p['ovr']}/{p['pot']} {ptText}" + '\n'
                    if added == 5:
                        line += '---' + '\n'
                    if added <= 15:
                        text += line
                    else:
                        overflow += line
        embed.add_field(name='Team Lineup', value=text)
        if overflow != '':
            embed.add_field(name='Continued', value=overflow, inline=False)
        return embed

def picks(embed, t, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    text = ""
    overflow = ""
    picks.sort(key=lambda p: p['season'])
    added = 0
    for p in picks:
        if p['tid'] == t['tid']:
            
            line = f"{p['season']} round {p['round']} pick"
            if p['pick'] != 0:
                line += f"(#{p['pick']})"
            if p['originalTid'] != p['tid']:
                for team in teams:
                    if team['tid'] == p['originalTid']:
                        abbrev = team['abbrev']
                line += f" ({abbrev})"
            if p['round'] == 1:
                line = '**' + line + '**'
            line += '\n'
            if added < 20:
                text += line
            else:
                overflow += line
            added+=1
    embed.add_field(name=f"{t['abbrev']} Draft Picks", value=text)
    if overflow != "":
        embed.add_field(name='Continued', value=overflow)
    return embed

def ownspicks(embed, t, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    text = ""
    overflow = ""
    picks.sort(key=lambda p: p['season'])
    added = 0
    for p in picks:
        if p['originalTid'] == t['tid']:
            
            line = f"{p['season']} round {p['round']} pick - owned by"
            for team in teams:
                if team['tid'] == p['tid']:
                    abbrev = team['abbrev']
            line += f" {abbrev}"
            if p['round'] == 1:
                line = '**' + line + '**'
            line += '\n'
            if added < 20:
                text += line
            else:
                overflow += line
            added+=1
    embed.add_field(name=f"{t['abbrev']} Draft Pick Owners", value=text)
    if overflow != "":
        embed.add_field(name='Continued', value=overflow, inline=False)
    return embed
def teamcompare(embed, team, commandInfo):
    message = commandInfo['message']
    export = shared_info.serverExports[str(message.guild.id)]
    season = export['gameAttributes']['season']
    players = export['players']
    teams = export['teams']
    if not "," in commandInfo['message'].content:
        return embed
    a = commandInfo['message'].content.split(",")[0]
    b = commandInfo['message'].content.split(",")[1]
    # first team
    commandSeasona = season
    text = a.split(" ")
    for m in text:
        try:
            m = int(m)
            commandSeasona = m
            text.remove(str(commandSeasona))
        except:
            pass
    try: commandTida = serversList[str(message.guild.id)]['teamlist'][str(message.author.id)]
    except KeyError: commandTida = -1
    if commandSeasona != season:
        for t in teams:
            seasons = t['seasons']
            for s in seasons:
                if s['season'] == commandSeasona:
                    teamNames = [s['abbrev'], s['region'], s['name'], s['region'] + ' ' + s['name']]
                    for name in teamNames:
                        if str.lower(name.strip()) in [str(m).lower() for m in text]:
                            commandTida = t['tid']
        if commandTida == -1:
            for t in teams:
                teamNames = [t['abbrev'], t['region'], t['name'], t['region'] + ' ' + t['name']]
                for name in teamNames:
                    if str.lower(name.strip()) in [str(m).lower() for m in text]:
                        commandTida = t['tid']
    else:
        for t in teams:
            teamNames = [t['abbrev'], t['region'], t['name'], t['region'] + ' ' + t['name']]
            for name in teamNames:

                if str.lower(name.strip()) in [str(m).lower() for m in text]:
                    commandTida= t['tid']
    # second team
    commandSeasonb = season
    text = b.split(" ")
    for m in text:
        try:
            m = int(m)
            commandSeasonb = m
            text.remove(str(commandSeasonb))
        except:
            pass
    try: commandTidb = serversList[str(message.guild.id)]['teamlist'][str(message.author.id)]
    except KeyError: commandTidb = -1
    if commandSeasonb != season:
        for t in teams:
            seasons = t['seasons']
            for s in seasons:
                if s['season'] == commandSeasonb:
                    teamNames = [s['abbrev'], s['region'], s['name'], s['region'] + ' ' + s['name']]
                    for name in teamNames:
                        if str.lower(name.strip()) in [str(m).lower() for m in text]:
                            commandTidb = t['tid']
        if commandTidb == -1:
            for t in teams:
                teamNames = [t['abbrev'], t['region'], t['name'], t['region'] + ' ' + t['name']]
                for name in teamNames:
                    if str.lower(name.strip()) in [str(m).lower() for m in text]:
                        commandTidb = t['tid']
    else:
        for t in teams:
            teamNames = [t['abbrev'], t['region'], t['name'], t['region'] + ' ' + t['name']]
            for name in teamNames:
                if str.lower(name.strip()) in [str(m).lower() for m in text]:
                    commandTidb= t['tid']
    print(commandTida)
    print(commandSeasona)
    print(commandTidb)
    print(commandSeasonb)
    for t in teams:

        if t['tid'] == commandTida:

            ainfo = pull_info.tinfo(t,commandSeasona)
            for s in t['seasons']:
                if s['season'] == commandSeasona:
                    aplayoffResult = pull_info.playoff_result(s['playoffRoundsWon'], export['gameAttributes']['numGamesPlayoffSeries'], s['season'], False)
            for s in t['stats']:
                if s['season'] == commandSeasona:
                    print(s)
                    if not ('playoffs' in s and s['playoffs']):
                        astats = s
            
        if t['tid'] == commandTidb:
            binfo = pull_info.tinfo(t,commandSeasonb)
            for s in t['seasons']:
                if s['season'] == commandSeasonb:
                    bplayoffResult = pull_info.playoff_result(s['playoffRoundsWon'], export['gameAttributes']['numGamesPlayoffSeries'], s['season'], False)
            for s in t['stats']:
                if s['season'] == commandSeasonb:
                    if not ('playoffs' in s and s['playoffs']):
                        bstats = s
    print(astats)
    astatssum = {'Points':astats['pts']/astats['gp'],"FG%":astats['fg']*100/astats['fga'],"TP%":astats['tp']*100/astats['tpa'],'Rebounds':(astats['orb']+astats['drb'])/astats['gp'],
                 'Assists':astats['ast']/astats['gp'],'Steals':astats['stl']/astats['gp'],'Blocks':astats['blk']/astats['gp'],'Turnovers':astats['tov']/astats['gp'],'Opp. Points':astats['oppPts']/astats['gp'],
                 "Opp. FG%":astats['oppFg']*100/astats['oppFga'],"Opp. TP%":astats['oppTp']*100/astats['oppTpa'],'Opp. Rebounds':(astats['oppOrb']+astats['oppDrb'])/astats['gp'],
                 'Opp. Assists':astats['oppAst']/astats['gp'],'Opp. Steals':astats['oppStl']/astats['gp'],'Opp. Blocks':astats['oppBlk']/astats['gp'],'Opp. Turnovers':astats['oppTov']/astats['gp']}
    bstatssum = {'Points':bstats['pts']/bstats['gp'],"FG%":bstats['fg']*100/bstats['fga'],"TP%":bstats['tp']*100/bstats['tpa'],'Rebounds':(bstats['orb']+bstats['drb'])/bstats['gp'],
                 'Assists':bstats['ast']/bstats['gp'],'Steals':bstats['stl']/bstats['gp'],'Blocks':bstats['blk']/bstats['gp'],'Turnovers':bstats['tov']/bstats['gp'],'Opp. Points':bstats['oppPts']/bstats['gp'],
                 "Opp. FG%":bstats['oppFg']*100/bstats['oppFga'],"Opp. TP%":bstats['oppTp']*100/bstats['oppTpa'],'Opp. Rebounds':(bstats['oppOrb']+bstats['oppDrb'])/bstats['gp'],
                 'Opp. Assists':bstats['oppAst']/bstats['gp'],'Opp. Steals':bstats['oppStl']/bstats['gp'],'Opp. Blocks':bstats['oppBlk']/bstats['gp'],'Opp. Turnovers':bstats['oppTov']/bstats['gp']}
    li = ['Points','FG%','TP%','Rebounds','Assists','Steals','Blocks', 'Turnovers']
    astring = ""
    bstring = ""
    for item in li:
        isturnovers = (item == 'Turnovers')
        if (isturnovers and astatssum[item] < bstatssum[item]) or (not isturnovers and astatssum[item] > bstatssum[item]):
            astring = astring + item + ": **"+str(round(astatssum[item],2))+"**\n"
            bstring = bstring + item + ": "+str(round(bstatssum[item],2))+"\n"
        elif (isturnovers and astatssum[item] > bstatssum[item]) or (not isturnovers and astatssum[item] < bstatssum[item]):
            astring = astring + item + ": "+str(round(astatssum[item],2))+"\n"
            bstring = bstring + item + ": **"+str(round(bstatssum[item],2))+"**\n"
        else:
            astring = astring + item + ": "+str(round(astatssum[item],2))+"\n"
            bstring = bstring + item + ": "+str(round(bstatssum[item],2))+"\n"
    aoppstring = ""
    boppstring = ""
    for item in li:
        item = "Opp. "+item
        isturnovers = (item == 'Opp. Turnovers')
        if (isturnovers and astatssum[item] > bstatssum[item]) or (not isturnovers and astatssum[item] < bstatssum[item]):
            aoppstring = aoppstring + item + ": **"+str(round(astatssum[item],2))+"**\n"
            boppstring = boppstring + item + ": "+str(round(bstatssum[item],2))+"\n"
        elif (isturnovers and astatssum[item] < bstatssum[item]) or (not isturnovers and astatssum[item] > bstatssum[item]):
            aoppstring = aoppstring + item + ": "+str(round(astatssum[item],2))+"\n"
            boppstring = boppstring + item + ": **"+str(round(bstatssum[item],2))+"**\n"
        else:
            aoppstring = aoppstring + item + ": "+str(round(astatssum[item],2))+"\n"
            boppstring = boppstring + item + ": "+str(round(bstatssum[item],2))+"\n"
    print(aoppstring)
    embed.add_field(name = ainfo['name']+" "+str(commandSeasona), value = "Record: "+ainfo['record']+"\nPlayoffs: "+aplayoffResult, inline = True)
    embed.add_field(name = binfo['name']+" "+str(commandSeasonb), value = "Record: "+binfo['record']+"\nPlayoffs: "+bplayoffResult, inline = True)
    embed.add_field(name = "filler",value = "Yeh", inline = True)
    embed.add_field(name = ainfo['name']+" "+str(commandSeasona)+" stats", value = astring, inline = True)
    embed.add_field(name = binfo['name']+" "+str(commandSeasonb)+" stats", value = bstring, inline = True)
    embed.add_field(name = "filler",value = "Yeh", inline = True)
    embed.add_field(name = ainfo['name']+" "+str(commandSeasona)+" opponent stats", value = aoppstring, inline = True)
    embed.add_field(name = binfo['name']+" "+str(commandSeasonb)+" opponent stats", value = boppstring, inline = True)
    embed.add_field(name = "filler",value = "Yeh", inline = True)
    aroster = dict()
    arosterdesc = dict()
    
    broster = dict()
    brosterdesc = dict()
    for p in players:
        for s in p['stats']:
            if not s['playoffs']:
                if s['season'] == commandSeasona:
                    if s['tid'] == commandTida:
                        stats = pull_info.pstats(p, s['season'], playoffs=False, qualifiers=False, tids = commandTida)
                        if stats['gp'] > 0:
                            # is on team a
                            if not p['pid'] in aroster:
                                aroster.update({p['pid']:s['min']})
                            else:
                                aroster.update({p['pid']:aroster[p['pid']]+s['min']})
                            for r in p['ratings']:
                                if r['season'] == commandSeasona:
                                    pot = r['pot']
                                    ovr = r['ovr']
                                    pos = r['pos']
                            age = commandSeasona-p['born']['year']
                            
                            
                            arosterdesc.update({p['pid']:"**"+p['firstName']+" "+p['lastName']+"**:\n"+str(ovr)+"/"+str(pot)+", "+str(pos)+", Age "+str(age)+"\n"+
                                                str(round(stats['gp'],0))+" GP, "+str(round(stats['gs'],0))+" GS, \n"+str(round(stats['pts'],1))+" pts, "+str(round(stats['orb']+stats['drb'],1))+" reb, "+str(round(stats['ast'],1))+" ast"})
                if s['season'] == commandSeasonb:
                    if s['tid'] == commandTidb:
                         stats = pull_info.pstats(p, s['season'], playoffs=False, qualifiers=False, tids = commandTidb)
                         if stats['gp'] > 0:
                            # is on team b
                            if not p['pid'] in broster:
                                broster.update({p['pid']:s['min']})
                            else:
                                broster.update({p['pid']:aroster[p['pid']]+s['min']})
                            for r in p['ratings']:
                                if r['season'] == commandSeasonb:
                                    pot = r['pot']
                                    ovr = r['ovr']
                                    pos = r['pos']
                            age = commandSeasonb-p['born']['year']
                           
                            brosterdesc.update({p['pid']:"**"+p['firstName']+" "+p['lastName']+"**:\n"+str(ovr)+"/"+str(pot)+", "+str(pos)+", Age "+str(age)+"\n"+
                                                str(round(stats['gp'],0))+" GP, "+str(round(stats['gs'],0))+" GS, \n"+str(round(stats['pts'],1))+" pts, "+str(round(stats['orb']+stats['drb'],1))+" reb, "+str(round(stats['ast'],1))+" ast"})
  
    print(aroster)
    k = sorted(aroster.keys(), key= lambda x: -aroster[x])
    l = sorted(broster.keys(), key = lambda x: -broster[x])
    stra = ""
    for obj in k[0:min(len(k),10)]:
        stra = stra + arosterdesc[obj]+"\n"
    strb = ""
    for obj in l[0:min(len(l),10)]:
        strb = strb + brosterdesc[obj]+"\n"
    print(k)
    embed.add_field(name = ainfo['name']+" "+str(commandSeasona)+" top players", value = stra, inline = True)
    embed.add_field(name = binfo['name']+" "+str(commandSeasonb)+" top players", value = strb, inline = True)
    return embed
def history(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    players = export['players']
    #GENERIC INFO
    overallRecord = [0, 0]
    totalSeasons = 0
    playoffs = 0
    titles = 0
    finals = 0
    bestRecord = [-1, 5]
    worstRecord = [2,0]

    #PREVIOUS 10 SEASONS
    lines = []
    for t in teams:
        if t['tid'] == team['tid']:
            seasons = t['seasons']
            for s in seasons:
                totalSeasons += 1
                overallRecord[0] += s['won']
                overallRecord[1] += s['lost']
                if s['playoffRoundsWon'] > -1:
                    playoffs += 1
                playoffResult = pull_info.playoff_result(s['playoffRoundsWon'], export['gameAttributes']['numGamesPlayoffSeries'], s['season'], True)
                if playoffResult == '**won championship**':
                    titles += 1
                    finals += 1
                if playoffResult == 'made finals':
                    finals += 1
                try: winP = s['won'] / (s['won'] + s['lost'])
                except ZeroDivisionError: winP = 0
                try:
                    if winP > bestRecord[0] / (bestRecord[0]+bestRecord[1]):
                        bestRecord = [s['won'], s['lost'], s['season']]
                    if winP < worstRecord[0] / (worstRecord[0]+worstRecord[1]):
                        worstRecord = [s['won'], s['lost'], s['season']]
                except ZeroDivisionError: pass
                line = f"{s['season']} - {s['abbrev']} - {s['won']}-{s['lost']}"
                if playoffResult != '':
                    line+= f', {playoffResult}'
                lines.append(line)
                #RETIRED JERSEYS
                retiredJerseys = ""
                if len(t['retiredJerseyNumbers']) == 0:
                    retiredJerseys = "*No retired jerseys.*"
                else:
                    for r in t['retiredJerseyNumbers']:
                        if not 'pid' in r:
                            retiredName = "Unknown"
                        else:
                            for p in players:
                                if p['pid'] == r['pid']:
                                    retiredName = p['firstName'] + ' ' + p['lastName']
                        retiredJerseys += '**#' + str(r['number']) + '** - ' + retiredName + '\n'
    #CALCULATE TOP PLAYERS
    topPlayers = []
    for p in players:
        if 'stats' in p:
            stats = p['stats']
            pts = 0
            reb = 0
            ast = 0
            ewa = 0
            for s in stats:
                if s['tid'] == team['tid'] and s['playoffs'] == False:
                    pts += s['pts']
                    reb += s['drb'] + s['orb']
                    ast += s['ast']
                    ewa += s['ewa']
            topPlayers.append([f"{p['firstName']} {p['lastName']}", pts, reb, ast, ewa])
    topPlayers.sort(key=lambda t: t[4], reverse=True)
    ewaText = ""
    number = 0
    for t in topPlayers[:5]:
        ewaText += f"{number}. **{t[0]}** - {round(t[4], 1)} EWA" + '\n'
        number+=1
    topPlayers.sort(key=lambda t: t[1], reverse=True)
    ptsText = ""
    number = 0
    for t in topPlayers[:3]:
        ptsText += f"{number}. **{t[0]}** - {t[1]} pts" + '\n'
        number+=1
    topPlayers.sort(key=lambda t: t[2], reverse=True)
    rebText = ""
    number = 0
    for t in topPlayers[:3]:
        rebText += f"{number}. **{t[0]}** - {t[2]} reb" + '\n'
        number+=1
    topPlayers.sort(key=lambda t: t[3], reverse=True)
    astText = ""
    number = 0
    for t in topPlayers[:3]:
        astText += f"{number}. **{t[0]}** - {t[3]} ast" + '\n'
        number+=1

    #compile past seasons
    lines.reverse()
    lines = lines[:15]
    pastSeasonText = '\n'.join(lines)
    
    #embed time
    try: overallWinP = str(round(overallRecord[0]/(overallRecord[0]+overallRecord[1]), 4))[1:]
    except ZeroDivisionError: overallWinP = '0'
    try: playoffsP = str(round(100*(playoffs/totalSeasons), 2))
    except ZeroDivisionError: playoffsP = 0
    embed.add_field(name='Generic', value=f"**Overall record:** {overallRecord[0]}-{overallRecord[1]} ({overallWinP})" + '\n'
                    + f"{totalSeasons} seasons, {playoffs} playoffs ({playoffsP}%)" + '\n'
                    + f"Finals Appearances: {finals}" + '\n' + f"**Championships:** {titles}" + '\n'
                    + f"Best Record: {bestRecord[0]}-{bestRecord[1]} ({bestRecord[2]})" + '\n' + f"Worst Record: {worstRecord[0]}-{worstRecord[1]} ({worstRecord[2]})")
    embed.add_field(name='Retired Jerseys', value=retiredJerseys)
    embed.add_field(name='Top Players', value=ewaText)
    embed.add_field(name='Top Statistics', value=f"**__Points__**" + '\n' + ptsText + '\n' + '**__Rebounds__**' + '\n' + rebText + '\n' + '**__Assists__**' + '\n' + astText)
    embed.add_field(name='Past 15 Seasons', value=pastSeasonText)
    
    return embed

def finances(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    players = export['players']

    if commandInfo['season'] < season:
        embed.add_field(name='Error', value='Finances cannot be shown for past seasons, only current and future ones.')
    else:
        roster = []
        playerCount = 0
        payroll = 0
        for p in players:
            if p['tid'] == team['tid']:
                if p['contract']['exp'] >= commandInfo['season']:
                    roster.append([p['pid'], p['contract']['amount'], False])
                    payroll+= p['contract']['amount']
                    playerCount += 1
        if 'releasedPlayers' in export:
            releasedPlayers = export['releasedPlayers']
            for rp in releasedPlayers:
                if rp['tid'] == team['tid']:
                    if rp['contract']['exp'] >= commandInfo['season']:
                        roster.append([rp['pid'], rp['contract']['amount'], True, rp['contract']['exp']])
                        payroll+= rp['contract']['amount']
        roster.sort(key=lambda r: r[1], reverse=True)
        text = ""
        overflow = ""
        contractNumber = 1
        number = 0
        if export['gameAttributes']['phase'] >= 7:
            contractNumber = 0
        for r in roster:
            for p in players:
                if p['pid'] == r[0]:
                    line = f"{p['ratings'][-1]['pos']} **{p['firstName'][0]}. {p['lastName']}** - $"
                    if r[2]:
                        line += f"{r[1]/1000}M/{r[3]-season+contractNumber }Y"
                        line = '*' + line + '*'
                    else:
                        line += f"{p['contract']['amount']/1000}M/{p['contract']['exp']-season+contractNumber }Y"
                    line += '\n'
                    if number < 16:
                        text += line
                    else:
                        overflow += line
                    number += 1
        embed.add_field(name=f"{team['abbrev']} Finances ({commandInfo['season']})", value=text)
        if overflow != "":
            embed.add_field(name='Continued', value=overflow)
        #add basic info
        salaryCap = export['gameAttributes']['salaryCap']/1000
        rosterLimit = export['gameAttributes']['maxRosterSize']
        for t in teams:
            if t['tid'] == team['tid']:
                hype = t['seasons'][-1]['hype']
        embed.add_field(name=f"Payroll: ${payroll/1000}M/${salaryCap}M", value=f"Cap space: ${round((salaryCap-(payroll/1000)), 2)}M" + '\n' + f'Roster spots: {rosterLimit-playerCount}' + '\n' + f'**Hype:** {hype}', inline=False)
    return embed

def seasons(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    players = export['players']
    #season is irrelevant. collect seasons of a team
    lines = []
    for t in teams:
        if t['tid'] == team['tid']:
            seasons = t['seasons']
            for s in seasons:
                info = pull_info.tinfo(t, s['season'])
                line = f"{s['season']} - {info['abbrev']} - {info['record']}"
                playoffResult = pull_info.playoff_result(info['roundsWon'], export['gameAttributes']['numGamesPlayoffSeries'], s['season'], True)
                if playoffResult != "":
                    line += f", {playoffResult}"
                lines.append(line)
    lines.reverse()
    numDivs, rem = divmod(len(lines), 15)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*15):((i*15)+15)]
        text = '\n'.join(newLines)
        embed.add_field(name='Seasons', value=text)
    return embed

def tstats(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    players = export['players']

    if commandInfo['command'] == 'tstats':
        playoffs = False
    else:
        playoffs = True

    #quick check
    gamesPlayed = False
    for t in teams:
        if t['tid'] == team['tid']:
            stats = t['stats']
            for s in stats:
                if s['season'] == commandInfo['season'] and s['playoffs'] == playoffs and s['gp'] > 0:
                    gamesPlayed = True
    if gamesPlayed == False:
        embed.add_field(name='Error', value='No stats found for the specified season or playoff.')
    else:
    
        def rank(season, statName, stat, type, worseBetter=False):
            rank = 1
            for t in teams:
                stats = t['stats']
                for s in stats:
                    if s['season'] == season and s['playoffs'] == playoffs:
                        s['reb'] = s['drb'] + s['orb']
                        s['oppReb'] = s['oppDrb'] + s['oppOrb']
                        if worseBetter:
                            if type == 'total':
                                if s[statName] < stat:
                                    rank += 1
                            if type == 'average':
                                if s[statName]/s['gp'] < stat:
                                    rank += 1
                            if type == 'percent':
                                try: teamAmount = s[statName[0]]/s[statName[1]]
                                except ZeroDivisionError: teamAmount = 10000000000
                                try: origAmount = stat[0] / (stat[1])
                                except ZeroDivisionError: origAMount = 0
                                if teamAmount < origAmount:
                                    rank += 1
                        else:
                            if type == 'total':
                                if s[statName] > stat:
                                    rank += 1
                            if type == 'average':
                                if s[statName]/s['gp'] > stat:
                                    rank += 1
                            if type == 'percent':
                                try: teamAmount = s[statName[0]]/s[statName[1]]
                                except ZeroDivisionError: teamAmount = 10000000000
                                try: origAmount = stat[0] / (stat[1])
                                except ZeroDivisionError: origAmount = 0
                                if teamAmount > origAmount:
                                    rank += 1
            return rank
        
        teamStats = [
            ['**Points**', 'pts', 'average', False], ['Rebounds', 'reb', 'average', False], ['Assists', 'ast', 'average', False], ['Blocks', 'blk', 'average', False], ['Steals', 'stl', 'average', False], ['Turnovers', 'tov', 'average', True], ['FG%', ['fg', 'fga'], 'percent', False], ['3P%', ['tp', 'tpa'], 'percent', False], ['FT%', ['ft', 'fta'], 'percent', False] 
        ]
        opponentStats = [
            ['**Opponent points**', 'oppPts', 'average', True], ['Opp. rebounds', 'oppReb', 'average', True], ['Opp. assists', 'oppAst', 'average', True], ['Opp. blocks', 'oppBlk', 'average', True], ['Opp. steals', 'oppStl', 'average', True], ['Opp. TOV', 'oppTov', 'average', False], ['Opp. FG%', ['oppFg', 'oppFga'], 'percent', True], ['Opp. 3P%', ['oppTp', 'oppTpa'], 'percent', True], ['Opp. FT%', ['oppFt', 'oppFta'], 'percent', True]
        ]

        text = ''
        for ts in teamStats:
            for t in teams:
                if t['tid'] == team['tid']:
                    stats = t['stats']
                    for s in stats:
                        if s['season'] == commandInfo['season'] and s['playoffs'] == playoffs:
                            s['reb'] = s['drb'] + s['orb']
                            s['oppReb'] = s['oppDrb'] + s['oppOrb']
                            if ts[2] == 'percent':
                                statAmount = [s[ts[1][0]], s[ts[1][1]]]
                            else:
                                statAmount = s[ts[1]]
                                if ts[2] == 'average':
                                    statAmount = statAmount/s['gp']
                            statRank = rank(s['season'], ts[1], statAmount, ts[2], ts[3])
            if isinstance(statAmount, list):
                statAmount = (statAmount[0] / statAmount[1]) * 100
            text += f"{ts[0]}: {round(statAmount, 1)} (Rank: #{statRank})" + '\n'
        embed.add_field(name='Team Stats', value=text)

        oppText = ''
        for ts in opponentStats:
            for t in teams:
                if t['tid'] == team['tid']:
                    stats = t['stats']
                    for s in stats:
                        if s['season'] == commandInfo['season'] and s['playoffs'] == playoffs:
                            s['reb'] = s['drb'] + s['orb']
                            s['oppReb'] = s['oppDrb'] + s['oppOrb']
                            if ts[2] == 'percent':
                                statAmount = [s[ts[1][0]], s[ts[1][1]]]
                            else:
                                statAmount = s[ts[1]]
                                if ts[2] == 'average':
                                    statAmount = statAmount / s['gp']
                            statRank = rank(s['season'], ts[1], statAmount, ts[2], ts[3])
            if isinstance(statAmount, list):
                statAmount = (statAmount[0] / +statAmount[1])*100
            oppText += f"{ts[0]}: {round(statAmount, 1)} (Rank: #{statRank})" + '\n'
        embed.add_field(name='Opponent Stats', value=oppText)

    return embed

def sos(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    players = export['players']
    schedule = export['schedule']

    oppWins = 0
    oppLoses = 0
    home = 0
    road = 0
    for s in schedule:
        oppTid = None
        if s['homeTid'] == team['tid']:
            oppTid = s['awayTid']
            home += 1
        if s['awayTid'] == team['tid']:
            oppTid = s['homeTid']
            road += 1
        if oppTid != None:
            for t in teams:
                if t['tid'] == oppTid:
                    oppWins += t['seasons'][-1]['won']
                    oppLoses += t['seasons'][-1]['lost']
    
    sos = oppWins / (oppWins+oppLoses)
    embed.add_field(name='Strength of Schedule', value=f"Remainder of season: {str(round(sos, 3))[1:]}" + '\n' + f"Home games: {home} | Road games: {road}")
    return embed

def schedule(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    players = export['players']
    schedule = export['schedule']

    lines = []
    for s in schedule:
        if s['homeTid'] == team['tid']:
            for t in teams:
                if t['tid'] == s['awayTid']:
                    line = f"**vs** {t['name']} ({t['seasons'][-1]['won']}-{t['seasons'][-1]['lost']})"
                    lines.append(line)
        if s['awayTid'] == team['tid']:
            for t in teams:
                if t['tid'] == s['homeTid']:
                    line = f"**@** {t['name']} ({t['seasons'][-1]['won']}-{t['seasons'][-1]['lost']})"
                    lines.append(line)
    
    numDivs, rem = divmod(len(lines), 15)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*15):((i*15)+15)]
        text = '\n'.join(newLines)
        embed.add_field(name='Schedule', value=text)
    
    return embed
    
def gamelog(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    players = export['players']
    try: games = export['games']
    except: 
        embed.add_field(name='Error', value='No box scores in file.')
        return embed
    
    lines = []
    number = 1
    for g in games:

        if (g['won']['tid'] == team['tid'] or g['lost']['tid'] == team['tid']) and g['season'] == season:
            #record the game
            homeTeam = g['teams'][0]['tid']
            roadTeam = g['teams'][1]['tid']
            line = f"``{number}.`` "
            for t in teams:
                if t['tid'] == roadTeam:
                    line += f"{t['abbrev']} {g['teams'][1]['pts']}"
                    if g['won']['tid'] == t['tid']:
                        line = '**' + line + '**'
                    line += ' - '
            for t in teams:
                if t['tid'] == homeTeam:
                    teamLine = f"{t['abbrev']} {g['teams'][0]['pts']}"
                    if g['won']['tid'] == t['tid']:
                        teamLine = '**' + teamLine + '**'
                    line+= teamLine
            for gt in g['teams']:
                if gt['tid'] == team['tid']:
                    line += f" ({gt['won']}-{gt['lost']})"
            lines.append(line)
            number += 1
    print(len(lines))
    numDivs, rem = divmod(len(lines), 20)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*20):((i*20)+20)]
        text = '\n'.join(newLines)
        embed.add_field(name='Game Log', value=text)
    
    return embed

def game(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    try: games = export['games']
    except: 
        embed.add_field(name='Error', value='No box scores in file.')
        return embed
    #just use commandseason as the number
    gameNum = commandInfo['season']
    number = 1
    found = False
    for g in games:
        if g['won']['tid'] == team['tid'] or g['lost']['tid'] == team['tid']:
            if number == gameNum:
                found = True
                number += 1
                gameData = pull_info.game_info(g, export, commandInfo['message'])
                text = f"{gameData['fullScore']}" + '\n' + f"{gameData['quarters']}" + '\n' + '\n' + f"**Top Performers:**" + '\n' + '\n'.join(gameData['topPerformances']) + '\n'
                if g['clutchPlays'] != []:
                    for c in g['clutchPlays']:
                        text += '\n' + '***' + c.split('>')[1].replace('</a', '') + '** ' + c.split('>')[2] + '*'
                embed.add_field(name='Game Summary', value=text)
            else:
                number += 1
    if found == False:
        embed.add_field(name='Error', value='No game found.')
    return embed

def boxscore(embed, team, commandInfo):
    export = shared_info.serverExports[str(commandInfo['serverId'])]
    season = export['gameAttributes']['season']
    picks = export['draftPicks']
    teams = export['teams']
    players = export['players']
    try: games = export['games']
    except: 
        embed.add_field(name='Error', value='No box scores in file.')
        return embed
    #just use commandseason as the number
    gameNum = commandInfo['season']
    number = 1
    found = False
    for g in games:
        if g['won']['tid'] == team['tid'] or g['lost']['tid'] == team['tid']:
            
            if number == gameNum:
                found = True
                number += 1
                gameData = pull_info.game_info(g, export, commandInfo['message'])
                #boxscore time
                embed.add_field(name='Game Info', value=f"{gameData['fullScore']}" + '\n' + f"{gameData['quarters']}" + '\n' + '\n', inline=False)
                numDivs, rem = divmod(len(gameData['boxScore'][1]), 8)
                numDivs += 1
                for i in range(numDivs):
                    newLines = gameData['boxScore'][1][(i*8):((i*8)+8)]
                    text ='\n'.join(newLines)
                    embed.add_field(name=f"{gameData['away']} Box Score", value=text, inline=False)
                numDivs, rem = divmod(len(gameData['boxScore'][0]), 8)
                numDivs += 1
                for i in range(numDivs):
                    newLines = gameData['boxScore'][0][(i*8):((i*8)+8)]
                    text ='\n'.join(newLines)
                    embed.add_field(name=f"{gameData['home']} Box Score", value=text, inline=False)
                
                

            else:
                number += 1
    if found == False:
        embed.add_field(name='Error', value='No game found.')
    return embed
                








        



    

    
            



                
 
