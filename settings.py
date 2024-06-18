import discord
import basics
import commands
import shared_info
serversList = shared_info.serversList


#SETTINGS
async def process_text(text, message):
    if text[0] == 'settings':
        if len(text) == 1:
            await main_prompt(message)
        else:
            if text[1] == 'fa': await fa_prompt(message)
            else:
                if text[1] == 'trade': await trade_prompt(message)
                else:
                    if text[1] == 'league': await league_prompt(message)
                    else:
                        if text[1] == 'draft': await draft_prompt(message)

    if text[0] == 'edit':
        if len(text) == 1:
            await message.channel.send('Please supply a value to edit.')
        else:
            if len(text) == 3:
                await edit_setting(text, message)
            else:
                await message.channel.send('When editing messages, please use the format ``-edit [setting] [new value]``. It looks like you supplied too many values.')

async def main_prompt(message):
    prefix = serversList[str(message.guild.id)]['prefix']
    serverName = message.guild.name
    serverSettings = shared_info.serversList[str(message.guild.id)]
    embed = discord.Embed(title="EldoBot Settings", description=f"Settings for server {serverName}." + "\n \n" + '**Specify a category of settings to see more. Categories are: draft, fa, league, and trade.**')
    embed.add_field(name='General', value='**Prefix:** ' + serverSettings['prefix'] + '\n' + f'*Edit with {prefix}edit [prefix]*' + '\n' +f"**Trade Confirmation Channel:** {serverSettings['tradechannel']}" + '\n' + '*Trade confirmations should be sent here. Edit with -edit tradechannel [new channel].*' + '\n' 
                    f"**FA Channel:** {serverSettings['fachannel']}" + '\n' + '*FA signings will be sent here. Edit with -edit fachannel [new channel].*' + '\n' +
                    f"**Release Announcement Channel:** {serverSettings['releasechannel']}" + '\n' + '*Releases will be sent here. Edit with -edit releasechannel [new channel].*' + '\n'
                    + f"**Trade Announcement Channel:** {serverSettings['tradeannouncechannel']}" + '\n' + f'*This channel is where all confirmed trades will be recorded. Edit with {prefix}edit tradeannouncechannel [#new channel].*' + '\n'
                    + f"**Pick Announcement Channel:** {serverSettings['draftchannel']}" + '\n' + f"*Draft picks will be sent here. Edit using {prefix}edit draftchannel [new channel].*")
    await message.channel.send(embed=embed)

