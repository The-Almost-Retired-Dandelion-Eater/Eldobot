import json
import random
commandsRaw = {}

iscrowded = False

with open('servers.json') as f:
    serversList = json.load(f)
    serversList['default'].update({'rfa':False})
    serversList['default'].update({'rfamultiplier':1.25})

with open('books.json') as f:
    bibleBooks = json.load(f)
with open('verses.json') as f:
    bibleVerses = json.load(f)
with open('points.json') as f:
    points = json.load(f)
with open('daily.json') as f:
    daily = json.load(f) #daily is a list

serverExports = {}
trivias = dict()
triviabl = dict()

bot = None

def getadjective():
    adjlist = ['merrily','blissfully','stupidly','gladly','lazily','resignedly','reluctantly','calmly','smartly','affectionately','casually','haphazardly','accidentally','hastily','excitedly','normally','wishfully','hesitantly','sorrowfully','allegedly']
    adjlist += ['opportunistically','strategically','carefully','boldly','rashly','shrewdly']

    return random.sample(adjlist,1)[0]

embedFooter = 'Coded by ClevelandFan#2909 - Redistributed by Illusion'
