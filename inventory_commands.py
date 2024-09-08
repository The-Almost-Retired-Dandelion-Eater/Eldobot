import shared_info
import json
import random
inv = shared_info.inv
pointdb = shared_info.points
shop = {'raft':100,'cookie':0.1,"note":10,"nail":10,"giftbox":10,"hitman":25,'bodyguard':50,'sail':250,'cod':10,'salmon':40,'jellyfish':100,'rod':100,'axe':30,"zipper":50,"magnet":1000,'spork':10,'gunpowder':5,
        'carrier':1000000,'gold':200,'camouflage':100,'fried seagull':6.2831853}

shopdesc = {'raft':'Sail the open ocean with a nice, comfortable raft!',
            'cookie':'Not useful for points, but you can eat them and enjoy some physical, sensory satisfaction',
            'note':'Use a note to send an anonomous message to anyone in the server, the bot will personally DM your message without revealing your identity.',
            'nail':'A tool used for construction of various boats, such as CANOES!',
            'giftbox':'allows you to give someone else any amount of one type of item.',
            "hitman":"A top secret agent you can use on another user to deprive them of 50% of their points with 20% probability. However, watch out, as there is a fine of up to 10% if he gets caught!",
            'bodyguard':"prevents one otherwise would-have-been-successful hitman from taking effect, but has a 25% chance of being used up in the process.",
            'rod':'A fishing rod which helps you get more fish with sailboats.',
            "zipper":"A sturdy tool to prevent items from being lost at sea",
            "magnet": "A giant electromagnet that's attached to your boat. But why would you want that? For decoration?",
            'spork':"A plastic dining utility. There's no use for it in the world of rafting, but it is a way for you to sell your excess plastic.",
            'camouflage':'A layer of sky- and ocean-colored fabric that blends your battleship into the background, and therefore it will not partake in any battles.',
            'fried seagull':'A fried delicacy made from the most annoying oceanic bird.'}
crafts = [{'output':'raft','input':{'log':5},'cost':10},
          {'output':'canoe','input':{'log':10, 'raft':1,'nail':10},'cost':50},
          {'output':'sailboat','input':{ 'canoe':1,'nail':10,'sail':2,'plastic':250},'cost':250},
          {'output':'sailboat','input':{'damaged sailboat':1,'sail':1},'cost':0},
          {'output':'sail','input':{'plastic':100,'nail':5},'cost':1},
          {'output':'steamboat','input':{'metal':400,'sailboat':1},'cost':1000},
          {'output':'battleship','input':{'metal':1000,'plastic':500,'steamboat':1},'cost':10000},
          {'output':'spork','input':{'plastic':10},'cost':0},
          {'output':'cannon','input':{'metal':10},'cost':20}]
def giveuseritem(db,author,item,count=1):
    if not item in db[str(author.id)]:
        db[str(author.id)].update({item:0})
    db[str(author.id)].update({item:db[str(author.id)][item]+count})
    return db
