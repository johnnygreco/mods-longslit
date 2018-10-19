from __future__ import print_function

import os
from pyraf import iraf
from . import calipath, outpath


__all__ = ['identify', 'reidentify']


def _check_working_dir(data_path):
    print(data_path)
    if data_path is None:
        os.chdir(outpath)
    else:
        os.chdir(data_path)


def identify(arc_fn, arc_lamp, mods_channel, data_path=None, params={}):
    """
    Run iraf identify to find and label lines in arc lamp for 
    wavelength solution. This one needs to be done by hand :( 

    Parameters
    ----------
    arc_fn : str
        The arc lamp fits file name
    arc_lamp : str
        The arc lamp
    mods_channel : str
        MODS red or blue channel
    data_path : str
        Directory that contains the data.
    params : dict
        Iraf identify parameters
    """

    _check_working_dir(data_path)

    line_list = os.path.join(
        calipath, 'line_lists/{}_{}.wav'.format(arc_lamp, mods_channel))
    database_path = os.path.join(outpath, 'database')

    iraf.unlearn('identify')
    iraf.identify.units = 'angstrom'
    iraf.identify.nsum = params.pop('nsum', 30)
    iraf.identify.function = params.pop('function', 'chebyshev')
    iraf.identify.order = params.pop('order', 4)
    iraf.identify.cradius = params.pop('cradius', 5)
    iraf.identify.database = params.pop('database', database_path)
    iraf.identify(images=arc_fn, coordlist=line_list)


def reidentify(ref_fn, img_fn, arc_lamp, mods_channel, data_path=None, 
               params={}):
    """
    Run iraf reidentify to trace identified lines along the spatial axis. 

    Parameters
    ----------
    ref_fn : str
        Reference image file name.
    img_fn : str
        Image(s) to be reidentified.
    arc_lamp : str
        The arc lamp
    mods_channel : str
        MODS red or blue channel
    data_path : str
        Directory that contains the data.
    params : dict
        Iraf redidentify parameters.
    """

    _check_working_dir(data_path)

    line_list = os.path.join(
        calipath, 'line_lists/{}_{}.wav'.format(arc_lamp, mods_channel))

    iraf.unlearn('reidentify')
    iraf.reidentify.interactive = params.pop('interactive', 'no')
    iraf.reidentify.newaps = params.pop('newaps', 'yes')
    iraf.reidentify.refit = params.pop('refit', 'yes')
    iraf.reidentify.override = params.pop('override', 'no')
    iraf.reidentify.nlost = params.pop('nlost', 5)
    iraf.reidentify.verbose = params.pop('verbose', 'yes')
    iraf.reidentify.coordlist = line_list
    iraf.reidentify(reference=ref_fn, images=img_fn)
