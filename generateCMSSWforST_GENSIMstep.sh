#!/bin/bash                                                                                                                                                         

export SCRAM_ARCH=slc6_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_3_18/src ] ; then
 echo release CMSSW_9_3_18 already exists
else
scram p CMSSW CMSSW_9_3_18
fi
cd CMSSW_9_3_18/src
eval `scram runtime -sh`


## EXO 17 LHE step                                                                                                                                                  
#curl -s --insecure https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/EXO-RunIIFall17GS-04847 --retry 2 --create-dirs -o Configuration/GenProduction/python/EXO-RunIIFall17GS-04847-fragment.py                                                                                                                        
#[ -s Configuration/GenProduction/python/EXO-RunIIFall17GS-04847-fragment.py ] || exit $?;                                                                          

#scram b                                                                                                                                                            
#cd ../../                                                                                                                                                          
#cmsDriver.py Configuration/GenProduction/python/EXO-RunIIFall17GS-04847-fragment.py --fileout file:EXO-RunIIFall17GS-04847.root --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --customise_commands "process.source.numberEventsInLuminosityBlock = cms.untracked.uint32(25)" --step GEN,SIM --geometry DB:Extended --era Run2_2017 --python_filename EXO-RunIIFall17GS-04847_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 44 || exit $? ;




# WJetsToLNu                                                                                                                                                        

curl -s --insecure https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/BTV-RunIIFall17wmLHEGS-00005 --retry 2 --create-dirs -o Configuration/GenProdu\
ction/python/BTV-RunIIFall17wmLHEGS-00005-fragment.py
[ -s Configuration/GenProduction/python/BTV-RunIIFall17wmLHEGS-00005-fragment.py ] || exit $?;

scram b
cd ../../
seed=$(($(date +%s) % 100 + 1))
cmsDriver.py Configuration/GenProduction/python/BTV-RunIIFall17wmLHEGS-00005-fragment.py --fileout file:BTV-RunIIFall17wmLHEGS-00005.root --mc --eventcontent RAWSI\
M,LHE --datatier GEN-SIM,LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step LHE,GEN,SIM --nThreads 8 --geometry DB:Ext\
ended --era Run2_2017 --python_filename BTV-RunIIFall17wmLHEGS-00005_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring --customise_co\
mmands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${seed})" -n 2470 || exit $? ;

