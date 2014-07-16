from taskinit import *

def imstat(
    imagename=None, axes=None, region=None, box=None, chans=None,
    stokes=None, listit=None, verbose=None, mask=None, stretch=None,
    logfile=None, append=None
):
    _myia = iatool()
    _myrg = rgtool()
    _mycs = cstool()
    try:
        casalog.origin('imstat')
        _myia.open(imagename)
        _mycs = _myia.coordsys()
        csrec = _mycs.torecord()
        shape =  _myia.shape()
        reg = _myrg.frombcs(
            csrec, shape,
            box, chans, stokes, "a", region
        )
        retValue = _myia.statistics(
            axes=axes, region=reg, list=listit,
            verbose=verbose, robust=True, mask=mask,
            stretch=stretch, logfile=logfile, append=append
        )
        return retValue
    except Exception, instance:
        casalog.post( '*** Error ***'+str(instance), 'SEVERE' )
        raise
    finally:
        _myia.done()
        _myrg.done()
        _mycs.done()
