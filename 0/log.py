#TODO Change logFile to actually mean the file
def prep( pre, message):
    print("["+pre+"] ".format(message))


def wtf( message):
    prep("WTF?", message)

def e( message):
    prep("E", message)

def w( message):
    if level > 0:
        prep("W", message)

def i( message):
    if level > 1:
        prep("I", message)

def d( message):
    if level > 2:
        prep("D", message)

def v( message):
    if level > 3:
        prep("V", message)
