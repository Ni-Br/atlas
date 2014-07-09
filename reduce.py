import sys
from pyraf import iraf

def reduceBias(biasListFilename, masterBiasFilename):
    iraf.imcombine("@" + biasListFilename, output=masterBiasFilename, logfile="STDOUT", weight="none", zero="none", reject="crreject", combine="median", scale="none")


if __name__ == "__main__":
    print(sys.argv[1])
    print(sys.argv[2])
    reduceBias(sys.argv[1], sys.argv[2])
    


