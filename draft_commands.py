import shared_info
from shared_info import serverExports
from shared_info import serversList
import pull_info
import basics
import discord
import os
import draft_runner

async def pick(embed, message):
    #see if user is affiliated with a team
    teamList = serversList[str(message.guild.id)]['teamlist']
    draftBoards = serversList[str(message.guild.id)]['draftBoards']
    draftStatus = serversList[str(message.guild.id)]['draftStatus']
    export = shared_info.serverExports[str(message.guild.id)]
    
    players = shared_info.serverExports[str(message.guild.id)]['players']
    season = shared_info.serverExports[str(message.guild.id)]['gameAttributes']['season']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:
        #see if user team is on the clock
        onTheClock = draftStatus['onTheClock']['tid']
        if onTheClock != userTeam:
            await message.channel.send("You aren't on the clock currently.")
        else:
            #find player
            playerToPick = basics.find_match(' '.join(message.content.split(' ')[1:]), shared_info.serverExports[str(message.guild.id)])
            for p in players:
                if p['pid'] == playerToPick:
                    name = p['firstName'] + ' ' + p['lastName']
                    tid = p['tid']
                    draftInfo = p['draft']
                    rating = str(p['ratings'][-1]['ovr']) + '/' + str(p['ratings'][-1]['pot'])
            if tid != -2 or draftInfo['year'] != season:
                text = f"{name} ({rating}) can't be selected. He might not be in this draft class, or may not be a draft prospect at all."
                await message.channel.send(text)
            else:
                new_export = await draft_runner.select_player(playerToPick, draftStatus['onTheClock'], message,shared_info.serverExports[str(message.guild.id)])
                shared_info.serverExports.update({str(message.guild.id):new_export})
                

                text = f"✅ **Selected {name} with R{draftStatus['onTheClock']['round']}, P{draftStatus['onTheClock']['pick']}.**"
                
                draftStatus['onTheClock'] = [0]
                current_dir = os.getcwd()
                path_to_file = os.path.join(current_dir, "exports", f"{message.guild.id}-export.json")
                await basics.save_db(new_export, path_to_file)
                
                await message.channel.send(text)
    return embed


async def board(embed, message):
    #see if user is affiliated with a team
    teamList = serversList[str(message.guild.id)]['teamlist']
    draftBoards = serversList[str(message.guild.id)]['draftBoards']
    draftFormulas = serversList[str(message.guild.id)]['draftPreferences']
    players = shared_info.serverExports[str(message.guild.id)]['players']
    season = shared_info.serverExports[str(message.guild.id)]['gameAttributes']['season']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:
        try:
            draftBoard = draftBoards[str(userTeam)]
        except KeyError:
            draftBoard = []
        if draftBoard == []:
            embed.add_field(name='Draft Board', value='No players!')
        else:
            text = ["", "", "", "", "", "", "", "", ""]
            number = 1
            for d in draftBoard:
                for p in players:
                    if p['pid'] == d:
                        fieldNum = divmod(number, 20)[0]
                        text[fieldNum] += f"{number}. {p['ratings'][-1]['pos']} **{p['firstName']} {p['lastName']}** ({season - p['born']['year']}yo {p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']})" + '\n'
                        number += 1
            for t in text:
                if t != "":
                    embed.add_field(name='Board', value=t)
        #formula
        try:
            userFormula = draftFormulas[str(userTeam)]
        except KeyError:
            userFormula = 'None set!'
        embed.add_field(name='Autodraft Formula', value=f"``{userFormula}``" + '\n' + '\n' + f"*Run {serversList[str(message.guild.id)]['prefix']}auto for full details on how to set this up, or modify it.*", inline=False)
    return embed

async def add(embed, message):
    #see if user is affiliated with a team
    teamList = serversList[str(message.guild.id)]['teamlist']
    draftBoards = serversList[str(message.guild.id)]['draftBoards']
    players = shared_info.serverExports[str(message.guild.id)]['players']
    season = shared_info.serverExports[str(message.guild.id)]['gameAttributes']['season']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:
        try:
            draftBoard = draftBoards[str(userTeam)]
        except KeyError:
            draftBoard = []
        pid = basics.find_match(' '.join(message.content.split(' ')[1:]), shared_info.serverExports[str(message.guild.id)])
        for p in players:
            if p['pid'] == pid:
                name = p['firstName'] + ' ' + p['lastName']
                if p['tid'] != -2 or p['draft']['year'] != season:
                    embed.add_field(name='Error', value=f"{name} is not an upcoming draft prospect.")
                else:
                    draftBoard.append(p['pid'])
                    serversList[str(message.guild.id)]['draftBoards'][str(userTeam)] = draftBoard
                    await basics.save_db(serversList)
                    embed.add_field(name='Success', value=f"{name} has been added to your draft board.")
    return embed