def battleship(embed, author, commandInfo):

    rj = author.name+"'s Battleship journey"
    if (not str(author.id) in inv) or (not 'battleship' in inv[str(author.id)]) or inv[str(author.id)]['battleship'] < 1:
        embed.add_field(name = "No Battleship?", value = "When you live off the seas, you don't waste a trip\nWhen you battle and plunder, you don't give a tip\nWhen you're grabbing  the treasure, you don't lose your grip\nWhen you're sailing the waters, you don't use a ship\n Wait, what?")
        return embed
    if not 'cannon' in inv[str(author.id)]:
        inv[str(author.id)].update({'cannon':1})
    if not 'gunpowder' in inv[str(author.id)]:
        inv[str(author.id)].update({'gunpowder':0})
    if random.random() < 0.25:
        # BATTLE
        if 'camouflage' in inv[str(author.id)] and inv[str(author.id)]['camouflage'] > 0:
            embed.add_field(name = rj, value = "Your camouflage prevented you from entering any battle.")
            return embed
        if pointdb[str(author.id)] < 10000:
            piratechance = 0.9
            smallbattleshipchance = 0.1
            largebattleshipchance  = 0
        elif pointdb[str(author.id)] < 100000:
            piratechance = 0.5
            smallbattleshipchance = 0.5
            largebattleshipchance  = 0
        else:
            piratechance = 0.3
            smallbattleshipchance = 0.4
            largebattleshipchance  = 0.3
        b = random.random()
        if b < piratechance:
            enemycannons =int(1+ random.random()*5)
            
            enemyreward = 'low'
            meettext = "You encountered a small, independent pirate ship."
        elif b < piratechance+smallbattleshipchance:
            enemycannons =int(5+ random.random()*25)
            enemyreward = 'mid'
            meettext = "You encountered a small battle ship run by a provincial coast guard."
        else:
            enemycannons =int(30+ random.random()*100)
            enemyreward = 'high'
            meettext = "You encountered a huge battleship run by some kind of evil marine empire."
        if random.random() < 0.2:
            enemycannons = enemycannons * 7
            meettext += " You shudder in fear as this particular enemy ship seems to have a high amount of investment in cannons."
        strength = min(inv[str(author.id)]['cannon'],inv[str(author.id)]['gunpowder'])
        
        if inv[str(author.id)]['gunpowder'] < inv[str(author.id)]['cannon']:
            meettext += " \n\n**However, your strength was limited by your lack of gunpowder**. In each battle, each cannon uses up 1 gunpowder. If your gunpowder is lower than your number of cannons, some cannons don't fire and are wasted. Gunpowder can simply be bought in the shop or found at sea."
        giveuseritem(inv, author, 'gunpowder',-strength)
        if inv[str(author.id)]['cannon'] < 5:
            meettext += "\n\n**You don't seem to have a lot of cannons.** Perhaps it is better to avoid battle with a camouflage first, and gather some resources. A camouflage can be bought in the store, somewhat unrealistic but it's how this works."
        meettext += "\n\n"
        if strength == enemycannons:
            embed.add_field(name = rj, value = meettext+"In the battle, you had "+str(strength)+" cannons firing and the opponent had "+str(enemycannons)+" cannons firing. It was a draw. However, the wasted gunpowder meant it was a net loss for both of you. War doesn't pay!")
            return embed
        if strength < enemycannons:
            # you lost
            howyoulost = "**You lost the battle**, having "+str(strength)+" cannons firing as opposed to the enemy's "+str(enemycannons)+".\n"
            if random.random() < 0.5:
                if 'chest' in inv[str(author.id)] and inv[str(author.id)] ['chest'] > 0:
                    giveuseritem(inv, author, 'chest',-1)
                    embed.add_field(name = rj, value = meettext+howyoulost+"Fortunately, the enemy mistook an **empty treasure chest** you obtained from a previous victory and stuffed with fish bones as the loot from your ship, and you escaped having lost only an empty chest.")
                    
                    return embed
            if random.random() < 0.7:
                if 'gold' in inv[str(author.id)] and inv[str(author.id)]['gold'] > 0:
                    if random.random() < 0.5:
                        amountlost = int(1+0.1*inv[str(author.id)]['gold'])
                        giveuseritem(inv, author, 'gold',-amountlost)
                        embed.add_field(name = rj, value = meettext+howyoulost+"The enemy stole a bit over 10% of your gold bars. They took "+str(amountlost)+ ", and you still have only "+str(inv[str(author.id)]['gold']))
                        return embed
                amount = pointdb[str(author.id)]
                amountlost = 0.25*min(100,amount)+0.01*max(amount-100,0)
                amountlost = min(3000,amountlost)
                pointdb.update({str(author.id):pointdb[str(author.id)]-amountlost})
                embed.add_field(name = rj, value = meettext+howyoulost+"The enemy stole some of your points. They took "+str(amountlost) +", and you still have only "+str(pointdb[str(author.id)]))
                return embed
            else:
                # you lose material
                if inv[str(author.id)]['cannon'] > 0:
                    if random.random() < 0.3:
                        giveuseritem(inv, author, 'cannon', -1)
                        howyoulost += "**One of your cannons** was also destroyed in the crossfire, and you now just have "+str(inv[str(author.id)]['cannon'])+" of them.\n"

                        
                boattypes = ["raft","canoe","sailboat","steamboat","battleship","carrier","cruiseship"]
                cantlose = boattypes
                cantlose.append("bodyguard")
                cantlose.append("hitman")
                cantlose.append("cannon")
                u = inv[str(author.id)]
                t = "raft"
                count= 0
                while ((t in cantlose) or u[t] == 0):
                    t = random.sample(u.keys(),1)[0]
                    count += 1
                    if (count > 300):
                        break
                if count > 300:
                    embed.add_field(name = rj, value = meettext+howyoulost+"However, you were also so poor that the enemy failed to locate anything valuable to steal from you")
                    return embed
                num = int(1+u[t]*0.1)
                giveuseritem(inv,author,t,count=-num)
                if num == 1:
                    plural = ""
                else:
                    plural = "s"
                embed.add_field(name = rj, value = meettext+howyoulost+"The enemy plundered your supplies for a specific item they really needed. Therefore, you lost **"+str(num)+" "+t+plural+"**. You only have "+str(u[t])+" left. Sucks to be you!")
                return embed
        if strength > enemycannons:
        # you win
            if enemyreward == 'low':
                pointvalue = random.random()*200+200
                goldbricks = 1+int(random.random()*3)
                numfish = 5
                gunpowder = 1+int(random.random()*3)
                metal = 1+int(random.random()*3)
                spork = 3+int(random.random()*4)
                name = "pirate ship"
                cannon = 0
            if enemyreward == 'mid':
                pointvalue = random.random()*500+1500
                goldbricks = 2+int(random.random()*6)
                numfish = 10
                gunpowder = 2+int(random.random()*4)
                metal = 4+int(random.random()*5)
                spork = 0
                name = "small battleship"
                cannon = 1
            if enemyreward == 'high':
                pointvalue = random.random()*2000+1000
                goldbricks = 5+int(random.random()*6)
                numfish = 15
                gunpowder = 3+int(random.random()*5)
                metal = 6+int(random.random()*6)
                spork = 0
                name = "large battleship"
                cannon = 1
            string = "From the "+name+" you freshly vanquished, you obtain as bounty: \n"
            pointdb.update({str(author.id):pointdb[str(author.id)]+pointvalue})
            string += "- "+str(pointvalue)+" points\n"
            if random.random() < 0.3:
                giveuseritem(inv, author, 'gold',goldbricks)
                string += "- "+str(goldbricks)+" shiny ingots of gold that can be sold for 100 points each\n"
            if random.random() < 0.25:
                fish = "salmon"
                if random.random()<0.5:
                    fish = "cod"
                giveuseritem(inv, author, fish,numfish)
                string += "- "+str(numfish)+" "+fish+"\n"
            if random.random() < 0.25 and cannon > 0:
                giveuseritem(inv, author, 'cannon',cannon)
                string += "- a functional cannon that has been added to your battleship\n"
            if random.random() < 0.2:
                giveuseritem(inv, author, 'metal',metal)
                string += "- "+str(metal)+" pieces of metal\n"
            if random.random() < 0.2:
                giveuseritem(inv, author, 'gunpowder',gunpowder)
                string += "- "+str(gunpowder)+" gunpowder\n"
            if random.random() < 0.02:
                giveuseritem(inv, author, 'chest',1)
                string += "- an empty treasure chest that may come in handy later.\n"
            if random.random() < 0.1:
                if spork > 0:
                    giveuseritem(inv, author, 'spork',spork)
                    string += "-"+str(metal)+" sporks that, to your surprise, were the dining utility of choice of the pirates\n"
            
            embed.add_field(name = rj, value = meettext+"You won the battle, having "+str(strength)+" cannons firing as opposed to the enemy's "+str(enemycannons)+".\n"+string)
            return embed
        
        
    else:
        r = random.random()
        metalthreshold = 0.525
        if 'camouflage' in inv[str(author.id)] and inv[str(author.id)]['camouflage'] > 0:
            metalthreshold = 0.725
        
        if r < 0.15:
            numnails = 1
            
            giveuseritem(inv, author, 'gunpowder',numnails)

            embed.add_field(name = rj, value = "You obtained "+str(numnails)+" gunpowder.")
            return embed
        elif r < 0.25:

            giveuseritem(inv, author, 'log',1)

            embed.add_field(name = rj, value = "You obtained a log from some kind of disintegrated raft.")
            return embed
        elif r < 0.3:
            giveuseritem(inv, author, 'cod')
            if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
                giveuseritem(inv, author, 'cod', count = 2)
                text = " You caught 3 cod with help from your fishing rod!"
                if random.random() < 0.1:
                    giveuseritem(inv, author, 'rod', count = -1)
                    text += " BUT your fishing rod broke."
                
                embed.add_field(name = rj, value = text)
                return embed
            else:
                
                embed.add_field(name = rj, value = " You caught a cod!")
                return embed
        elif r < 0.35:
            giveuseritem(inv, author, 'salmon')
            if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
                giveuseritem(inv, author, 'salmon', count = 1)
                text = " You caught 2 salmon with help from your fishing rod!"
                if random.random() < 0.1:
                    giveuseritem(inv, author, 'rod', count = -1)
                    text += " BUT your fishing rod broke."
                
                embed.add_field(name = rj, value = text)
                return embed
            else:
                embed.add_field(name = rj, value = " You caught a salmon!")
                return embed
        elif r < 0.375:
            giveuseritem(inv, author, 'jellyfish')
            if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
                giveuseritem(inv, author, 'jellyfish', count = 1)
                text = " You caught 2 jellyfish with help from your fishing rod!"
                if random.random() < 0.1:
                    giveuseritem(inv, author, 'rod', count = -1)
                    text += " BUT your fishing rod broke."
                embed.add_field(name = rj, value = text)
                return embed
            else:
                embed.add_field(name = rj, value = " You caught a jellyfish!")
                return embed
        elif r < metalthreshold:
            if "magnet" in inv[str(author.id)] and inv[str(author.id)]['magnet'] > 0 and random.random() > 0.25:
                giveuseritem(inv, author, 'metal', count = 5)
                embed.add_field(name = rj, value = " Your magnet attracted 5 pieces of metal! It wasn't as effective, as the battleship is so huge and the magnet was kind of buried and didn't have as much exposure to open waters.")
                return embed
            numnails = int(1 + 3*random.random())
            
            giveuseritem(inv, author, 'metal',numnails)

            embed.add_field(name = rj, value = "You obtained "+str(numnails)+" metal")
            return embed
        elif r > 0.9:
            giveuseritem(inv, author, 'fried seagull',1)
            embed.add_field(name = rj, value = "You saw a seagull, and instead of waving, you shot the annoying bird and killed it, and even collected its corpse and cooked it. You obtained 1 fried seagull.")
            return embed
        embed.add_field(name = rj, value = "You dozed off, and once you woke up, you were at the shore again. You remember nothing about your trip, except a vague recollection of the constant and annoying squawks of some seagulls.")
        return embed
            
