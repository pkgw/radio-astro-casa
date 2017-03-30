#####################################
#
# ORION-S SDtasks Regression Script
# Position-Switched data
# Version STM 2007-03-02
#
#####################################
import time
import os

casapath=os.environ['CASAPATH']

os.system('rm -rf OrionS_rawACSmod sdregress_orions* ')
datapath=casapath.split()[0]+'/data/regression/ATST5/OrionS/OrionS_rawACSmod'
#datapath='/home/rohir3/jmcmulli/SD/OrionS_rawACSmod'
copystring='cp -r '+datapath+' .'
os.system(copystring)

#restore()

##########################
#
# ORION-S SiO
# Position-Switched data
#
##########################
startTime=time.time()
startProc=time.clock()

# Set parameters
default('sdreduce')
infile = 'OrionS_rawACSmod'
telescope = 'FIX'
fluxunit = 'K'
specunit = 'channel'
calmode = 'ps'
average=True
scanaverage = False
timeaverage = True
tweight='tintsys' 
polaverage = True
pweight='tsys'
tau = 0.09
scanlist = [24,25,26,27]
iflist = [15]
kernel = 'boxcar'
kwidth = 10
maskmode='list'
blfunc='poly'
order=5
masklist = [[500,3500],[5000,7500]]
outfile = 'sdregress_orions_sio.asap'
outform = 'asap'
plotlevel = 0

sdreduce()

# Now do some region statistics
# First the line-free region
# Set parameters
default('sdstat')
infile = 'sdregress_orions_sio.asap'
fluxunit = 'K'
specunit = 'channel'
masklist = [[1000,3000]]
invertmask = False
xstat = {}

xstat = sdstat()

off_stat = xstat

# Then the line region
# Set parameters
infile = 'sdregress_orions_sio.asap'
fluxunit = 'K'
specunit = 'channel'
masklist = [[3900,4300]]
invertmask = False
xstat = {}

xstat=sdstat()

line_stat = xstat

# Now do some line fitting
# Set parameters
default('sdfit')
infile = 'sdregress_orions_sio.asap'
fluxunit = 'K'
specunit = 'channel'
fitmode = 'list'
maskline = [[3900,4300]]
nfit = [1]
outfile = 'sdregress_orions_sio.fit'
plotlevel = 0
xstat = {}

xstat=sdfit()

fit_stat = xstat

endProc = time.clock()
endTime = time.time()

project = 'OrionS-SiO'
prolog  = 'sdregress.ori.sio.'
# Compare to Joe's regression values
# sio_max=0.366
# sio_rms=0.037
# sio_sum=49.95
# Fit:
#   0: peak = 0.273 K , centre = 4096.952 channel, FWHM = 155.109 channel
#      area = 45.074 K channel
# GBTIDL:
# 0.3167 ( 0.005652)  4096.4663 (1.018)  116.4 ( 2.586)
#
# NEW:
#   0: peak = 0.275 K , centre = 4097.001 channel, FWHM = 156.038 channel
#      area = 45.751 K channel
#
# Regression values of CASA 2.3(#6654)+ASAP 2.2.0(#1448)
# on 64bit REL5.2 (2008/12/01)
#   0: peak = 0.275 K , centre = 4097.001 channel, FWHM = 156.038 channel
#      area = 45.751 K channel
prev_max=0.3662
prev_rms=0.03720
prev_sum=49.95
prev_peak=0.2754
prev_cent=4097.
prev_fwhm=156.0

