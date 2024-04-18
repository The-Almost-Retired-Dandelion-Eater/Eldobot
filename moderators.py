import shared_info
exports = shared_info.serverExports
import basics
import pull_info
import mod_commands
import discord

commandFuncs = {
    'addgm': mod_commands.add_gm,
    'teamlist': mod_commands.teamlist,
    'removegm': mod_commands.removegm,
    'assigngm': mod_commands.autoassigngm
}

async def process_text(text, message):
    export = shared_info.serverExports[str(message.guild.id)]
    season = export['gameAttributes']['season']
    command = str.lower(text[0])
    embed = discord.Embed(title=message.guild.name, description=f"{season} season")
    # uncomment the next line when debugging, to get a full error message in console
    # embed = commandFuncs[command](embed, text, message)
    try: embed = await commandFuncs[command](embed, text, message) #fill the embed with the specified function
    except Exception as e:
        print(e) 
        embed.add_field(name='Error', value="An error occured. Command may not be specified.", inline=False)
    
    await message.channel.send(embed=embed)
