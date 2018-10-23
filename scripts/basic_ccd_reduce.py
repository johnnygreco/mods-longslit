#!/Users/jgreco/miniconda3/envs/iraf27/bin/python

from __future__ import print_function
import os
import numpy as np
from os import path
from subprocess import call
from mods import logger, datapath, files, utils
import ccdproc


def run_cmd(cmd, logfile):
    call(cmd, shell='True')
    print(cmd + '\n', file=logfile)


def trim_image(fn, trim, logfile):
    print('trimming image')
    print('trimming image with {}'.format(trim), file=logfile)
    ccd = ccdproc.trim_image(ccdproc.CCDData.read(fn)[trim])
    return ccd


def reduce_object(name, channel, file_list, flat_fn, trim, 
                  clean_cosmic_rays, logfile, outpath):
    extra_files = []
    for num, fn in enumerate(file_list):
        fn = path.join(datapath, fn)
        cmd = 'modsProc.py -bf {} {}'.format(fn, flat_fn)
        run_cmd(cmd, logfile)
        newfn = fn[:-5] + '_otf.fits'
        ccd = trim_image(newfn, trim, logfile)
        if clean_cosmic_rays:
            print('cleaning cosmic rays')
            ccd = ccdproc.cosmicray_lacosmic(ccd)
            extra_files.append(newfn)
            newfn = path.join(
                datapath, '{}-{}-{}.fits'.format(name, channel, num+1))
            print('lacosmic algo: file name --> ' + newfn, file=logfile)
        ccd.write(newfn, overwrite=True)
        call('mv ' + newfn + ' ' + outpath, shell=True)
    return extra_files


def reduce_arc(channel, file_list, flat_fn, trim, logfile, outpath):
    extra_files = []
    for fn in file_list:
        fn = path.join(datapath, fn)
        cmd = 'modsProc.py -bf {} {}'.format(fn, flat_fn)
        run_cmd(cmd, logfile)
        newfn = fn[:-5] + '_otf.fits'
        extra_files.append(newfn)
        trimmed = trim_image(newfn, trim, logfile)
        lamp = trimmed.header['CALLAMPS'].replace(' ', '')
        trimmed.write(path.join(outpath, channel+'-'+lamp+'-arcs.fits'), 
                      overwrite=True)
    return extra_files


