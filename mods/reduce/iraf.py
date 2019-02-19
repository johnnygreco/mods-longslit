from __future__ import print_function


import os
from .. import calipath
from .. import logger

try:
    # load necessary iraf packages
    from pyraf import iraf
    iraf.onedspec(_doprint=0)
    iraf.twodspec(_doprint=0)
    iraf.longslit(_doprint=0)
    iraf.apextract(_doprint=0)
except:
    logger.warn('Pyraf not found. Iraf-dependent functions will not work.')

__all__ = ['identify', 'reidentify', 'fitcoords', 'transform', 'background', 
           'extinction', 'apall', 'standard_star', 'calibrate']


def _check_working_dir(data_path):
    if os.getcwd() != os.path.abspath(data_path):
        logger.debug('changing directory to ' + data_path)
        os.chdir(data_path)


def identify(arc_fn, arc_lamp, mods_channel, data_path='.', params={}):
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

    logger.info('running iraf identify')
    iraf.identify.unlearn()
    iraf.identify.units = 'angstrom'
    iraf.identify.nsum = params.pop('nsum', 30)
    iraf.identify.function = params.pop('function', 'chebyshev')
    iraf.identify.order = params.pop('order', 4)
    iraf.identify.cradius = params.pop('cradius', 5)
    iraf.identify.database = params.pop('database', 'database')
    iraf.identify(images=arc_fn, coordlist=line_list)