async def fa_prompt(message):
    prefix = serversList[str(message.guild.id)]['prefix']
    serverName = message.guild.name
    serverSettings = shared_info.serversList[str(message.guild.id)]
    embed = discord.Embed(title="EldoBot Settings - Free Agency", description=f"FA Settings for server {serverName}")
    embed.add_field(name='FA Settings', value=('***Note:** Some settings are pulled directly from the server export file, such as the minimum roster, the salary cap, and the hard cap (your in-game "luxury tax threshold" is viewed by ClevelandBot as the hard cap).*' + '\n' + '\n'
                    + f"**__Max Roster:__** ``{serverSettings['maxroster']}``" + '\n' + f"*Teams can not sign players once they have reached this threshold. Edit with {prefix}edit maxroster [new value].*" + '\n'
                    + f"**__Holdout %:__** ``{serverSettings['holdout']}%``" + '\n' + f"*If a contract is below {serverSettings['holdout']}% of a player's asking price, they will decline to sign that offer. Edit with {prefix}edit holdout [new %].*" + '\n'
                    + f"**__Tuodloh %:__** ``{serverSettings['tuodloh']}%``" + '\n' + f"*If a contract is above {serverSettings['tuodloh']}% of a player's asking price, they will decline to sign that offer. Edit with {prefix}edit tuodloh [new %].*" + '\n'
                    + f"**__Rookies Count Towards Max Roster:__** ``{serverSettings['rookiescount']}``" + '\n' + f'*If off, rookies will not be counted when adding up the total players for max roster checks. Only applies in the offseason, to rookies drafted in the immediately preceding draft. Edit with {prefix}edit rookiescount [on/off].*' + '\n'))
    embed.add_field(name='FA Settings II', value=f"**__Player/Team Options:__** ``{serverSettings['options']}``" + '\n' + f"*If on, teams can offer player and team options. A segment will be added to the FA help screen on how to use this. Edit with {prefix}edit options [on/off].*" + '\n'
                    + f"**__Open Market:__** ``{serverSettings['openmarket']}``" + '\n' + f"*If on, the teams with the top 3 existing offers are pinged when a new offer for a player is made. Essentially, offers are public and you get a bidding war. Edit with {prefix}edit openmarket [on/off].*" + '\n'
                    + f"**__Bird Rights:__** ``{serverSettings['birdrights']}``" + '\n' + f"*If on, teams are allowed to go over the soft cap (but not the hard cap) when offering and signing players who ended the previous season on their team. Edit with {prefix}edit birdrights [on/off].*" + '\n'
                    + f"**__3+ Year Offer Rule:__** ``{serverSettings['threeyearrule']}``" + '\n' + f"*If on, any offer that is 3 or more years must be worth at least 250% of the minimum salary. Rule originated in RBL and BGMA and is meant to prevent long-term cheap contracts from being too common. Does not apply to re-signings. Edit with {prefix}edit threeyearrule [on/off].*")
    embed.add_field(name='FA Settings III', value=f"**Mood Trait Base Weights**" + '\n' + '*These are used in FA decisions to weigh factors that correspond to each trait. By default, each one is weighed at 0.1. If a player has the trait, 1 is added to the weight, and decimals are added to winning/loyalty for old players and fame/money for young players. Increasing these weights, or making them negative, can change how much they impact free agency. I do not recommend going lower than -1 or higer than 1, or else you will get extreme results.*' + '\n'
                    + f"**__Winning:__** ``{serverSettings['winning']}``" + '\n' + f"**__Fame:__** ``{serverSettings['fame']}``" + '\n' + f"**__Loyalty:__** ``{serverSettings['loyalty']}``" + '\n' + f"**__Money:__** ``{serverSettings['money']}``" + '\n'
                    + f"*Edit with {prefix}edit [trait name] [new weight].*"+ '\n' + f"**__Restricted FA:__** ``{serverSettings['rfa']}``"+ '\n' + f"**__Restricted FA Multiplier:__** ``{serverSettings['rfamultiplier']}``")
    await message.channel.send(embed=embed)

async def trade_prompt(message):
    prefix = serversList[str(message.guild.id)]['prefix']
    serverName = message.guild.name
    serverSettings = shared_info.serversList[str(message.guild.id)]
    embed = discord.Embed(title="EldoBot Settings - Trades", description=f"Trade Settings for server {serverName}")
    embed.add_field(name='Trade Settings', value=f"**__Trade Channel:__** {serverSettings['tradechannel']}" + '\n' + f"*This channel will be scanned constantly for trades - all trades should be sent here.. Regular commands will not run in this channel. Edit with {prefix}edit tradechannel [#new channel].*" + '\n'
                    + f"**__Team Can Trade for Player Back Within the Same Season:__** ``{serverSettings['tradeback']}``" + '\n' + f'*If off, teams can not trade for a player who they traded away earlier in the same season. Resets at preseason. Edit with {prefix}edit tradeback [on/off].*' + '\n'
                    + f"**__# of Games Before Trading Signed FA:__** ``{serverSettings['tradefa']}``" + '\n' + f"*Signed FAs must spend this number of days with their team before being eligible for trade. Edit with {prefix}edit tradefa [new number].*" + '\n')
    await message.channel.send(embed=embed)

