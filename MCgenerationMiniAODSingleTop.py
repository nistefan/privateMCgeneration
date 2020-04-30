#!/usr/bin/env python

__author__ = 'Nicole Stefanov'
__date__ = 7/11/2019


## Usage python MCgeneration.py -verbose -check -submit 


import re
import subprocess
import os
import argparse
import sys
import datetime
import time
from os.path import basename
from shutil import *

from subprocess import call
import ROOT 
from ROOT import gROOT
from ROOT import TFile, TTree, TH1F, TObject, Math


## available colors for shell print-out                                                                                                                                                                                                      
class pycolors:
    header = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

a = datetime.datetime.now() ## For performance check
TheLibraryPath =os.environ['LD_LIBRARY_PATH']
parser = argparse.ArgumentParser(description=' This script is for NTuple production on HTCondor.')
parser.add_argument('-submit', '--submit', action='store_true', help='Submitting HTCondor scripts.',required=False)
parser.add_argument('-check', '--check', action='store_true', help='Creating HTCondor submission scripts.',required=False)
parser.add_argument('-verbose', '--verbose', action='store_true', help='Prints out detailed information during execution',required=False)
parser.add_argument('-cpu', '--cpurequest', help='Request more cpu for running a job at HTCondor', required=False)
parser.add_argument('-time', '--timerequest', help='Time request for running a job at HTCondor',required=False)
parser.add_argument('-memory', '--memoryrequest', help='Memory request for running a job at HTCondor',required=False)

memoryrequest = ""
timerequest = ""

### Getting changes for requests in memory and time than default ones and other options stated beforehand                                                                        
args = parser.parse_args()

### Switch off recovery mode in ROOT, if file is corrupted we don't want to keep even its ashes.
gROOT.ProcessLine("gEnv->SetValue(\"TFile.Recover\", 0);")

###### Method for creating HTCondor submission script                                                                                                     
###########################################################
def CreateSubmissionScript(Pathtodirectory, DirectoryName, CMSSW_BASE, cmsRunCommand, FileName, CreateEndOfSubmissionScript):
                                '''Create job submission file for HTCondor in sample subdirectory'''
                                file = open(DirectoryName+"/"+FileName+".submit","w")
                                file.write("universe            = vanilla\n \n")
                                file.write("transfer_executable = True \nshould_transfer_files   = IF_NEEDED \nwhen_to_transfer_output = ON_EXIT\n")
                                file.write("requirements = OpSysAndVer == \"SL6\"\ngetenv = true \n")
                                file.write("batch_name = "+FileName+"\n")
                                file.write("executable = "+CMSSW_BASE+"/src/wrapperScriptForHTCondor.sh\n")
#                                file.write("use_x509userproxy = true\n")
#                                file.write("output = "+DirectoryName+"/HTCondorOutput/"+FileName+"_$(Cluster)_$(Process).out\n")
 #                               file.write("error = "+DirectoryName+"/HTCondorOutput/"+FileName+"_$(Cluster)_$(Process).err\n")
                                file.write("output = HTCondorOutput/"+FileName+"_$(Cluster)_$(Process).out\n")
                                file.write("error = HTCondorOutput/"+FileName+"_$(Cluster)_$(Process).err\n")
                                file.write("initialdir = "+Pathtodirectory+"/"+DirectoryName+"\n")
                                file.write("arguments = \""+cmsRunCommand+"\" \n \n")
                                file.write(CreateEndOfSubmissionScript)
                                file.close()


###Creating the end of submission script which is fixed once for all HTCondor scripts
    
CreateEndOfSubmissionScript="environment = \"LD_LIB_PATH="+TheLibraryPath+" X509_USER_PROXY=/nfs/dust/cms/user/stefanon/DM_Sample_Production/CMSSW_9_4_15/src/tmp/x509up_u123 \" \n" #change this to your proxy path and proxy number  

if args.cpurequest is not None:
                                CreateEndOfSubmissionScript+=" request_cpus = "+ args.cpurequest + "\n"

if args.memoryrequest is not None:
                                CreateEndOfSubmissionScript+="request_memory = "+ args.memoryrequest +" \n" #has to be in MB