async def remove(embed, message):
    #see if user is affiliated with a team
    teamList = serversList[str(message.guild.id)]['teamlist']
    draftBoards = serversList[str(message.guild.id)]['draftBoards']
    players = shared_info.serverExports[str(message.guild.id)]['players']
    season = shared_info.serverExports[str(message.guild.id)]['gameAttributes']['season']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:
        try:
            draftBoard = draftBoards[str(userTeam)]
        except KeyError:
            draftBoard = []
        pid = basics.find_match(' '.join(message.content.split(' ')[1:]), shared_info.serverExports[str(message.guild.id)])
        for p in players:
            if p['pid'] == pid:
                name = p['firstName'] + ' ' + p['lastName']
        if pid in draftBoard:
            draftBoard.remove(pid)
            embed.add_field(name='Success', value=f"Removed {name} from your draft board.")
        else:
            embed.add_field(name='Error', value=f"Did not find {name} in your draft board.")
    return embed

async def move(embed, message):
    #see if user is affiliated with a team
    teamList = serversList[str(message.guild.id)]['teamlist']
    draftBoards = serversList[str(message.guild.id)]['draftBoards']
    players = shared_info.serverExports[str(message.guild.id)]['players']
    season = shared_info.serverExports[str(message.guild.id)]['gameAttributes']['season']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:
        moveTo = False
        try:
            moveTo = int(message.content.split(' ')[-1])
        except:
            embed.add_field(name='Error', value='Please provide the spot you wish to move the player to as the last term in the command.')
        if moveTo != False:
            try:
                draftBoard = draftBoards[str(userTeam)]
            except KeyError:
                draftBoard = []
            pid = basics.find_match(' '.join(message.content.split(' ')[1:-1]), shared_info.serverExports[str(message.guild.id)])
            for p in players:
                if p['pid'] == pid:
                    name = p['firstName'] + ' ' + p['lastName']
            if pid in draftBoard:
                newBoard = []
                spot = 1
                draftBoard.remove(pid)
                for player in draftBoard:
                    if spot == moveTo:
                        newBoard.append(pid)
                    spot+=1
                    if player != pid:
                        newBoard.append(player)
                if pid not in newBoard:
                    newBoard.append(pid)
                serversList[str(message.guild.id)]['draftBoards'][str(userTeam)] = newBoard
                await basics.save_db(serversList)
                embed.add_field(name='Success', value=f"Moved {name} to spot {moveTo}.")
            else:
                embed.add_field(name='Error', value=f'{name} is not on your board')
    return embed

async def clear(embed, message):
    #see if user is affiliated with a team
    teamList = serversList[str(message.guild.id)]['teamlist']
    draftBoards = serversList[str(message.guild.id)]['draftBoards']
    players = shared_info.serverExports[str(message.guild.id)]['players']
    season = shared_info.serverExports[str(message.guild.id)]['gameAttributes']['season']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:
        draftBoards[str(userTeam)] = []
        embed.add_field(name='Success', value='Cleared your draft board.')
        await basics.save_db(serversList)
    
    return embed

import ast
def is_valid_formula(formula, variables):
    try:
        tree = ast.parse(formula)
    except SyntaxError:
        return False
    # Define a visitor that will inspect the tree
    class Visitor(ast.NodeVisitor):
        def visit_Name(self, node):
            # If we encounter a variable that's not in the list, the formula is invalid
            if node.id not in variables:
                raise ValueError(f"Invalid variable: {node.id}")
    # Use the visitor to inspect the tree
    try:
        Visitor().visit(tree)
        return True
    except ValueError:
        return False


