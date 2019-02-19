from collections import namedtuple
SourceFiles = namedtuple('SourceFiles', 'red blue')


flats = SourceFiles(
    # Slitless Dual VFlat 5 ND1.5
    red=['mods1r.20180916.000[1-5].fits'], 
    # Slitless Dual VFlat 5 Clear, Slitless Dual VFlat 5 ND1.5
    blue=['mods1b.20180916.000[1-5].fits', 'mods1b.20180916.000[6-8].fits']
)

flats_2 = SourceFiles(
    # VFLAT + Clear + ND1.5 Spectral Flat
    red=['mods1r.20180915.005[3-7].fits'], 
    # VFLAT + Clear + ND1.5 Spectral Flat, VFLAT + UG5 Spectral Flat
    blue=['mods1b.20180915.004[3-7].fits', 'mods1b.20180915.004[8-9].fits']
)

bias = SourceFiles(
    red='mods1r.20180915.000[1-5].fits',
    blue='mods1b.20180915.000[1-5].fits'
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


# GD71 dual grating
GD71 = SourceFiles(
    red=['mods1r.20180916.0056.fits',
         'mods1r.20180916.0057.fits',
         'mods1r.20180916.0058.fits'],
    blue=['mods1b.20180916.0030.fits',
          'mods1b.20180916.0031.fits', 
          'mods1b.20180916.0032.fits']
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

G156 = SourceFiles(
    red=[],
    blue=['mods1b.20180916.0019.fits',
          'mods1b.20180916.0020.fits']
)

sources = dict(G196=G196, G191=G191, G156=G156)
standards = dict(Feige110=Feige110, GD71=GD71)
