startTime = time.time()
startProc = time.clock()

projname="cltest"

if os.path.exists(projname): shutil.rmtree(projname)

l=locals()
if "repodir" not in l:
    repodir=os.getenv("CASAPATH").split(' ')[0]

print(casa['build'])
print('I think the data repository is at '+repodir)
datadir=repodir+"/data/regression/simdata/"
if os.path.exists("6334.cl"): shutil.rmtree("6334.cl")
shutil.copytree(datadir+"6334.cl","6334.cl")

default("simobserve")
project            =  projname
complist           =  "6334.cl"
compwidth          =  "1.875GHz"
setpointings       =  True
integration        =  "10s"
direction          =  "J2000 17h20m53.2s -35d47m00s"
mapsize            =  "13arcsec"
maptype            =  "ALMA"
pointingspacing    =  ""
#observe            =  True
obsmode            =  "int"
refdate            =  "2014/01/01"
hourangle          =  "transit"
totaltime          =  "7200s"
antennalist        =  "alma.cycle0.extended.cfg"
thermalnoise       =  ""

if 'interactive' not in l: interactive=False
if interactive:
    graphics="both"
else:
    graphics="file"

verbose            =  True
overwrite          =  True

inp()
simobserve()


default("simanalyze")
project            =  projname
image              =  True
vis                =  "default"
imsize             =  300
imdirection        =  direction
cell               = "0.043294054arcsec"
niter              =  500
threshold          =  "0.1mJy"
analyze            =  True

if 'interactive' not in l: interactive=False
if interactive:
    graphics="both"
else:
    graphics="file"

verbose            =  True
overwrite          =  True

go()

endTime = time.time()
endProc = time.clock()

ia.open(project+"/"+project + '.alma.cycle0.extended.image')
hii_stats=ia.statistics(verbose=False,list=False)
ia.close()

reftol   = {'sum':  0.1,
            'max':  0.04,
            'min':  0.04,
            'rms':  0.1}

refstats = { 'max': 4.9786,
             'min': -0.13691,
             'rms': 0.096445,
             'sum': 325.71 }

import datetime
datestring = datetime.datetime.isoformat(datetime.datetime.today())
outfile    = project+"/"+project + '.' + datestring + '.log'
logfile    = open(outfile, 'w')

print('Writing regression output to ' + outfile + "\n")

print(casa['build'], file=logfile)

regstate = True
rskes = list(refstats.keys())
rskes.sort()
for ke in rskes:
    adiff=abs(hii_stats[ke][0] - refstats[ke])/abs(refstats[ke])
    if adiff < reftol[ke]:
        print("* Passed %-5s image test, got % -11.5g expected % -11.5g." % (ke, hii_stats[ke][0], refstats[ke]), file=logfile)
    else:
        print("* FAILED %-5s image test, got % -11.5g instead of % -11.5g." % (ke, hii_stats[ke][0], refstats[ke]), file=logfile)
        regstate = False

print('---', file=logfile)
if regstate:
    print('Passed', end=' ', file=logfile)
    print('')
    print('Regression PASSED')
    print('')
else:
    print('FAILED', end=' ', file=logfile)
    print('')
    print('Regression FAILED')
    print('')

print('regression test for component-only simdata', file=logfile)
print('---', file=logfile)
print('*********************************', file=logfile)

print('', file=logfile)
print('********** Benchmarking **************', file=logfile)
print('', file=logfile)
print('Total wall clock time was: %8.3f s.' % (endTime - startTime), file=logfile)
print('Total CPU        time was: %8.3f s.' % (endProc - startProc), file=logfile)
print('Wall processing  rate was: %8.3f MB/s.' % (17896.0 /
                                                            (endTime - startTime)), file=logfile)

msfstat = os.stat(project+"/"+project+'.alma.cycle0.extended.ms')
print('* Breakdown:                           *', file=logfile)
print('*  generating visibilities took %8.3fs,' % (msfstat[8] - startTime), file=logfile)
print('*  deconvolution with %d iterations took %8.3fs.' % ( niter,
                                                                       endTime - msfstat[8]), file=logfile)
print('*************************************', file=logfile)

logfile.close()


