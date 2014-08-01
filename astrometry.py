import logging
import subprocess
import os
import sys
import fnmatch

if __name__ == "__main__":
    root = sys.argv[1]
    source = "atlas_2/light/"
    dest = "atlas_3/"
    bfns = [os.path.splitext(os.path.relpath(os.path.join(dirpath, f), root + source))[0]
            for dirpath, dirnames, files in os.walk(root + source)
                for f in fnmatch.filter(files, "*.fits")]
    bfns.sort()


    for bfn in bfns:
        print(bfn)
        sys.stdout.flush()
        outputDir = os.path.dirname(bfn)
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        try:
            cmd = "solve-field " + root + source + bfn + ".fits --no-plots --scale-units arcminwidth --scale-low 20 --scale-high 22 --continue --parity neg --no-tweak --depth 15,30,45,60 --cpulimit 30 -D " + root + dest + outputDir
        except e:
            print(e)
        process = subprocess.Popen(cmd.split(" "))
        process.communicate()
        cmd = 'wcsinfo ' + root + dest + bfn + '.wcs | grep "\(ra_center \)\|\(dec_center \)" > ' + root + dest + bfn + '.center'
        process = subprocess.Popen(cmd, shell=True)
        process.communicate()
