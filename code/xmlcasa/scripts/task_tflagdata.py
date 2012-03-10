from taskinit import *
import time
import os
import sys
import flaghelper as fh

debug = False


def tflagdata(vis,
             mode,
             inpfile,       # mode list parameter
             reason,
             spw,           # data selection parameters
             field,
             antenna,
             uvrange,
             timerange,
             correlation,
             scan,
             intent,
             feed,
             array,
             observation,
             clipminmax,    # mode clip parameters
             datacolumn,
             clipoutside,
             channelavg,
             clipzeros,
             quackinterval, # mode quack parameters
             quackmode,
             quackincrement,
             tolerance,      # mode shadow parameter
             recalcuvw,
             antennafile,
             lowerlimit,    # mode elevation parameters
             upperlimit,
             ntime,         # mode tfcrop
             combinescans,
             timecutoff,    
             freqcutoff,
             timefit,
             freqfit,
             maxnpieces,
             flagdimension,
             usewindowstats,
             halfwin,
             winsize,    # rflag parameters
             timedev,
             freqdev,
             timedevscale,
             freqdevscale,
             spectralmax,
             spectralmin,
             extendpols,    # mode extend
             growtime,
             growfreq,
             growaround,
             flagneartime,
             flagnearfreq,
             minrel,        # mode summary
             maxrel,
             minabs,
             maxabs,
             spwchan,
             spwcorr,
             run,           # run or not the tool
             writeflags,
             display,
             flagbackup,
             savepars,      # save the current parameters to FLAG_CMD  or
             outfile):      # output file to save flag commands

    # Global parameters
    # vis, mode, run, savepars                      
    
    #
    # Task tflagdata
    #    Flags data based on data selection in various ways
    #    
    # This is a replacement task to flagdata. It takes different parameters and
    # different default values. This task uses a new tool and framework underneath.

    if pCASA.is_mms(vis):
        pCASA.execute("tflagdata", locals())
        return

    casalog.origin('tflagdata')

    tflocal = casac.homefinder.find_home_by_name('testflaggerHome').create()
    mslocal = casac.homefinder.find_home_by_name('msHome').create()

    # MS HISTORY
    mslocal.open(vis, nomodify=False)
    mslocal.writehistory(message='taskname = tflagdata', origin='tflagdata')
    mslocal.open(vis, nomodify=False)


    try: 
        # Verify the ntime value
        newtime = 0.0
        if type(ntime) == float or type(ntime) == int:
            if ntime <= 0:
                raise Exception, 'Parameter ntime cannot be < = 0'
            else:
                # units are seconds
                newtime = float(ntime)
        
        elif type(ntime) == str:
            if ntime == 'scan':
                # iteration time step is a scan
                newtime = 0.0
            else:
                # read the units from the string
                qtime = qa.quantity(ntime)
                
                if qtime['unit'] == 'min':
                    # convert to seconds
                    qtime = qa.convert(qtime, 's')
                elif qtime['unit'] == '':
                    qtime['unit'] = 's'
                    
                # check units
                if qtime['unit'] == 's':
                    newtime = qtime['value']
                else:
                    casalog.post('Cannot convert units of ntime. Will use default 0.0s', 'WARN')
                                    
        casalog.post("New ntime is of type %s and value %s"%(type(newtime),newtime), 'DEBUG')
                
        # Open the MS and attach it to the tool
        if ((type(vis) == str) & (os.path.exists(vis))):
            tflocal.open(vis, newtime)
        else:
            raise Exception, 'Visibility data set not found - please verify the name'


        # Get the parameters for the mode
        agent_pars = {}

        # List of parameters to save to outfile when mode != list
        sel_pars = ''
        
        
        # Default mode
        if mode == '':
            mode = 'manual'
        
        # Read in the list of commands
        if mode == 'list':
            casalog.post('List mode is active')
            # Parse the input file
            try:
                if inpfile == '':
                     casalog.post('Input file is empty', 'ERROR')
                     
                flaglist = fh.readFile(inpfile)
                
                # Make a FLAG_CMD compatible dictionary. Select by reason if requested
                flagcmd = fh.makeDict(flaglist, reason)
                
                # Update the list of commands with the selection
                flaglist = []
                for k in flagcmd.keys():
                    cmdline = flagcmd[k]['command']
                    flaglist.append(cmdline)
                                    
                # List of command keys in dictionary
                vrows = flagcmd.keys()
                
