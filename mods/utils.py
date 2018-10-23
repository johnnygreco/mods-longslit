import os
from . import logger


__all__ = ['check_working_dir', 'check_kwargs_defaults', 'mkdir_if_needed']


def check_working_dir(data_path):
    if data_path is None:
        logger.debug('changing directory to ' + outpath)
        os.chdir(outpath)
    else:
        if os.getcwd() != data_path:
            logger.debug('changing directory to ' + data_path)
            os.chdir(data_path)


def check_kwargs_defaults(kwargs, defaults):
    """ 
    Build keyword argument by changing a default set of parameters.
    Parameters
    ----------
    kwargs : dict
        Keyword arguments that are different for default values.
    defaults : dict
        The default parameter values.
    Returns
    -------
    kw : dict
        A new keyword argument.
    """
    kw = defaults.copy()
    for k, v in kwargs.items():
        kw[k] = v 
    return kw


def mkdir_if_needed(directory):
    """"
    Create directory if it does not exist.
    """
    if not os.path.isdir(directory):
        logger.info('creating directory ' + directory)
        os.mkdir(directory)
