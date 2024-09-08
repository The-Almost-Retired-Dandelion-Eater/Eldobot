import shared_info
import asyncio
import basics
import pull_info
from shared_info import serversList
from pull_info import pinfo
from pull_info import tinfo
import discord
import inventory_commands as ic
import json
import random
boatbl = set()
##PLAYER COMMANDS

commandFuncs = {
    'inventory':ic.inventory,
    'shop':ic.shopshow,
    'buy':ic.buy,
    'use':ic.use,
    'raft':ic.raft,
    'recipes':ic.recipes,
    'craft':ic.craft,
    'canoe':ic.canoe,
    'sell':ic.sell,
    'sailboat':ic.sailboat,
    'start':ic.start,
    'decktree':ic.techtree,
    'steamboat':ic.steamboat,
    'battleship':ic.battleship
}


async def process_text(text, message):
    
    

    command = str.lower(text[0])
    if command in ['sailboat','canoe','raft','steamboat','battleship']:
        if str(message.author.id) in boatbl:
            await message.channel.send("Your boats are in cooldown. Try again 1 second later")
            return
        else:
            boatbl.add(str(message.author.id))
  
    commandInfo = {"user":str(message.author.id)}
    commandInfo.update({"guild":message.guild})
    commandInfo.update({"message":message.content})
    commandInfo.update({"ch":message.channel})    
    commandInfo.update({"number":1})    
    embed = discord.Embed(title = "Inventory System:")
    for word in text:
        if word.__contains__("@"):
            commandInfo.update({"user":word.replace("<","").replace("!","").replace(">","").replace("@","")})
        try:
            commandInfo.update({"number":int(word)})
        except ValueError:
            pass
                            

    embed = commandFuncs[command](embed, message.author, commandInfo)
    if isinstance(embed,str):
        await message.channel.send(embed)
        return
    if isinstance(embed, tuple): # for using notes
        await embed[0].send("You have an anonymous message: \n"+embed[1])
        await message.channel.send("Done.")
        return
    #try: embed = commandFuncs[command](embed, p, commandInfo) #fill the embed with the specified function
    #except Exception as e:
     #   print(e) 
     #   embed.add_field(name='Error', value="An error occured. Command may not be specified.", inline=False)
    #print(pointdb)
     
    
    
    s = shared_info.embedFooter
    if random.random() < 0.05:
        s = "Dedicated to Ben135, the best multiplayer GM in history"
    embed.set_footer(text=s)
    if command == 'steamboat':
        embed.add_field(inline= False, name = "**Tip:** A zipper prevents items from being lost at sea", value = "buy one in the store.")

    else:
        embed.add_field(inline= False, name = "**Tip:** Do -help raft for all inventory-related commands", value = "Rafts are the best way to farm points in EldoBot!")
    await message.channel.send(embed=embed)
    x = open("inventory.json",'w')
    x.write(json.dumps(shared_info.inv))
    x.close()
    if command in ['sailboat','canoe','raft','steamboat','battleship']:
        print("waiting")
        await asyncio.sleep(1)
        boatbl.remove(str(message.author.id))

    




