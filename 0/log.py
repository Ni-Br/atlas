#TODO Change logFile to actually mean the file
class Log():
    def __init__(self, filename, level, doPrint):
        self.logFile = "" #Do something?
        self.level = level

    def log(self, line):
        #logFile.append(currentTime + line)
        print line

    def prep(self, pre, message):
        self.log("["+pre+"] "+message)


    def wtf(self, message):
        self.prep("WTF?", message)
    
    def e(self, message):
        self.prep("E", message)
    
    def w(self, message):
        if self.level > 0:
            self.prep("W", message)

    def i(self, message):
        if self.level > 1:
            self.prep("I", message)

    def d(self, message):
        if self.level > 2:
            self.prep("D", message)

    def v(self, message):
        if self.level > 3:
            self.prep("V", message)