async def auto(embed, message):
    #see if user is affiliated with a team
    teamList = serversList[str(message.guild.id)]['teamlist']
    autoFormulas = serversList[str(message.guild.id)]['draftPreferences']

    players = shared_info.serverExports[str(message.guild.id)]['players']
    season = shared_info.serverExports[str(message.guild.id)]['gameAttributes']['season']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:
        #split the message
        messageArgs = message.content.split(' ')
        if len(messageArgs) == 1:
            messageArgs.append(' ')
        commands = ['formula', 'preset', 'remove']
        if str.lower(messageArgs[1]) not in commands:
            #show default screen
            embed.add_field(name='Autodrafting Formula', value="When you don't have a draft board, or everyone on it has been selected, ClevelandBot will select the best player vailable, unless you specify preferences using an auto formula. This can be as complex or as simple as one wants, and to further streamline the process, preset formulas are included for you - no math required!" + '\n' + '\n' + f"Use ``{serversList[str(message.guild.id)]['prefix']}auto formula [your formula here]`` to set a formula - you can use the BBGM ratings as well as age, and all operations are allowed. ClevelandBot will calculate this value for every player on the board and select who scores the highest.")
            embed.add_field(name='Presets', value="If you want to bypass the need to make a mathmatical formula, these presets are available:" + '\n' + '\n'
                            + '**__Prefer Height__**' + '\n' + '*Abbreviation: ph1, ph2, or ph3.*' + '\n'
                            + '**__Prefer Athletisism__**' + '\n' + '*Abbreviation: pa1, pa2, or pa3.*' + '\n'
                            + '**__Prefer Inside__**' + '\n' + '*Abbreviation: pi1, pi2, or pi3.*' + '\n'
                            + '**__Prefer Shooting__**' + '\n' + '*Weighted more to preferring three-pointers. Abbreviation: ps1, ps2, or ps3.*' + '\n'
                            + '**__Prefer IQ__**' + '\n' + '*Abbreviation: piq1, piq2, or piq3.*' + '\n'
                            + '**__Prefer Dribbling/Passing__**' + '\n' + '*Abbreviation: pd1, pd2, or pd3.*' + '\n'
                            + '**__Prefer Younger Players__**' + '\n' + '*Abbreviation: py1, py2. or py3.*' + '\n'
                            + '**__Prefer Higher Rated Players__**' + '\n' + '*Abbreviation: pr1, pr2, or pr3.*')
            embed.add_field(name='Using Presets', value=f"Apply a preset using ``{serversList[str(message.guild.id)]['prefix']}auto preset [preset abbreviation]``. You will notice that each preset has 3 'levels' to choose from. 1 is subtle, only leaning towards that playstyle if the top players on the board are very similar. 2 is a middle ground, while 3 is the most aggressive, occasionally reaching for someone up to 3-4 OVR points lower, and at the same age, in order to fit the desired playstyle. **Note that these formulas are not absolute rules, they only influence how the bot views players.** If no good three-point shooters are on the board, you will find it will start to regard a shooting preference very little and only select the best available player. I feel these have been very well tuned to achieve good, practical results. I recommend level 2 if you are not sure which to use.")
            #formula
            try:
                userFormula = autoFormulas[str(userTeam)]
            except KeyError:
                userFormula = 'None set!'
            embed.add_field(name='Your Formula', value=f"``{userFormula}``" + '\n' + f"*You can set this back to default with ``{serversList[str(message.guild.id)]['prefix']}auto remove``.*", inline=False)
        else:
            if str.lower(messageArgs[1]) == 'formula':
                userFormula = ' '.join(messageArgs[2:])
                variables = {"hgt", "stre", "spd", "jmp", "endu", "ins", "dnk", "ft", "fg", "tp", "oiq", "diq", "drb", "pss", "reb", "age", "ovr", "pot"}
                check = is_valid_formula(userFormula, variables)
                if check:
                    autoFormulas[str(userTeam)] = userFormula
                    await basics.save_db(serversList)
                    embed.add_field(name='Success', value=f'Auto formula set to ``{userFormula}``.')
                    #calculate top players under formula
                    draftClass = []
                    for p in players:
                        if p['tid'] == -2 and p['draft']['year'] == season:
                            draftClass.append(p)
                    playerList = basics.formula_ranking(draftClass, season, userFormula)
                    playerList = playerList[:25]
                    text = ""
                    number = 1
                    for pid, value in playerList[0:12]:
                        for p in players:
                            if p['pid'] == pid:
                                text += f"{number}. {p['ratings'][-1]['pos']} **{p['firstName']} {p['lastName']}** ({season - p['born']['year']}yo {p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']}) | Approx. value: {round(value, 1)}" + '\n'
                                number += 1
                    

                    embed.add_field(name='Formula Test', value='These are the top 12.5(tan(45)+2sin(30)) players in the class, using this formula:' + '\n' + text, inline=False)
                    text = ""
                    for pid, value in playerList[12:]:
                        for p in players:
                            if p['pid'] == pid:
                                text += f"{number}. {p['ratings'][-1]['pos']} **{p['firstName']} {p['lastName']}** ({season - p['born']['year']}yo {p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']}) | Approx. value: {round(value, 1)}" + '\n'
                                number += 1
                    embed.add_field(name='Continued', value= text, inline=False)
                                
                else:
                    varText = ""
                    for v in variables:
                        varText += f"• {v}" + '\n'
                    embed.add_field(name='Error', value='Your formula was invalid. Be sure to use valid mathamatical notation, and only the following variables:' + '\n' + varText)
            else:
                if str.lower(messageArgs[1]) == 'preset':
                    if len(messageArgs) == 2:
                        embed.add_field(name='Please Specify a Preset', value=f"You can see available presets by running ``{serversList[str(message.guild.id)]['prefix']}auto``.")
                    else:
                        default = 'ovr + 5*(24-age) + '
                        presets = {
                            "ph1": 'hgt/20',
                            "ph2": 'hgt/15',
                            "ph3": 'hgt/7',
                            "pa1": '((stre+spd+jmp)/3)/20',
                            "pa2": '((stre+spd+jmp)/3)/15',
                            "pa3": '((stre+spd+jmp)/3)/7',
                            "pi1": 'ins/20',
                            "pi2": 'ins/15', 
                            "pi3": 'ins/7',
                            "ps1": '((fg+ft+tp*6)/8)/20',
                            "ps2": '((fg+ft+tp*6)/8)/15',
                            "ps3": '((fg+ft+tp*6)/8)/7',
                            "piq1": '((oiq+diq)/2)/20',
                            "piq2": '((oiq+diq)/2)/15',
                            "piq3": '((oiq+diq)/2)/7',
                            "pd1": '((drb+pss)/2)/20',
                            "pd2": '((drb+pss)/2)/15',
                            "pd3": '((drb+pss)/2)/7',
                            "py1": '(24-age)',
                            "py2": '2*(24-age)',
                            "py3": "4*(24-age)",
                            "pr1": '-0.5*(24-age)',
                            "pr2": '-1.5*(24-age)',
                            "pr3": '-2.5*(24-age)'
                        }
                        userFormula = None
                        try:
                            userFormula = default + presets[str.lower(messageArgs[2])]
                        except KeyError:
                            embed.add_field(name='Error', value=f"``{messageArgs[2]}`` is not a valid preset. Run ``{serversList[str(message.guild.id)]['prefix']}auto`` to see the list of available presets.")
                        if userFormula != None:
                            autoFormulas[str(userTeam)] = userFormula
                            await basics.save_db(serversList)
                            embed.add_field(name='Success', value=f'Auto formula set to preset ``{userFormula}``.')
                            #calculate top players under formula
                            draftClass = []
                            for p in players:
                                if p['tid'] == -2 and p['draft']['year'] == season:
                                    draftClass.append(p)
                            playerList = basics.formula_ranking(draftClass, season, userFormula)
                            playerList = playerList[:25]
                            text = ""
                            number = 1
                            for pid, value in playerList[0:12]:
                                for p in players:
                                    if p['pid'] == pid:
                                        text += f"{number}. {p['ratings'][-1]['pos']} **{p['firstName']} {p['lastName']}** ({season - p['born']['year']}yo {p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']}) | Approx. value: {round(value, 1)}" + '\n'
                                        number += 1
                                        
                            embed.add_field(name='Formula Test', value='These are the top 50cos(60) players in the class, using this preset:' + '\n' + text, inline=False)
                            text = ""
                            for pid, value in playerList[12:]:
                                for p in players:
                                    if p['pid'] == pid:
                                        text += f"{number}. {p['ratings'][-1]['pos']} **{p['firstName']} {p['lastName']}** ({season - p['born']['year']}yo {p['ratings'][-1]['ovr']}/{p['ratings'][-1]['pot']}) | Approx. value: {round(value, 1)}" + '\n'
                                        number += 1
                            embed.add_field(name='Continued', value=text, inline=False)
                else:
                    if messageArgs[1] == 'remove':
                        autoFormulas[str(userTeam)] = ''
                        embed.add_field(name='Success', value='Autodraft formula removed and restored to default setting.')


    
    return embed
    