#                casalog.post('Read the following lines from file', 'DEBUG')
#                casalog.post('%s',flagcmd,'DEBUG')

            except:
                raise Exception, 'Error reading the input file '+inpfile
            
            casalog.post('Read ' + str(vrows.__len__())
                         + ' lines from file ' + inpfile)
                             
        elif mode == 'manual':
            casalog.post('Manual mode is active')
            
        elif mode == 'clip':

            if correlation == '':
                # default
                correlation = "ABS_ALL"
                
            agent_pars['datacolumn'] = datacolumn
            agent_pars['clipoutside'] = clipoutside
            agent_pars['channelavg'] = channelavg
            agent_pars['clipzeros'] = clipzeros
            
            # If clipminmax = [], do not write it in the dictionary.
            # It will be handled by the framework to flag NaNs only
            if clipminmax.__len__() == 2:      
                # Cast to float to avoid the missing decimal point                 
                clipmin = float(clipminmax[0])
                clipmax = float(clipminmax[1])
                clipminmax = []
                clipminmax.append(clipmin)
                clipminmax.append(clipmax)     
                agent_pars['clipminmax'] = clipminmax
                
            casalog.post('Clip mode is active')
            
            # Replace the white spaces
            expr = delspace(correlation, '_')
            correlation = expr     
            cliprange = delspace(str(clipminmax), '')
            
            sel_pars = sel_pars+' datacolumn='+datacolumn+\
                       ' clipminmax='+str(cliprange)+' clipoutside='+str(clipoutside)+\
                       ' channelavg='+str(channelavg)+' clipzeros='+str(clipzeros)
            
        elif mode == 'shadow':
            agent_pars['tolerance'] = tolerance
            if antennafile != '':
            # Get a dictionary with the antenna names, positions and diameters
                addantenna = fh.readAntennaList(antennafile)                
                agent_pars['addantenna'] = addantenna
                
            agent_pars['recalcuvw'] = recalcuvw
            casalog.post('Shadow mode is active')
            
            sel_pars = sel_pars+' tolerance='+str(tolerance)+' recalcuvw='+str(recalcuvw)+\
                        ' antennafile='+str(antennafile)

        elif mode == 'quack':
            agent_pars['quackmode'] = quackmode
            agent_pars['quackinterval'] = quackinterval
            agent_pars['quackincrement'] = quackincrement
            casalog.post('Quack mode is active')
            
            sel_pars = sel_pars+' quackmode='+str(quackmode)+' quackinterval='+str(quackinterval)+\
                       ' quackincrement='+str(quackincrement)

        elif mode == 'elevation':
            agent_pars['lowerlimit'] = lowerlimit
            agent_pars['upperlimit'] = upperlimit
            casalog.post('Elevation mode is active')
            
            sel_pars = sel_pars+' lowerlimit='+str(lowerlimit)+' upperlimit='+str(upperlimit)

        elif mode == 'tfcrop':
            if correlation == '':
                # default
                correlation = "ABS_ALL"
                
            agent_pars['ntime'] = newtime
            agent_pars['combinescans'] = combinescans            
            agent_pars['datacolumn'] = datacolumn
            agent_pars['timecutoff'] = timecutoff
            agent_pars['freqcutoff'] = freqcutoff
            agent_pars['timefit'] = timefit
            agent_pars['freqfit'] = freqfit
            agent_pars['maxnpieces'] = maxnpieces
            agent_pars['flagdimension'] = flagdimension
            agent_pars['usewindowstats'] = usewindowstats
            agent_pars['halfwin'] = halfwin
            casalog.post('Time and Frequency (tfcrop) mode is active')

            expr = delspace(correlation, '_')
            correlation = expr
            
            sel_pars = sel_pars+' ntime='+str(ntime)+' combinescans='+str(combinescans)+\
                      '\" datacolumn='+datacolumn+\
                      ' timecutoff='+str(timecutoff)+' freqcutoff='+str(freqcutoff)+\
                      ' timefit='+str(timefit)+' freqfit='+str(freqfit)+' maxnpieces='+str(maxnpieces)+\
                      ' flagdimension='+str(flagdimension)+' usewindowstats='+str(usewindowstats)+\
                      ' halfwin='+str(halfwin)
                      
        elif mode == 'rflag':
            if correlation == '':
                # default
                correlation = "ABS_ALL"

            agent_pars['winsize'] = winsize
            agent_pars['timedevscale'] = timedevscale
            agent_pars['freqdevscale'] = freqdevscale
            agent_pars['spectralmax'] = spectralmax
            agent_pars['spectralmin'] = spectralmin

            # These can be double, doubleArray, or string.
            # writeflags=False : calculate and return thresholds.
            # writeflags=True : use given thresholds for this run.
            if( type(timedev) == str and writeflags == True):
                timedev = fh.readRFlagThresholdFile(timedev,'timedev')
            if( type(freqdev) == str and writeflags == True):
                freqdev = fh.readRFlagThresholdFile(freqdev,'freqdev')

            agent_pars['timedev'] = timedev
            agent_pars['freqdev'] = freqdev
            
            agent_pars['writeflags'] = writeflags
            agent_pars['display'] = display

            casalog.post('Rflag mode is active')

            expr = delspace(correlation, '_')
            correlation = expr

            sel_pars = sel_pars+' winsize='+str(winsize)+' timedev='+(str(timedev)).replace(' ','')+\
                    ' freqdev='+(str(freqdev)).replace(' ','')+' timedevscale='+str(timedevscale)+\
                    ' freqdevscale='+str(freqdevscale)+' spectralmax='+str(spectralmax)+\
                    ' spectralmin='+str(spectralmin)

        elif mode == 'extend':
            agent_pars['ntime'] = newtime
            agent_pars['combinescans'] = combinescans                            
            agent_pars['extendpols'] = extendpols
            agent_pars['growtime'] = growtime
            agent_pars['growfreq'] = growfreq
            agent_pars['growaround'] = growaround
            agent_pars['flagneartime'] = flagneartime
            agent_pars['flagnearfreq'] = flagnearfreq
            casalog.post('Extend mode is active')
            
            sel_pars = sel_pars+' ntime='+str(ntime)+' combinescans='+str(combinescans)+' extendpols='+\
                       str(extendpols)+' growtime='+str(growtime)+' growfreq='+\
                       str(growfreq)+' growaround='+str(growaround)+' flagneartime='+str(flagneartime)+\
                       ' flagnearfreq='+str(flagnearfreq)
            
        elif mode == 'unflag':      
            casalog.post('Unflag mode is active')                
            
        elif mode == 'summary':
            agent_pars['spwchan'] = spwchan
            agent_pars['spwcorr'] = spwcorr
            
            # Disable writeflags and savepars
            writeflags = False
            savepars = False
            casalog.post('Summary mode is active')

        # Setup global parameters in the agent's dictionary
        apply = True
                    
        # Correlation does not go in selectdata, but in the agent's parameters
        agent_pars['correlation'] = correlation.upper()
        
        
        # Hold the name of the agent
        agent_name = mode.capitalize()
        agent_pars['name'] = agent_name
        agent_pars['mode'] = mode
        agent_pars['apply'] = apply      

        # Purge the empty parameters from the selection string
        if mode != 'list' and mode != 'summary':
            sel_pars = sel_pars+' mode='+mode+' field='+field+' spw='+spw+' array='+array+' feed='+feed+\
                    ' scan='+scan+' antenna='+antenna+' uvrange='+uvrange+' timerange='+timerange+\
                    ' correlation='+correlation+' intent='+intent+' observation='+str(observation)
            flaglist = fh.purgeEmptyPars(sel_pars) 
            flagcmd = fh.makeDict([flaglist])
            
            # Number of commands in dictionary
            vrows = flagcmd.keys()
            casalog.post('There are %s cmds in dictionary of mode %s'%(vrows.__len__(),mode),'DEBUG')


                                  
                          
        ##########  Only save the parameters and exit; run = False        
        if not run and savepars:

            fh.writeFlagCmd(vis, flagcmd, vrows, False, outfile)  
            if outfile == '':
                casalog.post('Saving parameters to FLAG_CMD')
            else:
                casalog.post('Saving parameters to '+outfile)                            
            return 0

        
        ######### From now on it is assumed that run = True
        
        # Select the data and parse the agent's parameters
        if mode != 'list':
            tflocal.selectdata(field=field, spw=spw, array=array, feed=feed, scan=scan, \
                               baseline=antenna, uvrange=uvrange, time=timerange, \
                               intent=intent, observation=str(observation))   

            casalog.post('Parsing the parameters for the %s mode'%mode)
            if (not tflocal.parseagentparameters(agent_pars)):
                casalog.post('Failed to parse parameters for mode %s' %mode, 'ERROR')
                
            casalog.post('%s'%agent_pars, 'DEBUG')
       
        else:        
            # Select a loose union of the data selection from the list
            # The loose union will be calculated for field and spw only
            # antenna, correlation and timerange should be handled by the agent
            if vrows.__len__() == 0:
                raise Exception, 'There are no valid commands in list'
            
            unionpars = {}
            if vrows.__len__() > 1:
               unionpars = fh.getUnion(mslocal, vis, flaglist)
               
               if( len( unionpars.keys() ) > 0 ):
                    casalog.post('Pre-selecting a subset of the MS : ');
                    casalog.post('%s'%unionpars)
                    
               else:
                    casalog.post('Iterating through the entire MS');
                    
            # Get all the selection parameters, but set correlation to ''
            elif vrows.__len__() == 1:
                unionpars = fh.getSelectionPars(flaglist[0])
                casalog.post('The selected subset of the MS will be: ');
                casalog.post('%s'%unionpars);
                
            tflocal.selectdata(unionpars);
            
            # Parse the parameters for each agent in the list
            list2save = fh.setupAgent(tflocal, flagcmd, [], apply, writeflags, display)

        # Do display if requested
        if display != '':
            
            agent_pars = {}
            casalog.post('Parsing the display parameters')
                
            agent_pars['mode'] = 'display'
            # need to create different parameters for both, data and report.
            if display == 'both':
                agent_pars['datadisplay'] = True
                agent_pars['reportdisplay'] = True
            
            elif display == 'data':
                agent_pars['datadisplay'] = True
            
            elif display == 'report':
                agent_pars['reportdisplay'] = True
                
            tflocal.parseagentparameters(agent_pars)
            
            # Disable saving the parameters to avoid inconsistencies
            if savepars:
                casalog.post('Disabling savepars for the display', 'WARN')
                savepars = False
                    
        # Initialize the agents
        casalog.post('Initializing the agents')
        tflocal.init()

        # Backup the existing flags before applying new ones
        # TODO: backup for the list
        if flagbackup and writeflags:
            casalog.post('Backup original flags before applying new flags')