def run_basic_ccd_reduction(targets, standards, tred, tblu, keep_extra_files, 
                            clean_cosmic_rays, do_arcs, force_make_flats, 
                            log_fn, outpath):

    print('********************************************************')
    print('***** running basic ccd reduction using modsCCDRed *****')
    print('********************************************************')

    extra_files = []
    logfile = open(path.join(outpath, log_fn), 'w')
    trim_red = np.s_[tred[0]: tred[1], tred[2]: tred[3]]
    trim_blue = np.s_[tblu[0]: tblu[1], tblu[2]: tblu[3]]

    blue_flat_fn = path.join(outpath, 'blue_master_flat.fits')
    red_flat_fn = path.join(outpath, 'red_master_flat.fits')

    print('******* basic_ccd_reduce.py logfile *******', file=logfile)
    arg_log = '\ntargets: {}\nstandards: {}\ntrim red: {}\ntrim blue: {}\n'
    arg_log += 'keep extra files: {}\nclean cosmic rays: {}\n\n'
    arg_log = arg_log.format(
        targets, standards, tred, tblu, keep_extra_files, clean_cosmic_rays)
    print(arg_log, file=logfile)

    if not os.path.isfile(red_flat_fn) or force_make_flats:
        print('\n***** building master flat for red channel *****')

        print('\nbias correct with overscan region and trim image')
        cmd = 'modsBias.py -f ' + path.join(datapath, files.flats.red[0])
        run_cmd(cmd, logfile)

        print('\nmedian combining red flats')
        newfn = path.join(datapath, files.flats.red[0][:-5] + '_ot.fits')
        outfn = path.join(outpath, 'rflat_med.fits')
        extra_files.extend([newfn, outfn])
        cmd = 'modsMedian.py -f {} {}'.format(newfn, outfn)
        run_cmd(cmd, logfile)

        print('\ncreating normalized pixel red flat')
        newfn = path.join(outpath, 'rflat_fix.fits')
        extra_files.append(newfn)
        cmd = 'modsFixPix.py -f {} {}'.format(outfn, newfn)
        run_cmd(cmd, logfile)

        cmd = 'modsPixFlat.py -f {} {}'.format(newfn, red_flat_fn)
        run_cmd(cmd, logfile)

    if not os.path.isfile(blue_flat_fn) or force_make_flats:
        print('\n***** building master flat for blue channel *****')

        print('\nbias correct with overscan region and trim image')
        cmd = 'modsBias.py -f ' + path.join(datapath, files.flats.blue[0]) 
        cmd = cmd + ' ' + path.join(datapath, files.flats.blue[1])
        run_cmd(cmd, logfile)

        print('\nmedian combining blue flats')
        newfn = path.join(datapath, files.flats.blue[0][:-5] + '_ot.fits')
        bclfn = path.join(outpath, 'bclrflat_med.fits')
        extra_files.extend([newfn, bclfn])
        cmd = 'modsMedian.py -f {} {}'.format(newfn, bclfn)
        run_cmd(cmd, logfile)

        newfn = path.join(datapath, files.flats.blue[1][:-5] + '_ot.fits')
        ug5fn = path.join(outpath, 'ug5flat_med.fits')
        extra_files.extend([newfn, ug5fn])
        cmd = 'modsMedian.py -f {} {}'.format(newfn, ug5fn)
        run_cmd(cmd, logfile)

        outfn = path.join(outpath, 'bflat_med.fits')
        extra_files.append(outfn)
        cmd = 'modsAdd.py -f {} {} {}'.format(bclfn, ug5fn, outfn)
        run_cmd(cmd, logfile)

        print('\ncreating normalized pixel blue flat')
        newfn = path.join(outpath, 'bflat_fix.fits')
        extra_files.append(newfn)
        cmd = 'modsFixPix.py -f {} {}'.format(outfn, newfn)
        run_cmd(cmd, logfile)

        cmd = 'modsPixFlat.py -f {} {}'.format(newfn, blue_flat_fn)
        run_cmd(cmd, logfile)

    args = [clean_cosmic_rays, logfile, outpath]

    if targets[0].lower() != 'none':
        for target in targets:
            print('\nremoving instrument signature for target ' + target)
            fn = files.sources[target]
            extra_files.extend(
                reduce_object(target, 'red', fn.red, 
                              red_flat_fn, trim_red, *args))
            extra_files.extend(
                reduce_object(target, 'blue', fn.blue, 
                              blue_flat_fn, trim_blue, *args))

    if standards[0].lower() != 'none':
        for std in standards:
            print('\nremoving instrument signature for standard ' + std)
            fn = files.standards[std]
            extra_files.extend(
                reduce_object(std, 'red', fn.red, 
                              red_flat_fn, trim_red, *args))
            extra_files.extend(
                reduce_object(std, 'blue', fn.blue,
                              blue_flat_fn, trim_blue, *args))


    if do_arcs:
        args = [logfile, outpath]
        print('\nremoving instrument signature for arcs')
        extra_files.extend(
            reduce_arc('red', files.arcs.red, red_flat_fn, trim_red, *args))
        extra_files.extend(
            reduce_arc('blue', files.arcs.blue, blue_flat_fn, trim_blue, 
                       *args))

    print()
    if not keep_extra_files:
        for fn in extra_files:
            print('deleting', fn)
            run_cmd('rm ' + fn, logfile)

    logfile.close()

if __name__ == '__main__':
    from argparse import ArgumentParser

    default_out = os.path.join(datapath, 'mods-output')

    parser = ArgumentParser()
    parser.add_argument('--targets', nargs='+', default=['G196'], type=str)
    parser.add_argument(
        '--standards', nargs='+', default=['Feige110'], type=str)
    parser.add_argument('-o', '--outpath', default=default_out)
    parser.add_argument('--trim-red', nargs=4, type=int, dest='trim_red',
                        default=[1330, 1775, 1290, 7406], 
                        help='trimming bounds red image (row then col bounds)')
    parser.add_argument('--trim-blue', nargs=4, type=int, dest='trim_blue',
                        default=[1400, 1850, 1600, 7795], 
                        help='trimming bounds red image (row then col bounds)')
    parser.add_argument('--keep-extra-files', dest='keep_extra_files',
                        action='store_true')
    parser.add_argument('--clean-cosmic-rays', dest='clean_cosmic_rays',
                        action='store_true')
    parser.add_argument('--no-arcs', dest='no_arcs', action='store_true')
    parser.add_argument('--force-make-flats', dest='force_make_flats', 
                        action='store_true')
    parser.add_argument(
        '--log-fn', dest='log_fn', default='basic-reduce.log', type=str)
    args = parser.parse_args()

    logger.info('output directory will be ' + args.outpath)
    utils.mkdir_if_needed(args.outpath)

    run_basic_ccd_reduction(args.targets, 
                            args.standards,
                            args.trim_red, 
                            args.trim_blue, 
                            args.keep_extra_files, 
                            args.clean_cosmic_rays, 
                            not args.no_arcs, 
                            args.force_make_flats,
                            args.log_fn, 
                            args.outpath)

