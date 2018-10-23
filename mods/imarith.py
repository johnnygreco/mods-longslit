from __future__ import division, print_function

import os
import numpy as np
from astropy.io import fits
from . import logger
from .utils import check_working_dir


def stack(files, out_file=None, func=np.median, data_path=None):
    """
    Stack images. Either write to file or return HDU.

    Parameters
    ----------
    files : str
        FITS file names to stack.
    out_file : str (optional)
        If not None, then result will be written to this file.
    func : numpy function or str
        numpy stacking function (np.mean, np.median, or np.sum)
    data_path : str
        Directory that contains the data.
        
    Returns
    -------
    hdu : fits.PrimaryHDU
        HDU for stacked image. Only retuns is out_file = None. 
    """

    check_working_dir(data_path)

    if type(func) == str:
        func = dict(mean=np.mean, median=np.median, sum=np.sum)[func]

    stack = []
    logger.info('{} stacking {} images'.format(func.func_name, len(files)))
    for fn in files:
        stack.append(fits.getdata(fn))
    stack = func(stack, axis=0)

    header = fits.getheader(files[0])
    msg = 'STACKED: {} image from {} files'.format(func.func_name, len(files))
    header.add_history(msg)
    for i, fn in enumerate(files):
        header.add_history('STACKED: image {} = {}'.format(i + 1, fn))

    if out_file is not None:
        if os.path.isfile(out_file):
            logger.warn('Overwriting existing FITS file ' + out_file)
        fits.writeto(out_file, stack, header=header, overwrite=True)
    else:
        hdu = fits.PrimaryHDU(data=stack, header=header)
        return hdu
