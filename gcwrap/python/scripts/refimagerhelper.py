import os
import subprocess
import math
import shutil
import string
import time
import re;
from taskinit import *
import copy

'''
A set of helper functions for the tasks  tclean, xxxx

Summary...

    
'''

debug = False
#############################################
#############################################

#############################################
class PySynthesisImager:

    def __init__(self,params):
        ################ Tools
        self.initDefaults()

        # Check all input parameters, after partitioning setup.

        # Selection Parameters. Dictionary of dictionaries, indexed by 'ms0','ms1',...
        self.allselpars = params.getSelPars()
        # Imaging/Deconvolution parameters. Same for serial and parallel runs
        self.alldecpars = params.getDecPars()
        self.allimpars = params.getImagePars()
        self.allgridpars = params.getGridPars()
        self.allnormpars = params.getNormPars()
        self.weightpars = params.getWeightPars()
        # Iteration parameters
        self.iterpars = params.getIterPars() ## Or just params.iterpars

        # CFCache params
        self.cfcachepars = params.getCFCachePars()
        ## Number of fields ( main + outliers )
        self.NF = len(list(self.allimpars.keys()))
        self.stopMinor = {}  ##[0]*self.NF
        for immod in range(0,self.NF):
            self.stopMinor[str(immod)]=0
        ## Number of nodes. This gets set for parallel runs
        ## It can also be used serially to process the major cycle in pieces.
        self.NN = 1 
        ## for debug mode automask incrementation only
        self.ncycle = 0
#        isvalid = self.checkParameters()
#        if isvalid==False:
#            print 'Invalid parameters'

#############################################
#    def checkParameters(self):
#        # Copy the imagename from impars to decpars, for each field.
#        for immod in range(0,self.NF):
#            self.alldecpars[str(immod)]['imagename'] = self.allimpars[str(immod)]['imagename']
#        return True

#############################################
    def makeCFCache(self,exists):
        # Make the CFCache and re-load it.  The following calls become
        # NoOps (in SynthesisImager.cc) if the gridder is not one
        # which uses CFCache.
        if (exists):
            print("CFCache already exists");
        else:
            self.dryGridding();
            self.fillCFCache();
            self.reloadCFCache();
        
#############################################
    def initializeImagers(self):
        
        ## Initialize the tool for the current node
        self.SItool = casac.synthesisimager()
        
        ## Send in selection parameters for all MSs in the list.
        for mss in sorted( (self.allselpars).keys() ):
            self.SItool.selectdata( self.allselpars[mss] )
#            self.SItool.selectdata( **(self.allselpars[mss]) )

        ## For each image-field, define imaging parameters
#        nimpars = copy.deepcopy(self.allimpars)
#        for fld in range(0,self.NF):
#            self.SItool.defineimage( **( nimpars[str(fld)]  ) )
        
        # If cfcache directory already exists, assume that it is
        # usable and is correct.  makeCFCache call then becomes a
        # NoOp.
        cfCacheName=self.allgridpars['0']['cfcache'];
        exists=False;
        if (not (cfCacheName == '')):
            exists = (os.path.exists(cfCacheName) and os.path.isdir(cfCacheName));

        for fld in range(0,self.NF):
            #print "self.allimpars=",self.allimpars,"\n"
            self.SItool.defineimage( self.allimpars[str(fld)] , self.allgridpars[str(fld)] )
    
        # For cube imaging:  align the data selections and image setup
        if self.allimpars['0']['specmode'] != 'mfs' and self.allimpars['0']['specmode'] != 'cubedata':
            self.SItool.tuneselectdata()

        #self.makeCFCache(exists);

#############################################

    def initializeDeconvolvers(self):
         for immod in range(0,self.NF):
              self.SDtools.append(casac.synthesisdeconvolver())
              self.SDtools[immod].setupdeconvolution(decpars=self.alldecpars[str(immod)])

#############################################
    ## Overloaded by ParallelCont
    def initializeNormalizers(self):
        for immod in range(0,self.NF):
            self.PStools.append(casac.synthesisnormalizer())
            normpars = self.allnormpars[str(immod)]
            self.PStools[immod].setupnormalizer(normpars=normpars)

#############################################

    def initializeIterationControl(self):
        self.IBtool = casac.synthesisiterbot()
        itbot = self.IBtool.setupiteration(iterpars=self.iterpars)

#############################################

    def restoreImages(self):
         for immod in range(0,self.NF):
              self.SDtools[immod].restore()

#############################################
    def pbcorImages(self):
         for immod in range(0,self.NF):
              self.SDtools[immod].pbcor()

#############################################

    def getSummary(self,fignum=1):
        summ = self.IBtool.getiterationsummary()
        self.plotReport( summ, fignum )
        return summ

#############################################
    def deleteImagers(self):
        if self.SItool != None:
            self.SItool.done()

    def deleteDeconvolvers(self):
         for immod in range(0,len(self.SDtools)):
              self.SDtools[immod].done()

    def deleteNormalizers(self):
         for immod in range(0,len(self.PStools)):
            self.PStools[immod].done()

    def deleteIterBot(self):
         if self.IBtool != None:
              self.IBtool.done()

    def deleteCluster(self):
#         print 'no cluster to delete'
        return

    def initDefaults(self):
        # Reset globals/members
         self.NF=1
         self.stopMinor={'0':0}  # Flag to call minor cycle for this field or not.
         self.NN=1
         self.SItool=None
         self.SDtools=[]
         self.PStools=[]
         self.IBtool=None
    
#############################################

    def deleteTools(self):
         self.deleteImagers()
         self.deleteDeconvolvers()
         self.deleteNormalizers()
         self.deleteIterBot()
         self.initDefaults()
         self.deleteCluster()

#############################################

    def hasConverged(self):
        # Merge peak-res info from all fields to decide iteration parameters
         for immod in range(0,self.NF):
              #
              initrec =  self.SDtools[immod].initminorcycle() 
              
              self.IBtool.mergeinitrecord( initrec );
#              print "Peak res of field ",immod, " : " ,initrec['peakresidual']
#              casalog.post("["+self.allimpars[str(immod)]['imagename']+"] : Peak residual : %5.5f"%(initrec['peakresidual']), "INFO")

         self.runInteractiveGUI2()

        # Check with the iteration controller about convergence.
         stopflag = self.IBtool.cleanComplete()
         #print 'Converged : ', stopflag
         if( stopflag>0 ):
             #stopreasons = ['iteration limit', 'threshold', 'force stop','no change in peak residual across two major cycles']
             stopreasons = ['iteration limit', 'threshold', 'force stop','no change in peak residual across two major cycles', 'peak residual increased by more than 5 times']
             casalog.post("Reached global stopping criterion : " + stopreasons[stopflag-1], "INFO")

             # revert the current automask to the previous one 
             if self.iterpars['interactive']:
                 for immod in range(0,self.NF):
                     if self.alldecpars[str(immod)]['usemask']=='auto-thresh':
                        prevmask = self.allimpars[str(immod)]['imagename']+'.prev.mask'
                        if os.path.isdir(prevmask):
                          shutil.rmtree(self.allimpars[str(immod)]['imagename']+'.mask')
                          #shutil.copytree(prevmask,self.allimpars[str(immod)]['imagename']+'.mask')
                          shutil.move(prevmask,self.allimpars[str(immod)]['imagename']+'.mask')

         return (stopflag>0)

#############################################
    def runInteractiveGUI2(self):
        if self.iterpars['interactive'] == True:
            self.stopMinor = self.IBtool.pauseforinteraction()
            #print "Actioncodes in python : " , self.stopMinor

            #Check if force-stop has happened while savemodel != "none".
            # If so, warn the user that unless the Last major cycle has happened,
            # the model won't have been written into the MS, and to do a 'predict' run.
            if self.iterpars['savemodel'] != "none":
                all2=True;
                for akey in self.stopMinor:
                    all2 = all2 and self.stopMinor[akey]==2

                if all2==True:
                    if self.iterpars['savemodel'] == "modelcolumn":
                        wstr = "Saving model column"
                    else:
                        wstr = "Saving virtual model"
                    casalog.post("Model visibilities may not have been saved in the MS even though you have asked for it. Please check the logger for the phrases 'Run (Last) Major Cycle'  and  '" + wstr +"'. If these do not appear, then please save the model via a separate tclean run with niter=0,calcres=F,calcpsf=F. It will pick up the existing model from disk and save/predict it.   Reason for this : For performance reasons model visibilities are saved only in the last major cycle. If the X button on the interactive GUI is used to terminate a run before this automatically detected 'last' major cycle, the model isn't written. However, a subsequent tclean run as described above will predict and save the model. ","WARN")
                

#############################################
    def runInteractiveGUI(self):
        if self.iterpars['interactive'] == True:
            iterdetails = self.IBtool.getiterationdetails()
            for immod in range(0,self.NF):
                if self.stopMinor[str(immod)]==0 :
                    iterparsmod =  self.SDtools[immod].interactivegui( iterdetails ) 
                    #print 'Input iterpars : ', iterdetails['niter'], iterdetails['cycleniter'], iterdetails['threshold']
                    self.iterpars.update(iterparsmod) 
                    #print 'Output iterpars : ', self.iterpars['niter'],self.iterpars['cycleniter'],self.iterpars['threshold']
                    itbot = self.IBtool.setupiteration(iterpars=self.iterpars)

                    if 'actioncode' in iterparsmod :
                        self.stopMinor[str(immod)] = iterparsmod['actioncode']  # 0 or 1 or 2 ( old interactive viewer )

            alldone=True
            for immod in range(0,self.NF):
                alldone = alldone and (self.stopMinor[str(immod)]==2)
            if alldone==True:
                self.IBtool.changestopflag( True )
#            if self.stopMinor==[2]*self.NF:
#                self.IBtool.changestopflag( True )
             #itbot = self.IBtool.setupiteration(iterpars=self.iterpars)

#############################################
    def makePSF(self):

        self.makePSFCore()

        ### Gather PSFs (if needed) and normalize by weight
        for immod in range(0,self.NF):
            self.PStools[immod].gatherpsfweight() 
            self.PStools[immod].dividepsfbyweight()

#############################################

    def runMajorCycle(self):
        for immod in range(0,self.NF):
            self.PStools[immod].dividemodelbyweight()
            self.PStools[immod].scattermodel() 

        if self.IBtool != None:
            lastcycle = (self.IBtool.cleanComplete() > 0)
        else:
            lastcycle = True
        self.runMajorCycleCore(lastcycle)

        if self.IBtool != None:
            self.IBtool.endmajorcycle()
        ### Gather residuals (if needed) and normalize by weight
        for immod in range(0,self.NF):
            self.PStools[immod].gatherresidual() 
            self.PStools[immod].divideresidualbyweight()
            self.PStools[immod].multiplymodelbyweight()

#############################################
    def predictModel(self):
        for immod in range(0,self.NF):
            self.PStools[immod].dividemodelbyweight()
            self.PStools[immod].scattermodel() 

        self.predictModelCore()
##        self.SItool.predictmodel();

#############################################
    def dryGridding(self):
        self.SItool.drygridding(**(self.cfcachepars)) ;
