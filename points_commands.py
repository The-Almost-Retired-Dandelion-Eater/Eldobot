from shared_info import points
from shared_info import daily
import pull_info
import basics
import discord
import random
import json
import shared_info
import math
import os
from openai import OpenAI

f = open("openaikey.txt","r")
for line in f:
    key = line.replace("\n","")
f.close()
client2 = OpenAI(api_key = key)
def loseall(embed, author, commandInfo):
    points.update({str(author.id):0})
    return embed
def shared(embed, author, commandInfo):
    m = commandInfo['message']
    theg = commandInfo['guild']
    for g in shared_info.bot.guilds:
        if g.name.lower().replace(" ","").replace("'","").replace('"','').replace(",","").replace(".","") in m.lower().replace(" ","").replace("'","").replace('"','').replace(",","").replace(".",""):
            theg = g
    homeg = commandInfo['guild']
    l = ""
    if theg.id == homeg.id:
        w = ""
        l = []
        for g in shared_info.bot.guilds:
            l.append(g.name)
        l = sorted(l)
        for g in l:
            w += g+"\n"
            if len(w) > 960:
                embed.add_field(name = "this is the same server, or you didn't spell correctly", value = w)
                w = ""
        embed.add_field(name = "this is the same server, or you didn't spell correctly", value = w)
        
        return embed
    for item in points:
        if commandInfo["guild"].get_member(int(item)) is not None and theg.get_member(int(item)) is not None:
            l=l + "<@"+str(item)+">\n"
            if len(l) > 900:
                embed.add_field(name = "Shared members between this server and "+theg.name, value = l)
                l = ""
    if len(l) > 0:
        embed.add_field(name =  "Shared members between this server and "+theg.name, value = l)
    

    return embed
def bal(embed, author, commandInfo):
    if isinstance(commandInfo["user"],str):
        if str(author.id) == str(commandInfo["user"]):
             embed.add_field(name= "Your balance is", value = points[str(commandInfo["user"])])
        else:
            if str(commandInfo["user"]) in points:
                embed.add_field(name= "Points Balance", value ="<@"+commandInfo["user"]+">'s balance is "+ str(points[str(commandInfo["user"])]))
            else:
                embed.add_field(name= "This poor guy's balance is 0", value = "tell them to talk to get points")

        return embed
    if str(author.id) == str(commandInfo["user"].id):
        
        embed.add_field(name= "Your balance is", value = points[str(commandInfo["user"].id)])
    return embed
def balance(embed,author, guild):
    rank = 1
    local_rank = 1
    global_users = len(points)
    server_users = 0
    pts = points[str(author.id)]
    for t in points.keys():
        if guild.get_member(int(t)) is not None:
            server_users += 1
            if points[t] > pts:
                local_rank += 1
        if points[t] > pts:
            rank += 1
    embed.add_field(name =author.name, value = "Your points: "+str(round(pts, 2))+"\nYour Server Rank: "+str(local_rank)+"/"+str(server_users)+"\nYour Global Rank: "+str(rank)+"/"+str(global_users), inline = False)
    return embed
def rob(embed, author, commandInfo):
    ownpts = points[str(author.id)]
    if not commandInfo['user'] in points:
        embed.add_field(name ="Robbing", value = "Other user is not in the database.")
        return embed
    if commandInfo['guild'].get_member(int(commandInfo["user"])) is None:
        embed.add_field(name ="Robbing", value = "Oh boy, you almost found a loophole. Sniping users in other servers, while clever, is unethical and not allowed.")
        return embed
    if str(author.id) == commandInfo['user']:
        embed.add_field(name ="Robbing", value = "Stealing from yourself is against the law. Wait, what?")
        return embed
    otherpts = points[commandInfo['user']]
    successrate = (ownpts/(ownpts+otherpts+0.1))**2
    success = False
    if random.random() < successrate:
        success = True
        transfer = otherpts/4
        points.update({commandInfo['user']:points[commandInfo['user']]-transfer})
        points.update({str(author.id):points[str(author.id)]+transfer})
        embed.add_field(name ="Robbing", value = "Success rate "+str(round(successrate*100, 2))+"%\n"+"You did it! you make it away with "+str(round(transfer, 4))+" points.")
        return embed
    else:
        success = False
        transfer = ownpts/4
        points.update({commandInfo['user']:points[commandInfo['user']]+transfer})
        points.update({str(author.id):points[str(author.id)]-transfer})
        embed.add_field(name ="Robbing", value = "Success rate "+str(round(successrate, 3)*100)+"%\n"+"You failed! As punishment you paid your victim "+str(round(transfer, 4))+" points.")
        return embed
