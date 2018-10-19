import redmods


path = redmods.outpath + '/'

arc_fn = 'blue-AR-arcs.fits' 
arc_lamp = 'argon'
mods_channel = 'blue'

#redmods.identify(
#    path + 'blue-AR-arcs.fits', 'argon', 'blue')


params = dict(override='yes')

redmods.reidentify(
    arc_fn, arc_fn, arc_lamp, mods_channel, params=params)