#            backupFlags(tflocal, mode)
            fh.backupFlags(tflocal, mode)
        
        # Run the tool
        casalog.post('Running the testflagger tool')
        summary_stats_list = tflocal.run(writeflags, True)


        # Now, deal with all the modes that return output.
        # Summary : Currently, only one is allowed in the task
        # Rflag : There can be many 'rflags' in the list mode.

        ## Pull out RFlag outputs. There will be outputs only if writeflags=False
        if (mode == 'rflag' or mode== 'list') and (writeflags==False):  
            if type(summary_stats_list) is dict:
                nreps = summary_stats_list['nreport']
                for rep in range(0,nreps):
                    repname = 'report'+str(rep)
                    if summary_stats_list[repname]['type'] == "rflag":
                        # Pull out the rflag threshold dictionary. This has a 'name' in it.
                        rflag_thresholds = summary_stats_list[repname]
                        # Get the rflag id, to later construct a 'name' from to match the above.
                        rflagid = 0
                        if mode=='list':
                            rflagid = int( rflag_thresholds['name'].replace('Rflag_','') )
                        # Go through the flagcmd list, to find the 'rflags'.....
                        for key in flagcmd.keys():
                            cmdline = flagcmd[key]['command'];
                            if cmdline.__contains__('rflag'):
                                # Check for match between input flagcmd and output threshold, via the rflag id
                                if(key==rflagid):  
                                    # Pull out timedev, freqdev strings from flagcmd
                                    rflagpars = fh.getLinePars(flagcmd[key]['command'] , ['timedev','freqdev']);
                                    # Write RFlag thresholds to these file names. 
                                    newtimedev,newfreqdev = fh.writeRFlagThresholdFile(rflag_thresholds, rflagpars['timedev'], rflagpars['freqdev'], rflagid)
                                    ## Modify the flagcmd string, so that savepars sees the contents of the file
                                    oldstring = 'timedev='+str(rflagpars['timedev'])
                                    newstring = 'timedev='+str(newtimedev).replace(' ','')
                                    flagcmd[key]['command'] = flagcmd[key]['command'].replace( oldstring, newstring );
                                    oldstring = 'freqdev='+str(rflagpars['freqdev'])
                                    newstring = 'freqdev='+str(newfreqdev).replace(' ','')
                                    flagcmd[key]['command'] = flagcmd[key]['command'].replace( oldstring, newstring );


        # Save the current parameters/list to FLAG_CMD or to output
        if savepars:  

            if outfile == '':
                casalog.post('Saving parameters to FLAG_CMD')        
            else:
                casalog.post('Saving parameters to '+outfile)
                                      
            if mode != 'list':     
                fh.writeFlagCmd(vis, flagcmd, vrows, writeflags, outfile)  
            else:
                valid_rows = list2save.keys()
                fh.writeFlagCmd(vis, list2save, valid_rows, writeflags, outfile)        
            
        # Destroy the tool
        tflocal.done()

        # Pull out the 'summary' part of summary_stats_list.
        # (This is the task, and there will be only one such dictionary.)
        # After this step, the only thing left in summary_stats_list are the
        # list of reports/views, if any.  Return it, if the user wants it.
        summary_stats={};
        if mode == 'summary':
           if type(summary_stats_list) is dict:
               nreps = summary_stats_list['nreport'];
               for rep in range(0,nreps):
                    repname = "report"+str(rep);
                    if summary_stats_list[repname]['type'] == "summary":
                          summary_stats = summary_stats_list.pop(repname);
                          summary_stats_list[repname] = {'type':'none','name':'none'};
                          break;  # pull out only one summary.
        
           # Filter out baselines/antennas/fields/spws/... from summary_stats
           # which do not fall within limits
           if type(summary_stats) is dict:
               for x in summary_stats.keys():
                   if type(summary_stats[x]) is dict:
                       for xx in summary_stats[x].keys():
                           flagged = summary_stats[x][xx]
                           assert type(flagged) is dict
                           assert flagged.has_key('flagged')
                           assert flagged.has_key('total')
                           if flagged['flagged'] < minabs or \
                              (flagged['flagged'] > maxabs and maxabs >= 0) or \
                              flagged['flagged'] * 1.0 / flagged['total'] < minrel or \
                              flagged['flagged'] * 1.0 / flagged['total'] > maxrel:
                                   del summary_stats[x][xx]
        
        # if (need to return the reports/views as well as summary_stats) :
        #      return summary_stats , summary_stats_list;
        # else :
        #      return summary_stats;
        return summary_stats;
    
    except Exception, instance:
        casalog.post('%s'%instance,'ERROR')
        raise
        
    # Write history to the MS
    try:
            param_names = tflagdata.func_code.co_varnames[:tflagdata.func_code.co_argcount]
            param_vals = [eval(p) for p in param_names]
            retval &= write_history(mslocal, vis, 'tflagdata', param_names,
                                    param_vals, casalog)
    except Exception, instance:
            casalog.post("*** Error \'%s\' updating HISTORY" % (instance),
                         'WARN')
        
    return



