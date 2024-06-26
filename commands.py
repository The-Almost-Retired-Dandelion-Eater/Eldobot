import settings
import settings_checks as sc
import players
import basics
import moderators
import free_agency
import league
import draft
import draft_runner
import roster
import teams
import points
import help


commandsRaw = {
    "settings": 'settings',
    'playoffpredict':'league',
    'specialists':'league',
    'mostaverage':'league',
    'shots':'players',
    'draftorder':'league',
    'pshots':'players',
    'progspredict':'players',
    'penalty':'team',
    'standings':'league',
    "edit": 'settings',
    'playoffs':'league',
    'proster':'team',
    'progster':'team',
    'hint':'players',
    "load": 'load_export',
    'nickname':'roster',
    'wiigeneral':'points',
    'pcompare':'players',
    'pratings':'players',
    "stats": 'players',
    "bio": 'players',
    "ratings": 'players',
    'deleterule':'fa',
    'acceptto':'roster',
    "addgm": 'mods',
    'to':'league',
    "teamlist": 'mods',
    "removegm": 'mods',
    "assigngm": 'mods',
    "offer": 'fa',
    "bulkoffer": 'fa',
    "offers": 'fa',
    "deloffer": 'fa',
    "clearoffers": 'fa',
    "move": 'fa',
    "clearalloffers": 'fa',
    'addrule':'fa',
    'contractrules':'fa',
    'decidepo':'fa',
    "tosign": 'fa',
    'runfa': 'fa',
    'qo':'fa',
    'fa': 'league',
    'board': 'draft',
    'add': 'draft',
    'dmove': 'draft',
    'po':'league',
    'remove': 'draft',
    'clearboard': 'draft',
    'auto': 'draft',
    'startdraft': 'startdraft',
    'pick': 'draft',
    'draft': 'league',
    'shared':'points',
    'roster': 'team',
    'reprog':'league',
    'stripnames':'league',
    'resetgamestrade':'fa',
    'sroster': 'team',
    'psroster': 'team',
    'lineup': 'team',
    'lmove': 'roster',
    'pt': 'roster',
    'topall':'league',
    'padv':'players',
    'autosort': 'roster',
    'resetpt': 'roster',
    'changepos': 'roster',
    'picks': 'team',
    'ownspicks': 'team',
    'history': 'team',
    'finances': 'team',
    'seasons': 'team',
    'tstats': 'team',
    'sos': 'team',
    'schedule': 'team',
    'gamelog': 'team',
    'ptstats': 'team',
    'game': 'team',
    'boxscore': 'team',
    'resignings': 'fa',
    'runresignings': 'fa',
    'pr': 'league',
    'matchups': 'league',
    'top': 'league',
    'injuries': 'league',
    'deaths': 'league',
    'leaders': 'league',
    'summary': 'league',
    'adv': 'players',
    'progs': 'players',
    'hstats': 'players',
    'cstats': 'players',
    'match':'fa',
    'pstats': 'players',
    'awards': 'players',
    'pgamelog': 'players',
    'compare': 'players',
    'release': 'roster',
    'autocut': 'roster',
    'pausedraft': 'draft',
    'updatexport': 'updatexport',
    'help': 'help',
    'bulkadd': 'draft',
    'bal':'points',
    'pleaders':'points',
    'flip':'points',
    'rob':'points',
    'daily':'points',
    'resetdaily':'points',
    'globalleaders':'points',
    'lottery':'points',
    'mostunbalanced':'league',
    'pickvalue':'league',
    'lotterypool':'points',
    'chatgpt':'points',
    'proggraph':'players',
    'give':'points',
    'echo':'points',
    'trivia':'players',
    'capspace':'team',
    'rostergraph':'team',
    'rgoptions':'team',
    'leaguegraph':'league',
    'lgoptions':'league'
}
commandTypes = {
    'players': players.process_text,
    'settings': settings.process_text,
    'load_export': basics.load_export,
    'mods': moderators.process_text,
    'fa': free_agency.process_text,
    'league': league.process_text,
    'draft': draft.process_text,
    'startdraft': draft_runner.run_draft,
    'roster': roster.process_text,
    'team': teams.process_text,
    'updatexport': basics.update_export,
    'help': help.process_text,
    'points': points.process_text
}
commands = {}

for c, v in commandsRaw.items():
    commands[c] = commandTypes[v]


settingsDirectory = {
    "prefix": sc.prefix,
    "holdout": sc.percents,
    "tuodloh": sc.percents,
    "maxroster": sc.positive_int,
    "birdrights": sc.onoff,
    "rookiescount": sc.onoff,

    "options": sc.onoff,
    "openmarket": sc.onoff,
    "threeyearrule": sc.onoff,
    "winning": sc.numbers,
    "fame": sc.numbers,
    "loyalty": sc.numbers,
    "money": sc.numbers,
    "fachannel": sc.channel,
    "tradechannel": sc.channel,
    "tradeannouncechannel": sc.channel,
    "tradeback": sc.onoff,
    "tradefa": sc.nonnegative_int,
    "hardcap": sc.numbers,
    "draftclock": sc.numberlist,
    "draftchannel": sc.channel,
    "lineupovrlimit": sc.positive_int,
    'rfa':sc.onoff,
    'rfamultiplier':sc.numbers,
    "maxptmod": sc.positive_int,
    "maxptlimit": sc.numbers,
    "minptlimit": sc.numbers,
    "allowzero": sc.positive_int,
    "releasechannel": sc.channel,
    'maxovrrelease': sc.positive_int
}

