logFile=/afs/cern.ch/user/k/kiesel/alignment/manualPCLforReReco/acron.log

export SCRAM_ARCH=slc6_amd64_gcc453 >> $logFile 2>&1
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch >> $logFile 2>&1
source $VO_CMS_SW_DIR/cmsset_default.sh >> $logFile 2>&1

cd /cvmfs/cms.cern.ch/slc6_amd64_gcc530/cms/cmssw/CMSSW_8_0_12 >> $logFile 2>&1
eval `scramv1 runtime -sh` >> $logFile 2>&1
cd /afs/cern.ch/user/k/kiesel/alignment/manualPCLforReReco >> $logFile 2>&1
python main.py >> $logFile 2>&1


