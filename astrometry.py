import logging
import subprocess
import os
import sys
import fnmatch

if __name__ == "__main__":
    root = sys.argv[1]
    source = "atlas_1/light/"
    dest = "atlas_2/"
    bfns = [os.path.splitext(os.path.relpath(os.path.join(dirpath, f), root + "atlas_1/light/"))[0]
            for dirpath, dirnames, files in os.walk(root + "atlas_1/light/")
                for f in fnmatch.filter(files, "*.fits")]
    bfns.sort()


    for bfn in bfns:
        print(bfn)
        sys.stdout.flush()
        outputDir = os.path.dirname(bfn)
        try:
            cmd = "solve-field " + root + "atlas_1/light/" + bfn + ".fits --no-plots --scale-units arcminwidth --scale-low 20 --scale-high 22 --continue --parity neg --no-tweak --depth 15,30,45,60 --cpulimit 30 -D " + root + dest + " --new-fits " + root + dest + bfn + ".fits --wcs " + root + dest + bfn + ".wcs --solved " + root + dest + bfn + ".solved --rdls " + root + dest + bfn + ".rdls"
        except e:
            print(e)
        process = subprocess.Popen(cmd.split(" "))
        process.communicate()
        cmd = 'wcsinfo ' + root + bfn + ',wcs | grep "\(ra_center \)\|\(dec_center \)" > ' + root + bfn + '.center'
        process = subprocess.Popen(cmd, shell=True)
        process.communicate()