if args.timerequest is not None:
                                CreateEndOfSubmissionScript+="+RequestRuntime     = "+ args.timerequest+"\n"

### For accessing pileup root files which aren't on DESY Tier2:
### mkdir tmp in working directory, copy proxy credential into working directory: cp /tmp/x509up_XXX  WorkingDirectory/tmp/.


### max_materialize had problems once. Don't worry, simply deactivate if HTCondor submission does not work.
CreateEndOfSubmissionScript+="max_materialize = 1000\n"
CreateEndOfSubmissionScript+="queue \n"



def splitListintoSubListsOfPieceSize(ListToSplit, PieceSize):
    for item_splitListintoSubListsOfPieceSize in range(0, len(ListToSplit), PieceSize):
        yield ListToSplit[item_splitListintoSubListsOfPieceSize:item_splitListintoSubListsOfPieceSize + PieceSize]


##################
##################  START SCRIPT RUN
##################                         


pathArray =[
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraphMLM-pythia8-GENSIM/'

#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2017/TopDMJets_scalar_tWChan_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraphMLM-pythia8-PremixStep1/'
'/pnfs/desy.de/cms/tier2/store/user/nstefano/2017/TopDMJets_scalar_tWChan_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraphMLM-pythia8-AODSIM/'
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2017/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-ext1-GENSIM/GENSIM/191113_142950/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2017/TTbarDMJets_Dilepton_PS1_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-GENSIM/GENSIM/191113_161713/'
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2017/TTbarDMJets_Dilepton_pseudoscalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-GENSIM/GENSIM/191112_142815/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2017/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-GENSIM/GENSIM/191112_142652/'
#2018
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8_ext1-GENSIM/GENSIM/191105_203422/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-GENSIM/GENSIM/191105_031134/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TTbarDMJets_Dilepton_ps_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8_ext1-GENSIM/GENSIM/191105_205039/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TTbarDMJets_Dilepton_pseudoscalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-GENSIM/GENSIM/191105_135601/'
]

#templateFile = 'EXO-RunIIFall17DRPremix-00062_step1_template_cfg.py'

#templateFile = 'EXO-RunIIFall17DRPremix-00062_step2_template_cfg.py'

templateFile = 'EXO-RunIIFall17MiniAODv2-00053_template_cfg.py'
#pathArray =[
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2017/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-PremixStep1/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2017/TTbarDMJets_Dilepton_pseudoscalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-PremixStep1/'
#2018
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TTbarDMJets_Dilepton_ps_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8_ext1-PremixStep1/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TTbarDMJets_Dilepton_pseudoscalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-PremixStep1/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8_ext1-PremixStep1/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-PremixStep1/'
#]

#2018
#templateFile = 'EXO-RunIIAutumn18DRPremix-00004_step2_template_cfg.py'
#templateFile = 'EXO-RunIIFall17DRPremix-00062_step2_template_cfg.py'

#pathArray =[
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2018/TTbarDMJets_Dilepton_ps_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8_ext1-2018-AODSIM/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2018/TTbarDMJets_Dilepton_pseudoscalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-2018-AODSIM/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2018/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8_ext1-2018-AODSIM/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2018/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-2018-AODSIM/'
#]

#templateFile = 'EXO-RunIIAutumn18MiniAOD-00004_template_cfg.py'


#pathArray =[
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2018/TTbarDMJets_Dilepton_ps_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8_ext1-2018-MINIAODSIM/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2018/TTbarDMJets_Dilepton_pseudoscalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-2018-MINIAODSIM/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2018/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8_ext1-2018-MINIAODSIM/',
#'/pnfs/desy.de/cms/tier2/store/user/nstefano/2018/TTbarDMJets_Dilepton_scalar_LO_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraph-mcatnlo-pythia8-2018-MINIAODSIM/'
#]

#templateFile = 'EXO-RunIIAutumn18NanoAODv6-00363_template_cfg.py'

### Pathtodirectory = os.getcwd() has been temporarily broken on NAF, works now, but anyway. 
whatToAsk="pwd -P"
ask_currentpath = os.popen(whatToAsk).readlines()
Pathtodirectory = ask_currentpath[0][:-1]
print(Pathtodirectory)