new_rms = off_stat['rms']
new_max = line_stat['max']
new_sum = line_stat['sum']
#new_peak = fit_stat['peak'][0][0]
#new_cent = fit_stat['cent'][0][0]
#new_fwhm = fit_stat['fwhm'][0][0]
#err_peak = fit_stat['peak'][0][1]
#err_cent = fit_stat['cent'][0][1]
#err_fwhm = fit_stat['fwhm'][0][1]
new_peak = fit_stat['peak'][0][0][0]
new_cent = fit_stat['cent'][0][0][0]
new_fwhm = fit_stat['fwhm'][0][0][0]
err_peak = fit_stat['peak'][0][0][1]
err_cent = fit_stat['cent'][0][0][1]
err_fwhm = fit_stat['fwhm'][0][0][1]
diff_max = abs((prev_max-new_max)/prev_max)
diff_rms = abs((prev_rms-new_rms)/prev_rms)
diff_sum = abs((prev_sum-new_sum)/prev_sum)
diff_peak = abs((prev_peak-new_peak)/prev_peak)
diff_cent = abs((prev_cent-new_cent)/err_cent)
diff_fwhm = abs((prev_fwhm-new_fwhm)/prev_fwhm)

difpass_max = (diff_max < 0.05)
difpass_rms = (diff_rms < 0.05)
difpass_sum = (diff_sum < 0.05)
difpass = difpass_max & difpass_rms & difpass_sum
fitpass_peak = (diff_peak < 0.05)
fitpass_cent = (diff_cent < 1.00)
fitpass_fwhm = (diff_fwhm < 0.05)
fitpass = fitpass_peak & fitpass_cent & fitpass_fwhm

pass_regress = difpass & fitpass

if (difpass_max): print('* Passed spectrum max test ')
if (difpass_rms): print('* Passed spectrum rms test ')
if (difpass_sum): print('* Passed spectrum sum test')
if (difpass):
        print('---Passed Stat test for '+project)
else:
        print('---FAILED Stat test for '+project)
print(' ')
if (fitpass_peak): print('* Passed fit peak test ')
if (fitpass_cent): print('* Passed fit centroid test ')
if (fitpass_fwhm): print('* Passed fit FWHM test')
if (fitpass):
        print('---Passed Fit test for '+project)
else:
        print('---FAILED Fit test for '+project)
print('')
print('')
print('Total wall clock time was: '+str(endTime - startTime))
print('Total CPU        time was: '+str(endProc - startProc))
#print 'Processing rate MB/s  was: ', 35.1/(endTime - startTime)

#
# NOW TO REGRESSION LOGFILE 
#
import datetime
datestring=datetime.datetime.isoformat(datetime.datetime.today())
outfile=prolog+datestring+'.log'
logfile=open(outfile,'w')

print('', file=logfile)
print('************ Regression ****************', file=logfile)
print('*                                      *', file=logfile)
if (difpass_max): print('* Passed spectrum max test ', file=logfile)
print('*  Spectrum max '+str(new_max), file=logfile)
if (difpass_rms): print('* Passed spectrum rms test ', file=logfile)
print('*  Spectrum rms '+str(new_rms), file=logfile)
if (difpass_sum): print('* Passed spectrum sum test', file=logfile)
print('*  Spectrum sum '+str(new_sum), file=logfile)
if (difpass):
        print('---', file=logfile)
        print('Passed Stat test for '+project, file=logfile)
else:
        print('---', file=logfile)
        print('FAILED Stat test for '+project, file=logfile)
print('*                                      *', file=logfile)
print('****************************************', file=logfile)
print('*                                      *', file=logfile)
if (fitpass_peak): print('* Passed fit peak test ', file=logfile)
print('*  Line fit peak '+str(new_peak)+' +/- '+str(err_peak), file=logfile)
if (fitpass_cent): print('* Passed fit centroid test ', file=logfile)
print('*  Line fit centroid '+str(new_cent)+' +/- '+str(err_cent), file=logfile)
if (fitpass_fwhm): print('* Passed fit FWHM test', file=logfile)
print('*  Line fit FHWM '+str(new_fwhm)+' +/- '+str(err_fwhm), file=logfile)
if (fitpass):
        print('Passed Fit test for '+project, file=logfile)
        print('---', file=logfile)
else:
        print('---', file=logfile)
        print('FAILED Fit test for '+project, file=logfile)
