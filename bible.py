import shared_info
import random
from io import BytesIO
import discord
bibleBooks = shared_info.bibleBooks
bibleVerses = shared_info.bibleVerses

def range_converter(s):
    # Split the input string by "-"
    start, end = map(int, s.split('-'))
    # Return the list of integers from start to end (inclusive)
    return list(range(start, end + 1))

async def get_verse(input, message, bookName):
    if not ':' in input:
        return None
    bookNames = ['Joshua', '1 Samuel', '2 Samuel', '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Psalm', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Ezekiel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Micah', 'Jonah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi']
    alternateNames = {
        "joshua": 'Josue',
        "1 samuel": '1 Kings',
        "2 samuel": '2 Kings',
        '1 kings': '3 Kings',
        '2 kings': '4 Kings',
        "1 chronicles": '1 Paralipomenon',
        '2 chronicles': '2 Paralipomenon',
        'ezra': '1 Esdras',
        "nehamiah": '2 Esdras',
        "tobit": "Tobias",
        "psalm": "Psalms",
        "song of solomon": "Canticle of Canticles",
        "sirach": "Ecclesiasticus",
        'isaiah': "Isaias",
        "jeremiah": "Jeremias",
        "zzekiel": "Ezechiel",
        "hosea": "Osee",
        "obadiah": "Abdias",
        "micah": "Micheas",
        'habakkuk': "Habacuc",
        "zephaniah": "Sophonias",
        "haggai": "Aggeus",
        "zechariah": "Zacharias",
        "malachi": "Malachias",
        "1 maccabees": "1 Machabees",
        "2 maccabees": "2 Machabees",
        "revelation": "Apocalypse"
        }
    if str.lower(bookName) in alternateNames:
        bookName = alternateNames[str.lower(bookName)]
    input = input.split(' ')
    for i in input:
        if ':' in i:
            i = i.split(':')
            chapter = i[0]
            verse = i[1]

    if '-' in verse:
        verses = range_converter(verse)
    else:
        verses = [int(verse)]
    
    
    for book in bibleBooks:
        if str.lower(book['shortname']) == str.lower(bookName):
            bookNumber = book['booknumber']
            chapters = book['chapters']
            for c in chapters:
                if c['chapternumber'] == int(chapter):
                    titleLine = f"{c['chaptername']}"
                    try: descrip = f"*{c['chapterdesc']}*"
                    except: descrip = '*No chapter heading.*'
    
    notes = ""

    lines = []
    for v in bibleVerses:
        if v['booknumber'] == int(bookNumber) and v['chapternumber'] == int(chapter) and v['versenumber'] in verses:
            lines.append(f"{v['text']}")
            if 'notes' in v:
                notes += f"**{v['versenumber']}:** *{v['notes'][0]}* \n"
    

    embed = discord.Embed(title=titleLine, description=descrip)

    numDivs, rem = divmod(len(lines), 5)
    numDivs += 1
    for i in range(numDivs):
        newLines = lines[(i*5):((i*5)+5)]
        text = '\n'.join(newLines)
        embed.add_field(name=f"v{verse}", value=text, inline=False)
                          
    if notes != "":
        embed.add_field(name='Notes', value=notes, inline=False)

    await message.channel.send(embed=embed)


    