#############################################
# Getting to know what jobs are on HTCondor
#############################################

cmd = "bash -i <<< 'condor_q'"
ask_condor = os.popen(cmd).readlines()
ask_condor_getFileNames = []
for item_ask_condor in ask_condor:
    if len(item_ask_condor.split(' ')) > 1:
        ask_condor_getFileNames.append(item_ask_condor.split(' ')[1])

if args.verbose: print ask_condor
getJobsOnCondorAtMoment = ''
################ This script assumes first schedd being your submission node; if it's not the case: change it.
for item_condor in ask_condor:
    if "Total for" in item_condor:
        getJobsOnCondorAtMoment = item_condor.split(',')
        break
print(getJobsOnCondorAtMoment)
#getJobsOnCondorAtMoment = ask_condor[5].split(',')

getIdlingJobs = int(getJobsOnCondorAtMoment[2].split(' ')[1])
print("In the momemt idling jobs:")
print(getIdlingJobs)
#sys.exit("Stopping test run")
#################################
#                               #
# Change parameters           #
#                           #
###############           #
maxIdlingJobsAccepted = 5000 #600 #3000

SplitSizeStepOfFileList = 50 #2 #10

OldDirectoriesSuffix = "AODSIM" #"PremixStep1" #"AODSIM" #"2018-MINIAODSIM" #"2018-AODSIM" #"PremixStep1" #"GENSIM"

NewDirectoriesSuffix = "MINIAODSIM" #"AODSIM" #"PremixStep1"  #"2018-NANOAODSIM"
      #              ############
    #                           #
  #                  as needed  #
#                               #
#################################
if args.submit:
    if getIdlingJobs > maxIdlingJobsAccepted:
        sys.exit(pycolors.blue+"Stop running this script due to too many jobs idling on HTCondor; try later again"+pycolors.end)
WhatDirectoryToStoreIn = "TopDMJets_scalar_tWChan_Mchi_1_Mphi_100_TuneCP5_13TeV_madgraphMLM_pythia8_MINIAODSIM/240420_155333/0000/"
ExtraDirectoryCreationOnPNFS = "240420_155333/0000/" #"2017/" #"2018/" #Don't forget / at the end.
#Monitoring files being created during run
tobeRemovedtxt ="tobeRemovedAOD.txt"
FilesToBeCopiedToPNFStxt = "FilesToBeCopiedToPNFS_AOD.txt"
CleanupAreatxt = "CleanupAreaAOD.txt"
CleanupAreapy = "CleanupAreapyAOD.txt"

removetxtFile = "rm"

if os.path.exists(Pathtodirectory+"/"+tobeRemovedtxt):
    removetxtFile += " "+tobeRemovedtxt
if os.path.exists(Pathtodirectory+"/"+FilesToBeCopiedToPNFStxt):
    removetxtFile += " "+FilesToBeCopiedToPNFStxt
if os.path.exists(Pathtodirectory+"/"+CleanupAreatxt):
    removetxtFile += " "+CleanupAreatxt
if os.path.exists(Pathtodirectory+"/"+CleanupAreapy):
    removetxtFile += " "+CleanupAreapy

if len(removetxtFile)>2:
    subprocess.Popen([removetxtFile], shell=True,
                    stdout=subprocess.PIPE).communicate()[0]
##
## Now let's start the script run, looping over all directories provided in pathArray
######################################################################################
######################################################################################

for path in pathArray:
  numberOfFiles = 0
  files = []
  # r=root, d=directories, f = files  ### here root does not refer to .root-files    
  for r, d, f in os.walk(path):
    for file in f:
        if '.root' in file:
            files.append(os.path.join(r, file))

  if args.verbose: 
      print("FileNumberInDirectory is "+str(len(files)))
  #    print(files)

  
  getSlicedListwithPNFS = list(splitListintoSubListsOfPieceSize(files, SplitSizeStepOfFileList))
  fileswithoutPNFS = []
  for itemfile in files:
      itemfile = itemfile.replace("/pnfs/desy.de/cms/tier2","")
      fileswithoutPNFS.append(itemfile)
  getSlicedList = list(splitListintoSubListsOfPieceSize(fileswithoutPNFS, SplitSizeStepOfFileList)) 
  #print(getSlicedList)
  if args.verbose: print(len(getSlicedList))

  # Set CMSSW BASE
  CMSSW_BASE_GET = subprocess.Popen(["echo $CMSSW_BASE"], shell=True,
                          stdout=subprocess.PIPE).communicate()[0]
  CMSSW_BASE= CMSSW_BASE_GET[:-1]

  pathsplit = path.split("/")
  DirectoryName = ""  
  DirectoryNameOld = ""
