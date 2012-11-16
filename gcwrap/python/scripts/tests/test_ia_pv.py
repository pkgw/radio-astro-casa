##########################################################################
#
# Copyright (C) 2008, 2009
# Associated Universities, Inc. Washington DC, USA.
#
# This script is free software; you can redistribute it and/or modify it
# under the terms of the GNU Library General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
# License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
#
# Correspondence concerning AIPS++ should be adressed as follows:
#        Internet email: aips2-request@nrao.edu.
#        Postal address: AIPS++ Project Office
#                        National Radio Astronomy Observatory
#                        520 Edgemont Road
#                        Charlottesville, VA 22903-2475 USA
#
# <author>
# Dave Mehringer
# </author>
#
# <summary>
# Test suite for the CASA tool method ia.pv()
# </summary>
#
# <reviewed reviwer="" date="" tests="" demos="">
# </reviewed
#
# <prerequisite>
# <ul>
# </ul>
# </prerequisite>
#
# <etymology>
# Test for the ia.pv() tool method
# </etymology>
#
# <synopsis>
# Test the ia.pv() tool method
# </synopsis> 
#
# <example>
#
# This test runs as part of the CASA python unit test suite and can be run from
# the command line via eg
# 
# `echo $CASAPATH/bin/casapy | sed -e 's$ $/$'` --nologger --log2term -c `echo $CASAPATH | awk '{print $1}'`/code/xmlcasa/scripts/regressions/admin/runUnitTest.py test_ia_pv[test1,test2,...]
#
# </example>
#
# <motivation>
# To provide a test standard for the ia.pv() tool method to ensure
# coding changes do not break the associated bits 
# </motivation>
#

###########################################################################
import shutil
import casac
from tasks import *
from taskinit import *
from __main__ import *
import unittest
import numpy

class ia_pv_test(unittest.TestCase):
    
    def setUp(self):
        self.ia = iatool()
    
    def tearDown(self):
        pass
    
    def test_pv(self):
        """ ia.pv(): Test pv()"""
        myia = self.ia
        myia.fromshape("", [10, 10, 10])
        bb = myia.getchunk()
        # basic sanity test, no rotation involved
        for i in range(10):
            bb[i,5,:] = i
            bb[i,4,:] = i+1
            bb[i,6,:] = i+2
        myia.putchunk(bb)
        # no halfwidth
        pv = myia.pv(start=[1, 5], end=[9, 5])
        expec = [9, 1, 10]
        got = pv.shape()
        self.assertTrue((got == expec).all())
        expec = numpy.zeros(got)
        for i in range(10):
            expec[:,0,i] = range(1,10)
        got = pv.getchunk()
        self.assertTrue((got == expec).all())
        # halfwidth
        pv = myia.pv(start=[1, 1], end=[9, 1], halfwidth=1)
        expec = [9, 1, 10]
        got = pv.shape()
        self.assertTrue((got == expec).all())
    
    def test_stretch(self):
        """ ia.pv(): Test stretch parameter"""
        yy = iatool()
        mymask = "maskim"
        yy.fromshape(mymask, [200, 200, 1, 1])
        yy.addnoise()
        yy.done()
        shape = [200,200,1,20]
        yy.fromshape("", shape)
        yy.addnoise()
        self.assertRaises(
            Exception,
            yy.pv, start=[0,0], end=[20,0],
            mask=mymask + ">0", stretch=False
        )
        zz = yy.pv(
            start=[0,0], end=[20,0], mask=mymask + ">0", stretch=True
        )
        self.assertTrue(zz and type(zz) == type(yy))
        yy.done()
        zz.done()
    
def suite():
    return [ia_pv_test]
