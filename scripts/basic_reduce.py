#!/Users/jgreco/miniconda3/envs/iraf27/bin/python

from __future__ import print_function
import os
import numpy as np
from os import path
from subprocess import call
from modsls import outpath, datapath, files
import ccdproc

def run_cmd(cmd, logfile):
    call(cmd, shell='True')
    print(cmd, file=logfile)

def trim_image(fn, trim, logfile):
    print('trimming image')
    print('trimming image with {}'.format(trim), file=logfile)
    ccd = ccdproc.trim_image(ccdproc.CCDData.read(fn)[trim])
    return ccd

def run_basic_reduction(targets, tred, tblu, keep_extra_files, 
                        clean_cosmic_rays):

    print('****************************************************')
    print('***** running basic reduction using modsCCDRed *****')
    print('****************************************************')

    logfile = open(path.join(outpath, 'basic-reduce.log'), 'w')
    extra_files = []
    trim_red = np.s_[tred[0]: tred[1], tred[2]: tred[3]]
    trim_blue = np.s_[tblu[0]: tblu[1], tblu[2]: tblu[3]]

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

    red_flat_fn = path.join(outpath, 'red_master_flat.fits')
    cmd = 'modsPixFlat.py -f {} {}'.format(newfn, red_flat_fn)
    run_cmd(cmd, logfile)

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

    blue_flat_fn = path.join(outpath, 'blue_master_flat.fits')
    cmd = 'modsPixFlat.py -f {} {}'.format(newfn, blue_flat_fn)
    run_cmd(cmd, logfile)

    for target in targets:

        print('\nremoving instrument signature for target ' + target)

        for fn in files.sources[target].red:
            fn = path.join(datapath, fn)
            cmd = 'modsProc.py -bf {} {}'.format(fn, red_flat_fn)
            run_cmd(cmd, logfile)
            newfn = fn[:-5] + '_otf.fits'
            ccd = trim_image(newfn, trim_red, logfile)
            if clean_cosmic_rays:
                print('cleaning cosmic rays')
                print('lacosmic algo: _otf --> _otfc', file=logfile)
                ccd = ccdproc.cosmicray_lacosmic(ccd)
                extra_files.append(newfn)
                newfn = fn[:-5] + '_otfc.fits'
            ccd.write(newfn, overwrite=True)
            call('mv ' + newfn + ' ' + outpath, shell=True)

        for fn in files.sources[target].blue:
            fn = path.join(datapath, fn)
            cmd = 'modsProc.py -bf {} {}'.format(fn, blue_flat_fn)
            run_cmd(cmd, logfile)
            newfn = fn[:-5] + '_otf.fits'
            ccd = trim_image(newfn, trim_blue, logfile)
            if clean_cosmic_rays:
                print('cleaning cosmic rays')
                print('lacosmic algo: _otf --> _otfc', file=logfile)
                ccd = ccdproc.cosmicray_lacosmic(ccd)
                extra_files.append(newfn)
                newfn = fn[:-5] + '_otfc.fits'
            ccd.write(newfn, overwrite=True)
            call('mv ' + newfn + ' ' + outpath, shell=True)

    print('\nremoving instrument signature for arcs')
    red_arcs = []
    for fn in files.arcs.red:
        fn = path.join(datapath, fn)
        cmd = 'modsProc.py -bf {} {}'.format(fn, red_flat_fn)
        run_cmd(cmd, logfile)
        newfn = fn[:-5] + '_otf.fits'
        extra_files.append(newfn)
        red_arcs.append(trim_image(newfn, trim_red, logfile))
    ccd = ccdproc.combine(red_arcs)
    fn = path.join(outpath, 'red_NeXeAr_arcs.fits')
    ccd.write(fn, overwrite=True)
    
    blue_arcs = []
    for fn in files.arcs.blue:
        fn = path.join(datapath, fn)
        cmd = 'modsProc.py -bf {} {}'.format(fn, blue_flat_fn)
        run_cmd(cmd, logfile)
        newfn = fn[:-5] + '_otf.fits'
        extra_files.append(newfn)
        blue_arcs.append(trim_image(newfn, trim_blue, logfile))
    ccd = ccdproc.combine(blue_arcs)
    fn = path.join(outpath, 'blue_HgXeAr_arcs.fits')
    ccd.write(fn, overwrite=True)

    print()
    if not keep_extra_files:
        for fn in extra_files:
            print('deleting', fn)
            run_cmd('rm ' + fn, logfile)

    logfile.close()

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--targets', nargs='+', default=['G196'], type=str)
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
    args = parser.parse_args()

    run_basic_reduction(args.targets, 
                        args.trim_red, 
                        args.trim_blue, 
                        args.keep_extra_files, 
                        args.clean_cosmic_rays)