def backupFlags(tflocal, mode):
    ''' Backup the flags before applying new ones'''
    
    # Create names like this:
    # before_manual_1,
    # before_manual_2,
    # before_manual_3,
    # etc
    #
    # Generally  before_<mode>_<i>, where i is the smallest
    # integer giving a name, which does not already exist
    
    # Get the existing flags from the FLAG_VERSION_LIST file
    # in the MS directory
    existing = tflocal.getflagversionlist(printflags=False)

    # Remove the comments from strings
    existing = [x[0:x.find(' : ')] for x in existing]

    i = 1
    while True:
        versionname = mode +"_" + str(i)
#        versionname = mode + str(i)

        if not versionname in existing:
            break
        else:
            i = i + 1

    time_string = str(time.strftime('%Y-%m-%d %H:%M:%S'))

    if debug:
        casalog.post("Saving current flags to " + versionname + " before applying new flags")

                      
#    tflocal.saveflagversion(versionname=versionname,
#                           comment='flagdata autosave before ' + mode + ' on ' + time_string,
#                           merge='replace')
    tflocal.saveflagversion(versionname=versionname,
                           comment='backup flags before applying\"on ' + time_string,
                           merge='replace')

    # Save flagcmd to flagbackup
    # Need to consider flagmanager when writing this
    
    # We already have the flagbackup in disk, now append the FLAG_CMD
    # sub-table to it
#    mstable = msfile + '/FLAG_CMD'
#    try:
#        tb.open(mstable, nomodify=False)
#    except:
#        raise Exception, 'Error opening FLAG_CMD table ' + mstable
    
#    tb.copy(newtablename=versionname + '/FLAG_CMD')
#    tb.done()
    

    return


def delspace(word, replace):
    '''Replace the white space of a string with another character'''
    
    newword = word
    if word.count(' ') > 0:
        newword = word.replace(' ', replace)
    
    return newword
    