def recipes(embed, author, commandInfo):
    s = ""
    for c in crafts:
        s = s + "**"+c['output']+"**: "
        for item in c['input']:
            s += item+": "+str(c['input'][item])+", "
        s = s[:-2]
        s = s + ", Cost: "+str(c['cost'])
        s += "\n"
    embed.add_field(name = "Recipes", value = s)
    return embed

def start(embed, author, commandInfo):
    if (not str(author.id) in inv) or ('raft' not in inv[str(author.id)]):
        if (not str(author.id) in inv):
            inv.update({str(author.id):dict()})
        giveuseritem(inv, author, 'raft')
        embed.add_field(name = "Gave you a raft", value = "do -raft now. You got your free claim, now from now on you must craft or buy everything else")
        return embed
    else:
        embed.add_field(name = "Not eligible", value = "you already started")
        return embed

        
def inventory(embed, author, commandInfo):
    
    if str(commandInfo['user']) in inv:
        s = ""
        for key, value in inv[str(commandInfo['user'])].items():
            if value > 0:
                s = s +key+": "+str(value)+"\n"
        embed.add_field(name = "inventory of this user", value = s)
        return embed
    else:
        embed.add_field(name = "This person has no inventory", value = "See what can be bought using -shop")
        return embed
def craft(embed, author, commandInfo):
    if not str(author.id) in inv:
        embed.add_field(name = "Can't craft", value = "you got nothing.")
        return embed
    tocraft = None
    
    for item in commandInfo['message'].split(" "):
        for c in crafts:
            if c['output'] == item:
                if 'damaged sailboat' in c['input']:
                    # only use this recipe if the guy has a damaged boat
                    if str(author.id) in inv and 'damaged sailboat' in inv[str(author.id)] and inv[str(author.id)]['damaged sailboat'] > 0:
                        tocraft = c
                else:
                    tocraft = c
    amount = commandInfo['number']
    if amount < 1:
        amount = 1
    if not tocraft  == None:
        #Check that the guy has enough stuff
        for thing, quantity in tocraft['input'].items():
            neededquant = quantity*amount
            if not thing in inv[str(author.id)]:
                embed.add_field(name = "cant craft", value = "not enough "+thing+", you need "+str(neededquant)+", and you got none.")
                return embed
            if inv[str(author.id)][thing] < neededquant:
                embed.add_field(name = "cant craft", value = "not enough "+thing+", you need "+str(neededquant)+", and you got "+str(inv[str(author.id)][thing]))
                return embed
        # now, they have the stuff required. but how about the points?
        if pointdb[str(author.id)] < tocraft['cost']*amount:
            embed.add_field(name = "cant craft", value = "you need to pay the crafting fee of "+str(tocraft['cost']*amount)+" and you ain't got enough money")
            return embed
        # now, craft goes on
        pointdb.update({str(author.id):pointdb[str(author.id)]-tocraft['cost']*amount})
        for item, value in tocraft['input'].items():
            giveuseritem(inv, author, item, count = -value*amount)
        giveuseritem(inv, author, tocraft['output'], count = amount)
        embed.add_field(name = "Crafted "+str(amount)+" "+str(tocraft['output']), value = "paid "+str(tocraft['cost']*amount)+" points.", inline = True)
        embed = inventory(embed, author, commandInfo)
        return embed
    embed.add_field(name= "no recipe found", value = "whjgkwlgark")
    return embed