print('****************************************', file=logfile)
print('', file=logfile)
print('', file=logfile)
print('************ Benchmarking **************', file=logfile)
print('*                                      *', file=logfile)
print('Total wall clock time was: '+str(endTime - startTime), file=logfile)
print('Total CPU        time was: '+str(endProc - startProc), file=logfile)
#print >>logfile,'Processing rate MB/s  was: ', 35.1/(endTime - startTime)

logfile.close()

##########################
#
# ORION-S HC3N
# Position-Switched data
#
##########################
startTime=time.time()
startProc=time.clock()

# Set parameters
default('sdreduce')
infile = 'OrionS_rawACSmod'
telescope = 'FIX'
fluxunit = 'K'
specunit = 'channel'
calmode = 'ps'
average=True
scanaverage = False
timeaverage = True
tweight='tintsys' 
polaverage = True
pweight='tsys'
tau = 0.09
scanlist = [20,21,22,23]
iflist = [0]
kernel = 'boxcar'
kwidth = 5
maskmode='auto'
blfunc='poly'
order=2
avg_limit=4
#edge = [1000]
edge = [50]
thresh=5
masklist = []
outfile = 'sdregress_orions_hc3n.asap'
outform = 'asap'
plotlevel = 0

sdreduce()

# Now do some region statistics
# First the line-free region
# Set parameters
default('sdstat')
infile = 'sdregress_orions_hc3n.asap'
fluxunit = 'K'
specunit = 'channel'
masklist = [[5000,7000]]
invertmask = False
xstat = {}

xstat=sdstat()

off_stat = xstat

# Then the line region
# Set parameters
infile = 'sdregress_orions_hc3n.asap'
fluxunit = 'K'
specunit = 'channel'
masklist = [[3900,4200]]
invertmask = False
xstat = {}

xstat=sdstat()

line_stat = xstat

# Now do some line fitting
# Set parameters
default('sdfit')
infile = 'sdregress_orions_hc3n.asap'
fluxunit = 'K'
specunit = 'channel'
fitmode = 'list'
maskline = [[3928,4255]]
nfit = [1]
outfile = 'sdregress_orions_hc3n.fit'
plotlevel = 0
xstat = {}

xstat=sdfit()

fit_stat = xstat

endProc = time.clock()
endTime = time.time()

project = 'OrionS-HC3N'
prolog  = 'sdregress.ori.hc3n.'
# Compare to Joe's regression values
# hc3n_max=0.918
# hc3n_rms=0.049
# hc3n_sum=64.994
# Fit:
#   0: peak = 0.786 K , centre = 4091.236 channel, FWHM = 70.586 channel
#      area = 59.473 K channel
# GBTIDL:
# 0.8281 ( 0.01670) 4091.8367 ( 0.7487) 75.73 (     1.763)
#
# NEW:
#   0: peak = 0.811 K , centre = 4091.041 channel, FWHM = 72.898 channel
#      area = 62.917 K channel
#
# Regression values of CASA 2.3(#6654)+ASAP 2.2.0(#1448)
# on 64bit REL5.2 (2008/12/01)
#   0: peak = 0.808 K , centre = 4091.248 channel, FWHM = 70.872 channel
#      area = 60.919 K channel
prev_max=0.9186
prev_rms=0.04912
prev_sum=65.09
prev_peak=0.8075
prev_cent=4091.
prev_fwhm=70.87

new_rms = off_stat['rms']
new_max = line_stat['max']
new_sum = line_stat['sum']
#new_peak = fit_stat['peak'][0][0]
#new_cent = fit_stat['cent'][0][0]
#new_fwhm = fit_stat['fwhm'][0][0]
#err_peak = fit_stat['peak'][0][1]
#err_cent = fit_stat['cent'][0][1]
#err_fwhm = fit_stat['fwhm'][0][1]
new_peak = fit_stat['peak'][0][0][0]
new_cent = fit_stat['cent'][0][0][0]
new_fwhm = fit_stat['fwhm'][0][0][0]
err_peak = fit_stat['peak'][0][0][1]
err_cent = fit_stat['cent'][0][0][1]
err_fwhm = fit_stat['fwhm'][0][0][1]
diff_max = abs((prev_max-new_max)/prev_max)
diff_rms = abs((prev_rms-new_rms)/prev_rms)
diff_sum = abs((prev_sum-new_sum)/prev_sum)
diff_peak = abs((prev_peak-new_peak)/prev_peak)
diff_cent = abs((prev_cent-new_cent)/err_cent)
diff_fwhm = abs((prev_fwhm-new_fwhm)/prev_fwhm)