#GENSIM step adjustment
  if pathsplit[-1]:
    DirectoryName = pathsplit[-1]
  else:
    DirectoryName = pathsplit[-2]

#  if pathsplit[-1]:
#    DirectoryName = pathsplit[-1]  

#  else:
#    DirectoryName = pathsplit[-2]
  
  DirectoryNameOld = DirectoryName
  
  DirectoryName = DirectoryName.replace(OldDirectoriesSuffix, NewDirectoriesSuffix)
  if args.verbose:
    print(pathsplit)
    print(DirectoryName)

  if not os.path.exists(DirectoryName):
      os.makedirs(DirectoryName)
     
  HTCondorDirectory = DirectoryName+"/HTCondorOutput"
  if not os.path.exists(HTCondorDirectory):
      os.makedirs(HTCondorDirectory)
  NewDirectoryPath = Pathtodirectory+"/"+DirectoryName

  countTemplateFiles = 0
  whichDirectoryToCheck = "ls -lrt "+DirectoryName+"/HTCondorOutput"
  getListOfCondor = subprocess.Popen([whichDirectoryToCheck], shell=True,
                                     stdout=subprocess.PIPE).communicate()[0]
  getLineByLineCondor = getListOfCondor.split('\n')

  if args.verbose: print(getListOfCondor)

  for subListIngetSlicedList in getSlicedList:
      if args.verbose: print(subListIngetSlicedList)
      countTemplateFiles +=1
      TemplateFileNameAdjusted = ''
      if SplitSizeStepOfFileList ==1:
          subListIngetSlicedList = str(subListIngetSlicedList)
          print("subListIngetSlicedList "+subListIngetSlicedList)
          print("DirectoryNameOld ")
          print(DirectoryNameOld)
#          getNumberOfRootFileInDirectoryNameOld = subListIngetSlicedList.split(DirectoryNameOld+"_")
          getNumberOfRootFileInDirectoryNameOld = subListIngetSlicedList.split("/")
#          print(getNumberOfRootFileInDirectoryNameOld)
          getNumberOfRootFileInDirectoryNameOld = getNumberOfRootFileInDirectoryNameOld[-1].split("_")
 #         print(getNumberOfRootFileInDirectoryNameOld)