def shopshow(embed, author, commandInfo):
    s = ""
    for key, value in shop.items():
        s = s + "**"+key+"**: "+str(value)+" points"
        if key in shopdesc:
            s += ", "+shopdesc[key]
        s += "\n"
        if len(s) > 800:
            embed.add_field(name = "The EldoBot Shop!", value = s, inline = False)
            s = ""
    if len(s) > 1:
        embed.add_field(name = "The EldoBot Shop!", value = s,inline = False)
    return embed
def raft(embed, author, commandInfo):
    s = ""
    rj = author.name+"'s Raft journey"
    if (not str(author.id) in inv) or (not 'raft' in inv[str(author.id)]) or inv[str(author.id)]['raft'] < 1:
        embed.add_field(name = "No raft?", value = "You rode in to sea on your aircraft,\n you wait for a breeze and a stiff draft,\n you worked hard on your seafaring craft, \njust to notice you don't have a raft.")
        
        return embed
    r = random.random()
    #r = commandInfo['number']/100 # for testing purposes
    if r < 0.6:
        ptvalue = random.random()*2
        if r < 0.1:
            ptvalue = random.random()*10
        pointdb.update({str(author.id):pointdb[str(author.id)]+ptvalue})
        embed.add_field(name = rj, value = "You found "+str(ptvalue)+" points floating through the sea!.")
        return embed
    elif r < 0.625:
        if not 'note' in inv[str(author.id)]:
            inv[str(author.id)].update({'note':0})
        inv[str(author.id)].update({'note':inv[str(author.id)]['note']+1})
            
        embed.add_field(name = rj, value = "You saw some seagulls flying over the vast, open ocean and tried waving to them. To your **utter shock**, they responded to your greeting by swooping in and giving you a **note**.")
        return embed
    elif r < 0.675:
        numnails = int(1 + 3*random.random())
        
        if not 'nail' in inv[str(author.id)]:
            inv[str(author.id)].update({'nail':0})
        inv[str(author.id)].update({'nail':inv[str(author.id)]['nail']+numnails})
        embed.add_field(name = rj, value = "You found "+str(numnails)+" nails (the construction tool, not fingernails) floating in the ocean. Keep those nails, as they are a necessary component of **canoes**! Once you gather 10 nails and 10 logs, do -craft canoe to obtain a canoe, which can help you earn even more points than a raft! \n\nYou now have "+str(inv[str(author.id)]['nail'])+" nails.")
        return embed
    elif r < 0.75:
        numnails = int(1 + 3*random.random())
        
        if not 'log' in inv[str(author.id)]:
            inv[str(author.id)].update({'log':0})
        inv[str(author.id)].update({'log':inv[str(author.id)]['log']+numnails})
        embed.add_field(name = rj, value = "You found "+str(numnails)+" logs (processed tree trunks, not records of events) floating in the ocean. Keep those logs, as they are a necessary component of rafts and **canoes**! Once you gather 10 nails and 10 logs, do -craft canoe to obtain a canoe, which can help you earn even more points than a raft! \n\nYou now have "+str(inv[str(author.id)]['log'])+" logs.")
        return embed
    elif r < 0.99:
        embed.add_field(name = rj, value = "You saw some seagulls flying over the vast, open ocean and tried waving to them. They didn't wave back.")
        return embed
    else:
        numlogs = int(1 + 3*random.random())
        if not 'log' in inv[str(author.id)]:
            inv[str(author.id)].update({'log':0})
        inv[str(author.id)].update({'log':inv[str(author.id)]['log']+numlogs})
        inv[str(author.id)].update({'raft':inv[str(author.id)]['raft']-1})
        embed.add_field(name = rj, value = "**Your raft disintegrated**. Fortunately, you were able to recover "+str(numlogs)+" logs out of the 5 logs that compose all rafts in this universe.")
        
        return embed