difpass_max = (diff_max < 0.05)
difpass_rms = (diff_rms < 0.05)
difpass_sum = (diff_sum < 0.05)
difpass = difpass_max & difpass_rms & difpass_sum
fitpass_peak = (diff_peak < 0.05)
fitpass_cent = (diff_cent < 1.00)
fitpass_fwhm = (diff_fwhm < 0.05)
fitpass = fitpass_peak & fitpass_cent & fitpass_fwhm

pass_regress = pass_regress & difpass & fitpass

if (difpass_max): print('* Passed spectrum max test ')
if (difpass_rms): print('* Passed spectrum rms test ')
if (difpass_sum): print('* Passed spectrum sum test')
if (difpass):
        print('---Passed Stat test for '+project)
else:
        print('---FAILED Stat test for '+project)
print(' ')
if (fitpass_peak): print('* Passed fit peak test ')
if (fitpass_cent): print('* Passed fit centroid test ')
if (fitpass_fwhm): print('* Passed fit FWHM test')
if (fitpass):
        print('---Passed Fit test for '+project)
else:
        print('---FAILED Fit test for '+project)
print('')
print('')
print('Total wall clock time was: '+str(endTime - startTime))
print('Total CPU        time was: '+str(endProc - startProc))
#print 'Processing rate MB/s  was: ', 35.1/(endTime - startTime)

#
# NOW TO REGRESSION LOGFILE 
#
import datetime
datestring=datetime.datetime.isoformat(datetime.datetime.today())
outfile=prolog+datestring+'.log'
logfile=open(outfile,'w')

print('', file=logfile)
print('************ Regression ****************', file=logfile)
print('*                                      *', file=logfile)
if (difpass_max): print('* Passed spectrum max test ', file=logfile)
print('*  Spectrum max '+str(new_max), file=logfile)
if (difpass_rms): print('* Passed spectrum rms test ', file=logfile)
print('*  Spectrum rms '+str(new_rms), file=logfile)
if (difpass_sum): print('* Passed spectrum sum test', file=logfile)
print('*  Spectrum sum '+str(new_sum), file=logfile)
if (difpass):
        print('---', file=logfile)
        print('Passed Stat test for '+project, file=logfile)
else:
        print('---', file=logfile)
        print('FAILED Stat test for '+project, file=logfile)
print('*                                      *', file=logfile)
print('****************************************', file=logfile)
print('*                                      *', file=logfile)
if (fitpass_peak): print('* Passed fit peak test ', file=logfile)
print('*  Line fit peak '+str(new_peak)+' +/- '+str(err_peak), file=logfile)
if (fitpass_cent): print('* Passed fit centroid test ', file=logfile)
print('*  Line fit centroid '+str(new_cent)+' +/- '+str(err_cent), file=logfile)
if (fitpass_fwhm): print('* Passed fit FWHM test', file=logfile)
print('*  Line fit FHWM '+str(new_fwhm)+' +/- '+str(err_fwhm), file=logfile)
if (fitpass):
        print('---', file=logfile)
        print('Passed Fit test for '+project, file=logfile)
else:
        print('---', file=logfile)
        print('FAILED Fit test for '+project, file=logfile)
print('****************************************', file=logfile)
print('', file=logfile)
print('', file=logfile)
print('************ Benchmarking **************', file=logfile)
print('*                                      *', file=logfile)
print('Total wall clock time was: '+str(endTime - startTime), file=logfile)
print('Total CPU        time was: '+str(endProc - startProc), file=logfile)
#print >>logfile,'Processing rate MB/s  was: ', 35.1/(endTime - startTime)