async def pause(embed, message):
    draftStatus = serversList[str(message.guild.id)]['draftStatus']
    draftStatus['draftRunning'] = False
    await message.channel.send('Draft will pause after this selection. You can resume it with the startdraft command.')

async def bulkadd(embed, message):
    teamList = serversList[str(message.guild.id)]['teamlist']
    draftBoards = serversList[str(message.guild.id)]['draftBoards']
    players = shared_info.serverExports[str(message.guild.id)]['players']
    season = shared_info.serverExports[str(message.guild.id)]['gameAttributes']['season']
    try:
        userTeam = teamList[str(message.author.id)]
    except KeyError:
        userTeam = -1
    if userTeam == -1:
        embed.add_field(name='Error', value="You don't seem to be assigned as a GM of a team.")
    else:
        try:
            draftBoard = draftBoards[str(userTeam)]
        except KeyError:
            draftBoard = []
        bulkGroup = (' '.join(message.content.split(' ')[1:])).split('\n')
        for player in bulkGroup:
            for p in players:
                if p['firstName'] + ' ' + p['lastName'] == player:
                    name = p['firstName'] + ' ' + p['lastName']
                    thePlayer = p
            if thePlayer['tid'] != -2 or thePlayer['draft']['year'] != season:
                embed.add_field(name='Error', value=f"{name} is not an upcoming draft prospect.")
            else:
                draftBoard.append(thePlayer['pid'])
                serversList[str(message.guild.id)]['draftBoards'][str(userTeam)] = draftBoard
        await basics.save_db(serversList)
        embed.add_field(name='Success', value=f"Everyone who doesn't have an error message has been added to your draft board.")
    return embed