def canoe(embed, author, commandInfo):
    s = ""
    rj = author.name+"'s Canoe journey"
    if (not str(author.id) in inv) or (not 'canoe' in inv[str(author.id)]) or inv[str(author.id)]['canoe'] < 1:
        embed.add_field(name = "No canoe?", value = "You start your journey anew,\n you go to places traveled by few,\n you try sailing the ocean blue, \nbut you simply lack a canoe.")
        
        return embed
    r = random.random()
    #r = commandInfo['number']/100 # for testing purposes
    if r < 0.4:
        ptvalue = random.random()*4
        if r < 0.1:
            ptvalue = random.random()*20
        plastic = 0
        texts = "You found "+str(ptvalue)+" points floating through the sea!."
        if r < 0.35 and r > 0.1:
            plastic = int(random.random()*20+1)
            giveuseritem(inv,author,"plastic",plastic)
            texts = "You found "+str(ptvalue)+" points floating through the sea. \n\nAdditionally, you found "+str(plastic)+" pieces of plastic which are a byproduct from the harmful trend of oceanic pollution in the modern era. Fortunately, they can be used to construct **sailboats**!"
        pointdb.update({str(author.id):pointdb[str(author.id)]+ptvalue})
        
        embed.add_field(name = rj, value = texts)
        return embed
    elif r < 0.5:
        giveuseritem(inv, author, 'salmon')
        if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
            giveuseritem(inv, author, 'salmon', count = 1)
            text = " You caught 2 salmon with help from your fishing rod!"
            if random.random() < 0.1:
                giveuseritem(inv, author, 'rod', count = -1)
                text += " BUT your fishing rod broke."
            
            embed.add_field(name = rj, value = text)
            return embed
        else:
            embed.add_field(name = rj, value = " You caught a salmon! Selling salmon is a great way to earn points")
            return embed
    elif r < 0.6:
        giveuseritem(inv, author, 'cod')
        if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
            giveuseritem(inv, author, 'cod', count = 1)
            text = " You caught 2 cod with help from your fishing rod!"
            if random.random() < 0.1:
                giveuseritem(inv, author, 'rod', count = -1)
                text += " BUT your fishing rod broke."
            
            embed.add_field(name = rj, value = text)
            return embed
        else:
            embed.add_field(name = rj, value = " You caught a cod! Selling cod is a great way to earn points")
            return embed
    elif r < 0.61:
        if not 'note' in inv[str(author.id)]:
            inv[str(author.id)].update({'note':0})
        inv[str(author.id)].update({'note':inv[str(author.id)]['note']+1})
            
        embed.add_field(name = rj, value = "You saw some seagulls flying over the vast, open ocean and tried waving to them. To your **utter shock**, they responded to your greeting by swooping in and giving you a **note**.")
        return embed
    else:
        embed.add_field(name = rj, value = "You saw some seagulls flying over the vast, open ocean and tried waving to them. They didn't wave back.")
        return embed
    
        return embed
def sailboat(embed, author, commandInfo):
    s = ""
    rj = author.name+"'s sailboat journey"
    if (not str(author.id) in inv) or (not 'sailboat' in inv[str(author.id)]) or inv[str(author.id)]['sailboat'] < 1:
        embed.add_field(name = "No sailboat?", value = "You really liked to gloat, \nto show off all you've wrote,\nyou tried to put on your coat\n, but you didn't have a boat.")
        
        return embed
    r = random.random()
    #r = commandInfo['number']/100 # for testing purposes
    if r < 0.25:
        ptvalue = random.random()*5
        if r < 0.1:
            ptvalue = random.random()*50
        pointdb.update({str(author.id):pointdb[str(author.id)]+ptvalue})
        embed.add_field(name = rj, value = "You found "+str(ptvalue)+" points floating through the sea!.")
        return embed
    elif r < 0.3:
        if "magnet" in inv[str(author.id)] and inv[str(author.id)]['magnet'] > 0 and random.random() > 0.25:
            giveuseritem(inv, author, 'metal', count = 25)
            embed.add_field(name = rj, value = " Your magnet attracted 25 pieces of metal! Gather 400 of them to build a steamship!")
            return embed
        giveuseritem(inv, author, 'metal', count = 5)
        embed.add_field(name = rj, value = " You acquired 5 pieces of metal! Gather 400 of them to build a steamship!")
        return embed
    elif r < 0.4:
        giveuseritem(inv, author, 'cod')
        if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
            giveuseritem(inv, author, 'cod', count = 2)
            text = " You caught 3 cod with help from your fishing rod!"
            if random.random() < 0.1:
                giveuseritem(inv, author, 'rod', count = -1)
                text += " BUT your fishing rod broke."
            
            embed.add_field(name = rj, value = text)
            return embed
        else:
            
            embed.add_field(name = rj, value = " You caught a cod!")
            return embed
    elif r < 0.5:
        giveuseritem(inv, author, 'salmon')
        if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
            giveuseritem(inv, author, 'salmon', count = 1)
            text = " You caught 2 salmon with help from your fishing rod!"
            if random.random() < 0.1:
                giveuseritem(inv, author, 'rod', count = -1)
                text += " BUT your fishing rod broke."
            
            embed.add_field(name = rj, value = text)
            return embed
        else:
            embed.add_field(name = rj, value = " You caught a salmon!")
            return embed
    elif r < 0.55:
        giveuseritem(inv, author, 'jellyfish')
        if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
            giveuseritem(inv, author, 'jellyfish', count = 1)
            text = " You caught 2 jellyfish with help from your fishing rod!"
            if random.random() < 0.1:
                giveuseritem(inv, author, 'rod', count = -1)
                text += " BUT your fishing rod broke."
            
            embed.add_field(name = rj, value = text)
            return embed
        else:

            embed.add_field(name = rj, value = " You caught a jellyfish!")
            return embed

    elif r < 0.6:
        plastic = int(random.random()*20+1)
        giveuseritem(inv,author,"plastic",plastic)
        embed.add_field(name = rj, value = "You saw some seagulls flying over the vast, open ocean and tried waving to them. To your **tremendous surprise**, they responded to your greeting by swooping in and giving you "+str(plastic)+" pieces of junk plastic.")
        return embed
        
    elif r < 0.99:
        embed.add_field(name = rj, value = "You saw some seagulls flying over the vast, open ocean and tried waving to them. They didn't wave back.")
        return embed
    else:
        giveuseritem(inv, author, "sailboat",-1)
        giveuseritem(inv, author, "damaged sailboat",1)
        embed.add_field(name = rj, value = "**Your sailboat was damaged**. \n\n It's now a damaged boat. Obtain another sail, and run -craft sailboat to get your sailboat up and running again.")
        
        return embed
