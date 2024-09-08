import json
import random
commandsRaw = {}
commandAliases = {
    "r": "ratings",
    "s": "stats",
    "b": "bio",
    "setgm": "addgm",
    'phs':'hstats',
    'phstats':'hstats',
    "ts": "tstats",
    "tsp": 'ptstats',
    "rs": "resignings",
    "runrs": "runresignings",
    "ppr":"playoffpredict",
    "cs": "cstats",
    "hs": "hstats",
    'updateexport': 'updatexport',
    'update':'updatexport',
    "balance":"bal",
    "gl":"globalleaders",
    "l":"pleaders",
    'lp':'lotterypool',
    'mostuniform':'mostaverage',
    'inv':'inventory'
}
iscrowded = False

with open('servers.json') as f:
    serversList = json.load(f)
    serversList['default'].update({'rfa':False})
    serversList['default'].update({'tuodloh':10000})
    serversList['default'].update({'rfamultiplier':1.25})
    serversList['default'].update({'idiosyncratic':0.0})

with open('books.json') as f:
    bibleBooks = json.load(f)
with open('verses.json') as f:
    bibleVerses = json.load(f)
with open('points.json') as f:
    points = json.load(f)
with open('daily.json') as f:
    daily = json.load(f) #daily is a list
with open('inventory.json') as f:
    inv = json.load(f)
serverExports = {}
trivias = dict()
triviabl = dict()

bot = None

def getadjective():
    adjlist = ['merrily','blissfully','stupidly','gladly','lazily','resignedly','reluctantly','calmly','smartly','affectionately','casually','haphazardly','accidentally','hastily','excitedly','normally','wishfully','hesitantly','sorrowfully','allegedly']
    adjlist += ['opportunistically','strategically','carefully','boldly','rashly','shrewdly']

    return random.sample(adjlist,1)[0]

embedFooter = 'Coded by ClevelandFan#2909 - Redistributed by Illusion'
