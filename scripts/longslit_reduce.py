#!/Users/jgreco/miniconda3/envs/iraf27/bin/python

from __future__ import print_function
import os
import numpy as np
import mods

def run_longslit_reduce(config_filename): 

    mods.logger('starting mods longslit reduction...')

    config = mods.ReduceConfig(config_filename)
    data_path = config.data_path

    if config.do_identify:
        mods.reduce.identify(
            config.arc_fn, config.arc_lamp, config.mods_channel, data_path, 
            config.identify_params)

    if config.do_reidentify:
        mods.reduce.reidentify(
            config.arc_fn, config.arc_fn, config.arc_lamp, config.mods_channel, 
            data_path, config.reidentify_params)

    if config.do_fitcoords:
        mods.reduce.fitcoords(
            config.arc_fn, data_path, config.fitcoords_params)

    object_types = [config.sources, config.standards]
    object_files = [config.src_files, config.std_files]

    if config.do_transform:
        in_fn = config.arc_fn
        out_fn = in_fn[:-5] + '-t.fits'
        mods.reduce.transform(
            in_fn, out_fn, config.arc_fn[:-5], data_path, 
            config.transform_params)
        for i in range(2):
            for obj in object_types[i]:
                for in_fn in object_files[i][obj]:
                    out_fn = in_fn[:-5] + 't.fits'
                    mods.reduce.transform(
                        in_fn + '[0]', out_fn, config.arc_fn[:-5], data_path, 
                        config.transform_params)

    if config.do_background:
        for i in range(2):
            for obj in object_types[i]:
                files = [fn[:-5] + 't.fits' for fn in object_files[i][obj]]
                out =  [fn[:-5] + 'b.fits' for fn in files]
                files = ','.join(files)
                out = ','.join(out)
                mods.reduce.background(
                    files, out, data_path, config.background_params)

    stack_files = []
    stack_funcs = [config.src_stack_func, config.std_stack_func]
    for i in range(2):
        for obj in object_types[i]:
            files = [fn[:-5] + 'tb.fits' for fn in object_files[i][obj]]
            out_fn = '{}-{}-tb.fits'.format(obj, stack_funcs[i])
            stack_files.append(out_fn)
            if config.do_stack:
                mods.imarith.stack(files, out_fn, stack_funcs[i], data_path)

    ext_files = []
    for fn in stack_files:
        out_fn = fn[:-5] + 'e.fits'
        ext_files.append(out_fn)
        if config.do_extinction:
            mods.reduce.extinction(fn, out_fn, data_path)

    if config.do_apall:
        out = [fn[:-5] + '-1d.fits' for fn in ext_files]
        out = ','.join(out)
        files = ','.join(ext_files)
        mods.reduce.apall(files, out, data_path, config.apall_params)

    std_files = []
    for std in config.standards:
        in_fn = '{}-{}-tbe-1d.fits'.format(std, config.std_stack_func)
        out_fn = in_fn[:-5] + '.std'
        std_files.append(out_fn)
        sens_prefix = 'sens-' + std
        if config.do_standard_star:
            mods.reduce.standard_star(
                in_fn, out_fn, std, config.std_sampling, data_path,
                sens_prefix, config.standard_star_params)
    
    if config.do_calibrate:
        std_fn = std_files[config.calibrate_star_idx]
        std = config.standards[config.calibrate_star_idx]
        sens_prefix = 'sens-' + std
        for src in config.sources:
            in_fn = '{}-{}-tbe-1d.fits'.format(src, config.src_stack_func)
            out_fn = in_fn[:-5] + '-flam.fits'
            mods.reduce.calibrate(
                in_fn, out_fn, data_path, sens_prefix, config.calibrate_params)

    mods.logger.info('you are *finally* finished <3')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('config_filename')
    args = parser.parse_args()
    run_longslit_reduce(args.config_filename)