#          getNumberOfRootFileInDirectoryNameOld = getNumberOfRootFileInDirectoryNameOld[-1].split(".")
#          print(getNumberOfRootFileInDirectoryNameOld)
          getNumberOfRootFileInDirectoryNameOld = getNumberOfRootFileInDirectoryNameOld[-3]
  #        print(getNumberOfRootFileInDirectoryNameOld)
          TemplateFileNameAdjusted = DirectoryName+"_"+str(getNumberOfRootFileInDirectoryNameOld)+"_"+templateFile
   #       print(TemplateFileNameAdjusted)
    #      sys.exit("Stopping test")          
      else:
          TemplateFileNameAdjusted = DirectoryName+"_"+str(countTemplateFiles)+"_"+templateFile
      if not TemplateFileNameAdjusted: sys.exit("Error in  assinging a label in TemplateFileNameAdjusted.")
      outputRootfile = TemplateFileNameAdjusted[:-16]+".root"
      FileName = outputRootfile[:-5]
        #if args.verbose:                                                                                                                                                                                                               
      if args.verbose: print(pycolors.red+FileName+pycolors.end)
      modifiedOutputRootfile = outputRootfile.replace("-", "_").replace("_EXO-RunIIFall17MiniAODv2-00053", "")
      if not os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+WhatDirectoryToStoreIn+"/"+modifiedOutputRootfile):
       if not os.path.exists(NewDirectoryPath+"/"+outputRootfile): # and not os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+outputRootfile):
        if not os.path.exists(NewDirectoryPath+"/"+TemplateFileNameAdjusted):
          numberOfFiles += 1
          #if numberOfFiles == 1000:
           #   sys.exit("numberOfFiles reached 1000. We stop this run here.")
          copy(Pathtodirectory+"/"+templateFile, NewDirectoryPath+"/"+TemplateFileNameAdjusted)
          whatToReplace = "sed -i -e \"s?FileListToAdd?"+str(subListIngetSlicedList)+"?g\" "+NewDirectoryPath+"/"+TemplateFileNameAdjusted
          subprocess.Popen([whatToReplace], shell=True,
                          stdout=subprocess.PIPE).communicate()[0]
          print(whatToReplace)
          whatToReplace = "sed -i -e \"s?OUTPUTROOT?"+outputRootfile+"?g\" "+NewDirectoryPath+"/"+TemplateFileNameAdjusted
          subprocess.Popen([whatToReplace], shell=True,
                           stdout=subprocess.PIPE).communicate()[0]
          print(whatToReplace)
          #sys.exit()
        cmsRunCommand = "cmsRun "+NewDirectoryPath+"/"+TemplateFileNameAdjusted
        CreateSubmissionScript(Pathtodirectory, DirectoryName, CMSSW_BASE, cmsRunCommand, FileName, CreateEndOfSubmissionScript)
        jobInBatch = False
        for item_ask_condor in ask_condor:
            if FileName in item_ask_condor:
                jobInBatch = True
                if args.verbose: print("Job is already at HTCondor. No Job submission")
        if not jobInBatch:
           if args.submit:
            submitToHTCondor = "condor_submit "+DirectoryName+"/"+FileName+".submit"
            if args.verbose: print(pycolors.red+submitToHTCondor+pycolors.end)
            with open("cmsRuncommands.txt", 'a') as cobj1:
                                   cobj1.write(cmsRunCommand+"\n \n")

            subprocess.Popen([submitToHTCondor], shell=True,
                              stdout=subprocess.PIPE).communicate()[0]
            getIdlingJobs += 1
            if getIdlingJobs > maxIdlingJobsAccepted:
                          sys.exit(pycolors.blue+"Stop running this script due to too many jobs idling on HTCondor; try later again"+pycolors.end)
      if args.check:
          
          if os.path.exists(NewDirectoryPath+"/"+outputRootfile): # or os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+outputRootfile):
              if args.verbose: print("Passed is File in NewDirectoryPath outputRootfile:")
              jobInBatch = False
              #print(ask_condor_getFileNames)
              #for item_ask_condor in ask_condor:
              if FileName in ask_condor_getFileNames:
                      jobInBatch = True
                      if args.verbose: print("Job is still at HTCondor. No Job submission")
               #       print(ask_condor_getFileNames)
              if not jobInBatch:
                      #sys.exit()
                      getNEventsTier2 = 0
                     # if FileName in checkifAlreadyBeenCheckedInPreviousRun: getNEventsTier2 = 200
                      #else:                                                                                                                                        
                      try:
                           inputFile = ROOT.TFile.Open(NewDirectoryPath+"/"+outputRootfile, "read")
                           getNEventsTier2Sample = inputFile.Get("Events")
                           getNEventsTier2 = getNEventsTier2Sample.GetEntries()
                           inputFile.Close()

                      except:
                           if args.verbose: print("File seems to be corrupted; let's remove it ...")

                      if args.verbose:
                          print("Number of Entries in "+FileName+": "+str(getNEventsTier2))
                      if getNEventsTier2 == 10000:
                       #if args.verbose:                                                                                                                                                                                                                                                                           
                           if args.verbose: print("File passed sanity check!")
                           if not os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+WhatDirectoryToStoreIn+"/"+modifiedOutputRootfile):