logfile.close()

##########################
#
# ORION-S CH3OH
# Position-Switched data
#
##########################
startTime=time.time()
startProc=time.clock()

# Set parameters
default('sdreduce')
infile = 'OrionS_rawACSmod'
telescope = 'FIX'
fluxunit = 'K'
specunit = 'channel'
calmode = 'ps'
average=True
scanaverage = False
timeaverage = True
tweight='tintsys' 
polaverage = True
pweight='tsys'
tau = 0.09
scanlist = [20,21,22,23]
iflist = [2]
kernel = 'boxcar'
kwidth = 10
maskmode='list'
blfunc='poly'
order=5
#edge = [1000]
masklist = [[350,2700],[3500,7500]]
outfile = 'sdregress_orions_ch3oh.asap'
outform = 'asap'
plotlevel = 0

sdreduce()

# Now do some region statistics
# First the line-free region
# Set parameters
default('sdstat')
infile = 'sdregress_orions_ch3oh.asap'
fluxunit = 'K'
specunit = 'channel'
masklist = [[4000,6000]]
invertmask = False
xstat = {}

xstat=sdstat()

off_stat = xstat

# Then the line region
# Set parameters
infile = 'sdregress_orions_ch3oh.asap'
fluxunit = 'K'
specunit = 'channel'
masklist = [[2900,3150]]
invertmask = False
xstat = {}

xstat=sdstat()

line_stat = xstat

# Now do some line fitting
# Set parameters
default('sdfit')
infile = 'sdregress_orions_ch3oh.asap'
fluxunit = 'K'
specunit = 'channel'
fitmode = 'list'
maskline = [[2900,3150]]
nfit = [1]
outfile = 'sdregress_orions_ch3oh.fit'
plotlevel = 0
xstat = {}

xstat=sdfit()

fit_stat = xstat

endProc = time.clock()
endTime = time.time()

project = 'OrionS-CH3OH'
prolog  = 'sdregress.ori.ch3oh.'
# Compare to Joe's regression values
# ch3oh_max=1.275
# ch3oh_rms=0.0921
# ch3oh_sum=90.350
# Fit:
#   0: peak = 1.054 K , centre = 3037.182 channel, FWHM = 71.654 channel
#      area = 80.382 K channel
# GBTIDL:
# 1.117 (0.02187) 3037.1758 (0.6879) 71.68 (1.620)
#
# NEW:
#   0: peak = 1.110 K , centre = 3037.175 channel, FWHM = 71.679 channel
#      area = 84.728 K channel
#
# Regression values of CASA 2.3(#6654)+ASAP 2.2.0(#1448)
# on 64bit REL5.2 (2008/12/01)
#   0: peak = 1.110 K , centre = 3037.176 channel, FWHM = 71.677 channel
#      area = 84.728 K channel
prev_max=1.275
prev_rms=0.09209
prev_sum=90.35
prev_peak=1.110
prev_cent=3037.
prev_fwhm=71.68

new_rms = off_stat['rms']
new_max = line_stat['max']
new_sum = line_stat['sum']
#new_peak = fit_stat['peak'][0][0]
#new_cent = fit_stat['cent'][0][0]
#new_fwhm = fit_stat['fwhm'][0][0]
#err_peak = fit_stat['peak'][0][1]
#err_cent = fit_stat['cent'][0][1]
#err_fwhm = fit_stat['fwhm'][0][1]
new_peak = fit_stat['peak'][0][0][0]
new_cent = fit_stat['cent'][0][0][0]
new_fwhm = fit_stat['fwhm'][0][0][0]
err_peak = fit_stat['peak'][0][0][1]
err_cent = fit_stat['cent'][0][0][1]
err_fwhm = fit_stat['fwhm'][0][0][1]
diff_max = abs((prev_max-new_max)/prev_max)
diff_rms = abs((prev_rms-new_rms)/prev_rms)
diff_sum = abs((prev_sum-new_sum)/prev_sum)
diff_peak = abs((prev_peak-new_peak)/prev_peak)
diff_cent = abs((prev_cent-new_cent)/err_cent)
diff_fwhm = abs((prev_fwhm-new_fwhm)/prev_fwhm)

