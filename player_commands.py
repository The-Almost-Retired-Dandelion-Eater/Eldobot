from shared_info import serverExports
import pull_info
import basics
import plotly_express as px
import pandas
import random
import plotly.graph_objects as go
from shared_info import trivias
import discord
from shared_info import triviabl
import shared_info

##PLAYER COMMANDS

def default(embed, player, commandInfo):
    embed.add_field(name='A New Player Command', value=f'This is the template for player commands that have no assigned funtion to fill the embed. Player name: {player["name"]}')
    return (embed)
def formatchange(old, new):
    if new > old:
        return "+"+str(new-old)
    if new == old:
        return 0
    if old > new:
        return "-"+str(old-new)
def pratings(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    season = commandInfo['season']
    s = dict()
    r = dict()
    
    for p in players:
        if p['pid'] == player['pid']:
            if player['retiredYear'] is not None and season > player['retiredYear']:
                season = player['retiredYear']
            
            for rating in p['ratings']:
                if rating['season'] == season - 1:
                    for element in rating:
                        s.update({element:rating[element]})
                if rating['season'] == season:
                    for element in rating:
                        r.update({element:rating[element]})
            break
    if len(s.keys()) > 2:
        
        overallBlock = (f"**Overall:** {r['ovr']} ({formatchange(s['ovr'],r['ovr'])}) \n"
             + f" **Potential:** {r['pot']} ({formatchange(s['pot'],r['pot'])})" )
        physicalBlock = (f"**Height:** {r['hgt']} ({formatchange(s['hgt'],r['hgt'])})" + '\n'
             + f"**Strength:** {r['stre']} ({formatchange(s['stre'],r['stre'])})" + '\n'
             + f"**Speed:** {r['spd']} ({formatchange(s['spd'],r['spd'])})" + '\n'
             + f"**Jumping:** {r['jmp']} ({formatchange(s['jmp'],r['jmp'])})" + '\n'
             + f"**Endurance:** {r['endu']} ({formatchange(s['endu'],r['endu'])})")
        shootingBlock = (f"**Inside:** {r['ins']} ({formatchange(s['ins'],r['ins'])})" + '\n'
                         + f"**Dunks/Layups:** {r['dnk']} ({formatchange(s['dnk'],r['dnk'])})" + '\n'
                         + f"**Free Throws:** {r['ft']} ({formatchange(s['ft'],r['ft'])})" + '\n'
                         + f"**Two Pointers:** {r['fg']} ({formatchange(s['fg'],r['fg'])})" + '\n'
                         + f"**Three Pointers:** {r['tp']} ({formatchange(s['tp'],r['tp'])})")
        skillBlock = (f"**Offensive IQ:** {r['oiq']} ({formatchange(s['oiq'],r['oiq'])})" + '\n'
                      + f"**Defensive IQ:** {r['diq']} ({formatchange(s['diq'],r['diq'])})" + '\n'
                      + f"**Dribbling:** {r['drb']} ({formatchange(s['drb'],r['drb'])})" + '\n'
                      + f"**Passing:** {r['pss']} ({formatchange(s['pss'],r['pss'])})" + '\n'
                      + f"**Rebounding:** {r['reb']} ({formatchange(s['reb'],r['reb'])})")
        embed.add_field(name = 'Overall', value = overallBlock, inline = False)
        embed.add_field(name='Physical', value=physicalBlock)
        embed.add_field(name='Shooting', value=shootingBlock)
        embed.add_field(name='Skill', value=skillBlock)
        return embed
    else:
        if len(r.keys()) == 0:
            poem = "I've traveled to lands reached by few\n"
            poem += "I've braved the waves of the ocean blue\n"
            poem += "I've searched all the lines that I ran through\n"
            poem+= "But I've got no ratings for you.\n\n"
            poem += "I've tracked down hints, and followed clues\n"
            poem += "I've looked at every year, and season too\n"
            poem += "But if you've watched, you already knew\n"
            poem += "That I've got no ratings for you."
            embed.add_field(name="Enjoy a little song, will ya?", value=poem)
            return embed
                        
        else:
            embed.add_field(name="This guy hasn't progged yet", value="And I'm too lazy to supply his ratings")
            return embed
                
            
def shots(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    playoffs = False
    if commandInfo['commandName'] == 'pshots':
        playoffs = True
    for p in players:
        if p['pid'] == player['pid']:
            d = dict()
            catalog = ['fgAtRim','fgaAtRim','fgMidRange','fgaMidRange','fgLowPost','fgaLowPost','tp','tpa','ft','fta','fg','fga','gp']
            for stat in catalog:
                d.update({stat:0})
            for s in p['stats']:
                if s['season'] == commandInfo['season'] and s['playoffs'] == playoffs:
                    for stat in catalog:
                        d.update({stat:d[stat]+s[stat]})

            if d['fga'] == 0:
                embed.add_field(name = "Error", value = "player did not attempt a shot here")
                return embed
            for item in ['fgaAtRim','fgaMidRange','fgaLowPost','tpa','fta','fga']:
                if d[item] == 0:
                    d.update({item:0.00000001})
            for item in ['gp']:
                if d[item] == 0:
                    d.update({item:0.00001})
            t = "Made per game: "+str(round(d['fgAtRim']/d['gp'],1)) + "\nAttempts per game: "+str(round(d['fgaAtRim']/d['gp'],1))+"\nPercentage: "+str(round(d['fgAtRim']*100/d['fgaAtRim'],1))+"%"
            
            embed.add_field(name = "At rim", value = t, inline = True)
            t = "Made per game: "+str(round(d['fgLowPost']/d['gp'],1)) + "\nAttempts per game: "+str(round(d['fgaLowPost']/d['gp'],1))+"\nPercentage: "+str(round(d['fgLowPost']*100/d['fgaLowPost'],1))+"%"
            
            embed.add_field(name = "Low Post", value = t, inline = True)
            t = "Made per game: "+str(round(d['fgMidRange']/d['gp'],1)) + "\nAttempts per game: "+str(round(d['fgaMidRange']/d['gp'],1))+"\nPercentage: "+str(round(d['fgMidRange']*100/d['fgaMidRange'],1))+"%"
            
            embed.add_field(name = "Mid Range", value = t, inline = True)
            t = "Made per game: "+str(round(d['tp']/d['gp'],1)) + "\nAttempts per game: "+str(round(d['tpa']/d['gp'],1))+"\nPercentage: "+str(round(d['tp']*100/d['tpa'],1))+"%"
            
            embed.add_field(name = "Threes", value = t, inline = True)
            t = "Made per game: "+str(round(d['ft']/d['gp'],1)) + "\nAttempts per game: "+str(round(d['fta']/d['gp'],1))+"\nPercentage: "+str(round(d['ft']*100/d['fta'],1))+"%"
            
            embed.add_field(name = "Free Throws", value = t, inline = True)
            for item in ['fgaAtRim','fgaMidRange','fgaLowPost','tpa','fta']:
                if d[item] < 0.5:
                    d.update({item:0})
            t = "At Rim: "+str(round(d['fgaAtRim']/d['fga']*100,1)) +"%\n"
            t += "Low Post: "+str(round(d['fgaLowPost']/d['fga']*100,1)) +"%\n"
            t += "Mid Range: "+str(round(d['fgaMidRange']/d['fga']*100,1)) +"%\n"
            t += "Three Point: "+str(round(d['tpa']/d['fga']*100,1)) +"%\n"
            t += "Ft/Fg: "+str(round(d['fta']/d['fga'],2)) 
            
            embed.add_field(name = "Shot Distribution", value = t, inline = True)
    return embed
                    
    
    

def stats(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    teams = export['teams']
    for p in players:
        if p['pid'] == player['pid']:
            if commandInfo['commandName'] == 'stats':
                s = pull_info.pstats(p, commandInfo['season'])
                title = f"{commandInfo['season']} Season Stats "
            if commandInfo['commandName'] == 'cstats':
                s = pull_info.pstats(p, 'career')
                title = 'Player Career Stats '
            if commandInfo['commandName'] == 'pstats':
                s = pull_info.pstats(p, commandInfo['season'], playoffs = True)
                title = 'Player Playoff Stats '
    statsTeams = '('
    for tid in s['teams']:
        for t in teams:
            if t['tid'] == tid:
                name = t['abbrev']
                for season in t['seasons']:
                    if season['season'] == commandInfo['season']:
                        name = season['abbrev']
        statsTeams += name + '/'
    if statsTeams == '(':
        statsTeams = ''
    else:
        statsTeams = statsTeams[:-1] + ')'
    if s['gp'] == 0:
        statsLine = f'*No stats available.*'
        effLine = f'*No stats available.*'
    else:
        statsLine = f"{s['pts']} pts, {s['orb'] + s['drb']} reb, {s['ast']} ast, {s['blk']} blk, {s['stl']} stl, {s['tov']} tov"
        effLine = f"{str(s['gp']).replace('.0', '')} GP, {s['min']} MPG, {s['per']} PER, {s['fg']}% FG, {s['tp']} 3PT%, {s['ft']} FT%"
    embed.add_field(name=title+statsTeams, value=statsLine, inline=False)
    embed.add_field(name='Other', value=effLine, inline=False)

    return(embed)

def bio(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    teams = export['teams']
    for p in players:
        if p['pid'] == player['pid']:
            stats = pull_info.pstats(p, 'career')
    teamsPlayedFor = ""
    for t in stats['teams']:
        for team in teams:
            if team['tid'] == t:
                teamsPlayedFor += team['abbrev'] + ', '
    teamsPlayedFor = teamsPlayedFor[:-2]
    p = player

    try: statLine = f"{str(stats['gp'])[:-2]} G, {stats['pts']} pts, {stats['orb'] + stats['drb']} reb, {stats['ast']} ast, {stats['per']} PER"
    except: statLine = '*Could not access stats.*'
    leagueBlock = (f"**Experience:** {len(player['seasonsPlayed'])} seasons ({basics.group_numbers(player['seasonsPlayed'])})" + '\n'
    + f"**Career Stats:** {statLine}" + '\n'
    + f'**Teams:** {teamsPlayedFor}')
    embed.add_field(name='League', value=leagueBlock, inline=False)

    if p['deathInfo']['died']:
        ageText = f"Died in {p['deathInfo']['yearDied']} (age {p['deathInfo']['ageDied']})"
    else:
        ageText = str(export['gameAttributes']['season'] - p['born']) + ' yo'
    physicalBlock = (f"**Height:** {p['height']}" + '\n'
                     + f"**Weight:** {p['weight']} lbs" + '\n'
                     + f"**Age:** {ageText}")
    embed.add_field(name='Physical', value=physicalBlock)

    personalBlock = (f"**Country:** {p['country']}" + '\n'
                     + f"**College:** {p['college']}" + '\n'
                     + f"**Mood Traits:** {p['moodTraits']}")
    embed.add_field(name='Personal', value=personalBlock)

    for bbgmPlayer in players:
        if bbgmPlayer['pid'] == p['pid']:
            draftTid = bbgmPlayer['draft']['tid']
            draftRating = f"{bbgmPlayer['draft']['ovr']}/{bbgmPlayer['draft']['pot']}"
    draftTeam = 'Undrafted'
    for t in teams:
        if t['tid'] == draftTid:
            draftTeam = t['region'] + ' ' + t['name']
    draftBlock = (f"{p['draft']}" + '\n'
                  + f"{draftTeam}" + '\n'
                  + f"{draftRating} at draft")
    embed.add_field(name='Draft', value=draftBlock)

    teamdict = dict()
    for p2 in players:
        if p2['pid'] == player['pid']:
            peakovr = 0
            peakszn = 0
            peakpot = 0
            for r in p2['ratings']:
                if r['ovr'] > peakovr:
                    peakovr = r['ovr']
                    peakszn = r['season']
                    peakpot = r['pot']
                
            for s in p2['stats']:

                if s['playoffs'] == False:
                    if s['tid'] not in teamdict:
                        teamdict.update({s['tid']:[s['season']]})
                    else:
                        l = teamdict[s['tid']]
                        l.append(s['season'])
                        teamdict.update({s['tid']:l})
            k = sorted(teamdict.keys(), key = lambda x:min(teamdict[x]), reverse = False)
            s = ""
            for tid in k:
                abbrev= "WHAAAAA"
                for t in teams:
                    if t['tid'] == tid:
                        abbrev=t['abbrev']
                x = sorted(teamdict[tid])
                years = ""
                index = 0

                while index < len(x):
                    y = x[index]
                    if not y+1 in x:
                        years += str(y)+", "
                        index += 1
                    else:
                        index += 1
                        j = 1
                        while y+j in x:
                            j += 1
                            index += 1
                        years += str(y)+"-"+str(y+j-1)+", "
                if len(years) > 2:
                    years = years[0:-2]
                    
                s += abbrev + ": "+str(years)+"\n"
                
            embed.add_field(name = "Teams", value = s)
            embed.add_field(name = "Peaks", value = str(peakovr)+"/"+str(peakpot)+" at "+str(peakszn))
    random.seed(player['pid'])
    col = random.sample(["Red","Yellow","Green","White","Black","Indigo","Blue","Purple","Gold","Gray","Orange","Magenta"],1)[0]
    food = random.sample(["Fried Chicken","Spaghetti","Cheeseburgers","Pizza","Ice Cream","Chocolate","Cake","Noodle Soup","Steak","Potato Chips","Lemons","Barbeque Ribs","Omelette"],1)[0]
    dy = 0
    dr = []
    randomscore = 0
    for p2 in players:
        if p2['pid'] == p['pid']:
            dy = p2['draft']['year']
            dr = p2['ratings'][0]
            dpos = p2['ratings'][0]['pos']
            for i in p2['firstName']+p2['lastName']:
                randomscore += ord(i)
    idol = "None"
    maxscore = -1000000000
    for p2 in players:
        if p2['draft']['year'] - dy < -10 and p2['draft']['year'] - dy > -30:
            isgoated = False
            allstars = 0
            for a in p2['awards']:
                if a['type'] == "All-Star":
                    if a['season'] < dy-2:
                        allstars += 1
            peakovrrating = []
            peakovr = 0
            for r in p2['ratings']:
                if r['ovr'] > 70:
                    isgoated = True
                if r['ovr'] > peakovr:
                    peakovr = r['ovr']
                    peakovrrating = r
            
            if allstars > 4:
                isgoated = True
            if isgoated:
                diffs = []

                for ratingitem in ['hgt','stre','endu','jmp','spd','fg','ft','tp','ins','dnk','oiq','diq','drb','pss','reb']:
                    diffs.append(peakovrrating[ratingitem]-dr[ratingitem])
                mean = sum(diffs)/len(diffs)
                var = 0
                for item in diffs:
                    var += abs(item-mean)
                score = -var
                if dpos == peakovrrating['pos']:
                    score += 50
                for l in dpos:
                    if l in peakovrrating['pos']:
                        score += 10
                for a in p2['awards']:
                    if a['type'] == "Finals MVP":
                        score += 10
                    if a['type'] == "Most Valuable Player":
                        score += 10
                if peakovrrating['ovr'] < dr['pot']-3:
    
                    score = score - 75
                if peakovrrating['ovr'] > 78:
                    score += (peakovrrating['ovr']-78)*10
                

                if p['country'].split(" ")[-1] == p2['born']['loc'].split(" ")[-1]:
                    if not ('USA' in p['country'] or 'United States' in p['country']):

                        score += 150
                namescore = 0
                for i in p2['firstName']+p2['lastName']:
                    namescore += ord(i)
                score += (namescore + randomscore) % 200

                if score > maxscore:
                    maxscore = score
                    idol = p2['firstName']+" "+p2['lastName']

                    
                
                    
    h = random.sample(["Left","Right","Right","Right"],1)[0]
    nname = "None"
    if "nickname" in shared_info.serversList[str(commandInfo['id'])]:
        nicks = shared_info.serversList[str(commandInfo['id'])]['nickname']
        
        if str(p['pid']) in nicks:
            nname = nicks[str(p['pid'])]
    embed.add_field(name = "Facts", value = "Favorite Color: "+col+"\n Favorite Food: "+food+"\n Idol: "+idol+"\n Handedness: "+h + "\n Nickname: "+nname)
    
    
        
    

    return(embed)

    
def ratings(embed, player, commandInfo):
    r = player['ratings']

    physicalBlock = (f"**Height:** {r['hgt']}" + '\n'
                     + f"**Strength:** {r['stre']}" + '\n'
                     + f"**Speed:** {r['spd']}" + '\n'
                     + f"**Jumping:** {r['jmp']}" + '\n'
                     + f"**Endurance:** {r['endu']}")
    shootingBlock = (f"**Inside:** {r['ins']}" + '\n'
                     + f"**Dunks/Layups:** {r['dnk']}" + '\n'
                     + f"**Free Throws:** {r['ft']}" + '\n'
                     + f"**Two Pointers:** {r['fg']}" + '\n'
                     + f"**Three Pointers:** {r['tp']}")
    skillBlock = (f"**Offensive IQ:** {r['oiq']}" + '\n'
                  + f"**Defensive IQ:** {r['diq']}" + '\n'
                  + f"**Dribbling:** {r['drb']}" + '\n'
                  + f"**Passing:** {r['pss']}" + '\n'
                  + f"**Rebounding:** {r['reb']}")
    embed.add_field(name='Physical', value=physicalBlock)
    embed.add_field(name='Shooting', value=shootingBlock)
    embed.add_field(name='Skill', value=skillBlock)
    return embed

def pcompare(embed, player, commandInfo):
    if commandInfo['message'].content.count(",") != 1:
        embed.add_field(name = "use , to deliminate exactly 2 players to compare", value = "yeah, you saw the title")
        return embed
    first,second = " ".join(commandInfo['message'].content.split(" ")[1:]).split(",")
    export = shared_info.serverExports[str(commandInfo['id'])]
    fyear = export['gameAttributes']['season']
    for i in first.split(" "):
        try: fyear = int(i)
        except ValueError:
            pass
        if i.lower() == "career":
            fyear = "career"
    syear = export['gameAttributes']['season']
    for i in second.split(" "):
        try: syear = int(i)
        except ValueError:
            pass
        if i.lower() == "career":
            syear = "career"

    if syear == "career" and (not fyear == "career"):
        fyear = "career"
    if fyear == "career" and (not syear == "career"):
        syear = "career"

    
    poff = False

    if commandInfo['message'].content.__contains__("playoff"):
        poff = True
    first = first.replace(str(fyear),"").replace("playoff","")
    second = second.replace(str(syear),"").replace("playoff","")
    # obtain player names
    fp = basics.find_match(first, export,settings =  shared_info.serversList[str(commandInfo['id'])])
    sp = basics.find_match(second, export,settings =  shared_info.serversList[str(commandInfo['id'])])
    for p in export['players']:
        if p['pid'] == fp:
            fplayer = p
        if p['pid'] == sp:
            splayer = p
    if fyear == export['gameAttributes']['season']:
        if fplayer['draft']['year'] > export['gameAttributes']['season']:
            fyear = fplayer['draft']['year']
    if syear == export['gameAttributes']['season']:
        if splayer['draft']['year'] > export['gameAttributes']['season']:
            syear = splayer['draft']['year'] 
    # biographical info

    fname=fplayer['firstName']+" "+fplayer['lastName']
    fposition = fplayer['ratings'][-1]['pos']
    for r in fplayer['ratings']:
        if r['season'] == fyear:
            fposition = r['pos']
    fround = fplayer['draft']['round']
    fpick = fplayer['draft']['pick']
    fdraft = str(fplayer['draft']['round'])+"-"+str(fplayer['draft']['pick'])
    sname=splayer['firstName']+" "+splayer['lastName']
    sposition = splayer['ratings'][-1]['pos']
    for r in splayer['ratings']:
        if r['season'] == syear:
            sposition = r['pos']
    sround = splayer['draft']['round']
    spick = splayer['draft']['pick']
    sdraft = str(splayer['draft']['round'])+"-"+str(splayer['draft']['pick'])
   

    string = ""
    
    if len(fname) > len(sname):
        string += "**"+str(len(fname))+"**"+"|-Length-|"+str(len(sname))+"\n"
    elif len(sname) > len(fname):
        string += str(len(fname))+"|-Length-|"+"**"+str(len(sname))+"**"+"\n"
    else:
        string += str(len(fname))+"|-Length-|"+""+str(len(sname))+""+"\n"
    string += str(fposition)+"|Position|"+""+str(sposition)+""+"\n"
    if sround*1000+spick < fround*1000+fpick:
        string += fdraft+"|Draft Pick|"+"**"+sdraft+"**"+"\n"
    elif sround*1000+spick > fround*1000+fpick:
        string += "**"+fdraft+"**"+"|Draft Pick|"+sdraft+"\n"
    else:
        string += fdraft+"|Draft Pick|"+sdraft+"\n"
    if not fyear == "career":
        fage = fyear - fplayer['born']['year']
        sage = syear - splayer['born']['year']
        string += str(fage)+"|--Age--|"+""+str(sage)+""+"\n"
    embed.add_field(name ="**"+ fname +" ("+str(fyear)+") V.S. "+sname+" ("+str(syear)+")"+"**", value = string.replace("|"," ** | ** "), inline = False)
    string = ""

    for r in ['ovr','pot','hgt','stre','spd','jmp','endu','ins','dnk','ft','fg','tp','oiq','diq','drb','pss','reb']:
        if fyear == 'career':
            peak = 0
            for rat in fplayer['ratings']:

                if rat[r] > peak:
                    peak = rat[r]
            fvalue = peak
            peak = 0
            for rat in splayer['ratings']:
                if rat[r] > peak:
                    peak = rat[r]
            svalue = peak
        else:
            fvalue= 0
            for rat in fplayer['ratings']:
                if rat['season'] == fyear:
                    fvalue = rat[r]
            svalue= 0
            for rat in splayer['ratings']:
                if rat['season'] == syear:
                    svalue = rat[r]

        if fvalue > svalue:
            string += "**"+str(fvalue)+"**|"+r.upper()+"|"+str(svalue)+"\n"
        elif svalue > fvalue:
            string += str(fvalue)+"|"+r.upper()+"|**"+str(svalue)+"**\n"
        else:
            string += str(fvalue)+"|"+r.upper()+"|"+str(svalue)+"\n"
    ratingsnamestring = "Ratings"
    if fyear == "career":
        ratingsnamestring = "Peak Ratings"
    embed.add_field(name =ratingsnamestring, value = string.replace("|"," ** | ** "))
    # STATS - which are complicated
    fgp = 0
    fpoints = 0
    frebs = 0
    fasts = 0
    fstls = 0
    fblks = 0
    ftovs = 0
    fows = 0
    fdws=0
    fper = 0
    fewa=0
    for fs in fplayer['stats']:
        if fs['playoffs'] == poff:
            if fs['season'] == fyear or fyear == 'career':
                fgp += fs['gp']
                fpoints += fs['pts']
                frebs += fs['orb']+fs['drb']
                fasts += fs['ast']
                fstls += fs['stl']
                fblks += fs['blk']
                ftovs += fs['tov']
                fper += fs['per']*fs['gp']
                fewa += fs['ewa']
                fows += fs['ows']
                fdws += fs['dws']
    sgp = 0
    spoints = 0
    srebs = 0
    sasts = 0
    sstls = 0
    sblks = 0
    stovs = 0
    sows = 0
    sdws = 0
    sper = 0
    sewa=0
    for ss in splayer['stats']:
        if ss['playoffs'] == poff:
            if ss['season'] == syear or syear == 'career':
                sgp += ss['gp']
                spoints += ss['pts']
                srebs += ss['orb']+ss['drb']
                sasts += ss['ast']
                sstls += ss['stl']
                sblks += ss['blk']
                stovs += ss['tov']
                sper += ss['per']*ss['gp']
                sewa += ss['ewa']
                sows += ss['ows']
                sdws += ss['dws']
    if fgp == 0:
        fgp = 0.1
    if sgp == 0:
        sgp = 0.1
    fppg = fpoints/fgp
    frpg = frebs/fgp
    fapg = fasts/fgp
    fstls = fstls/fgp
    fblks = fblks/fgp
    ftovs = ftovs/fgp
    fper = fper/fgp
    sppg = spoints/sgp
    srpg = srebs/sgp
    sapg = sasts/sgp
    sstls = sstls/sgp
    sblks = sblks/sgp
    stovs = stovs/sgp
    sper = sper/sgp

    string = ""
    l1 = [fppg,frpg,fapg,fstls,fblks,ftovs,fper,fows,fdws,fewa]
    l2 = [sppg,srpg,sapg,sstls,sblks,stovs,sper,sows,sdws,sewa]
    names = ['pts','reb','ast','stl','blk','tov','per','ows','dws','ewa']
    for item in range (0, len(l1)):
        if l1[item] > l2[item]:
            string += '**'+str(round(l1[item],1))+'**|'+names[item]+"|"+str(round(l2[item],1))+"\n"
        elif l2[item] > l1[item]:
            string +=str(round(l1[item],1))+'|'+names[item]+"|**"+str(round(l2[item],1))+"**\n"
        else:
            string += str(round(l1[item],1))+'|'+names[item]+"|"+str(round(l2[item],1))+"\n"
    string += "**Awards**\n"
    fa = [0,0,0,0,0,0]
    sa = [0,0,0,0,0,0]
    for a in fplayer['awards']:

        if a['type'] == "Most Valuable Player":
            if fyear == a['season'] or fyear == 'career':
                fa[0] += 1
        if a['type'] == "Won Championship":
            if fyear == a['season'] or fyear == 'career':
                fa[1] += 1
        if a['type'] == "Finals MVP":
            if fyear == a['season'] or fyear == 'career':
                fa[2] += 1
        if a['type'] == "Defensive Player of the Year":
            if fyear == a['season'] or fyear == 'career':
                fa[3] += 1
        if a['type'] == "All-Star":
            if fyear == a['season'] or fyear == 'career':
                fa[4] += 1
    if len(fplayer['awards']) == 0:
        fa[5] = 1
    for a in splayer['awards']:
        if a['type'] == "Most Valuable Player":
            if syear == a['season'] or syear == 'career':
                sa[0] += 1
        if a['type'] == "Won Championship":
            if syear == a['season'] or syear == 'career':
                sa[1] += 1
        if a['type'] == "Finals MVP":
            if syear == a['season'] or syear == 'career':
                sa[2] += 1
        if a['type'] == "Defensive Player of the Year":
            if syear == a['season'] or syear == 'career':
                sa[3] += 1
        if a['type'] == "All-Star":
            if syear == a['season'] or syear == 'career':
                sa[4] += 1

    if len(splayer['awards']) == 0:
        sa[5] = 1
    names = ['MVP','Rings','FMVP','DPOY','AS','Player Exists']
    for item in range (0, len(fa)):
        if fa[item] > sa[item]:
            string += '**'+str(fa[item])+'**|'+names[item]+"|"+str(sa[item])+"\n"
        elif sa[item] > fa[item]:
            string +=str(fa[item])+'|'+names[item]+"|**"+str(sa[item])+"**\n"
        else:
            string += str(fa[item])+'|'+names[item]+"|"+str(sa[item])+"\n"
    embed.add_field(name = "Stats", value = string.replace("|"," ** | ** "))
                
        
    return embed
    

def adv(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    teams = export['teams']
    poffs = False
    if commandInfo['message'].content.__contains__('padv'):
        poffs = True
    for p in players:
        if p['pid'] == player['pid']:
            s = pull_info.pstats(p, commandInfo['season'], poffs)
    statsTeams = '('
    for tid in s['teams']:
        for t in teams:
            if t['tid'] == tid:
                name = t['abbrev']
                for season in t['seasons']:
                    if season['season'] == commandInfo['season']:
                        name = season['abbrev']
        statsTeams += name + '/'
    if statsTeams == '(':
        statsTeams = ''
    else:
        statsTeams = statsTeams[:-1] + ')'
    if s['gp'] == 0:
        statsLine = f'*No stats available.*'
        effLine = f'*No stats available.*'
        shootingLine = '*No stats available.*'
    else:
        statsLine = f"{str(s['gp']).replace('.0', '')} GP, {s['min']} MPG, {s['per']} PER, {s['ewa']} EWA, {s['obpm']+s['dbpm']} BPM ({s['obpm']} OBPM, {s['dbpm']} DBPM), {s['vorp']} VORP"
        effLine = f"{s['ows']+s['dws']} WS ({s['ows']} OWS, {s['dws']} DWS), {str(round(((s['ows']+s['dws'])/(s['min']*s['gp']))*48, 3)).replace('0.', '.')} WS/48, {s['ortg']} ORTG, {s['drtg']} DRTG, {s['usgp']}% USG, {s['pm100']} +/- per 100 pos., {s['onOff100']} on/off per 100 pos."
        shootingLine = f"{s['fg']}% FG, {s['tp']}% 3P, {s['ft']}% FT, {s['at-rim']}% at-rim, {s['low-post']}% low-post, {s['mid-range']}% mid-range \n {s['dd']} double-doubles, {s['td']} triple doubles"
    names = f"{commandInfo['season']} Advanced Stats {statsTeams}"
    if poffs:
        names = f"{commandInfo['season']} Playoff Advanced Stats {statsTeams}"
    print(names)
    embed.add_field(name=names, value=statsLine, inline=False)
    embed.add_field(name='Team-Based', value=effLine, inline=False)
    embed.add_field(name='Shooting and Feats', value=shootingLine, inline=False)

    return embed
def hint(embed, player, commandInfo):
    embed  = discord.Embed(title="Trivia", description="Guess who")
    channel = commandInfo['message'].channel
    if channel in trivias:
        answer = trivias[channel]
        init = [x[0] for x in answer.split(" ")]
        embed.add_field(name = 'Hint',value = ".".join(init))
        return embed
    else:
        embed.add_field(name = 'Hint',value = "Here's a hint for you: use -trivia to start a trivia in this channel, then you can use this command!")
        return embed
def progs(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    teams = export['teams']
    lines = []
    fname = ""
    for p in players:
        if p['pid'] == player['pid']:
            fname = p['firstName']
            ratings = p['ratings']
            for r in ratings:
                line = f"{r['season']} - {player['name']} - {r['season'] - player['born']} yo {r['ovr']}/{r['pot']} {' '.join(r['skills'])}"
                lines.append(f"{r['season']} - {player['name']} - {r['season'] - player['born']} yo {r['ovr']}/{r['pot']} {' '.join(r['skills'])}")
    numDivs, rem = divmod(len(lines), 20)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*20):((i*20)+20)]
        text = '\n'.join(newLines)
        if len(text) > 1020:
            text = text.replace(fname, fname[0]+".")
        embed.add_field(name='Player Progressions', value=text)
    return embed

def hstats(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    playoffs = False
    teams = export['teams']
    if commandInfo['message'].content.split(" ")[0].__contains__('phs') or commandInfo['message'].content.split(" ")[0].__contains__('phstats'):
        playoffs = True
    lines = []
    for season in player['seasonsPlayed']:
        for p in players:
            if p['pid'] == player['pid']:
                stats = pull_info.pstats(p, season, playoffs)
        if stats['gp'] > 0:
            teamText = '('
            for tid in stats['teams']:
                for t in teams:
                    if t['tid'] == tid:
                        t = pull_info.tinfo(t, season)
                        teamText += t['abbrev'] + '/'
            teamText = teamText[:-1] + ')'
            line = f"**{season}** {teamText} - {stats['pts']} pts, {stats['reb']} reb, {stats['ast']} ast, {stats['stl']} stl, {stats['blk']} blk, {stats['per']} PER"
            lines.append(line)
    numDivs, rem = divmod(len(lines), 10)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*10):((i*10)+10)]
        text = '\n'.join(newLines)
        embed.add_field(name='Player Stats', value=text, inline=False)
    return embed  

def awards(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    teams = export['teams']
    lines = []
    for p in players:
        if p['pid'] == player['pid']:
            awards = p['awards']
            totalAwards = []
            for a in awards:
                totalAwards.append(a['type'])
            totalAwards = list(dict.fromkeys(totalAwards))
            for t in totalAwards:
                numAward = 0
                awardSeasons = []
                for a in awards:
                    if a['type'] == t:
                        numAward += 1
                        awardSeasons.append(str(a['season']))
                awardYears = ', '.join(awardSeasons)
                awardYears = '(' + awardYears + ')'
                awardYears = awardYears.replace(', )', ')')
                lines.append(f'{numAward}x {t} {awardYears}')
    if lines == []:
        numAward = 1
        t = "Player Exists"
        awardYears = str(commandInfo['season'])
        lines.append(f'{numAward}x {t} ({awardYears})')
    numDivs, rem = divmod(len(lines), 15)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*15):((i*15)+15)]
        text = '\n'.join(newLines)
        embed.add_field(name='Player Awards', value=text, inline=False)
    return embed
def compare(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    #print(commandInfo)
    players = export['players']
    teams = export['teams']
    tocompare = None
    #print(player)
    for play in players:
        if player["pid"] == play["pid"]:
            trueplayer = play
    #print(trueplayer)
    #trueplayer = players[player["pid"]]
    for r in trueplayer['ratings']:
        
        if r['season'] == commandInfo['season']:
            tocompare = r
    if tocompare == None:
        if trueplayer['retiredYear'] == None:
            tocompare = trueplayer['ratings'][-1]
            commandInfo.update({"season":tocompare["season"]})
        else:
            peakovr = 0
            for item in trueplayer['ratings']:
                if item['ovr'] > peakovr:
                    tocompare = item
                    peakovr = item['ovr']
    page = commandInfo["season"]-player["born"]
    mindifference = 10000000
    players2 = []

    for p in players:
        
        if not p["pid"] == trueplayer["pid"]:
            if export['gameAttributes']['season'] > p['draft']['year']:
        
                for r in p['ratings']:
                    age = r['season']-p['born']['year']
                    if age == page:
                        dif = 0
                        for i in ["hgt","stre","endu","reb","drb","pss","oiq","diq","fg","ft","tp","ins","dnk","jmp","spd"]:
                            if i in ["hgt","oiq","diq","stre","jmp","spd","drb","dnk","tp"]:
                                dif += (r[i]-tocompare[i])**2
                            else:
                                dif += 0.5*(r[i]-tocompare[i])**2
                        dif += 5*(r["ovr"]-tocompare["ovr"])**2
                        players2.append((p,r['season'],dif,p['ratings'], p['born']['year']))
    players2 = sorted(players2, key = lambda i: i[2])

    for i in range (0,5):
        resultingplayer = players2[i]
        peakovr = 0
        r = resultingplayer[3]


        peakszn = r[0]['season']
        peakpos = r[0]['pos']
        for r in resultingplayer[3]:
            if r['season']-resultingplayer[4]>= page:
                if r['ovr'] > peakovr:
                    peakovr = r['ovr']
                    peakszn = r['season']
                    peakpos = r['pos']
            
        resultingplayer =pull_info.pinfo(resultingplayer[0], season = peakszn)
        if resultingplayer['tid'] >= 0:
             t = pull_info.tinfo(teams[resultingplayer['tid']], peakszn)
        else:
             t = pull_info.tgeneric(resultingplayer['tid'])
        s= str(resultingplayer["stats"]['pts'])+"pts, "+str(resultingplayer["stats"]['reb'])+"reb, "+str(resultingplayer["stats"]['ast'])+"ast, "+str(resultingplayer["stats"]['stl'])+"stl, "+str(resultingplayer["stats"]['blk'])+"blk, "+str(resultingplayer["stats"]['per'])+" PER"
        if 'abbrev' in t:
            text = str(peakszn)+" "+peakpos+" "+ resultingplayer["name"]+", "+str(peakszn-resultingplayer["born"])+" years old, "+str(resultingplayer["ovr"])+"/"+str(resultingplayer["pot"])+" ("+t["abbrev"]+")\n"+s
        else:
            text = str(peakszn)+" "+peakpos+" "+ resultingplayer["name"]+", "+str(peakszn-resultingplayer["born"])+" years old, "+str(resultingplayer["ovr"])+"/"+str(resultingplayer["pot"])+" ("+t["name"]+")\n"+s

        embed.add_field(name='Player Comparison', value=text, inline=False)
    return embed
def progschart(embed, player, commandInfo):
    
    finalthree = commandInfo['message'].content[-3:]
    #print(finalthree)
    key = "ovr"
    pname = player["name"]
    for item in ["pot", "hgt","dnk","oiq","tre","ins","diq","spd"," ft","drb","jmp","pss"," fg","ndu"," tp","reb"]:
        if finalthree == item:
            key = item
            if key == " ft":
                key = "ft"
            if key == "tre":
                key = "stre"
            if key == " fg":
                key = "fg"
            if key == "ndu":
                key = "endu"
            if key == " tp":
                key = "tp"
    export = shared_info.serverExports[str(commandInfo['id'])]
    #print(commandInfo)
    players = export['players']
    teams = export['teams']
    for play in players:
        if player["pid"] == play["pid"]:
            player = play
    #player = players[player['pid']]
    newthing = player['ratings']
            
    birthyear = player.get("born").get("year")
    seasons = []
    ages = []
    rtg = []
    season = -1000
                
    names = [key]
    for item in newthing:
         if int(item.get("season"))>=season:
            print(item)
            seasons.append(int(item.get("season")))
            ages.append(-birthyear+int(item.get("season")))
            rtg.append(int(item.get(key)))
    df = pandas.DataFrame(rtg, index=ages,columns = names)
    fig = px.line(df,labels = {"index":"Age","value":"Rating"}, title = "Progs for "+pname+" "+key)
    fig.update_layout(

    yaxis=dict( # Here
        range=[0,100] # Here
    ) # Here
    )
    fig.write_image('first_figure.png')
    
    return embed

def pgamelog(embed, player, commandInfo):
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    teams = export['teams']
    try: games = export['games']
    except KeyError: 
        embed.add_field(name='Error', value='No box scores in this export.')
        return embed
    lines = []
    totallength = 0
    for g in games:
        if g['won']['tid'] > -1 and g['season'] == export['gameAttributes']['season']:
            for gt in g['teams']:
                for pl in gt['players']:
                    if pl['pid'] == player['pid']:
                        if pl['min'] > 0:
                            statLine = f"{round(pl['min'], 1)} min, {pl['pts']} pts, {pl['orb']+pl['drb']} reb, {pl['ast']} ast, {pl['blk']} blk, {pl['stl']} stl, {pl['fg']}/{pl['fga']} FG, {pl['tp']}/{pl['tpa']} 3P"
                        else:
                            statLine = 'Did not play'
                        gameInfo = pull_info.game_info(g, export, commandInfo['message'])
                        newLine = f"{gameInfo['abbrevScore']} - ``{statLine}``"
                        lines.append(newLine)
                        
    numDivs, rem = divmod(len(lines), 10)
    numDivs += 1
    pagenum = 1
    pages = []
    for item in commandInfo['message'].content.split(" "):
        try:

            pagenum = int(item)
        except ValueError:
            pass
        
    for i in range(numDivs):
        newLines = lines[(i*10):((i*10)+10)]
        text = '\n'.join(newLines)
        pages.append(text+"\n Page " +str(i+1)+" out of "+str(numDivs))
    if pagenum > len(pages):
        pagenum = 1

    embed.add_field(name='Player Game Log '+str( export['gameAttributes']['season']), value=pages[pagenum-1], inline=False)
    return embed
def progspredict(embed, player, commandInfo):
    timespent = 100
    for item in commandInfo['message'].content.split(" "):
        if item == "next":
            timespent = 1
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    play = 0
    for p in players:
        if p['pid'] == player['pid']:
            play = p
    ratings = play['ratings']
    keyrating = None
    if play['draft']['year'] > export['gameAttributes']['season']:
        if export['gameAttributes']['season'] == commandInfo['season']:
            commandInfo.update({'season':play['draft']['year']})
    for item in ratings:
        if commandInfo['season'] == item['season']:
            keyrating = item
    if keyrating == None:
        embed.add_field(name = "Error: Out of Range", value = "nothing I can do.")
        return embed
    curage = commandInfo['season'] - play['born']['year']
    curovr = keyrating['ovr']

    try:

        f = open("progs.txt")
    except Exception:
        embed.add_field(name = "Error: Database could not be found", value = "probably an error on Illusion's part.")
        return embed
    peaks = []
    print("ok")
    threshold = 1.5
    if timespent == 1:
        threshold = 0.5
    for line in f:
        peak = 99999
        start = 999999


       

        for item in line.replace("\n","").split(","):

            age, ovr = item.split(":")
            diff = int(age)-start
            if diff > timespent:
                break
            
            
            if int(age) == curage and abs(int(ovr) - curovr) <  threshold:
                peak = 0
                start = int(age)

            elif int(ovr) > peak:
                peak = int(ovr)
            
        if peak > 0 and peak < 1000:
            peaks.append(peak)

    if len(peaks) < 1:
        embed.add_field(name = "Error: Nobody found with same age and overall in database", value = "Your player is just one of a kind.")
        return embed
    values = []
    quantities = []

    for elm in range(min(peaks),max(peaks)+1):
        values.append(elm)
        quantities.append(peaks.count(elm))
    df = pandas.DataFrame(quantities,index=values)
    bid = "Career peak ovr for players similar to "+player['name']+" "+str(commandInfo['season'])
    if timespent == 1:
        bid = "Next prog result for players similar to "+player['name']+" "+str(commandInfo['season'])
    fig = px.bar(df,title =bid)
    peaks = sorted(peaks)
    median = peaks[int(len(peaks)/2)]
    mean = round(sum(peaks)/len(peaks),2)
    fq = peaks[int(len(peaks)/4)]
    tq = peaks[int(len(peaks)/4*3)]

    text = ""
    text1=str(max(peaks))
    text2=str(tq)+"\n"
    text3=str(median)+"\n"
    text4=str(mean)+"\n"
    text5=str(fq)+"\n"
    text6=str(min(peaks))
    embed.add_field(name="Mean",value=text4,inline=True)
    if len(peaks) < 50:
        embed.add_field(name="Maximum",value=text1,inline=True)
        embed.add_field(name="Minimum",value=text6,inline=True)
        embed.add_field(name="Median",value=text3,inline=True)
        embed.add_field(name="25th percentile",value=text5,inline=True)
        embed.add_field(name="75th percentile",value=text2,inline=True)
    else:
        embed.add_field(name="10th percentile",value=peaks[int(len(peaks)/10)],inline=True)
        embed.add_field(name="25th percentile",value=text5,inline=True)
        embed.add_field(name="Median",value=text3,inline=True)
        embed.add_field(name="75th percentile",value=text2,inline=True)
        embed.add_field(name="90th percentile",value=peaks[int(9*len(peaks)/10)],inline=True)
    
    embed.add_field(name="Sample Size",value=str(len(peaks)),inline=True)
    fig.write_image('first_figure.png')
    print("wrote")
    return embed
        
            

    
    
def trivia(embed, player, commandInfo):
    
    
    embed  = discord.Embed(title="Trivia", description="Guess who")
    d = "Guess who"
    if commandInfo['message'].channel in trivias:
        d = "By the way, the last trivia's solution was "+trivias[commandInfo['message'].channel]
    embedresult  = discord.Embed(title="Trivia", description=d)
    export = shared_info.serverExports[str(commandInfo['id'])]
    players = export['players']
    newcommandinfo = {'id':commandInfo['id']}
    found = False
    track = 1
    while not found:
        track += 1
        player_key = random.sample(players, 1)[0]
        player = pull_info.pinfo(player_key)
        if player['peakOvr'] > 59 or track == 10000:
            found = True
    t = "Player Progressions"
    if random.random() < 0.5:
        embed2 = progs(embed, player, newcommandinfo)
    else:
        t = "Player Stats"
        embed2 = hstats(embed, player, newcommandinfo)
    newstring = ""
    for field in embed.fields:
        newstring = field.value.replace(player['name'], 'X')
        if "(" in newstring:
            while "(" in newstring:
                #print(newstring)

                newstring = newstring[0:newstring.index("(")]+newstring[newstring.index(")")+1:]
        embedresult.add_field(name = t, value = newstring)
    print(player['pid'])
    trivias.update({commandInfo['message'].channel:player['name']})
    todelete = set()
    for item, value in triviabl.items():
        if value == commandInfo['message'].channel:
            todelete.add(item)
    for item in todelete:
        del triviabl[item]

    return embedresult