def steamboat(embed, author, commandInfo):
    s = ""
    rj = author.name+"'s steamboat journey"
    if (not str(author.id) in inv) or (not 'steamboat' in inv[str(author.id)]) or inv[str(author.id)]['steamboat'] < 1:
        embed.add_field(name = "No steamboat?", value = "Guess one can say that you ran out of *steam*.")
        
        return embed
    r = random.random()
    #r = commandInfo['number']/100 # for testing purposes
    boattypes = ["raft","canoe","sailboat","steamboat","battleship","carrier","cruiseship"]
    cantlose = boattypes
    cantlose.append("bodyguard")
    cantlose.append("hitman")
    cantlose.append("cannon")
    cantlose.append("magnet")
    print(cantlose)
    if random.random() < 0.1:
        u = inv[str(author.id)]
        t = "raft"
        count = 0
        if "zipper" in u and u['zipper'] > 0:
            if random.random() < 0.15:
                giveuseritem(inv,author,'zipper',count=-1)
                embed.add_field(name = rj, value = "**Your zipper broke** from the insane pressure the bulge of your inventory put on it")
                return embed
            else:
                embed.add_field(name = rj, value = "The winds were huge and your boat swayed side to side. Thankfully, your zipper made sure nothing was lost.")
                return embed
        
        while ((t in cantlose) or u[t] == 0):
            t = random.sample(u.keys(),1)[0]
            count += 1
            if (count > 300):
                break
        if count > 300:
            embed.add_field(name = rj, value = "You're so broke that even though the winds were huge and your boat swayed side to side, nothing was lost. You got lucky, basically.")
        
            return embed
        num = int(1+u[t]*0.1)
        giveuseritem(inv,author,t,count=num)
        if num == 1:
            plural = ""
        else:
            plural = "s"
        embed.add_field(name = rj, value = "The winds were huge and your boat swayed side to side. As a result, "+str(num)+" "+t+plural+" fell out and were lost. You only have "+str(u[t])+" left. Sucks to be you!")
        return embed
    if r < 0.5:
        ptvalue = random.random()*10
        if r < 0.1:
            ptvalue = random.random()*100
        pointdb.update({str(author.id):pointdb[str(author.id)]+ptvalue})
        embed.add_field(name = rj, value = "You found "+str(ptvalue)+" points floating through the sea!.")
        return embed
    elif r < 0.55:
        if "magnet" in inv[str(author.id)] and inv[str(author.id)]['magnet'] > 0 and random.random() > 0.25:
            giveuseritem(inv, author, 'metal', count = 30)
            embed.add_field(name = rj, value = " Your magnet attracted 30 pieces of metal! Gather 1000 of them to build a battleship!")
            return embed
        giveuseritem(inv, author, 'metal', count = 10)
        embed.add_field(name = rj, value = " You acquired 10 pieces of metal! Gather 1000 of them to build a battleship!")
        return embed
    elif r < 0.6:
        plastic = int(random.random()*20+1)
        giveuseritem(inv,author,"plastic",plastic)
        embed.add_field(name = rj, value = "You saw a turtle entangled in some kind of plastic wrapper. Out of the kindness of your heart, you free him from the plastic. To your **incredible disbelief**, he thanks you by bringing "+str(plastic)+" pieces of plastic to you.")
        return embed
    elif r < 0.625:
        giveuseritem(inv, author, 'log', count = 1)
        embed.add_field(name = rj, value = " You acquired 1 log!")
        return embed
    elif r < 0.655:
        giveuseritem(inv, author, 'cod')
        if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
            giveuseritem(inv, author, 'cod', count = 2)
            text = " You caught 3 cod with help from your fishing rod!"
            if random.random() < 0.1:
                giveuseritem(inv, author, 'rod', count = -1)
                text += " BUT your fishing rod broke."
            
            embed.add_field(name = rj, value = text)
            return embed
        else:
            
            embed.add_field(name = rj, value = " You caught a cod!")
            return embed
    elif r < 0.685:
        giveuseritem(inv, author, 'salmon')
        if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
            giveuseritem(inv, author, 'salmon', count = 1)
            text = " You caught 2 salmon with help from your fishing rod!"
            if random.random() < 0.1:
                giveuseritem(inv, author, 'rod', count = -1)
                text += " BUT your fishing rod broke."
            
            embed.add_field(name = rj, value = text)
            return embed
        else:
            embed.add_field(name = rj, value = " You caught a salmon!")
            return embed
    elif r < 0.7:
        giveuseritem(inv, author, 'jellyfish')
        if 'rod' in inv[str(author.id)] and inv[str(author.id)]['rod'] > 0:
            giveuseritem(inv, author, 'jellyfish', count = 1)
            text = " You caught 2 jellyfish with help from your fishing rod!"
            if random.random() < 0.1:
                giveuseritem(inv, author, 'rod', count = -1)
                text += " BUT your fishing rod broke."
            embed.add_field(name = rj, value = text)
            return embed
        else:
            embed.add_field(name = rj, value = " You caught a jellyfish!")
            return embed
    else:
        embed.add_field(name = rj, value = "Nothing happened. You didn't even see any seagulls to wave to.")
        return embed
        
        
        
        