#############################################
## Overloaded for parallel runs
    def fillCFCache(self):
        cfcName = self.allgridpars['0']['cfcache'];
        cflist=[];
        if (not (cfcName == '')):
            cflist=[f for f in os.listdir(cfcName) if re.match(r'CFS*', f)];
        #cflist = ["CFS_0_0_CF_0_0_0.im"];
        self.cfcachepars['cflist']=cflist;

        #self.SItool.fillcfcache(**(self.cfcachepars), self.allgridpars['0']['gridder'],cfcName);
        
        self.SItool.fillcfcache(cflist, self.allgridpars['0']['gridder'],
                                cfcName,
                                self.allgridpars['0']['psterm'],
                                self.allgridpars['0']['aterm']);
                  
#############################################
    def reloadCFCache(self):
        self.SItool.reloadcfcache();

#############################################
    def makePB(self):
        self.makePBCore()
        for immod in range(0,self.NF):
            self.PStools[immod].normalizeprimarybeam() 

#############################################
    def makePBCore(self):
        self.SItool.makepb()

#############################################

## Overloaded for parallel runs
    def setWeighting(self):
        ## Set weighting parameters, and all pars common to all fields.
        self.SItool.setweighting( **(self.weightpars) )
        
 #       print "get set density from python"
 #       self.SItool.getweightdensity()
 #       self.SItool.setweightdensity()

        
#############################################
## Overloaded for parallel runs
    def makePSFCore(self):
        self.SItool.makepsf()
#############################################
## Overloaded for parallel runs
    def runMajorCycleCore(self, lastcycle):
        self.SItool.executemajorcycle(controls={'lastcycle':lastcycle})
#############################################
## Overloaded for parallel runs
    def predictModelCore(self):
        self.SItool.predictmodel()
#############################################

    def runMinorCycle(self):
        # Get iteration control parameters
        iterbotrec = self.IBtool.getminorcyclecontrols()
        ##print "Minor Cycle controls : ", iterbotrec
        #
        # Run minor cycle
        self.ncycle+=1
        for immod in range(0,self.NF):  
            if self.stopMinor[str(immod)]<2 :
                exrec = self.SDtools[immod].executeminorcycle( iterbotrecord = iterbotrec )
                #print '.... iterdone for ', immod, ' : ' , exrec['iterdone']
                self.IBtool.mergeexecrecord( exrec )
                if 'SAVE_ALL_AUTOMASKS' in os.environ and os.environ['SAVE_ALL_AUTOMASKS']=="true":
                    maskname = self.allimpars[str(immod)]['imagename']+'.mask'
                    tempmaskname = self.allimpars[str(immod)]['imagename']+'.autothresh'+str(self.ncycle)
                    if os.path.isdir(maskname):
                        shutil.copytree(maskname, tempmaskname)
                
                # Some what duplicated as above but keep a copy of the previous mask
                # for interactive automask to revert to it if the current mask
                # is not used (i.e. reached deconvolution stopping condition).
                if self.iterpars['interactive'] and self.alldecpars[str(immod)]['usemask']=='auto-thresh':
                    maskname = self.allimpars[str(immod)]['imagename']+'.mask'
                    prevmaskname=self.allimpars[str(immod)]['imagename']+'.prev.mask'
                    if os.path.isdir(maskname):
                        if os.path.isdir(prevmaskname):
                            shutil.rmtree(prevmaskname)
                        shutil.copytree(maskname, prevmaskname)

#############################################
    def runMajorMinorLoops(self):
         self.runMajorCycle()
         while ( not self.hasConverged() ):
              self.runMinorCycle()
              self.runMajorCycle()

#############################################

    def plotReport( self, summ={} ,fignum=1 ):

        if not ( 'summaryminor' in summ and 'summarymajor' in summ and 'threshold' in summ and summ['summaryminor'].shape[0]==6 ):
            print('Cannot make summary plot. Please check contents of the output dictionary from tclean.')
            return summ

        import pylab as pl
        from numpy import max as amax

        # 0 : iteration number (within deconvolver, per cycle)
        # 1 : peak residual
        # 2 : model flux
        # 3 : cyclethreshold
        # 4 : deconvolver id
        # 5 : subimage id (channel, stokes..)

        pl.ioff()

        pl.figure(fignum)
        pl.clf();
        minarr = summ['summaryminor']
        if minarr.size==0:
            casalog.post("Zero iteration: no summary plot is generated.", "WARN")
        else:
	    iterlist = minarr[0,:]
	    eps=0.0
	    peakresstart=[]
	    peakresend=[]
	    modfluxstart=[]
	    modfluxend=[]
	    itercountstart=[]
	    itercountend=[]
	    peakresstart.append( minarr[1,:][0] )
	    modfluxstart.append( minarr[2,:][0] )
	    itercountstart.append( minarr[0,:][0] + eps )
	    peakresend.append( minarr[1,:][0] )
	    modfluxend.append( minarr[2,:][0] )
	    itercountend.append( minarr[0,:][0] + eps )
	    for ii in range(0,len(iterlist)-1):
		if iterlist[ii]==iterlist[ii+1]:
		    peakresend.append( minarr[1,:][ii] )
		    peakresstart.append( minarr[1,:][ii+1] ) 
		    modfluxend.append( minarr[2,:][ii] )
		    modfluxstart.append( minarr[2,:][ii+1] )
		    itercountend.append( iterlist[ii]-eps )
		    itercountstart.append( iterlist[ii]+eps )

	    peakresend.append( minarr[1,:][len(iterlist)-1] )
	    modfluxend.append( minarr[2,:][len(iterlist)-1] )
	    itercountend.append( minarr[0,:][len(iterlist)-1] + eps )

    #        pl.plot( iterlist , minarr[1,:] , 'r.-' , label='peak residual' , linewidth=1.5, markersize=8.0)
    #        pl.plot( iterlist , minarr[2,:] , 'b.-' , label='model flux' )
    #        pl.plot( iterlist , minarr[3,:] , 'g--' , label='cycle threshold' )

	    pl.plot( itercountstart , peakresstart , 'r.--' , label='peak residual (start)')
	    pl.plot( itercountend , peakresend , 'r.-' , label='peak residual (end)',linewidth=2.5)
	    pl.plot( itercountstart , modfluxstart , 'b.--' , label='model flux (start)' )
	    pl.plot( itercountend , modfluxend , 'b.-' , label='model flux (end)',linewidth=2.5 )
	    pl.plot( iterlist , minarr[3,:] , 'g--' , label='cycle threshold', linewidth=2.5 )
	    maxval = amax( minarr[1,:] )
	    maxval = max( maxval, amax( minarr[2,:] ) )
	    
	    bcols = ['b','g','r','y','c']
	    minv=1
	    niterdone = len(minarr[4,:])
	  
	    if len(summ['summarymajor'].shape)==1 and summ['summarymajor'].shape[0]>0 :       
		pl.vlines(summ['summarymajor'],0,maxval, label='major cycles', linewidth=2.0)

	    pl.hlines( summ['threshold'], 0, summ['iterdone'] , linestyle='dashed' ,label='threshold')
	
	    pl.xlabel( 'Iteration Count' )
	    pl.ylabel( 'Peak Residual (red), Model Flux (blue)' )

	    ax = pl.axes()
	    box = ax.get_position()
	    ax.set_position([box.x0, box.y0, box.width, box.height*0.8])

	    pl.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05),
		      ncol=3, fancybox=True, shadow=True)

	    pl.savefig('summaryplot_'+str(fignum)+'.png')
	    pl.ion()

        return summ;

#######################################################
#######################################################


#############################################
#############################################
## Parallelize only major cycle.
#############################################
class PyParallelContSynthesisImager(PySynthesisImager):

    def __init__(self,params=None):

         PySynthesisImager.__init__(self,params)

         self.PH = PyParallelImagerHelper()
         self.NN = self.PH.NN
         self.selpars = self.allselpars;
         self.allselpars = self.PH.partitionContDataSelection(self.allselpars)
         # self.allcflist = self.PH.partitionCFCacheList(self.cfcachepars['cflist']);
         # self.allcflist = self.PH.partitionCFCacheList(self.allgridpars['0']);
         self.listOfNodes = self.PH.getNodeList();

#############################################
    def initializeImagersBase(self,thisSelPars,partialSelPars):
        #
        # Start the imagers on all nodes.
        #
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("toolsi = casac.synthesisimager()", node) );
        self.PH.checkJobs(joblist);

        #
        # Select data.  If partialSelPars is True, use the thisSelPars
        # data structure as a list of partitioned selections.
        #
        joblist=[];
        nodes=self.listOfNodes;#[1];
        if (not partialSelPars):
            nodes = [1];
        for node in nodes:
            for mss in sorted( self.selpars.keys() ):
                if (partialSelPars):
                    selStr=str(thisSelPars[str(node-1)][mss]);
                else:
                    #joblist.append( self.PH.runcmd("toolsi.selectdata( "+str(thisSelPars[mss])+")", node) )
                    selStr=str(thisSelPars[mss]);
                joblist.append( self.PH.runcmd("toolsi.selectdata( "+selStr+")", node) )
        self.PH.checkJobs(joblist);

        #
        # Call defineimage at each node.
        #
        joblist=[];
        for node in nodes:
            ## For each image-field, define imaging parameters
            nimpars = copy.deepcopy(self.allimpars)
            #print "nimpars = ",nimpars;
            ngridpars = copy.deepcopy(self.allgridpars)
            for fld in range(0,self.NF):
                if self.NN>1:
                    nimpars[str(fld)]['imagename'] = self.PH.getpath(node) + '/' + nimpars[str(fld)]['imagename']+'.n'+str(node)

                joblist.append( self.PH.runcmd("toolsi.defineimage( impars=" + str( nimpars[str(fld)] ) 
                                               + ", gridpars=" + str( ngridpars[str(fld)] )   + ")", node ) )
        self.PH.checkJobs(joblist);
        
#############################################

    def initializeImagers(self):

        #---------------------------------------
        #  Check if cfcache exists.
        #
        cfCacheName=self.allgridpars['0']['cfcache'];
        
        if (not (cfCacheName == '')):
            cfcExists = (os.path.exists(cfCacheName) and os.path.isdir(cfCacheName));
        else:
            cfcExists = False;
        # print "##########################################"
        # print "CFCACHE = ",cfCacheName,cfcExists;
        # print "##########################################"

        # Initialize imagers with full data selection at each node.
        # This is required only for node-1 though (for dryGridding
        # later).
        self.initializeImagersBase(self.selpars,False);

        if (not cfcExists):
            self.dryGridding();
            self.fillCFCache();
#        self.reloadCFCache();

        # TRY: Start all over again!  This time do partial data
        # selection at each node using the allselpars data structure
        # which has the partitioned selection.
        self.deleteImagers();

        self.initializeImagersBase(self.allselpars,True);

######################################################################################################################################
        #---------------------------------------
        #  4. call setdata() for images on all nodes
        #
        # joblist=[];
        # for node in self.listOfNodes:
        #     ## Send in Selection parameters for all MSs in the list
        #     #### MPIInterface related changes (the -1 in the expression below)
        #     for mss in sorted( (self.allselpars[str(node-1)]).keys() ):
        #         joblist.append( self.PH.runcmd("toolsi.selectdata( "+str(self.allselpars[str(node-1)][mss])+")", node) )
        # self.PH.checkJobs(joblist);

        #---------------------------------------
        #  5. Call defineImage() on all nodes.  This sets up the FTMs.
        #
