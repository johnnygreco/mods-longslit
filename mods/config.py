from __future__ import print_function


import sys
import yaml
import numpy as np
from . import logger


def _get_list(param, dtype=str):
    if type(param) == int:
        return [param]
    elif type(param) == str:
        param = param.split(',')
        return [dtype(p.replace(' ', '')) for p in param]
    else:
        logger.exception(
            '{} for {} is not an valid type'.format(type(param), param))
        sys.exit(1)


class ReduceConfig(object):

    lamp_abbrev = dict(argon='AR', 
                       neon_mercury='NEHG', 
                       xenon_krypton='XEKR')

    def __init__(self, filename):

        with open(filename, 'r') as fn:
            logger.info('loading config file ' + filename)
            config = yaml.load(fn)

        self.data_path = config['data_path']
        self.mods_channel = config['mods_channel']
        self.arc_lamp = config['arc_lamp']
        self.arc_fn = '{}-{}-arcs.fits'.format(
            self.mods_channel, self.lamp_abbrev[self.arc_lamp])

        self.sources = _get_list(config['sources']['name'])
        self.src_nexp = _get_list(config['sources']['nexp'], int)
        self.src_stack_func = config['sources']['stack_func']

        self.src_files = {}
        for src, nexp in zip(self.sources, self.src_nexp):
            self.src_files[src] = []
            for num in range(1, nexp+1):
                fn = '{}-{}-{}.fits'.format(src, self.mods_channel, num)
                self.src_files[src].append(fn)

        self.standards = _get_list(config['standards']['name'])
        self.std_nexp = _get_list(config['standards']['nexp'], int)
        self.std_stack_func = config['standards']['stack_func']
        self.std_sampling = config['standards']['sampling']
        self.calibrate_star_idx = config['standards']['calibrate_star_idx']

        self.std_files = {}
        for std, nexp in zip(self.standards, self.std_nexp):
            self.std_files[std] = []
            for num in range(1, nexp+1):
                fn = '{}-{}-{}.fits'.format(std, self.mods_channel, num)
                self.std_files[std].append(fn)

        self.pipeline_steps = config['pipeline_steps']
        self.do_identify = self.pipeline_steps['identify']
        self.do_reidentify = self.pipeline_steps['reidentify']
        self.do_fitcoords = self.pipeline_steps['fitcoords']
        self.do_transform = self.pipeline_steps['transform']
        self.do_background = self.pipeline_steps['background']
        self.do_stack = self.pipeline_steps['stack']
        self.do_extinction = self.pipeline_steps['extinction']
        self.do_apall = self.pipeline_steps['apall']
        self.do_standard_star = self.pipeline_steps['standard_star']
        self.do_calibrate = self.pipeline_steps['calibrate']

        self.identify_params = config['identify_params']
        self.reidentify_params = config['reidentify_params']
        self.fitcoords_params = config['fitcoords_params']
        self.transform_params = config['transform_params']
        self.background_params = config['background_params']
        self.apall_params = config['apall_params']
        self.standard_star_params = config['apall_params']
        self.calibrate_params = config['calibrate_params']