async def league_prompt(message):
    prefix = serversList[str(message.guild.id)]['prefix']
    serverName = message.guild.name
    serverSettings = shared_info.serversList[str(message.guild.id)]
    embed = discord.Embed(title="EldoBot Settings - League", description=f"General league settings, mostly relating to finances. **Many of these values are fixed according to what is in your export file. Some, however, can be edited.**")
    embed.add_field(name='Finance Settings', value=f"**Salary Cap:** ${shared_info.serverExports[str(message.guild.id)]['gameAttributes']['salaryCap']/1000}M" + '\n' + '\n'
                    + f"**Hard Cap:** ${serverSettings['hardcap']}M" + '\n' + f'*Teams cannot surpass this payroll for any reason other than draft picks. Edit with {prefix}edit hardcap [new value].*' + '\n' + '\n'
                    + f"**Minimum Contract:** ${shared_info.serverExports[str(message.guild.id)]['gameAttributes']['minContract']/1000}M" + '\n' + f"**Maximum Contract:** ${shared_info.serverExports[str(message.guild.id)]['gameAttributes']['maxContract']/1000}M" + '\n' + '\n'
                    + f"**Minimum Contract Years:** {shared_info.serverExports[str(message.guild.id)]['gameAttributes']['minContractLength']}" + '\n' + f"**Minimum Contract Years:** {shared_info.serverExports[str(message.guild.id)]['gameAttributes']['maxContractLength']}")
    embed.add_field(name='Lineup Settings', value=f"**Max OVR Difference: Starter vs Bench:** {serverSettings['lineupovrlimit']}" + '\n' + f"*A team cannot set a lineup where a bench player is this much OVR higher than a starter. Edit with {prefix}edit lineupovrlimit [new limit].*" + '\n' + '\n'
                    + f"**Max PT Modificiations:** {serverSettings['maxptmod']}" + '\n' + f'*The maximum number of allowed playing time modifications. Edit with {prefix}edit maxptmod [new value].*' + '\n' + '\n'
                    + f"**Max PT Modifier:** {serverSettings['maxptlimit']}" + '\n' + f"**Min PT Modifier:** {serverSettings['minptlimit']}" + '\n' + f"*This regulates the maximum and minimum amounts of modification a GM can do to playing time. With current settings, they cannot increase a player's playing time OVR by more than {(float(serverSettings['maxptlimit'])-1)}% or decrease it to less than {float(serverSettings['minptlimit'])}%. + minutes corresponds to a 25% increase, so 1.25, whereas - corresponds to 75%, so 0.75. Adjust with {prefix}edit maxptlimit or {prefix}edit minptlimit [new max/min modifier].*" + '\n' + '\n'
                    + f"**Max OVR that can be released:** {serverSettings['maxovrrelease']}" + '\n' + f"*Players higher than this rating can not be released. Edit with {prefix}edit maxovrrelease [new OVR].*")
    await message.channel.send(embed=embed)

async def draft_prompt(message):
    prefix = serversList[str(message.guild.id)]['prefix']
    serverName = message.guild.name
    serverSettings = shared_info.serversList[str(message.guild.id)]
    embed = discord.Embed(title="EldoBot Settings - Draft", description=f"Settings relating to the draft.")
    embed.add_field(name='Clock Settings', value='Your clock times are set as:' + '\n' + f"``{serverSettings['draftclock']}``" + '\n' + f"Adjust this by using {prefix}edit draftclock [new value]. **You should provide a list of numbers separated by commas, and each number represents the number of seconds of the clock in that round.** Some examples:" + '\n' + f"• ``300,200,0`` - this sets the round one clock to 300 seconds, round two to 200 seconds, and the third round will be autopicked." + '\n' + f"• ``300,0`` - this sets the first round to 300 seconds, and the second round will be auto-picked." + '\n' + '\n' + 'If a value is not specified for a round, it defaults to a 3 minute clock, which is 180 seconds. Setting the time to 0 is perfectly fine and will use boards or formulas to make each pick.')
    await message.channel.send(embed=embed)

async def edit_setting(text, message):
    toEdit = str.lower(text[1])
    newValue = text[2]
    server = str(message.guild.id)
    if toEdit in serversList[server]:
        valid = commands.settingsDirectory[toEdit](newValue)
        if valid:
            serversList[server][toEdit] = newValue
            await basics.save_db(serversList)
            text = '**Success!** New ' + toEdit + ' set to ' + str(newValue) + '!'
            await message.channel.send(text)
        else:
            text = 'Value ``' + str(newValue) + '`` is invalid.'
            await message.channel.send(text)

    else:
        await message.channel.send('Invalid setting provided. Please check the -settings pages to confirm the setting you are dying to edit.')
