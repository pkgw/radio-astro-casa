import os
import re
import sys
import time
from casac import *

homedir = os.getenv('HOME')
if homedir == None :
   print("Environment variable HOME is not set, please set it")
   sys.exit(1)

import casadef

##
## first set up CASAPATH
##
if 'CASAPATH' in os.environ :
    __casapath__ = os.environ['CASAPATH'].split(' ')[0]
    if not os.path.exists(__casapath__ + "/data") :
        raise RuntimeError("CASAPATH environment variable is improperly set")
else :
    __casapath__ = casac.__file__
    while __casapath__ and __casapath__ != "/" :
        if os.path.exists( __casapath__ + "/data") :
            break
        __casapath__ = os.path.dirname(__casapath__)
    if __casapath__ and __casapath__ != "/" :
        os.environ['CASAPATH']=__casapath__ + " linux local host"
    else :
        raise RuntimeError("CASAPATH environment variable must be set")

casa = { 'build': {
             'time': casadef.build_time,
             'version': casadef.casa_version,
             'number': casadef.subversion_revision
         },
         'source': {
             'url': casadef.subversion_url,
             'revision': casadef.subversion_revision
         },
         'helpers': {
             'logger': 'casalogger',
             'viewer': 'casaviewer',
             'info': None,
             'dbus': None,
             'ipcontroller': None,
             'ipengine': None
         },
         'dirs': {
             'rc': homedir + '/.casa',
             'data': __casapath__ + "/data",
             'recipes': __casapath__ + "/lib/python2.7/recipes",
             'root': __casapath__,
             'python':  __casapath__ + "/lib/python2.7",
             'pipeline': None,
             'xml': __casapath__ + "/xml"
         },
         'flags': { },
         'files': { 
             'logfile': os.getcwd( ) + '/casapy-'+time.strftime("%Y%m%d-%H%M%S", time.gmtime())+'.log'
         },
         'state' : {
             'startup': True,
             'unwritable': set( )
         }
       }

##
## next adjust the PYTHONPATH
##
def adapt_pythonpath(searchroot):
    # tarball location
    guess = os.path.join(searchroot, 'lib/python2.7/site-packages/numpy')
    if os.path.isdir(guess):
        sys.path.append(os.path.dirname(guess))
    else:
        for root, dirs, files in os.walk(searchroot):
            # skip data folder which might be a network mount
            if root == searchroot and 'data' in dirs:
                del dirs[dirs.index('data')]
            if root.endswith("/numpy"):
                sys.path.append(os.path.dirname(root))
                break

if re.match( r'.*/\d+\.\d+\.\d+\w*-\d+$', __casapath__ ) :
    adapt_pythonpath(os.path.dirname(__casapath__))
else:
    adapt_pythonpath(__casapath__)

##
## next adjust PATH and LD_LIBRARY_PATH
##
def setup_path():
    global __ipcontroller__, __ld_library_path__
    _rootdir = None
    if os.path.exists(os.path.join(__casapath__, 'bin', 'casapyinfo')):
        _rootdir = os.path.join(__casapath__, 'bin')
    else:
        for root, dirs, files in os.walk(__casapath__):
            # skip data folder which might be a network mount
            if root == __casapath__ and 'data' in dirs:
                del dirs[dirs.index('data')]
            if root.endswith("/bin") and "casapyinfo" in files :
                _rootdir = root
                break
    if _rootdir is None:
        return

    __ipcontroller__ = (lambda fd: fd.readline().strip('\n'))(os.popen(_rootdir + "/casapyinfo --exec 'which ipcontroller'"))
    if os.path.exists(__ipcontroller__) :
        os.environ['PATH'] = os.path.dirname(__ipcontroller__) + ":" + os.environ['PATH']
    else :
        raise RuntimeError("cannot configure CASA tasking system")
    __ld_library_path__ = (lambda fd: fd.readline().strip('\n').split(':'))(os.popen(_rootdir + "/casapyinfo --exec 'echo $LD_LIBRARY_PATH'"))
    for x in __ld_library_path__:
       sys.path.append(x)

setup_path()

##
## finally load tools
##

