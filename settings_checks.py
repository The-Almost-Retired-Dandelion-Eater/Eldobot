#settings dict

def prefix(input):
    if len(input) > 1:
        return False
    else:
        return True

def positive_int(input):
    try:
        input = int(input)
        if input > 0:
            return True
        else:
            return False
    except: return False

def percents(input):
    try:
        input = float(input)
        input = input/100
        if input >= 0:
            return True
        else: return False
    except: return False

def onoff(input):
    acceptable = ['on', 'off']
    if str.lower(input) in acceptable:
        return True
    else:
        return False

def numbers(input):
    try:
        input = float(input)
        return True
    except: return False

def channel(input):
    if input.startswith('<#') and input.endswith('>') and input[2:-1].isdigit():
        return True
    else:
        return False

def numberlist(input):
    input = input.split(',')
    valid = True
    for i in input:
        try: 
            i = int(i)
            if i < 0:
                valid = False
        except: valid=False
    return valid

