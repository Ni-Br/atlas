atlas
=====

Automatic Transit Lightcurve Analysis System

Work very much in beta. Dependencies are not fully graphed and some parts may or may not work because of that. It has worked successfully many times before.

This pipeline is divided into several smaller steps, allowing refactoring for purpooses entirely different from exoplanet lightcurves.

Phase 0
=======

Getting all the data gathered by one instrument into a single folder, not covered by atlas

Phase 1
=======
Going through the files and preparing them to be reduced

Phase 2
=======
Reducing the light frames using the files established during Phase 1

Phase 3
=======
Preparing the files from photometry. This means: finding the frames containing (at least 1) object of interest and establishing a run and finding comparison stars.

Phase 4
=======
Running photometry, using a procedure established during Phase 3

Phase 5 (optional)
=======
Putting the data in a nice human-readable format.