def chatgpt(embed, author, commandInfo):
    embed.add_field(name = "Now look what you've done!", value = "You lot using this bot got this command disabled through spamming it. Happy now?")
    return embed
    m = " ".join(commandInfo['message'].split(" ")[1:])
    if len(m) < 2:
        m = "artistically describe an empty void in fewer than 50 words"
    print(m)
    chat_completion = client2.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": m
            }
        ],
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[0].message.content
    f = min(2000, len(response))
    return response[0:f]
    
def give(embed, author, commandInfo):
    ownpts = points[str(author.id)]
    if not commandInfo['user'] in points:
        embed.add_field(name ="Gifting", value = "Other user is not in the database.")
        return embed
    if commandInfo['guild'].get_member(int(commandInfo["user"])) is None:
        embed.add_field(name ="Gifting", value = "I appreciate your kindness but you cannot give someone who isn't even in the SERVER.")
        return embed
    if str(author.id) == commandInfo['user']:
        embed.add_field(name ="Gifting", value = "Giving to yourself is against the law. Wait, what?")
        return embed

    transfer = commandInfo['bet']

    if transfer < ownpts and transfer > 0:


        points.update({commandInfo['user']:points[commandInfo['user']]+transfer})
        points.update({str(author.id):points[str(author.id)]-transfer})
        embed.add_field(name ="Gifting", value = "You did it! you gave <@"+commandInfo['user']+"> "+str(round(transfer, 4))+" points.\nThey now have "+str(round(points[commandInfo['user']],3))+" points.")
        return embed
    else:
        embed.add_field(name ="Gifting", value = "You are either gifting more than you have, or gifting a negative amount. What are you doing?")
        return embed
def flip(embed, author, commandInfo):
    
    if commandInfo["bet"] > points[str(author.id)]:
        embed.add_field(name = "Coin Flip", value= "Not enough points")
        return embed
    if commandInfo["bet"] < 0:
        embed.add_field(name = "Coin Flip", value= "This was a bug once upon a time. People used it to gain infinite points. Not anymore!")
        return embed
    result = 'Heads'
    if random.random()<0.5:
        result = 'Tails'
    win = False
    if result == commandInfo['guess']:
        win = True
    if win:
        points.update({str(author.id):points[str(author.id)]+commandInfo["bet"]})
    else:
        points.update({str(author.id):points[str(author.id)]-commandInfo["bet"]})
    v = "Result: "+str(result)+"\n"
    bet = commandInfo["bet"]
    if win:
        v = v + "You win! You gain "+str(round(bet, 3))+" points."
    else:
        v = v + "You lost. You lose "+str(round(bet, 3))+" points."
    embed.add_field(name = "Coin Flip", value= v)
    return embed
def dailyclaim(embed, author, commandInfo):
    if str(author.id) in daily['members']:
        embed.add_field(name = "Daily", value= "You already claimed")
        return embed
    d = daily['members']
    d.append(str(author.id))
    daily.update({'members':d})
    p = points["1142491919193223228"]/10
    points.update({"1142491919193223228":points["1142491919193223228"]-p})
    points.update({str(author.id):points[str(author.id)]+p})
    embed.add_field(name = "Daily", value = "Claimed "+str(round(p,3))+" from the bot's bank account")
    with open('daily.json','w') as f:
        f.write(json.dumps(daily))
    f.close()
    return embed