#         joblist=[];
#         for node in self.listOfNodes:
#             ## For each image-field, define imaging parameters
#             nimpars = copy.deepcopy(self.allimpars)
#             #print "nimpars = ",nimpars;
#             ngridpars = copy.deepcopy(self.allgridpars)
#             for fld in range(0,self.NF):
#                 if self.NN>1:
#                     nimpars[str(fld)]['imagename'] = self.PH.getpath(node) + '/' + nimpars[str(fld)]['imagename']+'.n'+str(node)
# ###                    nimpars[str(fld)]['imagename'] = self.allnormpars[str(fld)]['workdir'] + '/' + nimpars[str(fld)]['imagename']+'.n'+str(node)
# ###                    nimpars[str(fld)]['imagename'] = nimpars[str(fld)]['imagename']+'.n'+str(node)

# #                    ngridpars[str(fld)]['cfcache'] = ngridpars[str(fld)]['cfcache']+'.n'+str(node)
#                     # # Give the same CFCache name to all nodes
#                     ngridpars[str(fld)]['cfcache'] = ngridpars[str(fld)]['cfcache'];

#                 joblist.append( self.PH.runcmd("toolsi.defineimage( impars=" + str( nimpars[str(fld)] ) + ", gridpars=" + str( ngridpars[str(fld)] )   + ")", node ) )
#         self.PH.checkJobs(joblist);

        #---------------------------------------
        #  6. If cfcache does not exist, call fillCFCache()
        #       This will fill the "empty" CFCache in parallel
        #  7. Now call reloadCFCache() on all nodes.
        #     This reloads the latest cfcahce.



        # TRY: Start all over again!
        # self.deleteImagers();

        # joblist=[]

        # for node in self.listOfNodes:
        #     joblist.append( self.PH.runcmd("toolsi = casac.synthesisimager()", node) );
        # self.PH.checkJobs(joblist);

        # joblist=[];
        # nodes=self.listOfNodes;#[1];
        # for node in nodes:
        #     for mss in sorted( (self.allselpars[str(node-1)]).keys() ):
        #         joblist.append( self.PH.runcmd("toolsi.selectdata( "+str(self.allselpars[str(node-1)][mss])+")", node) )
        #             # for mss in sorted( self.selpars.keys() ):
        #             #     joblist.append( self.PH.runcmd("toolsi.selectdata( "+str(self.selpars[mss])+")", node) )
        # self.PH.checkJobs(joblist);

        # joblist=[];
        # for node in self.listOfNodes:
        #     nimpars = copy.deepcopy(self.allimpars)
        #     ngridpars = copy.deepcopy(self.allgridpars)
        #     for fld in range(0,self.NF):
        #         if self.NN>1:
        #             nimpars[str(fld)]['imagename'] = self.PH.getpath(node) + '/' + nimpars[str(fld)]['imagename']+'.n'+str(node)
        #             # # Give the same CFCache name to all nodes
        #             ngridpars[str(fld)]['cfcache'] = ngridpars[str(fld)]['cfcache'];

        #         joblist.append( self.PH.runcmd("toolsi.defineimage( impars=" + str( nimpars[str(fld)] ) + ", gridpars=" + str( ngridpars[str(fld)] )   + ")", node ) )
        # self.PH.checkJobs(joblist);


#############################################

    def initializeNormalizers(self):
        for immod in range(0,self.NF):
            self.PStools.append(casac.synthesisnormalizer())
            normpars = copy.deepcopy( self.allnormpars[str(immod)] )
            partnames = []
            if(self.NN>1):
#                if not shutil.os.path.exists(normpars['workdir']):
#                    shutil.os.system('mkdir '+normpars['workdir'])
                #### MPIInterface related changes
                #for node in range(0,self.NN):
                for node in self.listOfNodes:
                    onename = self.allimpars[str(immod)]['imagename']+'.n'+str(node)
                    partnames.append( self.PH.getpath(node) + '/' + onename  )
##                    partnames.append( normpars['workdir'] + '/' + onename  )
##                    partnames.append( onename  )
                    self.PH.deletepartimages( self.PH.getpath(node), onename ) # To ensure restarts work properly.
                normpars['partimagenames'] = partnames
            self.PStools[immod].setupnormalizer(normpars=normpars)


#############################################
    def setWeighting(self):

        ## Set weight parameters and accumulate weight density (natural)
        joblist=[];
        for node in self.listOfNodes:
            ## Set weighting pars
            joblist.append( self.PH.runcmd("toolsi.setweighting( **" + str(self.weightpars) + ")", node ) )
        self.PH.checkJobs( joblist )

        ## If only one field, do the get/gather/set of the weight density.
        if self.NF == 1 and self.allimpars['0']['stokes']=="I":   ## Remove after gridded wts appear for all fields correctly (i.e. new FTM).
   
          if self.weightpars['type'] != 'natural' :  ## For natural, this array isn't created at all.
                                                                       ## Remove when we switch to new FTM

            casalog.post("Gathering/Merging/Scattering Weight Density for PSF generation","INFO")

            joblist=[];
            for node in self.listOfNodes:
                joblist.append( self.PH.runcmd("toolsi.getweightdensity()", node ) )
            self.PH.checkJobs( joblist )

           ## gather weightdensity and sum and scatter
            print("******************************************************")
            print(" gather and scatter now ")
            print("******************************************************")
            for immod in range(0,self.NF):
                self.PStools[immod].gatherweightdensity()
                self.PStools[immod].scatterweightdensity()

           ## Set weight density for each nodel
            joblist=[];
            for node in self.listOfNodes:
                joblist.append( self.PH.runcmd("toolsi.setweightdensity()", node ) )
            self.PH.checkJobs( joblist )



    def deleteImagers(self):
         self.PH.runcmd("toolsi.done()")

    def deleteCluster(self):
         self.PH.takedownCluster()
    
# #############################################
    def dryGridding(self):
        nodes=[1];
        joblist=[];
        for node in nodes:
            dummy=[''];
            cmd = "toolsi.drygridding("+str(dummy)+")";
            joblist.append(self.PH.runcmd(cmd,node));
        self.PH.checkJobs(joblist);

#############################################
    def reloadCFCache(self):
        joblist=[];
        for node in self.listOfNodes:
            cmd = "toolsi.reloadcfcache()";
            print("CMD = ",node," ",cmd);
            joblist.append(self.PH.runcmd(cmd,node));
        self.PH.checkJobs(joblist);
#############################################
    def fillCFCache(self):
        #print "-----------------------fillCFCache------------------------------------"
        # cflist=[f for f in os.listdir(self.allgridpars['cfcache']) if re.match(r'CFS*', f)];
        # partCFList = 
        allcflist = self.PH.partitionCFCacheList(self.allgridpars['0']);
        cfcPath = "\""+str(self.allgridpars['0']['cfcache'])+"\"";
        ftmname = "\""+str(self.allgridpars['0']['gridder'])+"\"";
        psTermOn = str(self.allgridpars['0']['psterm']);
        aTermOn = str(self.allgridpars['0']['aterm']);
        #aTermOn = str(True);
        # print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@";
        # print "AllCFList = ",allcflist;
        m = len(allcflist);
        # print "No. of nodes used: ", m,cfcPath,ftmname;
        # print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@";

        joblist=[];
        for node in self.listOfNodes[:m]:
            #print "#!$#!%#!$#@$#@$ ",allcflist;
            cmd = "toolsi.fillcfcache("+str(allcflist[node])+","+str(ftmname)+","+str(cfcPath)+","+psTermOn+","+aTermOn+")";
            # print "CMD = ",node," ",cmd;
            joblist.append(self.PH.runcmd(cmd,node));
        self.PH.checkJobs(joblist);

        # Linear code
        # cfcName = self.allgridpars['0']['cfcache'];
        # cflist=[f for f in os.listdir(cfcName) if re.match(r'CFS*', f)];
        # self.cfcachepars['cflist']=cflist;
        # self.SItool.fillcfcache(**(self.cfcachepars)) ;
#############################################
    def makePSFCore(self):
        ### Make PSFs
        joblist=[]
        #### MPIInterface related changes
        #for node in range(0,self.PH.NN):
        for node in self.listOfNodes:
             joblist.append( self.PH.runcmd("toolsi.makepsf()",node) )
        self.PH.checkJobs( joblist ) # this call blocks until all are done.

#############################################
    def makePBCore(self):
        joblist=[]
        # Only one node needs to make the PB. It reads the freq from the image coordsys
        joblist.append( self.PH.runcmd("toolsi.makepb()",self.listOfNodes[0]) )
        self.PH.checkJobs( joblist )

#############################################

    def runMajorCycleCore(self, lastcycle):
        casalog.post("-----------------------------  Running Parallel Major Cycle ----------------------------","INFO")
        ### Run major cycle
        joblist=[]
        #### MPIInterface related changes
        #for node in range(0,self.PH.NN):
        for node in self.listOfNodes:
             joblist.append( self.PH.runcmd("toolsi.executemajorcycle(controls={'lastcycle':"+str(lastcycle)+"})",node) )
        self.PH.checkJobs( joblist ) # this call blocks until all are done.

#############################################
    def predictModelCore(self):
        joblist=[]
        #### MPIInterface related changes
        #for node in range(0,self.PH.NN):
        for node in self.listOfNodes:
             joblist.append( self.PH.runcmd("toolsi.predictmodel()",node) )
        self.PH.checkJobs( joblist ) # this call blocks until all are done.

