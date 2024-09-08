import commands
import os
import json
import random
from datetime import datetime
if not "tracking.json" in os.listdir():
    f = open("tracking.json",'w')
    f.write("{}")
    f.close()
f = open("tracking.json")
for line in f:
    tracks = json.loads(line)
f.close()
async def budubudu(command,text, message):
    
    
    await commands.commands[command](text, message)

    today = datetime.today().strftime('%Y-%m-%d')
    if not str(message.guild.id) in tracks:
        tracks.update({str(message.guild.id):dict()})
    servertracks = tracks[str(message.guild.id)]
    if not today in servertracks:
        servertracks.update({today:dict()})
    daytracks = servertracks[today]
    if not str(message.author.id) in daytracks:
        daytracks.update({str(message.author.id):dict()})
    usertracks = daytracks[str(message.author.id)]
    if not command in usertracks:
        usertracks.update({command:1})
    else:
        usertracks.update({command:usertracks[command]+1})
    if random.random() < 0.99999:
        os.rename("tracking.json","tracking_backup.json")
        f = open("tracking.json","w")
        f.write(json.dumps(tracks))
        f.close()
                