def techtree(embed, author, commandInfo):
    boattypes = ["raft","canoe","sailboat","steamboat","battleship",'carrier']
    tree = dict()
    for b in boattypes:
        tree.update({b:[]})
    highest = dict()
    for user, inven in inv.items():
        for b in boattypes:
            if b in inven:
                highest.update({user:b})
    for user, hightype in highest.items():
        tree[hightype].append(user)
    print(tree)
    for i in range (len(boattypes)-1, -1,-1):
        count = 0
        s = ""
        for userid in tree[boattypes[i]]:
            count += 1
            if (count < 15):
                s += "<@"+userid+">\n"
        if count >= 15:
            s += "And more!"
        embed.add_field(name = boattypes[i], value = s, inline = False)
    return embed
                    
        
            
def buy(embed, author, commandInfo):

    s = ""
    topurchase = None
    
    for item in commandInfo['message'].split(" "):
        if item in shop.keys():
            topurchase = item
        if item == 'seagull':
            topurchase = 'fried seagull'
        if len(item) > 1 and item[-1] == 's' and item[:-1] in shop.keys():
            topurchase = item[:-1]
    amount = commandInfo['number']
    if not topurchase == None:
        price = amount * shop[topurchase]
        bal = pointdb[str(author.id)]
        if bal >= price-0.00001:
            if amount < 0:
                mi = max(pointdb[str(author.id)]-1,0)
                pointdb.update({str(author.id):mi})
                return "Stop trying to cheat. You have been deducted 1 point as a penalty"
            print("buy successful")
            #buy successful
            if not str(author.id) in inv:
                inv.update({str(author.id):dict()})
            if not topurchase in inv[str(author.id)]:
                inv[str(author.id)].update({topurchase:0})
            inv[str(author.id)].update({topurchase:inv[str(author.id)][topurchase]+amount})
            pointdb.update({str(author.id):pointdb[str(author.id)]-price})
            x = open("points.json",'w')
            x.write(json.dumps(pointdb))
            x.close()
            embed.add_field(name = "Purchased "+str(amount)+" "+str(topurchase)+" for a total price of "+str(price), value = "You now have "+str(inv[str(author.id)][topurchase])+" of this item.")
            return embed
        else:
            embed.add_field(name = "You're broke", value = "You need "+str(round(price-bal,3))+" more points to do this.")
            return embed
    embed.add_field(name = "Canoes and sailboats can't be bought. Buy a raft, and work your way up to them", value = "You think you can just waltz in and get a luxury item? You start with nothing. NOTHING. Your only refuge at first should be a piece of wood floating in the ocean. Anything good takes work. WORK!!!! Go on your raft and begin your journey, because economic privilege has to be earned, not given, this is the way the social hierarchy functions...")
    return embed
def sell(embed, author, commandInfo):
    
    s = ""
    topurchase = None
    
    for item in commandInfo['message'].split(" "):
        if item in shop.keys():
            topurchase = item
        if item == "seagull":
            topurchase ="fried seagull"
        if len(item) > 1 and item[-1] == 's' and item[:-1] in shop.keys():
            topurchase = item[:-1]
    amount = commandInfo['number']
    if not topurchase == None:
        price = amount * shop[topurchase]*0.5
        curowned = 0
        if str(author.id) in inv:
            if topurchase in inv[str(author.id)]:
                curowned = inv[str(author.id)][topurchase]
        bal = pointdb[str(author.id)]
        if curowned >= amount:
            if amount < 0:
                mi = max(pointdb[str(author.id)]-1,0)
                pointdb.update({str(author.id):mi})
                return "Stop trying to cheat. You have been deducted 1 point as a penalty"
            print("sell successful")
            #buy successful
            inv[str(author.id)].update({topurchase:inv[str(author.id)][topurchase]-amount})
            pointdb.update({str(author.id):pointdb[str(author.id)]+price})
            x = open("points.json",'w')
            x.write(json.dumps(pointdb))
            x.close()
            embed.add_field(name = "Sold "+str(amount)+" "+str(topurchase)+" for a total price of "+str(price), value = "Sell prices are half of buy prices for all buyable items. You now have "+str(inv[str(author.id)][topurchase])+" of this item.")
            return embed
        else:
            embed.add_field(name = "You're broke", value = "You need "+str(round(price-bal,3))+" more points to do this.")
            return embed
    embed.add_field(name = "can't sell", value = "You think you can force people ot buy something? To convert something into money against their will? There is an idea of voluntary exchange at the underpinning of our economic system. If our transactions are not mutually agreed upon, this is a violation of fundamental democratic principles of egality and fairness....")
    
    return embed