#############################################
# Parallelize both the major and minor cycle for Cube imaging
# Run a separate instance of PySynthesisImager on each node.
#### ( later, use the live-object interface of ImStore to reference-break the cubes )
#### For nprocesses > nnodes, run the whole 'clean' loop multiple times. 
#############################################
class PyParallelCubeSynthesisImager():

    def __init__(self,params=None):

        self.params=params

        allselpars = params.getSelPars()
        allimagepars = params.getImagePars()
        self.allinimagepars = copy.deepcopy(allimagepars)
        self.allgridpars = params.getGridPars()
        self.allnormpars = params.getNormPars()
        self.weightpars = params.getWeightPars()
        self.decpars = params.getDecPars()
        self.iterpars = params.getIterPars()
        alldataimpars={}
         
        self.PH = PyParallelImagerHelper()
        self.NN = self.PH.NN
        self.NF = len(list(allimagepars.keys()))
        self.listOfNodes = self.PH.getNodeList();
        ## Partition both data and image coords the same way.
        #self.allselpars = self.PH.partitionCubeDataSelection(allselpars)
        #self.allimpars = self.PH.partitionCubeDeconvolution(allimagepars)

        # to define final image coordinates, run selecdata and definemage
        self.SItool = casac.synthesisimager()
        #print "allselpars=",allselpars
        for mss in sorted( allselpars.keys() ):
            self.SItool.selectdata( allselpars[mss] )
        for fid in sorted( allimagepars.keys() ):
            self.SItool.defineimage( allimagepars[fid], self.allgridpars[fid] )
            # insert coordsys record in imagepars 
            # partionCubeSelection works per field ...
            allimagepars[fid]['csys'] = self.SItool.getcsys()
            if allimagepars[fid]['nchan'] == -1:
                allimagepars[fid]['nchan'] = self.SItool.updatenchan()
            alldataimpars[fid] = self.PH.partitionCubeSelection(allselpars,allimagepars[fid])

        #print "********************** ", alldataimpars.keys()
        #for kk in alldataimpars.keys():
        #    print "KEY : ", kk , " --->", alldataimpars[kk].keys()

        # reorganize allselpars and allimpars for partitioned data        
        synu = casac.synthesisutils()
        self.allselpars={}
        self.allimpars={}
        ###print "self.listOfNodes=",self.listOfNodes
        # Repack the data/image parameters per node
        #  - internally it stores zero-based node ids
        #  
        for ipart in self.listOfNodes:
            # convert to zero-based indexing for nodes
            nodeidx = str(ipart-1)
            tnode = str(ipart)
            selparsPerNode= {tnode:{}}
            imparsPerNode= {tnode:{}}
            for fid in allimagepars.keys():
                for ky in alldataimpars[fid][nodeidx].keys():
                    selparsPerNode[tnode]={}
                    if ky.find('ms')==0:
                        # data sel per field
                        selparsPerNode[tnode][ky] = alldataimpars[fid][nodeidx][ky].copy();
                        if alldataimpars[fid][nodeidx][ky]['spw']=='-1':
                            selparsPerNode[tnode][ky]['spw']=''
                        else: 
                            # remove chan selections (will be adjusted by tuneSelectData)
                            newspw=selparsPerNode[tnode][ky]['spw']
                            newspwlist = newspw.split(',')
                            spwsOnly = ''
                            for sp in newspwlist:
                                if spwsOnly!='': spwsOnly+=','
                                spwsOnly+=sp.split(':')[0]   
                            selparsPerNode[tnode][ky]['spw']=spwsOnly

                imparsPerNode[tnode][fid] = allimagepars[fid].copy()
                imparsPerNode[tnode][fid]['csys'] = alldataimpars[fid][nodeidx]['coordsys'].copy()
                imparsPerNode[tnode][fid]['nchan'] = alldataimpars[fid][nodeidx]['nchan']
                imparsPerNode[tnode][fid]['imagename'] = imparsPerNode[tnode][fid]['imagename'] + '.n'+str(tnode) 

                # skip this for now (it is not working properly, but should not affect results without this)
                #imparsPerNode[tnode][fid]=synu.updateimpars(imparsPerNode[tnode][fid])
            self.allselpars.update(selparsPerNode)
            self.allimpars.update(imparsPerNode)


        #print "****** SELPARS in init **********", self.allselpars
        #print "****** SELIMPARS in init **********", self.allimpars
        
        joblist=[]
        #### MPIInterface related changes
        #for node in range(0,self.NN):
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("from refimagerhelper import ImagerParameters, PySynthesisImager", node) )
        self.PH.checkJobs( joblist )

        joblist=[]
        #### MPIInterface related changes
        #for node in range(0,self.NN):
        for node in self.listOfNodes:

            joblist.append( self.PH.runcmd("paramList = ImagerParameters()", node) )
            joblist.append( self.PH.runcmd("paramList.setSelPars("+str(self.allselpars[str(node)])+")", node) )
            joblist.append( self.PH.runcmd("paramList.setImagePars("+str(self.allimpars[str(node)])+")", node) )

            joblist.append( self.PH.runcmd("paramList.setGridPars("+str(self.allgridpars)+")", node) )
            joblist.append( self.PH.runcmd("paramList.setWeightPars("+str(self.weightpars)+")", node) )
            joblist.append( self.PH.runcmd("paramList.setDecPars("+str(self.decpars)+")", node) )
            joblist.append( self.PH.runcmd("paramList.setIterPars("+str(self.iterpars)+")", node) )
            joblist.append( self.PH.runcmd("paramList.setNormPars("+str(self.allnormpars)+")", node) )

            joblist.append( self.PH.runcmd("paramList.checkParameters()", node) )

            joblist.append( self.PH.runcmd("imager = PySynthesisImager(params=paramList)", node) )

        self.PH.checkJobs( joblist )

    def initializeImagers(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.initializeImagers()", node) )
        self.PH.checkJobs( joblist )

    def initializeDeconvolvers(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.initializeDeconvolvers()", node) )
        self.PH.checkJobs( joblist )

    def initializeNormalizers(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.initializeNormalizers()", node) )
        self.PH.checkJobs( joblist )

    def setWeighting(self):
        ## Set weight parameters and accumulate weight density (natural)
        joblist=[];
        for node in self.listOfNodes:
            ## Set weighting pars
            joblist.append( self.PH.runcmd("imager.setWeighting()", node ) )
        self.PH.checkJobs( joblist )


    def initializeIterationControl(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.initializeIterationControl()", node) )
        self.PH.checkJobs( joblist )

    def makePSF(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.makePSF()", node) )
        self.PH.checkJobs( joblist )

    def runMajorMinorLoops(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.runMajorMinorLoops()", node) )
        self.PH.checkJobs( joblist )

    def runMajorCycle(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.runMajorCycle()", node) )
        self.PH.checkJobs( joblist )

    def runMinorCycle(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.runMinorCycle()", node) )
        self.PH.checkJobs( joblist )

    ## Merge the results from all pieces. Maintain an 'active' list of nodes...
    def hasConverged(self):
        self.PH.runcmdcheck("rest = imager.hasConverged()")

        retval = True
        for node in self.listOfNodes:
             rest = self.PH.pullval("rest", node )
             retval = retval and rest[node]
             print("Node " , node , " converged : ", rest[node]);

        return retval

    def predictModel(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.predictmodel()", node) )
        self.PH.checkJobs( joblist )

    def restoreImages(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.restoreImages()", node) )
        self.PH.checkJobs( joblist )

    def makePB(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.makePB()", node) )
        self.PH.checkJobs( joblist )

    def concatImages(self, type='virtualnomove'):
        import subprocess
        imtypes=['image','psf','model','residual','mask','pb', 'pbcor', 'weight', 'sumwt']
        for immod in range(0,self.NF):
            for ext in imtypes:
                subimliststr="'"
                concatimname=self.allinimagepars[str(immod)]['imagename']+'.'+ ext
                distpath = os.getcwd()
                fullconcatimname = distpath+'/'+concatimname
                for node in self.listOfNodes:
                    rootimname=self.allinimagepars[str(immod)]['imagename']+'.n'+str(node)
                    fullimname =  self.PH.getpath(node) + '/' + rootimname 
                    if (os.path.exists(fullimname+'.'+ext)):
                        subimliststr+=fullimname+'.'+ext+' '
                subimliststr+="'"
                if subimliststr!="''":
                    # parent images need to be cleaned up for restart=T
                    if self.allinimagepars[str(immod)]['restart'] and os.path.exists(fullconcatimname):
                        try:
                            casalog.post("Cleaning up the existing "+fullconcatimname,"DEBUG")
                            shutil.rmtree(fullconcatimname)
                        except:
                            casalog.post("Cleaning up the existing file named "+fullconcatimname,"DEBUG")
                            os.remove(fullconcatimname)
                    cmd = 'imageconcat inimages='+subimliststr+' outimage='+"'"+fullconcatimname+"'"+' type='+type      
                    # run virtual concat
                    ret=os.system(cmd)
                    if ret!=0:
                        casalog.post("concatenation of "+concatimname+" failed","WARN")
             


    def getSummary(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("summ = imager.getSummary("+str(node)+")", node) )
        self.PH.checkJobs( joblist )

        fullsumm={}
        for node in self.listOfNodes:
             summ = self.PH.pullval("summ", node )
             fullsumm["node"+str(node)] = summ

        return fullsumm

    def deleteTools(self):
        joblist=[]
        for node in self.listOfNodes:
            joblist.append( self.PH.runcmd("imager.deleteTools()", node) )
        self.PH.checkJobs( joblist )

#############################################
#############################################
#############################################

class PyParallelDeconvolver(PySynthesisImager):

    def __init__(self,params):

        PySynthesisImager.__init__(self,params)

        self.PH = PyParallelImagerHelper()
        self.NF = len( list(allimpars.keys()) )
        self.listOfNodes = self.PH.getNodeList();
        #### MPIInterface related changes
        #self.NN = self.PH.NN
        self.NN = len(self.listOfNodes);
        if self.NF != self.NN:
             print('For now, cannot handle nfields != nnodes. Will implement round robin allocation later.')
             print('Using only ', self.NN, ' fields and nodes')
             

#############################################
    def initializeDeconvolvers(self):
         joblist=[]
         #### MPIInterface related changes
         #for immod in range(0,self.NF):
         for immod in self.listOfNodes:
              self.PH.runcmd("toolsd = casac.synthesisdeconvolver()", immod )
              joblist.append( self.PH.runcmd("toolsd.setupdeconvolution(decpars="+ str(self.alldecpars[str(immod)]) +")", immod ) )
         self.PH.checkJobs( joblist )

#############################################
    def deleteDeconvolvers(self):
         self.PH.runcmd("toolsd.done()")
              
#############################################
    def restoreImages(self):
         self.PH.runcmdcheck("toolsd.restore()")

#############################################
#############################################

    def hasConverged(self):
        # Merge peak-res info from all fields to decide iteration parameters
        self.PH.runcmdcheck("initrec = toolsd.initminorcycle()")

        #### MPIInterface related changes
        #for immod in range(0,self.NF):
        for immod in self.listOfNodes:
             retrec = self.PH.pullval("initrec", immod )
             self.IBtool.mergeinitrecord( retrec[immod] )
#             print "Peak res of field ",immod, " on node ", immod , ": " ,retrec[immod]['peakresidual']
#             casalog.post("["+self.allimpars[str(immod)]['imagename']+"] : Peak residual : %5.5f"%(initrec['peakresidual']), "INFO")

        # Check with the iteration controller about convergence.
        stopflag = self.IBtool.cleanComplete()
        print('Converged : ', stopflag)
        if( stopflag>0 ):
            stopreasons = ['iteration limit', 'threshold', 'force stop','no change in peak residual across two major cycles','peak residual increased by more than 5 times']
            casalog.post("Reached global stopping criterion : " + stopreasons[stopflag-1], "INFO")
            if self.iterpars['interactive']:
                for immod in range(0,self.listOfNodes):
                    if self.alldecpars[str(immod)]['usemask']=='auto-thresh':
                        prevmask = self.allimpars[str(immod)]['imagename']+'.prev.mask'
                        if os.path.isdir(prevmask):
                            shutil.rmtree(self.allimpars[str(immod)]['imagename']+'.mask')
                        shutil.move(prevmask,self.allimpars[str(immod)]['imagename']+'.mask')
        return (stopflag>0)


#############################################

    def runMinorCycle(self):
        # Get iteration control parameters
        iterbotrec = self.IBtool.getminorcyclecontrols()
        # Run minor cycle
        self.PH.CL.push( iterbotrec = iterbotrec )

        self.PH.runcmdcheck( "exrec = toolsd.executeminorcycle(iterbotrec)" )

        #### MPIInterface related changes
        #for immod in range(0,self.NF):
        for immod in self.listOfNodes:
             retrec = self.PH.pullval("exrec", immod )
             self.IBtool.mergeexecrecord( retrec[immod] )

#############################################
#############################################



#############################################
###  Parallel Imager Helper.
#############################################
#casalog.post('Using clustermanager from MPIInterface', 'WARN')
from mpi4casa.MPIInterface import MPIInterface as mpi_clustermanager

class PyParallelImagerHelper():

    def __init__(self):

        ############### Cluster Info
         self.CL=None
         self.sc=None
         self.nodeList=None;
         # Initialize cluster, and partitioning.
        ############### Number of nodes to parallelize on

         # self.nodeList gets filled by setupCluster()
         self.NN = self.setupCluster()

    def getNodeList(self):
        return self.nodeList;

#############################################
    def chunkify(self,lst,n):
        return [ lst[i::n] for i in range(n) ]

    def partitionCFCacheList(self,gridPars):

        cfcName = gridPars['cfcache'];
        cflist=[];
        if (not (cfcName == '')):
            cflist=[f for f in os.listdir(cfcName) if re.match(r'CFS*', f)];
        nCF = len(cflist);
        nProcs=len(self.nodeList);
        
        if (nProcs > nCF):
            n=nCF;
        else:
            n=nProcs;
        if (nCF > 0):
            casalog.post("########################################################");
            casalog.post("nCF = " + str(nCF) + " nProcs = " + str(n) + " NodeList=" + str(self.nodeList));
            casalog.post("########################################################");
        xx=self.chunkify(cflist,n);
        allcfs={};
        for i in range(n):
            allcfs[i+1]=xx[i];

        return allcfs;
#############################################
# The above version works better (better balanced chunking).
# Keeping the code below in the file sometime, just in case...(SB).
    # def partitionCFCacheList(self,gridPars):

    #     cfcName = gridPars['cfcache'];
    #     cflist=[];
    #     if (not (cfcName == '')):
    #         cflist=[f for f in os.listdir(cfcName) if re.match(r'CFS*', f)];

    #     nCF = len(cflist);
    #     nProcs=len(self.nodeList);
        
    #     print "########################################################"
    #     print "nCF = ",nCF," nProcs = ",nProcs," NodeList=",self.nodeList;
    #     print "########################################################"

    #     #n0=int(nCF/self.NN);
    #     n0=int(float(nCF)/nProcs+0.5);
    #     if (nProcs >= nCF):
    #         n0 = 1;
    #     allcfs = {};
    #     nUsed=0; i=1;
    #     while (nUsed < nCF):
    #         m = nUsed+n0;
    #         if (m > nCF): 
    #     	m=nCF;
    #         allcfs[i]=cflist[nUsed:m];
    #         nUsed = m;
    #         if (i >= nProcs):
    #             break;
    #         i=i+1;
    #     if (nUsed < nCF):
    #         allcfs[nProcs].append(cflist[i]);
    #     return allcfs;
            
#############################################
## Very rudimentary partitioning - only for tests. The actual code needs to go here.
    def partitionContDataSelection(self,oneselpars={}):

        synu = casac.synthesisutils()
        allselpars =  synu.contdatapartition( oneselpars , self.NN )
        synu.done()

        print('Partitioned Selection : ', allselpars)
        return allselpars

#############################################
## Very rudimentary partitioning - only for tests. The actual code needs to go here.
    def partitionCubeDataSelection(self,oneselpars={}):

        synu = casac.synthesisutils()
        allselpars =  synu.cubedatapartition( oneselpars , self.NN )
        synu.done()

        print('Partitioned Selection : ', allselpars)
        return allselpars

#############################################
    def partitionCubeDeconvolution(self,impars={}):

        synu = casac.synthesisutils()
        allimpars =  synu.cubeimagepartition( impars , self.NN )
        synu.done()

        print('ImSplit : ', allimpars)
        return allimpars

#############################################
    def partitionCubeSelection(self, oneselpars={}, oneimpars={}):
        incsys = oneimpars['csys']
        nchan = oneimpars['nchan']
        synu = casac.synthesisutils()
        allpars = synu.cubedataimagepartition(oneselpars, incsys, self.NN, nchan)
        synu.done()

        #print "Cube Data/Im partitioned selection :", allpars
        return allpars

#############################################
    def setupCluster(self):
        # Initialize cluster

        # * Terminal: Client logs + Server logs
        # * casapy-<timestamp>.log: Client logs
        # * casapy-<timestamp>.log-server-<rank>-host-<hostname>-pid-<pid>: Server logs 
        mpi_clustermanager.set_log_mode('redirect');

        self.sc=mpi_clustermanager.getCluster()
        self.sc.set_log_level('DEBUG')

        self.CL=self.sc._cluster
        self.nodeList = self.CL.get_engines();
        numproc=len(self.CL.get_engines())
        numprocperhost=len(self.nodeList)/len(self.nodeList) if (len(self.nodeList) >0 ) else 1

        owd=os.getcwd()
        self.CL.pgc('import os')
        self.CL.pgc('from numpy import array,int32')
        self.CL.pgc('os.chdir("'+owd+'")')
        os.chdir(owd)
        print("Setting up ", numproc, " engines.")
        return numproc

#############################################
    def takedownCluster(self):
        # Check that all nodes have returned, before stopping the cluster
         self.checkJobs()
         print('Ending use of cluster, but not closing it. Call clustermanager.stop_cluster() to close it if needed.')
#         self.sc.stop_cluster()
         self.CL=None
         self.sc=None

#############################################
    # This is a blocking call that will wait until jobs are done.
    def checkJobs(self,joblist=[]):
        #### MPIInterface related changes
        numcpu = len(self.nodeList)
        
        if len(joblist)==0:
             joblist = list(range(numcpu))
             #for k in range(numcpu):
             for k in self.nodeList:
                 joblist[k-1] = self.CL.odo('casalog.post("node '+str(k)+' has completed its job")', k)

        print('Blocking for nodes to finish')
        over=False
        while(not over):
            overone=True
            time.sleep(1)
            for k in range(len(joblist)):
                try:
                    overone =  self.CL.check_job(joblist[k],False) and overone
                except Exception as e:
                     raise Exception(e)
            over = overone
        print('...done')

#############################################
    def runcmd(self, cmdstr="", node=-1):
         if node >= 0:
              return self.CL.odo( cmdstr , node)
         else:
              self.CL.pgc( cmdstr )

#############################################
    def runcmdcheck(self, cmdstr):
         joblist=[]
         #### MPIInterface related changes
         #for node in range(0,self.NN):
         for node in self.nodeList:
              joblist.append( self.CL.odo( cmdstr, node ) )
         self.checkJobs( joblist )

#############################################
    def pullval(self, varname="", node=0):
         return self.CL.pull( varname , node )

#############################################
    def getpath(self, node=0):
        enginepath = self.sc.get_engine_store(node)
        if enginepath==None:
            return ""
        else:
            return enginepath
#############################################
    def deletepartimages(self, dirname, imname):
        namelist = shutil.fnmatch.filter( os.listdir(dirname), imname+".*" )
        #print "Deleting : ", namelist, ' from ', dirname, ' starting with ', imname
        for aname in namelist:
            shutil.rmtree( dirname + "/" + aname )
##########################################################################################



######################################################
######################################################
######################################################
######################################################

class ImagerParameters():
    def __init__(self, 

                 ## Data Selection
                 msname='',
                 field='',
                 spw='',
                 timestr='',
                 uvdist='',
                 antenna='',
                 scan='',
                 obs='',
                 state='',
                 datacolumn='corrected',

                 ## Image Definition
                 imagename='', 
                 imsize=[1,1], 
                 cell=[10.0,10.0],
                 phasecenter='',
                 stokes='I',
                 projection='SIN',
                 startmodel='', 

                 ## Spectral Parameters
                 specmode='mfs', 
                 reffreq='',
                 nchan=1, 
                 start='', 
                 width='',
                 outframe='LSRK', 
                 veltype='radio', 
                 restfreq=[''],
                 sysvel='', 
                 sysvelframe='',
                 interpolation='nearest',

                 gridder="standard",
#                 ftmachine='gridft', 
                 facets=1, 
                 chanchunks=1,

                 wprojplanes=1,

                 vptable="",

                 aterm=True,
                 psterm=True,
                 mterm=True,
                 wbawp = True,
                 cfcache = "",
                 dopointing = False,
                 dopbcorr = True,
                 conjbeams = True,
                 computepastep =360.0,
                 rotatepastep =360.0,
                 
                 pblimit=0.01,
                 normtype='flatnoise',

                 outlierfile='',
                 restart=True,

                 weighting='natural', 
                 robust=0.5,
                 npixels=0,
                 uvtaper=[],

                 niter=0, 
                 cycleniter=0, 
                 loopgain=0.1,
                 threshold='0.0Jy',
                 cyclefactor=1.0,
                 minpsffraction=0.1,
                 maxpsffraction=0.8,
                 interactive=False,

                 deconvolver='hogbom',
                 scales=[],
                 nterms=1,
                 scalebias=0.6,
                 restoringbeam=[],
#                 mtype='default',

                 usemask='user',
                 mask='',
                 pbmask=0.0,
                 maskthreshold='',
                 maskresolution='',
                 nmask=0,
                 autoadjust=False,

                 sidelobethreshold=5.0,
                 noisethreshold=3.0,
                 lownoisethreshold=3.0,
                 smoothfactor=1.0,
                 minbeamfrac=0.3,
                 cutthreshold=0.01,

#                 usescratch=True,
#                 readonly=True,
                 savemodel="none",

                 workdir='',

                 ## CFCache params
                 cflist=[]
                 ):

        self.defaultKey="0";

        ## Selection params. For multiple MSs, all are lists.
        ## For multiple nodes, the selection parameters are modified inside PySynthesisImager
        self.allselpars = {'msname':msname, 'field':field, 'spw':spw, 'scan':scan,
                           'timestr':timestr, 'uvdist':uvdist, 'antenna':antenna, 'obs':obs,'state':state,
                           'datacolumn':datacolumn,
                           'savemodel':savemodel }
#                           'usescratch':usescratch, 'readonly':readonly}

        ## Imaging/deconvolution parameters
        ## The outermost dictionary index is image field. 
        ## The '0' or main field's parameters come from the task parameters
        ## The outlier '1', '2', ....  parameters come from the outlier file
        self.outlierfile = outlierfile
        ## Initialize the parameter lists with the 'main' or '0' field's parameters
        ######### Image definition
        self.allimpars = { self.defaultKey :{'imagename':imagename, 'nchan':nchan, 'imsize':imsize, 
                                 'cell':cell, 'phasecenter':phasecenter, 'stokes': stokes,
                                 'specmode':specmode, 'start':start, 'width':width, 'veltype':veltype,
                                 'nterms':nterms,'restfreq':restfreq, 
                                 'outframe':outframe, 'reffreq':reffreq, 'sysvel':sysvel, 'sysvelframe':sysvelframe,
                                 'projection':projection,
                                 'restart':restart, 'startmodel':startmodel,'deconvolver':deconvolver}    }
        ######### Gridding
        self.allgridpars = { self.defaultKey :{'gridder':gridder,
                                   'aterm': aterm, 'psterm':psterm, 'mterm': mterm, 'wbawp': wbawp, 
                                   'cfcache': cfcache,'dopointing':dopointing, 'dopbcorr':dopbcorr, 
                                   'conjbeams':conjbeams, 'computepastep':computepastep,
                                   'rotatepastep':rotatepastep, #'mtype':mtype, # 'weightlimit':weightlimit,
                                   'facets':facets,'chanchunks':chanchunks,
                                   'interpolation':interpolation, 'wprojplanes':wprojplanes,
                                   'deconvolver':deconvolver, 'vptable':vptable }     }
        ######### weighting
        self.weightpars = {'type':weighting,'robust':robust, 'npixels':npixels,'uvtaper':uvtaper}

        ######### Normalizers ( this is where flat noise, flat sky rules will go... )
        self.allnormpars = { self.defaultKey : {#'mtype': mtype,
                                 'pblimit': pblimit,'nterms':nterms,'facets':facets,
                                 'normtype':normtype, 'workdir':workdir,
                                 'deconvolver':deconvolver}     }

        ######### Deconvolution
        self.alldecpars = { self.defaultKey: { 'id':0, 'deconvolver':deconvolver, 'nterms':nterms, 
                                    'scales':scales, 'scalebias':scalebias, 'restoringbeam':restoringbeam, 'usemask':usemask, 
                                    'mask':mask, 'pbmask':pbmask, 'maskthreshold':maskthreshold,
                                    'maskresolution':maskresolution, 'nmask':nmask,'autoadjust':autoadjust,
                                    'sidelobethreshold':sidelobethreshold, 'noisethreshold':noisethreshold,
                                    'lownoisethreshold':lownoisethreshold, 'smoothfactor':smoothfactor,
                                    'minbeamfrac':minbeamfrac, 'cutthreshold':cutthreshold,
                                    'interactive':interactive, 'startmodel':startmodel} }

        ######### Iteration control. 
        self.iterpars = { 'niter':niter, 'cycleniter':cycleniter, 'threshold':threshold, 
                          'loopgain':loopgain, 'interactive':interactive,
                          'cyclefactor':cyclefactor, 'minpsffraction':minpsffraction, 
                          'maxpsffraction':maxpsffraction, 'savemodel':savemodel}

        ######### CFCache params. 
        self.cfcachepars = {'cflist': cflist};


        #self.reusename=reuse

        ## List of supported parameters in outlier files.
        ## All other parameters will default to the global values.
        self.outimparlist = ['imagename','nchan','imsize','cell','phasecenter','startmodel',
                             'start','width',
                             'nterms','reffreq','specmode']
        self.outgridparlist = ['gridder','deconvolver','wprojplanes']
        self.outweightparlist=[]
        self.outdecparlist=['deconvolver','startmodel','nterms','usemask','mask']
        self.outnormparlist=['deconvolver','weightlimit','nterms']
#        self.outnormparlist=['imagename','mtype','weightlimit','nterms']

        ret = self.checkParameters()
        if ret==False:
            casalog.post('Found errors in input parameters. Please check.', 'WARN')

        self.printParameters()

    def getSelPars(self):
        return self.allselpars
    def getImagePars(self):
        return self.allimpars
    def getGridPars(self):
        return self.allgridpars
    def getWeightPars(self):
        return self.weightpars
    def getDecPars(self):
        return self.alldecpars
    def getIterPars(self):
        return self.iterpars
    def getNormPars(self):
        return self.allnormpars
    def getCFCachePars(self):
        return self.cfcachepars;

    def setSelPars(self,selpars):
        self.allselpars = selpars
    def setImagePars(self,impars):
        self.allimpars = impars
    def setGridPars(self,gridpars):
        self.allgridpars = gridpars
    def setWeightPars(self,weightpars):
        self.weightpars = weightpars
    def setDecPars(self,decpars):
        self.alldecpars = decpars
    def setIterPars(self,iterpars):
        self.iterpars = iterpars
    def setNormPars(self,normpars):
        self.allnormpars = normpars



    def checkParameters(self):
        #casalog.origin('refimagerhelper.checkParameters')
        casalog.post('Verifying Input Parameters')
        # Init the error-string
        errs = "" 
        errs += self.checkAndFixSelectionPars()
        errs += self.makeImagingParamLists()
        errs += self.checkAndFixIterationPars()
        errs += self.checkAndFixNormPars()

        ### MOVE this segment of code to the constructor so that it's clear which parameters go where ! 
        ### Copy them from 'impars' to 'normpars' and 'decpars'
        self.iterpars['allimages']={}
        for immod in list(self.allimpars.keys()) :
            self.allnormpars[immod]['imagename'] = self.allimpars[immod]['imagename']
            self.alldecpars[immod]['imagename'] = self.allimpars[immod]['imagename']
            self.allgridpars[immod]['imagename'] = self.allimpars[immod]['imagename']
            self.iterpars['allimages'][immod] = { 'imagename':self.allimpars[immod]['imagename'] , 'multiterm': (self.alldecpars[immod]['deconvolver']=='mtmfs') }

        ## Integers need to be NOT numpy versions.
        self.fixIntParam(self.allimpars, 'imsize')
        self.fixIntParam(self.allimpars, 'nchan')
        self.fixIntParam(self.allimpars,'nterms')
        self.fixIntParam(self.allnormpars,'nterms')
        self.fixIntParam(self.alldecpars,'nterms')
        self.fixIntParam(self.allgridpars,'facets')
        self.fixIntParam(self.allgridpars,'chanchunks')
 
        ## If there are errors, print a message and exit.
        if len(errs) > 0:
#            casalog.post('Parameter Errors : \n' + errs,'WARN')
            raise Exception("Parameter Errors : \n" + errs)
 #           return False
        return True

    ###### Start : Parameter-checking functions ##################


    def checkAndFixSelectionPars(self):
        errs=""

        # If it's already a dict with ms0,ms1,etc...leave it be.
        ok=True
        for kk in list(self.allselpars.keys()):
            if kk.find('ms')!=0:
                ok=False

        if ok==True:
            print("Already in correct format")
            return errs

        # msname, field, spw, etc must all be equal-length lists of strings, or all except msname must be of length 1.
        if 'msname' not in self.allselpars:
            errs = errs + 'MS name(s) not specified'
        else:

            selkeys = list(self.allselpars.keys())

            # Convert all non-list parameters into lists.
            for par in selkeys:
                if type( self.allselpars[par] ) != list:
                    self.allselpars[par] = [ self.allselpars[par]  ]
                    
            # Check that all are the same length as nvis
            # If not, and if they're single, replicate them nvis times
            nvis = len(self.allselpars['msname'])
            for par in selkeys:
                if len( self.allselpars[par] ) > 1 and len( self.allselpars[par] ) != nvis:
                    errs = errs + str(par) + ' must have a single entry, or ' + str(nvis) + ' entries to match vis list \n'
                    return errs
                else: # Replicate them nvis times if needed.
                    if len( self.allselpars[par] ) == 1:
                        for ms in range(1,nvis):
                            self.allselpars[par].append( self.allselpars[par][0] )
                    

            # Now, all parameters are lists of strings each of length 'nvis'.
            # Put them into separate dicts per MS.
            selparlist={}
            for ms in range(0,nvis):
                selparlist[ 'ms'+str(ms) ] = {}
                for par in selkeys:
                    selparlist[ 'ms'+str(ms) ][ par ] = self.allselpars[par][ms]

                synu = casac.synthesisutils()
                selparlist[ 'ms'+str(ms) ] = synu.checkselectionparams( selparlist[ 'ms'+str(ms)] )
                synu.done()

#            print selparlist

            self.allselpars = selparlist

        return errs


    def makeImagingParamLists(self ):
        errs=""

        ## Multiple images have been specified. 
        ## (1) Parse the outlier file and fill a list of imagedefinitions
        ## OR (2) Parse lists per input parameter into a list of parameter-sets (imagedefinitions)
        ### The code below implements (1)
        outlierpars=[]
        parseerrors=""
        if len(self.outlierfile)>0:
            outlierpars,parseerrors = self.parseOutlierFile(self.outlierfile) 

        if len(parseerrors)>0:
            errs = errs + "Errors in parsing outlier file : " + parseerrors
            return errs

        # Initialize outlier parameters with defaults
        # Update outlier parameters with modifications from outlier files
        for immod in range(0, len(outlierpars)):
            modelid = str(immod+1)
            self.allimpars[ modelid ] = copy.deepcopy(self.allimpars[ '0' ])
            self.allimpars[ modelid ].update(outlierpars[immod]['impars'])
            self.allgridpars[ modelid ] = copy.deepcopy(self.allgridpars[ '0' ])
            self.allgridpars[ modelid ].update(outlierpars[immod]['gridpars'])
            self.alldecpars[ modelid ] = copy.deepcopy(self.alldecpars[ '0' ])
            self.alldecpars[ modelid ].update(outlierpars[immod]['decpars'])
            self.allnormpars[ modelid ] = copy.deepcopy(self.allnormpars[ '0' ])
            self.allnormpars[ modelid ].update(outlierpars[immod]['normpars'])
            self.alldecpars[ modelid ][ 'id' ] = immod+1  ## Try to eliminate.


        #print self.allimpars

#
#        print "REMOVING CHECKS to check..."
#### This does not handle the conversions of the csys correctly.....
####
#        for immod in self.allimpars.keys() :
#            tempcsys = {}
#            if self.allimpars[immod].has_key('csys'):
#                tempcsys = self.allimpars[immod]['csys']
#
#            synu = casac.synthesisutils()
#            self.allimpars[immod] = synu.checkimageparams( self.allimpars[immod] )
#            synu.done()
#
#            if len(tempcsys.keys())==0:
#                self.allimpars[immod]['csys'] = tempcsys

        ## Check for name increments, and copy from impars to decpars and normpars.
        self.handleImageNames()

        return errs

    def handleImageNames(self):

            for immod in list(self.allimpars.keys()) :
                inpname = self.allimpars[immod]['imagename']

                ### If a directory name is embedded in the image name, check that the dir exists.
                if inpname.count('/'):
                    splitname = inpname.split('/')
                    prefix = splitname[ len(splitname)-1 ]
                    dirname = inpname[0: len(inpname)-len(prefix)]   # has '/' at end
                    if not os.path.exists( dirname ):
                        casalog.post('Making directory : ' + dirname, 'INFO')
                        os.mkdir( dirname )
                    
            ### Check for name increments 
            #if self.reusename == False:

            if self.allimpars['0']['restart'] == False:   # Later, can change this to be field dependent too.
                ## Get a list of image names for all fields (to sync name increment ids across fields)
                inpnamelist={}
                for immod in list(self.allimpars.keys()) :
                    inpnamelist[immod] = self.allimpars[immod]['imagename'] 

                newnamelist = self.incrementImageNameList( inpnamelist )

                if len(newnamelist) != len(list(self.allimpars.keys())) :
                    casalog.post('Internal Error : Non matching list lengths in refimagerhelper::handleImageNames. Not updating image names','WARN')
                else : 
                    for immod in list(self.allimpars.keys()) :
                        self.allimpars[immod]['imagename'] = newnamelist[immod]
                
    def checkAndFixIterationPars(self ):
        errs=""

        # Bother checking only if deconvolution iterations are requested
        if self.iterpars['niter']>0:
            # Make sure cycleniter is less than or equal to niter. 
            if self.iterpars['cycleniter']<=0 or self.iterpars['cycleniter'] > self.iterpars['niter']:
                if self.iterpars['interactive']==False:
                    self.iterpars['cycleniter'] = self.iterpars['niter']
                else:
                    self.iterpars['cycleniter'] = min(self.iterpars['niter'] , 100)

        return errs

    def checkAndFixNormPars(self):  
        errs=""

#        for modelid in self.allnormpars.keys():
#            if len(self.allnormpars[modelid]['workdir'])==0:
#                self.allnormpars[modelid]['workdir'] = self.allnormpars['0']['imagename'] + '.workdir'

        return errs

    ###### End : Parameter-checking functions ##################

    ## Parse outlier file and construct a list of imagedefinitions (dictionaries).
    def parseOutlierFile(self, outlierfilename="" ):
        returnlist = []
        errs=""  #  must be empty for no error

        if len(outlierfilename)>0 and not os.path.exists( outlierfilename ):
             errs +=  'Cannot find outlier file : ' +  outlierfilename + '\n'
             return returnlist, errs

        fp = open( outlierfilename, 'r' )
        thelines = fp.readlines()
        tempimpar={}
        tempgridpar={}
        tempweightpar={}
        tempdecpar={}
        tempnormpar={}
        for oneline in thelines:
            aline = oneline.replace('\n','')
#            aline = oneline.replace(' ','').replace('\n','')
            if len(aline)>0 and aline.find('#')!=0:
                parpair = aline.split("=")  
                parpair[0] = parpair[0].replace(' ','')
                #print parpair
                if len(parpair) != 2:
                    errs += 'Error in line containing : ' + oneline + '\n'
                if parpair[0] == 'imagename' and tempimpar != {}:
                    #returnlist.append({'impars':tempimpar, 'gridpars':tempgridpar, 'weightpars':tempweightpar, 'decpars':tempdecpar} )
                    returnlist.append({'impars':tempimpar, 'gridpars':tempgridpar, 'weightpars':tempweightpar, 'decpars':tempdecpar, 'normpars':tempnormpar} )
                    tempimpar={}
                    tempgridpar={}
                    tempweightpar={}
                    tempdecpar={}
                    tempnormpar={}
                usepar=False
                if parpair[0] in self.outimparlist:
                    tempimpar[ parpair[0] ] = parpair[1]
                    usepar=True
                if parpair[0] in self.outgridparlist:
                    tempgridpar[ parpair[0] ] = parpair[1]
                    usepar=True
                if parpair[0] in self.outweightparlist:
                    tempweightpar[ parpair[0] ] = parpair[1]
                    usepar=True
                if parpair[0] in self.outdecparlist:
                    tempdecpar[ parpair[0] ] = parpair[1]
                    usepar=True
                if parpair[0] in self.outnormparlist:
                    tempnormpar[ parpair[0] ] = parpair[1]
                    usepar=True
                if usepar==False:
                    print('Ignoring unknown parameter pair : ' + oneline)

        if len(errs)==0:
            returnlist.append( {'impars':tempimpar,'gridpars':tempgridpar, 'weightpars':tempweightpar, 'decpars':tempdecpar, 'normpars':tempnormpar} )

        ## Extra parsing for a few parameters.
        returnlist = self.evalToTarget( returnlist, 'impars', 'imsize', 'intvec' )
        returnlist = self.evalToTarget( returnlist, 'impars', 'nchan', 'int' )
        returnlist = self.evalToTarget( returnlist, 'impars', 'cell', 'strvec' )
        returnlist = self.evalToTarget( returnlist, 'impars', 'nterms', 'int' )
        returnlist = self.evalToTarget( returnlist, 'decpars', 'nterms', 'int' )
        returnlist = self.evalToTarget( returnlist, 'normpars', 'nterms', 'int' )
        returnlist = self.evalToTarget( returnlist, 'gridpars', 'wprojplanes', 'int' )
#        returnlist = self.evalToTarget( returnlist, 'impars', 'reffreq', 'strvec' )


        #print returnlist
        return returnlist, errs


    def evalToTarget(self, globalpars, subparkey, parname, dtype='int' ):
        try:
            for fld in range(0, len( globalpars ) ):
                if parname in globalpars[ fld ][subparkey]:
                    if dtype=='int' or dtype=='intvec':
                        val_e = eval( globalpars[ fld ][subparkey][parname] )
                    if dtype=='strvec':
                        tcell =  globalpars[ fld ][subparkey][parname]
                        tcell = tcell.replace(' ','').replace('[','').replace(']','').replace("'","")
                        tcells = tcell.split(',')
                        val_e = []
                        for cell in tcells:
                            val_e.append( cell )

                    globalpars[ fld ][subparkey][parname] = val_e
        except:
            print('Cannot evaluate outlier field parameter "' + parname + '"')

        return globalpars


    def printParameters(self):
        casalog.post('SelPars : ' + str(self.allselpars), 'INFO2')
        casalog.post('ImagePars : ' + str(self.allimpars), 'INFO2')
        casalog.post('GridPars : ' + str(self.allgridpars), 'INFO2')
        casalog.post('NormPars : ' + str(self.allnormpars), 'INFO2')
        casalog.post('Weightpars : ' + str(self.weightpars), 'INFO2')
        casalog.post('DecPars : ' + str(self.alldecpars), 'INFO2')
        casalog.post('IterPars : ' + str(self.iterpars), 'INFO2')


    def incrementImageName(self,imagename):
        dirname = '.'
        prefix = imagename

        if imagename.count('/'):
            splitname = imagename.split('/')
            prefix = splitname[ len(splitname)-1 ]
            dirname = './' + imagename[0: len(imagename)-len(prefix)]   # has '/' at end

        inamelist = [fn for fn in os.listdir(dirname) if any([fn.startswith(prefix)])];

        if len(inamelist)==0:
            newimagename = dirname[2:] + prefix
        else:
            nlen = len(prefix)
            maxid=1
            for iname in inamelist:
                startind = iname.find( prefix+'_' )
                if startind==0:
                    idstr = ( iname[nlen+1:len(iname)] ).split('.')[0]
                    if idstr.isdigit() :
                        val = eval(idstr)
                        if val > maxid : 
                            maxid = val
            newimagename = dirname[2:] + prefix + '_' + str(maxid+1)

        print('Using : ',  newimagename)
        return newimagename

    def incrementImageNameList(self, inpnamelist ):

        dirnames={}
        prefixes={}

        for immod in list(inpnamelist.keys()) : 
            imagename = inpnamelist[immod]
            dirname = '.'
            prefix = imagename

            if imagename.count('/'):
                splitname = imagename.split('/')
                prefix = splitname[ len(splitname)-1 ]
                dirname = './' + imagename[0: len(imagename)-len(prefix)]   # has '/' at end

            dirnames[immod] = dirname
            prefixes[immod] = prefix


        maxid=0
        for immod in list(inpnamelist.keys()) : 
            prefix = prefixes[immod]
            inamelist = [fn for fn in os.listdir(dirnames[immod]) if any([fn.startswith(prefix)])];
            nlen = len(prefix)

            if len(inamelist)==0 : 
                locmax=0
            else: 
                locmax=1

            cleanext = ['.image','.residual','.model','.psf','.sumwt','.tt0']
            incremented=False
            for iname in inamelist:
                rootname,ext = os.path.splitext(iname)
                if ext in cleanext:
                    startind = iname.find( prefix+'_' )
                    if startind==0:
                        idstr = ( iname[nlen+1:len(iname)] ).split('.')[0]
                        if idstr.isdigit() :
                            val = eval(idstr)
                            incremented=True
                            if val > locmax : 
                                locmax = val
                    elif startind==-1:
                        if ext=='.tt0':
                           # need one more pass to extract rootname 
                           rootname,ext = os.path.splitext(rootname)
                        if rootname==prefix:
                            # the file name with root file name only
                            incremented=True
                             
            if not incremented: 
                locmax = 0; 
            if locmax > maxid:
                maxid = locmax

        
        newimagenamelist={}
        for immod in list(inpnamelist.keys()) : 
            if maxid==0 : 
                newimagenamelist[immod] = inpnamelist[immod]
            else:
                newimagenamelist[immod] = dirnames[immod][2:] + prefixes[immod] + '_' + str(maxid+1) 

#        print 'Input : ',  inpnamelist
#        print 'Dirs : ', dirnames
#        print 'Pre : ', prefixes
#        print 'Max id : ', maxid
#        print 'Using : ',  newimagenamelist
        return newimagenamelist

    ## Guard against numpy int32,int64 types which don't convert well across tool boundary.
    ## For CAS-8250. Remove when CAS-6682 is done.
    def fixIntParam(self, allpars, parname ):
        for immod in list(allpars.keys()) :
            if parname in allpars[immod]:
                ims = allpars[immod][parname]
                if type(ims) != list:
                    ims = int(ims)
                else:
                    for el in range(0,len(ims)):
                        ims[el] = int(ims[el])
                allpars[immod][parname] = ims
      ############################

import time
import resource
class PerformanceMeasure():
    def __init__(self):
        self.t0=self.timestart()
        self.t1=0.0
        self.mem=0.0

    def timestart(self):
        self.t0 = time.time()

    def gettime(self,label=""):
        self.t1 = time.time()
        return "'%s: time=%s'"%(label,self.t1-self.t0)

    def getresource(self,label=""):
        usage=resource.getrusage(resource.RUSAGE_SELF)
        return '''%s: usertime=%s systime=%s mem=%s mb '''%(label,usage[0],usage[1], (usage[2]*resource.getpagesize())/1000000.0 )


##########################################
import os
import sys
import shutil
import subprocess
import numpy
import inspect
#from tasks import delmod

class TestHelpers():
     def __init__(self):
         self.epsilon = 0.05
    
     def write_file(self,filename,str_text):
          """Save the string in a text file"""
          inp = filename
          cmd = str_text
          # remove file first
          if os.path.exists(inp):
               os.system('rm -f '+ inp)
          # save to a file    
          with open(inp, 'w') as f:
               f.write(cmd)
          f.close()
          return

     def get_max(self,imname):
          """Get Image max"""
          ia.open(imname)
          stat = ia.statistics()
          ia.close()
          return stat['max'],stat['maxpos']

     def get_pix(self,imname,pos):
          """Get Image val"""
          ia.open(imname)
          apos = ia.pixelvalue(pos)
          ia.close()
          if apos == {}:
               return None
          else:
               return apos['value']['value']

     def exists(self,imname):
          """ Image exists """
          return os.path.exists(imname)

     def checkpeakres(self,summ,correctres):
          peakres = self.getpeakres(summ)
          out = True
          if correctres == None and peakres != None: 
               out = False
          if correctres != None and peakres == None: 
               out = False
          if out==True and peakres != None:
               if abs(correctres - peakres)/abs(correctres) > self.epsilon:
                    out=False
          return out,peakres

     def checkmodflux(self,summ,correctmod):
          modflux = self.getmodflux(summ)
          out = True
          if correctmod == None and modflux != None: 
               out = False
          if correctmod != None and modflux == None: 
               out = False
          if out==True and modflux != None:
               if abs(correctmod - modflux)/abs(correctmod) > self.epsilon:
                    out=False
          return out,modflux

#     def checkiterdone(self,summ,correctiterdone):
#          iters = self.getiterdone(summ)
#          out=True
#          if correctiterdone == None and iters != None: 
#               out = False
#          if correctiterdone != None and iters == None: 
#               out = False
#          if out==True and iters != None:
#               if abs(correctiterdone - iters)/correctiterdone > self.epsilon:
#                    out=False
#          return out, iters

     def getpeakres(self,summ):
          if 'summaryminor' in summ:
               reslist = summ['summaryminor'][1,:]
               peakres = reslist[ len(reslist)-1 ]
          else:
               peakres = None
          return peakres

     def getmodflux(self,summ):
          if 'summaryminor' in summ:
               modlist = summ['summaryminor'][2,:]
               modflux = modlist[ len(modlist)-1 ]
          else:
               modflux = None
          return modflux

     def getiterdone(self,summ):
          if 'iterdone' in summ:
               iters = summ['iterdone']
          else:
               iters = None
          return iters

     def verdict(self,boolval):
          if boolval:
               return "Pass"
          else:
               return "Fail"

     def checkret(self,summ,correctres,correctmod):
          testname = inspect.stack()[1][3]
          retres,peakres = self.checkpeakres(summ,correctres)
          retmod,modflux = self.checkmodflux(summ,correctmod)
          
          pstr =  "[" + testname + "] PeakRes is " + str(peakres) + " ("+self.verdict(retres)+" : should be " + str(correctres) + ")\n"
          pstr = pstr + "[" + testname + "] Modflux is " + str(modflux) + " ("+self.verdict(retmod)+" : should be " + str(correctmod) + ")"
          print(pstr)
          if retres==False or retmod==False:
               self.fail(pstr)

     def checkall(self, ret=None,
                  peakres=None, # a float
                  modflux=None, # a float
                  iterdone=None, # an int
                  nmajordone=None, # an int
                  imexist=None,  # list of image names
                  imexistnot=None, # list of image names
                  imval=None,  # list of tuples of (imagename,val,pos)
                  tabcache=True
                  ):
          pstr = ""

          if ret != None and type(ret)==dict:

               try:

                    if peakres != None:
                         pstr += self.checkval( val=self.getpeakres(ret), correctval=peakres, valname="peak res" )

                    if modflux != None:
                         pstr += self.checkval( val=self.getmodflux(ret), correctval=modflux, valname="mod flux" )

                    if iterdone != None:
                         pstr += self.checkval( val=ret['iterdone'], correctval=iterdone, valname="iterdone", exact=True )

                    if nmajordone != None:
                         pstr += self.checkval( val=ret['nmajordone'], correctval=nmajordone, valname="nmajordone", exact=True )

               except Exception as e:
                    print(ret)
                    raise

          if imexist != None:
               if type(imexist)==list:
                    pstr += self.checkims(imexist, True)

          if imexistnot != None:
               if type(imexistnot)==list:
                    pstr += self.checkims(imexistnot, False)

          if imval != None:
               if type(imval)==list:
                    for ii in imval:
                         if type(ii)==tuple and len(ii)==3:
                              pstr += self.checkpixval(ii[0],ii[1],ii[2])

          if tabcache==True:
               opentabs = tb.showcache()
               if len(opentabs)>0 : 
                    pstr += "["+inspect.stack()[1][3]+"] "+self.verdict(False) + ": Found open tables after run "
          
          return pstr
          #self.checkfinal(pstr)

     def checkchanvals(self,msname,vallist): # list of tuples of (channumber, relation, value) e.g. (10,">",1.0)
          testname = inspect.stack()[1][3]
          pstr = ""
          for val in vallist:
               if len(val)==3:
                    thisval = self.checkmodelchan(msname,val[0])
                    if val[1]==">":
                         ok = thisval > val[2]
                    elif val[1]=="==":     
                         ok = abs( (thisval - val[2])/val[2] ) < self.epsilon
                    elif val[1]=="<":     
                         ok = thisval < val[2]
                    else:
                         ok=False
                    pstr =  "[" + testname + "] Chan "+ str(val[0]) + "  is " + str(thisval) + " ("+self.verdict(ok)+" : should be " + str(val[1]) + str(val[2]) + ")\n"

          print(pstr)
          return pstr
          #pstr = self.checkfinal(pstr)

#     def checkfinal(self,pstr=""):
#          if( pstr.count("(Fail") > 0 ):
#              pstr += "["+inspect.stack()[2][3]+"] : To re-run this test :  runUnitTest.main(['test_refimager["+ inspect.stack()[2][3] +"]']) "
#              #self.fail("\n"+pstr)
#              return False
#          else:
#              return True

     def checkval(self,val, correctval, valname='Value', exact=False):
          testname = inspect.stack()[2][3]
          
          out = True

          if numpy.isnan(val) or numpy.isinf(val):
               out=False

          if correctval == None and val != None: 
               out = False
          if correctval != None and val == None: 
               out = False
          if out==True and val != None:
               if exact==True:
                    if correctval != val:
                         out=False
               else:
                    if abs(correctval - val)/abs(correctval) > self.epsilon:
                         out=False

          pstr = "[" + testname + "] " + valname + " is " + str(val) + " ("+self.verdict(out)+" : should be " + str(correctval) + ")"
          print(pstr)
          pstr=pstr+"\n"
#          if out==False:
#               self.fail(pstr)

          return pstr

     def checkims(self,imlist,truth):
          testname = inspect.stack()[2][3]
          imex=[]
          out=True
          for imname in imlist:
               ondisk = self.exists(imname)
               imex.append( ondisk )
               if ondisk != truth:
                    out=False

          pstr = "[" + testname + "] Image made : " + str(imlist) + " = " + str(imex) + "(" + self.verdict(out) + " : should all be " + str(truth) + ")"
          print(pstr)
          pstr=pstr+"\n"
#          if all(imex) == False:
#               self.fail(pstr)
          return pstr

     def checkpixval(self,imname,theval=0, thepos=[0,0,0,0]):
          testname = inspect.stack()[2][3]
#          maxvals, maxvalposs = self.get_max(imname)
          readval = self.get_pix(imname,thepos)

          res=True

          if readval==None:
               res=False
          elif numpy.isnan(readval) or numpy.isinf(readval):
               res=False
          else:
               if abs(theval)>self.epsilon:
                  if abs(readval - theval)/abs(theval) > self.epsilon: 
                       res = False
                  else:
                       res = True
               else:  ## this is to guard against exact zero... sort of.
                  if abs(readval - theval) > self.epsilon: 
                       res = False
                  else:
                       res = True
               
          pstr =  "[" + testname + "] " + imname + ": Value is " + str(readval) + " at " + str(thepos) + " (" + self.verdict(res) +" : should be " + str(theval) + " )"
          print(pstr)
          pstr=pstr+"\n"
#          if res==False:
#               self.fail(pstr)
          return pstr
   
     def checkspecframe(self,imname,frame, crval=0.0):
          testname = inspect.stack()[1][3]
          pstr = ""
          if os.path.exists(imname):
               res = True
               coordsys = self.getcoordsys(imname)
               baseframe = coordsys['spectral2']['system']
               basecrval = coordsys['spectral2']['wcs']['crval']
               if baseframe != frame:
                    res = False 
               else:
                    res = True
                    if crval!=0.0:
                         if abs(basecrval - crval)/crval > 1.0e-6: 
                              res = False
                    else:
                         # skip the crval test
                         thecrval = ""
               thecorrectans = frame + " "+ str(crval) 
               pstr =  "[" + testname + "] " + imname + ": Spec frame is " +\
               str(baseframe) + " with crval " + str(basecrval) + " (" +\
               self.verdict(res) +" : should be " + thecorrectans +" )"
               print(pstr)
               pstr=pstr+"\n"
          #self.checkfinal(pstr)
          return pstr
        
     def getcoordsys(self,imname):
         ia.open(imname)
         csys = ia.coordsys().torecord()
         ia.close()
         return csys


     def modeltype(self,msname):
          """has no model, otf model, modelcol"""
          mtype = 0
          return mtype

     def delmodkeywords(self,msname=""):
#          delmod(msname)
          tb.open( msname+'/SOURCE', nomodify=False )
          keys = tb.getkeywords()
          for key in keys:
               tb.removekeyword( key )
          tb.close()

     def resetmodelcol(self,msname="",val=0.0):
          tb.open( msname, nomodify=False )
          hasmodcol = (  (tb.colnames()).count('MODEL_DATA')>0 )
          if not hasmodcol:
               cb.open(msname)
               cb.close()
          hasmodcol = (  (tb.colnames()).count('MODEL_DATA')>0 )
          if hasmodcol:
               dat = tb.getcol('MODEL_DATA')
               dat.fill( complex(val,0.0) )
               tb.putcol('MODEL_DATA', dat)
          tb.close();

     def delmodels(self,msname="",modcol='nochange'):
#          delmod(msname)  ## Get rid of OTF model and model column
          self.delmodkeywords(msname) ## Get rid of extra OTF model keywords that sometimes persist...

          if modcol=='delete':
               self.delmodelcol(msname) ## Delete model column
          if modcol=='reset0':
               self.resetmodelcol(msname,0.0)  ## Set model column to zero
          if modcol=='reset1':
               self.resetmodelcol(msname,1.0)  ## Set model column to one

     def delmodelcol(self,msname=""):
          tb.open( msname, nomodify=False )
          hasmodcol = (  (tb.colnames()).count('MODEL_DATA')>0 )
          if hasmodcol:
               tb.removecols('MODEL_DATA')
          tb.close()

     def checkmodel(self,msname=""):
          tb.open( msname )
          hasmodcol = (  (tb.colnames()).count('MODEL_DATA')>0 )
          modsum=0.0
          if hasmodcol:
               dat = tb.getcol('MODEL_DATA')
               modsum=dat.sum()
          tb.close()

          hasvirmod=False

          tb.open( msname+'/SOURCE' )
          keys = tb.getkeywords()
          if len(keys)>0:
               hasvirmod=True
          tb.close()

          tb.open( msname )
          keys = tb.getkeywords()
          for key in keys:
               if key.count("model_")>0:
                    hasvirmod=True
          tb.close()

          print(msname , ": modelcol=", hasmodcol, " modsum=", modsum, " virmod=", hasvirmod)
          return hasmodcol, modsum, hasvirmod

     def checkmodelchan(self,msname="",chan=0):
          tb.open( msname )
          hasmodcol = (  (tb.colnames()).count('MODEL_DATA')>0 )
          modsum=0.0
          if hasmodcol:
               dat = tb.getcol('MODEL_DATA')[:,chan,:]
               modsum=dat.mean()
          tb.close()
          ##print modsum
          return modsum

     def checkMPI(self):
          from mpi4casa.MPIInterface import MPIInterface as mpi_clustermanager
          try:
               self.nproc = len(mpi_clustermanager.getCluster()._cluster.get_engines())
               return True
          except Exception as e:
               self.nproc = 0
               return False
          

     def getNParts(self,imprefix='', imexts=[]):
          
          from mpi4casa.MPIInterface import MPIInterface as mpi_clustermanager
          try:
               self.nproc = len(mpi_clustermanager.getCluster()._cluster.get_engines())
          except Exception as e:
               self.nproc = 0

          if( self.nproc>0 ):
               
               imlist=[];
               for imext in imexts:
                    for part in range(1,self.nproc+1):
                         imlist.append( imprefix + '.n'+str(part)+'.'+imext )
               #self.checkall(imexist = imlist)

          else:
               print('Not a parallel run of CASA')

          return imlist

##############################################