quanta = casac.quanta()
measures = casac.measures()
imager = casac.imager()
calibrater = casac.calibrater()
ms = casac.ms()
tableplot = casac.tableplot()
msplot = casac.msplot()
pmtool = casac.plotms()
calplot = casac.calplot()
table = casac.table()
#flagger = casac.flagger()
agentflagger = casac.agentflagger()
image = casac.image()
imagepol = casac.imagepol()
simulator = casac.simulator()
componentlist = casac.componentlist()
coordsys = casac.coordsys()
regionmanager = casac.regionmanager()
spectralline = casac.spectralline()
utils = casac.utils()
deconvolver = casac.deconvolver()
vpmanager = casac.vpmanager()
vlafillertask = casac.vlafillertask()
atmosphere = casac.atmosphere()
mstransformer = casac.mstransformer()

from accum import  accum
from applycal import  applycal
from asdmsummary import  asdmsummary
from autoclean import  autoclean
from bandpass import  bandpass
from blcal import  blcal
from boxit import  boxit
from browsetable import  browsetable
from calstat import  calstat
from clean import  clean
from clearcal import  clearcal
from clearplot import  clearplot
from clearstat import  clearstat
#from concat import  concat
from cvel import  cvel
from cvel2 import  cvel2
from deconvolve import  deconvolve
from exportfits import  exportfits
from exportuvfits import  exportuvfits
from feather import  feather
from find import  find
from fixvis import  fixvis
from flagdata import  flagdata
from flagmanager import  flagmanager
from fluxscale import  fluxscale
from ft import  ft
from gaincal import  gaincal
from gencal import  gencal
from hanningsmooth import  hanningsmooth
#from hanningsmooth2 import  hanningsmooth2
from imcontsub import  imcontsub
from imfit import  imfit
from imhead import  imhead
from immath import  immath
from immoments import  immoments
from importasdm import  importasdm
from importfits import  importfits
from importgmrt import  importgmrt
from importuvfits import  importuvfits
from importvla import  importvla
from imregrid import  imregrid
from imsmooth import  imsmooth
from imstat import  imstat
from imval import  imval
from imview import imview
from listcal import  listcal
from listhistory import  listhistory
from listobs import  listobs
from listvis import  listvis
from mosaic import  mosaic
from mstransform import mstransform
from msview import msview
from oldhanningsmooth import  oldhanningsmooth
from oldsplit import  oldsplit
from partition import partition
from plotants import  plotants
from plotcal import  plotcal
from plotms import  plotms
#from plotxy import  plotxy
from polcal import  polcal
from rmtables import  rmtables
from setjy import  setjy
from simalma import  simalma
from simobserve import  simobserve
from simanalyze import  simanalyze
from smoothcal import  smoothcal
from specfit import  specfit
from split import  split
#from split2 import split2
from tclean import tclean
from tclean2 import tclean2
from tsdbaseline import tsdbaseline
from tsdcal import tsdcal
from tsdfit import tsdfit
from uvcontsub import  uvcontsub
from uvmodelfit import  uvmodelfit
from uvsub import  uvsub
from viewer import  viewer
from vishead import  vishead
from visstat import  visstat
from visstat2 import  visstat2
from widefield import  widefield


##
## asap may not be available with every casa installation
##
try:
    import asap as sd
    from sdcal import sdcal
    from sdsmooth import sdsmooth
    from sdbaseline import sdbaseline
    from sdbaseline2 import sdbaseline2
    from sdreduce import sdreduce
    from sdcoadd import sdcoadd
    from sdsave import sdsave
    from sdscale import sdscale
    from sdfit import sdfit
    from sdplot import sdplot
    from sdstat import sdstat
    from sdlist import sdlist
    from sdflag import sdflag
    from sdflag2 import sdflag2
    from sdmath import sdmath
    from sdimaging import sdimaging
    from sdimprocess import sdimprocess
except ImportError:
    sd = None
    sdcoadd = None
    sdscale = None
    sdlist = None
    sdfit = None
    sdbaseline = None
    sdbaseline2 = None
    sdstat = None
    sdsave = None
    sdflag = None
    sdflag2 = None
    sdcal = None
    sdplot = None
    sdsmooth = None
    sdreduce = None