def resetdaily(embed, author, commandInfo):
    if not (author.id == 1020519991512158210 or author.id == 1097659721562980404):
        embed.add_field(name = "Daily",value = "Daily can only be reset with the approval of Illusion himself.")
        return embed
    daily.update({'members':[]})
    with open('daily.json','w') as f:
        f.write(json.dumps(daily))
    f.close()
    s = 0
    for k,t in points.items():
        if not k == "1142491919193223228":
            s += t
        
    points.update({"1142491919193223228":math.sqrt(s)})
    embed.add_field(name = "Daily",value = "reset daily")
    return embed
def lottery(embed, author, commandInfo):
    cost = 1
    if points[str(author.id)] < cost:
        embed.add_field(name = "Lottery entrance", value = "Not enough points. Amass 1 point to buy a lottery ticket. \nSeriously, it's just 1 point. How hard can that be?")
        return embed
    points.update({str(author.id):points[str(author.id)]-cost})
    daily.update({'pool':daily['pool']+cost})

    if random.random() < 0.05:
        pool = daily["pool"]
        points.update({str(author.id):points[str(author.id)]+pool})
        daily.update({'pool':5})
        embed.add_field(name = "Lottery entrance", value = "**WINNER**\nLucky you, who won the pool of "+str(pool))
    else:
        embed.add_field(name = "Lottery entrance", value = "You lost. The pool is now "+str(daily['pool'])+", please try again!")
    with open('daily.json','w') as f:
        f.write(json.dumps(daily))
    f.close()
    return embed
def lotterypool(embed, author, commandInfo):
    embed.add_field(name = "Lottery pool", value = "The lotto pool is now "+str(daily["pool"]))
    return embed
def all_leaders(embed, author, commandInfo):
    l = []
    for item in points:
        l.append(["<@"+item+">: ",points[item]])
    l = sorted(l, key = lambda l:l[1], reverse = True)
    pages = int(len(l)/10) + 1
    
    i = commandInfo["number"]
    if i > pages or i <= 0:
        i = 1
    if i < pages:
        s = ""
        for j in range (i*10-10, i*10):
            if l[j][0][2:-3] == str(author.id):
                #print("leaders case has been detected")
                s += '**'+str(j+1)+": "+l[j][0]+str(round(l[j][1],3))+"**\n"
            else:
                s += str(j+1)+": "+l[j][0]+str(round(l[j][1],3))+"\n"
    if i == pages:
        s = ""
        for j in range (i*10-10, len(l)):


            if l[j][0][2:-1] == str(author.id):
                s +='**'+str(j+1)+": "+ l[j][0]+str(round(l[j][1],3))+"**\n"
            else:
                s +=str(j+1)+": "+ l[j][0]+str(round(l[j][1],3))+"\n"
    embed.add_field(name = "Discord-wide Points Leaders", value = s+"Page "+str(i)+" out of "+str(pages))
    return embed
    
def leaders(embed, author, commandInfo):
    l = []
    for item in points:
        if commandInfo["guild"].get_member(int(item)) is not None:
            l.append(["<@"+item+">: ",points[item]])
    l = sorted(l, key = lambda l:l[1], reverse = True)
    pages = int(len(l)/10) + 1
    
    i = commandInfo["number"]
    if i > pages or i <= 0:
        i = 1
    if i < pages:
        s = ""
        for j in range (i*10-10, i*10):
            if l[j][0][2:-3] == str(author.id):
                #print("leaders case has been detected")
                s += '**'+str(j+1)+": "+l[j][0]+str(round(l[j][1],3))+"**\n"
            else:
                s += str(j+1)+": "+l[j][0]+str(round(l[j][1],3))+"\n"
    if i == pages:
        s = ""
        for j in range (i*10-10, len(l)):


            if l[j][0][2:-1] == str(author.id):
                s +='**'+str(j+1)+": "+ l[j][0]+str(round(l[j][1],3))+"**\n"
            else:
                s +=str(j+1)+": "+ l[j][0]+str(round(l[j][1],3))+"\n"
    embed.add_field(name = commandInfo["guild"].name+" Points Leaders", value = s+"Page "+str(i)+" out of "+str(pages))

    return embed
