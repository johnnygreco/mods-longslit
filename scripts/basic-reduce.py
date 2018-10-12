#!/Users/jgreco/miniconda3/envs/iraf27/bin/python

from __future__ import print_function
import os
from os import path
from subprocess import call
from argparse import ArgumentParser
from modsls import outpath, datapath, files
import ccdproc

def run_cmd(cmd, logfile):
    call(cmd, shell='True')
    print(cmd, file=logfile)

parser = ArgumentParser()
parser.add_argument('--targets', nargs='+', default=['G196'], type=str)
parser.add_argument('--keep-extra-files', dest='keep_extra_files',
                    action='store_true')
parser.add_argument('--clean-cosmic-rays', dest='clean_cosmic_rays',
                    action='store_true')
args = parser.parse_args()

print('****************************************************')
print('***** running basic reduction using modsCCDRed *****')
print('****************************************************')

logfile = open(path.join(outpath, 'basic-reduce.log'), 'w')
extra_files = []

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

for target in args.targets:

    print('\nremoving instrument signature for target ' + target)

    for fn in files.sources[target].red:
        fn = path.join(datapath, fn)
        cmd = 'modsProc.py -b {} {}'.format(fn, red_flat_fn)
        run_cmd(cmd, logfile)
        newfn = fn[:-5] + '_otf.fits'
        if args.clean_cosmic_rays:
            print('cleaning cosmic rays')
            print('lacosmic algo: _otf --> _otfc', file=logfile)
            ccd = ccdproc.cosmicray_lacosmic(ccdproc.CCDData.read(newfn))
            extra_files.append(newfn)
            newfn = fn[:-5] + '_otfc.fits'
            ccd.write(newfn)
        call('mv ' + newfn + ' ' + outpath, shell=True)

    for fn in files.sources[target].blue:
        fn = path.join(datapath, fn)
        cmd = 'modsProc.py -b {} {}'.format(fn, blue_flat_fn)
        run_cmd(cmd, logfile)
        newfn = fn[:-5] + '_otf.fits'
        if args.clean_cosmic_rays:
            print('cleaning cosmic rays')
            print('lacosmic algo: _otf --> _otfc', file=logfile)
            ccd = ccdproc.cosmicray_lacosmic(ccdproc.CCDData.read(newfn))
            extra_files.append(newfn)
            newfn = fn[:-5] + '_otfc.fits'
            ccd.write(newfn)
        call('mv ' + newfn + ' ' + outpath, shell=True)

print('\nremoving instrument signature for arcs')
for fn in files.arcs.red:
    fn = path.join(datapath, fn)
    cmd = 'modsProc.py -b {} {}'.format(fn, red_flat_fn)
    run_cmd(cmd, logfile)
    newfn = fn[:-5] + '_otf.fits'
    call('mv ' + newfn + ' ' + outpath, shell=True)

for fn in files.arcs.blue:
    fn = path.join(datapath, fn)
    cmd = 'modsProc.py -b {} {}'.format(fn, blue_flat_fn)
    run_cmd(cmd, logfile)
    newfn = fn[:-5] + '_otf.fits'
    call('mv ' + newfn + ' ' + outpath, shell=True)

print()
if not args.keep_extra_files:
    for fn in extra_files:
        print('deleting', fn)
        run_cmd('rm ' + fn, logfile)

logfile.close()
