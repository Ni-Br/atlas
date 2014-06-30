import argparse

parser = argparse.ArgumentParser()
parser.add_argument("dir", default=".", help="Search for images in specified directory")
parser.add_argument("-s", "--summary", default=".atlas_0.sum", help="Specifies location of for the summary of all decisions made, default is dir/atlas_0.sum")
parser.add_argument("-t", "--temp", default="atlas_0/", help="Specifies the directory in which files sent to atlas_1 will be stored")
parser.add_argument("-v", "--verbose", action="store_true", help="Outputs contents of log to stdout as well as to the log file")
parser.add_argument("--log-level", type=int, default=3, help="Sets the level of logging that is recorded: 0=error, 1=warning, 2=information, 3=debug, 4=verbose. It is impossible to set it below 0.")

args = parser.parse_args()

global pwd
global logLevel
global tempDir
global verbose
global summary
pwd = args.dir
logLevel = args.log_level
tempDir = args.temp
verbose = args.verbose
summary = args.summary