#os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+outputRootfile): # or  os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+DirectoryName+"/"+outputRootfile):                                             
                               with open(FilesToBeCopiedToPNFStxt, 'a') as fobj1:
                                   fobj1.write("gfal-copy "+NewDirectoryPath+"/"+outputRootfile+" \'srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/store/user/nstefano/"+WhatDirectoryToStoreIn+"/"+modifiedOutputRootfile+"\'"+"\n \n")
                               gfalCopyCommand = "gfal-copy "+NewDirectoryPath+"/"+outputRootfile+" \'srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/store/user/nstefano/"+WhatDirectoryToStoreIn+"/"+modifiedOutputRootfile+"\'"
                               subprocess.Popen([gfalCopyCommand], shell=True,
                                             stdout=subprocess.PIPE).communicate()[0]
                               #sys.exit()                                                                                                                                                                                                                                               
                           
                           if os.path.exists(NewDirectoryPath+"/"+outputRootfile) and os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+WhatDirectoryToStoreIn+"/"+modifiedOutputRootfile):
                               with open(CleanupAreatxt, 'a') as cobj1:
                                   cobj1.write("rm  "+DirectoryName+"/"+outputRootfile+"\n \n")
                               CleanupRootFile = "rm  "+NewDirectoryPath+"/"+outputRootfile
                               subprocess.Popen([CleanupRootFile], shell=True,
                                             stdout=subprocess.PIPE).communicate()[0] 
                           if os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+WhatDirectoryToStoreIn+"/"+modifiedOutputRootfile):
                               if os.path.exists(NewDirectoryPath+"/"+TemplateFileNameAdjusted):
                                   with open(CleanupAreapy, 'a') as dobj1:
                                       dobj1.write("rm "+NewDirectoryPath+"/"+TemplateFileNameAdjusted+"\n \n")
                      else:
                              if args.verbose: print("File seems to be corrupted; let's remove it ...")
                              checkremoveFile = "rm "+NewDirectoryPath+"/"+outputRootfile
                              if args.verbose: print(pycolors.red+checkremoveFile+pycolors.end)
                              subprocess.Popen([checkremoveFile], shell=True,
                                             stdout=subprocess.PIPE).communicate()[0]
                              with open(tobeRemovedtxt, 'a') as cobj:
                                  cobj.write(checkremoveFile+"\n \n")
                              if args.verbose: print(pycolors.blue+"Corrupted file successfully removed."+pycolors.end)

#              if args.verbose: print("Passed is File in NewDirectoryPath outputRootfile:")
#              jobInBatch = False
#              for item_ask_condor in ask_condor:
#                  if FileName in item_ask_condor:
#                      jobInBatch = True
#                      if args.verbose: print("Job is already at HTCondor. No Job submission")
#              if not jobInBatch:
#               getAllJobsSendForThatFile = []
#               for item_getListOfCondor in getLineByLineCondor:
#                   if FileName in item_getListOfCondor:
#                       if args.verbose: print(item_getListOfCondor)
#                       getAllJobsSendForThatFile.append(item_getListOfCondor)
#               BeginProcess = False
#               GotMessageLoggerSummary = False
#               GotLastCheck = False
#               FatalException = True
#               if args.verbose: print(getAllJobsSendForThatFile)

# Let's check latest created HTCondor output file with suffix .err
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~               

# --- --- --- Finding the correct HTCondor output file --- --- ---

#               getExactJobFileName = ''
 #              if ".err" in  getAllJobsSendForThatFile[-1]:
  #                 getExactJobFileName = getAllJobsSendForThatFile[-1].split(' ')
   #            elif ".err" in  getAllJobsSendForThatFile[-2]:
    #               if args.verbose: print("Passed  if not .err in getExactJobFileName:")
     #              getExactJobFileName = getAllJobsSendForThatFile[-2].split(' ')
      #         if not getExactJobFileName:
       #            sys.exit("Error! Haven't found the correct HTCondor .err file for  "+FileName)
        #       whichJobFileToCheck = DirectoryName+"/HTCondorOutput/"+getExactJobFileName[-1]
#               print(getFileContent)