difpass_max = (diff_max < 0.05)
difpass_rms = (diff_rms < 0.05)
difpass_sum = (diff_sum < 0.05)
difpass = difpass_max & difpass_rms & difpass_sum
fitpass_peak = (diff_peak < 0.05)
fitpass_cent = (diff_cent < 1.00)
fitpass_fwhm = (diff_fwhm < 0.05)
fitpass = fitpass_peak & fitpass_cent & fitpass_fwhm

pass_regress = pass_regress & difpass & fitpass

if (difpass_max): print('* Passed spectrum max test ')
if (difpass_rms): print('* Passed spectrum rms test ')
if (difpass_sum): print('* Passed spectrum sum test')
if (difpass):
        print('---Passed Stat test for '+project)
else:
        print('---FAILED Stat test for '+project)
print(' ')
if (fitpass_peak): print('* Passed fit peak test ')
if (fitpass_cent): print('* Passed fit centroid test ')
if (fitpass_fwhm): print('* Passed fit FWHM test')
if (fitpass):
        print('---Passed Fit test for '+project)
else:
        print('---FAILED Fit test for '+project)
print('')
print('')
print('Total wall clock time was: '+str(endTime - startTime))
print('Total CPU        time was: '+str(endProc - startProc))
#print 'Processing rate MB/s  was: ', 35.1/(endTime - startTime)

#
# NOW TO REGRESSION LOGFILE 
#
import datetime
datestring=datetime.datetime.isoformat(datetime.datetime.today())
outfile=prolog+datestring+'.log'
logfile=open(outfile,'w')

print('', file=logfile)
print('************ Regression ****************', file=logfile)
print('*                                      *', file=logfile)
if (difpass_max): print('* Passed spectrum max test ', file=logfile)
print('*  Spectrum max '+str(new_max), file=logfile)
if (difpass_rms): print('* Passed spectrum rms test ', file=logfile)
print('*  Spectrum rms '+str(new_rms), file=logfile)
if (difpass_sum): print('* Passed spectrum sum test', file=logfile)
print('*  Spectrum sum '+str(new_sum), file=logfile)
if (difpass):
        print('---', file=logfile)
        print('Passed Stat test for '+project, file=logfile)
else:
        print('---', file=logfile)
        print('FAILED Stat test for '+project, file=logfile)
print('*                                      *', file=logfile)
print('****************************************', file=logfile)
print('*                                      *', file=logfile)
if (fitpass_peak): print('* Passed fit peak test ', file=logfile)
print('*  Line fit peak '+str(new_peak)+' +/- '+str(err_peak), file=logfile)
if (fitpass_cent): print('* Passed fit centroid test ', file=logfile)
print('*  Line fit centroid '+str(new_cent)+' +/- '+str(err_cent), file=logfile)
if (fitpass_fwhm): print('* Passed fit FWHM test', file=logfile)
print('*  Line fit FHWM '+str(new_fwhm)+' +/- '+str(err_fwhm), file=logfile)
if (fitpass):
        print('---', file=logfile)
        print('Passed Fit test for '+project, file=logfile)
else:
        print('---', file=logfile)
        print('FAILED Fit test for '+project, file=logfile)
print('****************************************', file=logfile)
print('', file=logfile)
print('', file=logfile)
print('************ Benchmarking **************', file=logfile)
print('*                                      *', file=logfile)
print('Total wall clock time was: '+str(endTime - startTime), file=logfile)
print('Total CPU        time was: '+str(endProc - startProc), file=logfile)
#print >>logfile,'Processing rate MB/s  was: ', 35.1/(endTime - startTime)

logfile.close()

if ( pass_regress ):
	print("All regressions passed")
else:
	print("WARNING: There were some regressions FAILED")

##########################
#
# End ORION-S Regression
#
##########################