def reidentify(ref_fn, images, arc_lamp, mods_channel, data_path='.', 
               params={}):
    """
    Run iraf reidentify to trace identified lines along the spatial axis. 

    Parameters
    ----------
    ref_fn : str
        Reference image file name.
    images : str
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

    logger.info('running iraf reidentify')

    iraf.reidentify.unlearn()
    iraf.reidentify.interactive = params.pop('interactive', 'no')
    iraf.reidentify.newaps = params.pop('newaps', 'yes')
    iraf.reidentify.refit = params.pop('refit', 'yes')
    iraf.reidentify.override = params.pop('override', 'no')
    iraf.reidentify.nlost = params.pop('nlost', 5)
    iraf.reidentify.verbose = params.pop('verbose', 'yes')
    iraf.reidentify.coordlist = line_list
    iraf.reidentify(reference=ref_fn, images=images)


def fitcoords(images, data_path='.', params={}):
    """
    Run iraf fitcoords to fit 2D function to wavelength as a function of 
    column and line number. 

    Parameters
    ----------
    images : str
        Image(s) to be reidentified.
    data_path : str
        Directory that contains the data.
    params : dict
        Iraf fitcoords  parameters.
    """

    _check_working_dir(data_path)

    logger.info('running iraf fitcoords')

    iraf.fitcoords.unlearn()
    iraf.fitcoords.function = params.pop('function', 'legendre')
    iraf.fitcoords.xorder = params.pop('xorder', 5)
    iraf.fitcoords.yorder = params.pop('yorder', 3)
    iraf.fitcoords.interactive = params.pop('interactive', 'yes')

    images = images.replace('.fits', '')
    iraf.fitcoords(images=images)


def transform(images, out_images, coord_fits, data_path='.',  params={}):
    """
    Run iraf transform to rectify 2D spectrum.

    Parameters
    ----------
    images : str
        Images to transform.
    out_images : str
        Output image file names.
    coord_fits:
        Name of coordinate fits in database.
    data_path : str
        Directory that contains the data.
    params : dict
        Iraf fitcoords  parameters.
    """

    _check_working_dir(data_path)

    logger.info('running iraf transform')

    iraf.transform.unlearn()
    iraf.transform.x1 = params.pop('x1', 'INDEF')
    iraf.transform.x2 = params.pop('x2', 'INDEF')
    iraf.transform.dx = params.pop('dx', 'INDEF')
    iraf.transform.nx = params.pop('nx', 'INDEF')
    iraf.transform.flux = params.pop('flux', 'yes')
    iraf.transform.interptype = params.pop('interptype', 'linear')

    iraf.transform(input=images, output=out_images, fitnames=coord_fits)


def background(images, out_images, data_path='.',  params={}):
    """
    Run iraf background subtraction.

    Parameters
    ----------
    images : str
        Images to transform.
    out_images : str
        Output image file names.
    data_path : str
        Directory that contains the data.
    params : dict
        Iraf background parameters.
   """ 

    _check_working_dir(data_path)

    logger.info('running iraf background')

    iraf.background.unlearn()
    iraf.background.axis = params.pop('axis', 2)
    iraf.background.function = params.pop('function', 'chebyshev')
    iraf.background.order = params.pop('order', 3)
    iraf.background.low_reject = params.pop('low_reject', 2.0)
    iraf.background.high_reject= params.pop('high_reject', 1.5)
    iraf.background.niterate = params.pop('niterate', 5)
    iraf.background.grow = params.pop('grow', 0.0)
    
    iraf.background(input=images, output=out_images)


def extinction(images, out_images, data_path='.'):
    """
    Run iraf extinction correction.

    Parameters
    ----------
    images : str
        Images to transform.
    out_images : str
        Output image file names.
    data_path : str
        Directory that contains the data.
   """ 

    _check_working_dir(data_path)

    logger.info('running iraf extinction')

    iraf.extinction.unlearn()
    iraf.extinction.extinct = os.path.join(calipath, 'lbtextinct.dat')
    iraf.extinction(input=images, output=out_images)


def apall(images, out_images, data_path='.', params={}):
    """
    Run iraf apall to extract 1d spectrum. 

    Parameters
    ----------
    images : str
        Images to transform.
    out_images : str
        Output image file names.
    data_path : str
        Directory that contains the data.
    params : dict
        Iraf apall parameters.
   """ 

    _check_working_dir(data_path)

    logger.info('running iraf apall')

    iraf.apall.unlearn()
    iraf.apall.format = params.pop('format', 'onedspec')
    iraf.apall.interactive = params.pop('interactive', 'yes')
    iraf.apall.find = params.pop('find', 'yes')
    iraf.apall.recenter = params.pop('recenter', 'no')
    iraf.apall.resize = params.pop('resize', 'no')
    iraf.apall.edit = params.pop('edit', 'yes')
    iraf.apall.trace = params.pop('trace', 'yes')
    iraf.apall.fittrace = params.pop('fittrace', 'yes')
    iraf.apall.extract = params.pop('extract', 'yes')
    iraf.apall.extras = params.pop('extras', 'no')
    iraf.apall.review = params.pop('review', 'no')
    iraf.apall.review = params.pop('background', 'no')

    # aperture 
    iraf.apall.line = params.pop('line', 3500)
    iraf.apall.nsum = params.pop('nsum', 500)
    iraf.apall.lower = params.pop('lower', -20)
    iraf.apall.upper = params.pop('upper', 20)

    # trace
    iraf.apall.t_nsum = params.pop('t_nsum', 300)
    iraf.apall.t_step = params.pop('t_step', 10)
    iraf.apall.t_nlost = params.pop('t_nlost', 10)

    # aperture centering 
    iraf.apall.width = params.pop('width', 20.0)
    iraf.apall.radius= params.pop('radius', 10.0)

    iraf.apall.readnoise = params.pop('readnoise', 2.5)
    iraf.apall.gain= params.pop('gain', 2.5)
    
    iraf.apall(input=images, output=out_images)


def standard_star(std_in, std_out, star_name, sampling=10, data_path='.',  
                  sens_prefix='sens', params={}):
    """
    Run iraf transform to rectify 2D spectrum.

    Parameters
    ----------
    std_in : str
        Input standard star extracted spectrum file name prefix.
    std_out : str
        Output file name prefix.
    star_name : str
        Standard star name.
    sampling : str
        Delta wavelength in angstrom (10 or 50 angstrom)
    data_path : str
        Directory that contains the data.
    sens_prefix : str
        Sensitivity correction file name prefix.
    params : dict
        Iraf standard and senfunc parameters.
    """

    _check_working_dir(data_path)

    logger.info('running iraf standard')


    iraf.standard.unlearn()
    interactive = params.pop('interactive', 'yes')
    iraf.standard.extinct = os.path.join(calipath, 'lbtextinct.dat')
    iraf.standard.caldir = os.path.join(calipath, 'modsSpecPhot/Tables') + '/'
    iraf.standard.star_name = '{}_{}a'.format(star_name.lower(), sampling)
    iraf.standard.interact = interactive
    iraf.standard.answer = params.pop('answer', 'yes')
    iraf.standard(input=std_in, output=std_out)

    logger.info('running iraf sensfunc')

    iraf.sensfunc.unlearn()
    iraf.sensfunc.interactive = interactive
    iraf.sensfunc.extinction = os.path.join(calipath, 'lbtextinct.dat')
    iraf.sensfunc.newextinction = params.pop('newextinction', 'newext.dat')
    iraf.sensfunc.sensitivity = params.pop('sensitivity', sens_prefix)
    iraf.sensfunc.answer = params.pop('answer', 'yes')
    iraf.sensfunc(standards=std_out)


def calibrate(spec_in, spec_out, data_path='.', sens_prefix='sens', params={}):
    """
    Run iraf calibrate to flux calibrate input spectrum.

    Parameters
    ----------
    spec_in : str
        Input spectrum file name.
    spec_out : str
        Output spectrum file name.
    data_path : str
        Directory that contains the data.
    sens_prefix : str
        Sensitivity correction file name prefix.
    params : dict
        Iraf calibrate parameters.
    """

    _check_working_dir(data_path)

    logger.info('running iraf calibrate')

    iraf.calibrate.unlearn()
    iraf.calibrate.extinct = params.pop('extinct', 'no')
    iraf.calibrate.flux = params.pop('flux', 'yes')
    iraf.calibrate.extinction = params.pop('extinction', '')
    iraf.calibrate.ignoreaps = params.pop('ignoreaps', 'yes')
    iraf.calibrate.sensitivity = params.pop('sensitivity', sens_prefix)
    iraf.calibrate.fnu = params.pop('fnu', 'no')
    iraf.calibrate(input=spec_in, output=spec_out)
