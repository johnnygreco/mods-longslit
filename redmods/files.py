from collections import namedtuple

SourceFiles = namedtuple('SourceFiles', 'red blue')

flats = SourceFiles(
    red=['mods1r.20180916.000[1-5].fits'], 
    blue=['mods1b.20180916.000[1-5].fits', 'mods1b.20180916.000[6-8].fits']
    # Slitless Dual VFlat 5 Clear, Slitless Dual VFlat 10.0 + UG5
)

arcs = SourceFiles(
    red=['mods1r.20180916.0010.fits', 
         'mods1r.20180916.0011.fits', 
         'mods1r.20180916.0012.fits'], 
    blue=['mods1b.20180916.0010.fits', 
          'mods1b.20180916.0011.fits', 
          'mods1b.20180916.0012.fits']
)


# Feige 110 dual grating
Feige110 = SourceFiles(
    red=['mods1r.20180916.0021.fits', 
         'mods1r.20180916.0022.fits', 
         'mods1r.20180916.0023.fits'],
    blue=['mods1b.20180916.0016.fits',
          'mods1b.20180916.0017.fits',
          'mods1b.20180916.0018.fits']
)


G196 = SourceFiles(
    red=[#'mods1r.20180916.0045.fits', something is up with these frames
         #'mods1r.20180916.0046.fits', 
         'mods1r.20180917.0004.fits',
         'mods1r.20180917.0005.fits', 
         'mods1r.20180917.0006.fits'],
    blue=[#'mods1b.20180916.0028.fits', 
          #'mods1b.20180916.0029.fits', 
          'mods1b.20180917.0001.fits',
          'mods1b.20180917.0002.fits', 
          'mods1b.20180917.0003.fits']
)

G191 = SourceFiles(
    red=['mods1r.20180916.0039.fits',
         'mods1r.20180916.0040.fits',
         'mods1r.20180916.0041.fits'],
    blue=['mods1b.20180916.0025.fits',
          'mods1b.20180916.0026.fits',
          'mods1b.20180916.0027.fits']
)

sources = dict(G196=G196, G191=G191)
standards = dict(Feige110=Feige110)