def use(embed, author, commandInfo):
    text = commandInfo['message'].split(" ")[1]
    if text in shop:
        unusable = ['raft','canoe','log','nail','bodyguard','plastic']
        if text in unusable:
            embed.add_field(name = "You can't use this item", value = "Chances are, you tried to use a form of water transportation. Just call its associated command instead.")
            return embed
        if not str(author.id) in inv:
            embed.add_field(name = "Note: you don't have an inventory at all", value = "do -shop to see what's available")
            return embed
        if (not text in inv[str(author.id)]) or inv[str(author.id)][text] <=0:
            embed.add_field(name = "Note: you don't have a "+text, value = "do -buy "+text)
            return embed
        
        if text == 'note':
            if len(commandInfo['message'].split(" ")) < 4:
                embed.add_field(name = "Not enough things.", value = "Must provide a user to secretly send to, and the message itself")
                return embed
            try:
                tosend = int(commandInfo['message'].split(" ")[2].replace("<","").replace("!","").replace("@","").replace(">",""))
            except ValueError:
                embed.add_field(name = "Not a valid user.", value = "the thing after -use note should be a ping or user id")
                return embed
            u = commandInfo['guild'].get_member(tosend)
            if u is None:
                embed.add_field(name = "Not a valid user.", value = "the thing after -use note should be a ping or user id of someone IN THE SERVER!!!!!")
                return embed
            msg =  " ".join(commandInfo['message'].split(" ")[3:])
            inv[str(author.id)].update({text:inv[str(author.id)][text]-1})
            return ((u,msg))
        if text == 'cookie':
            inv[str(author.id)].update({text:inv[str(author.id)][text]-1})
            embed.add_field(name = "You ate a cookie.", value = "The soft, creamy, delicious cookie gave you a tremendous sense of satisfaction.")
            return embed
        if text == 'giftbox':
            if len(commandInfo['message'].split(" ")) < 4:
                embed.add_field(name = "Not enough things.", value = "Must provide a user to give to, and the gift itself, and optionally a quantity")
                return embed
            try:
                tosend = int(commandInfo['message'].split(" ")[2].replace("<","").replace("!","").replace("@","").replace(">",""))
            except ValueError:
                embed.add_field(name = "Not a valid user.", value = "the thing after -use note should be a ping or user id")
                return embed
            u = commandInfo['guild'].get_member(tosend)
            if u is None:
                embed.add_field(name = "Not a valid user.", value = "the thing after -use note should be a ping or user id of someone IN THE SERVER!!!!!")
                return embed
            itemtosend = commandInfo['message'].split(" ")[3]
            if (not itemtosend in inv[str(author.id)]):
                embed.add_field(name = "Not a valid item.", value = "You don't have that item!!!!!")
                return embed
            quantity = 1
            if len(commandInfo['message'].split(" ")) > 4:
                try:
                    quantity= int(commandInfo['message'].split(" ")[4])
                except ValueError:
                    quantity = 1
            if inv[str(author.id)][itemtosend] < quantity:
                embed.add_field(name = "You don't have enough of that item.", value = "You have "+str(inv[str(author.id)][itemtosend])+", and tried to send "+str(quantity))
                return embed
            inv[str(author.id)].update({text:inv[str(author.id)][text]-1})
            giveuseritem(inv, author, itemtosend, count = -quantity)
            if not str(u.id) in inv:
                inv.update({str(u.id):dict()})
            giveuseritem(inv, u, itemtosend, count = quantity)
            embed.add_field(name = "Giftbox usage.", value = "You gave <@"+str(u.id)+"> "+str(quantity)+" of the item "+itemtosend+".")
            return embed
        if text == 'cookie':
            inv[str(author.id)].update({text:inv[str(author.id)][text]-1})
            embed.add_field(name = "You ate a cookie.", value = "The soft, creamy, delicious cookie gave you a tremendous sense of satisfaction.")
            return embed
        if text == 'axe':
            inv[str(author.id)].update({text:inv[str(author.id)][text]-1})
            numlogs = 1
            while random.random() < 0.35:
                numlogs += 1
            v = "<@"+str(author.id)+"> obtained "+str(numlogs)+" logs."
            giveuseritem(inv, author, 'log',numlogs)
            embed.add_field(name = "Axe usage", value = v)
            return embed
        if text == 'hitman':
            if len(commandInfo['message'].split(" ")) < 3:
                embed.add_field(name = "Not enough things.", value = "Must provide a user to use the hitman on")
                return embed
            try:
                tosend = int(commandInfo['message'].split(" ")[2].replace("<","").replace("!","").replace("@","").replace(">",""))
            except ValueError:
                embed.add_field(name = "Not a valid user.", value = "the thing after -use note should be a ping or user id")
                return embed
            u = commandInfo['guild'].get_member(tosend)
            if u is None:
                embed.add_field(name = "Not a valid user.", value = "the thing after -use note should be a ping or user id of someone IN THE SERVER!!!!!")
                return embed
            inv[str(author.id)].update({text:inv[str(author.id)][text]-1})
            if random.random() < 0.2:
                if (not str(u.id) in inv) or (not 'bodyguard' in inv[str(u.id)]) or (inv[str(u.id)]['bodyguard'] < 1):
                    points = pointdb[str(u.id)]*0.5
                    pointdb.update({str(u.id):pointdb[str(u.id)]*0.5})
                    pointdb.update({str(author.id):pointdb[str(author.id)]+points})
                    # Hitman successful
                    embed.add_field(name = author.name+"'s hitman was successful.", value = "You got'em! The hitman successfully incapacitated "+u.name+" and forced him to give you "+str(points) +" in monetary value.")
                    return embed
                else:
                    if random.random() < 0.25:
                        giveuseritem(inv,u,'bodyguard',-1)
                        return "The bodyguard of <@"+str(u.id)+"> took effect, preventing an otherwise successful hitman from stealing any money by shooting him dead at the spot. The bodyguard, unfortunately, **died valiantly in the process**. At least this meant <@"+str(author.id)+"> didn't pay any fine for this illegal transgression."
                    else:
                        return "The bodyguard of <@"+str(u.id)+"> took effect, preventing an otherwise successful hitman from stealing any money by shooting him dead at the spot. The bodyguard, meanwhile, survived. At least this meant <@"+str(author.id)+"> didn't pay any fine for this illegal transgression."

            else:
                fine = pointdb[str(author.id)]*0.1
                pointdb.update({str(author.id):pointdb[str(author.id)]*0.9})
                embed.add_field(name = author.name+"'s hitman was unsuccessful.", value = "You had to pay a fine of 10% your net worth to the government for attempting this illegal activity. You got fined "+str(fine)+" points.")
                return embed
    else:
        embed.add_field(name = "Nothing was used", value = "The thing you tried to use can't be used. If it is some kind of boat, just do -raft, -canoe, or similar.")
        return embed
            
            
                
            
            
    