# --- --- --- Checking HTCondor output file if key words included/not included --- --- --- 
  
         #      checkBeginProcess = subprocess.Popen(["grep -r \"Begin processing the\" "+whichJobFileToCheck], shell=True,
          #                           stdout=subprocess.PIPE).communicate()[0]
           #    if checkBeginProcess:
 #                  BeginProcess = True
  #                 if args.verbose: print("Found: Begin processing the")
   #            checkFatalException  = subprocess.Popen(["grep -r \"Fatal Exception\" "+whichJobFileToCheck], shell=True,
    #                                 stdout=subprocess.PIPE).communicate()[0]
     #          if not checkFatalException:
      #             FatalException = False
       #            if args.verbose: print("Found: No Fatal Exception")
#
 #              checkMessageLogger =  subprocess.Popen(["grep -r \"MessageLogger Summary\" "+whichJobFileToCheck], shell=True,
  #                                   stdout=subprocess.PIPE).communicate()[0]
   #            if args.verbose:
    #               print("checkMessageLogger")
     #              print(checkMessageLogger)
      #         if checkMessageLogger:
       #            GotMessageLoggerSummary = True
        #           if args.verbose: print("Found: MessageLogger Summary")
         #      checkGotLastCheck = subprocess.Popen(["grep -r \"dropped waiting message count 0\" "+whichJobFileToCheck+" | tail -1"], shell=True,
#                                     stdout=subprocess.PIPE).communicate()[0]
#               if args.verbose:
 #                  print("checkGotLastCheck")
  #                 print(checkGotLastCheck)
   #            if checkGotLastCheck: 
    #               GotLastCheck = True
     #              if args.verbose: print("Found: dropped waiting message count 0")
               #if GotLastCheck[-1].count("Aborted"):
                #   print "found aborted"
      #         if args.verbose:
       #            print("BeginProcess")
        #           print(BeginProcess)
         #          print("GotMessageLoggerSummary")
          #         print(GotMessageLoggerSummary)
           #        print("GotLastCheck")
            #       print(GotLastCheck)

# --- --- --- Decision about file's sanity according to  HTCondor output --- --- ---   

#               if BeginProcess:
 #               if GotMessageLoggerSummary:
  #                if  GotLastCheck:
   #                  if not checkFatalException:
                       #if args.verbose: 
    #                       if args.verbose: print("File passed sanity check!")
     #                      if not os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+outputRootfile): # or  os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+DirectoryName+"/"+outputRootfile):
       #                        with open(FilesToBeCopiedToPNFStxt, 'a') as fobj1:
      #                             fobj1.write("gfal-copy "+DirectoryName+"/"+outputRootfile+" \'srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+outputRootfile+"\'"+"\n \n")
        #                   if os.path.exists(NewDirectoryPath+"/"+outputRootfile) and os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+outputRootfile):
         #                      with open(CleanupAreatxt, 'a') as cobj1:
          #                         cobj1.write("rm  "+DirectoryName+"/"+outputRootfile+"\n \n")
           #                
            #               if os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+outputRootfile):
             #              
              #                 if os.path.exists(NewDirectoryPath+"/"+TemplateFileNameAdjusted):
               #                    with open(CleanupAreapy, 'a') as dobj1:
                #                       dobj1.write("rm "+NewDirectoryPath+"/"+TemplateFileNameAdjusted+"\n \n")
                                   
   #            else:

# --- --- --- If HTCondor output's not okay, let's remove that file.  --- --- ---   
    #                          if args.verbose: print("File seems to be corrupted; let's remove it ...")
     #                         checkremoveFile = "rm "+DirectoryName+"/"+outputRootfile
      #                        if args.verbose: print(pycolors.red+checkremoveFile+pycolors.end)
       #                       subprocess.Popen([checkremoveFile], shell=True,
        #                                     stdout=subprocess.PIPE).communicate()[0]
         #                     with open(tobeRemovedtxt, 'a') as cobj:
          #                        cobj.write(checkremoveFile+"\n \n")
           #                   if args.verbose: print(pycolors.blue+"Corrupted file successfully removed."+pycolors.end)

          

      #print getIdlingJobs      
#      if countTemplateFiles > 10:
#          sys.exit("Here we stop the test run ...")
#    if "data" in path: print(Run)
  
  #samplename = ""
#  toaddInCommand =""
#  sampleNameLoop = []
  #pathsplit = path.split(".")



b = datetime.datetime.now()
print(b-a)
