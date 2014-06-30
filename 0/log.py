import args

#TODO Change logFile to actually mean the file
def prep( pre, message):
    print("["+pre+"] "+message)

def wtf( message):
    prep("WTF?", message)

def e( message):
    prep("E", message)

def w( message):
    if args.logLevel > 0:
        prep("W", message)

def i( message):
    if args.logLevel > 1:
        prep("I", message)

def d( message):
    if args.logLevel > 2:
        prep("D", message)

def v( message):
    if args.logLevel > 3:
        prep("V", message)
