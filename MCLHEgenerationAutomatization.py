#!/usr/bin/python

__author__ = 'Nicole Stefanov'
__date__ = 7/11/2019


## Usage python MCLHEgeneration.py -verbose -check -submit 


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
    italic = '\033[0;3m'

a = datetime.datetime.now() ## For performance check
TheLibraryPath =os.environ['LD_LIBRARY_PATH']
parser = argparse.ArgumentParser(description=' This script is for NTuple production on HTCondor.')
parser.add_argument('-submit', '--submit', action='store_true', help='Submitting HTCondor scripts.',required=False, default=False)
parser.add_argument('-check', '--check', action='store_true', help='Creating HTCondor submission scripts.',required=False, default=False)
parser.add_argument('-verbose', '--verbose', action='store_true', help='Prints out detailed information during execution',required=False, default=False)
parser.add_argument('-cpu', '--cpurequest', help='Request more cpu for running a job at HTCondor', required=False)
parser.add_argument('-time', '--timerequest', help='Time request for running a job at HTCondor',required=False)
parser.add_argument('-memory', '--memoryrequest', help='Memory request for running a job at HTCondor',required=False)

memoryrequest = ""
timerequest = ""

### Getting changes for requests in memory and time than default ones and other options stated beforehand                                                                        
args = parser.parse_args()


print(args)
#sys.exit()
### Switch off recovery mode in ROOT, if file is corrupted we don't want to keep even its ashes.
gROOT.ProcessLine("gEnv->SetValue(\"TFile.Recover\", 0);")

###### Method for creating HTCondor submission script                                                                                                     
###########################################################
def CreateSubmissionScript(Pathtodirectory, DirectoryName, CMSSW_BASE, cmsRunCommand, FileName, CreateEndOfSubmissionScript, NewGridpackPathDirectory):
                                '''Create job submission file for HTCondor in sample subdirectory'''
                                file = open(Pathtodirectory+"/"+DirectoryName+"/"+FileName+".submit","w")
                                file.write("universe            = vanilla\n \n")
                                file.write("transfer_executable = True \nshould_transfer_files   = IF_NEEDED \nwhen_to_transfer_output = ON_EXIT\n")
                                file.write("requirements = OpSysAndVer == \"SL6\"\ngetenv = true \n")
                                file.write("batch_name = "+FileName+"\n")
                                file.write("executable = "+CMSSW_BASE+"/src/wrapperScriptForHTCondor.sh\n")
                                file.write("output = "+Pathtodirectory+"/"+DirectoryName+"/HTCondorOutput/"+FileName+"_$(Cluster)_$(Process).out\n")
                                file.write("error = "+Pathtodirectory+"/"+DirectoryName+"/HTCondorOutput/"+FileName+"_$(Cluster)_$(Process).err\n")
   #                             file.write("output = HTCondorOutput/"+FileName+"_$(Cluster)_$(Process).out\n")
    #                            file.write("error = HTCondorOutput/"+FileName+"_$(Cluster)_$(Process).err\n")
                                file.write("initialdir = "+NewGridpackPathDirectory+"\n")
                                file.write("arguments = \""+cmsRunCommand+"\" \n \n")
                                file.write(CreateEndOfSubmissionScript)
                                file.close()


###Creating the end of submission script which is fixed once for all HTCondor scripts
    
CreateEndOfSubmissionScript="environment = \"LD_LIB_PATH="+TheLibraryPath+" X509_USER_PROXY=/nfs/dust/cms/user/stefanon/DM_Sample_Production/CMSSW_9_4_15/src/tmp/x509up_u28074 \" \n"
if args.cpurequest is not None:
                                CreateEndOfSubmissionScript+=" request_cpus = "+ args.cpurequest + "\n"

if args.memoryrequest is not None:
                                CreateEndOfSubmissionScript+="request_memory = "+ args.memoryrequest +" \n" #has to be in MB

if args.timerequest is not None:
                                CreateEndOfSubmissionScript+="+RequestRuntime     = "+ args.timerequest+"\n"

### For accessing pileup root files which aren't on DESY Tier2:
### mkdir tmp in working directory, copy proxy credential into working directory: cp /tmp/x509up_XXX  WorkingDirectory/tmp/.
### add X509_USER_PROXY= with exact path in environment, see above
#CreateEndOfSubmissionScript+="transfer_input_files = /tmp/x509up_u28074\n"

### max_materialize had problems once. Don't worry, simply deactivate if HTCondor submission does not work.
CreateEndOfSubmissionScript+="max_materialize = 1000\n"
CreateEndOfSubmissionScript+="queue \n"



def splitListintoSubListsOfPieceSize(ListToSplit, PieceSize):
    for item_splitListintoSubListsOfPieceSize in range(0, len(ListToSplit), PieceSize):
        yield ListToSplit[item_splitListintoSubListsOfPieceSize:item_splitListintoSubListsOfPieceSize + PieceSize]


##################
##################  START SCRIPT RUN
##################                         

# Define new directory being created during this script run when uploading finished files
pathArray =[#'/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi_1_Mphi_10_TuneCP5_13TeV_madgraphMLM_pythia8_RunIIFall17_GENSIM/',
            #'/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi_1_Mphi_20_TuneCP5_13TeV_madgraphMLM_pythia8_RunIIFall17_GENSIM/',
#            '/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi_1_Mphi_50_TuneCP5_13TeV_madgraphMLM_pythia8_RunIIFall17_GENSIM/',
            '/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi_1_Mphi_200_TuneCP5_13TeV_madgraphMLM_pythia8_RunIIFall17_GENSIM/',
#            '/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi_1_Mphi_300_TuneCP5_13TeV_madgraphMLM_pythia8_RunIIFall17_GENSIM/',
#            '/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi_1_Mphi_500_TuneCP5_13TeV_madgraphMLM_pythia8_RunIIFall17_GENSIM/',
#            '/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi_1_Mphi_1000_TuneCP5_13TeV_madgraphMLM_pythia8_RunIIFall17_GENSIM/',
]
#pathArray =['/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi-1_Mphi-100_TuneCP5_13TeV-madgraphMLM-pythia8-GENSIM/']

templateFile = 'EXO-RunIIFall17wmLHEGS-00005_ST-scalar_template_cfg.py'

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

SplitSizeStepOfFileList = 1 #10

OldDirectoriesSuffix = "AODSIM" #"PremixStep1" #"AODSIM" #"2018-MINIAODSIM" #"2018-AODSIM" #"PremixStep1" #"GENSIM"

NewDirectoriesSuffix = "GENSIM" # "MINIAODSIM" #"AODSIM" #"PremixStep1"  #"2018-NANOAODSIM"
      #              ############
    #                           #
  #                  as needed  #
#                               #
#################################
if args.submit:
    if getIdlingJobs > maxIdlingJobsAccepted:
        sys.exit(pycolors.blue+"Stop running this script due to too many jobs idling on HTCondor; try later again"+pycolors.end)

#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_Mphi10_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_Mphi20_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_MphiXXX_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_Mphi50_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_Mphi100_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_Mphi200_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_Mphi300_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_Mphi500_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
#PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_Mphi1000_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'

ExtraDirectoryCreationOnPNFS = "" #"2017/" #"2018/" #Don't forget / at the end.
#Monitoring files being created during run
tobeRemovedtxt ="tobeRemoved1.txt"
FilesToBeCopiedToPNFStxt = "FilesToBeCopiedToPNFS1.txt"
checkifAlreadyBeenCheckedInPreviousRun = []
if os.path.exists(Pathtodirectory+"/"+FilesToBeCopiedToPNFStxt):
  with open(FilesToBeCopiedToPNFStxt, 'r') as toreadin:
    for line in toreadin:
        checkifAlreadyBeenCheckedInPreviousRun.append(line.replace("\n", ''))
print(checkifAlreadyBeenCheckedInPreviousRun)
#sys.exit()
CleanupAreatxt = "CleanupArea1.txt"
CleanupAreapy = "CleanupAreapy1.txt"

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

#  files = []
  # r=root, d=directories, f = files  ### here root does not refer to .root-files    
 # for r, d, f in os.walk(path):
  #  for file in f:
   #     if '.root' in file:
    #        files.append(os.path.join(r, file))

  #if args.verbose: 
   #   print("FileNumberInDirectory is "+str(len(files)))
  #    print(files)

  
  #getSlicedListwithPNFS = list(splitListintoSubListsOfPieceSize(files, SplitSizeStepOfFileList))
  #fileswithoutPNFS = []
  #for itemfile in files:
  #    itemfile = itemfile.replace("/pnfs/desy.de/cms/tier2","")
   #   fileswithoutPNFS.append(itemfile)
  #getSlicedList = list(splitListintoSubListsOfPieceSize(fileswithoutPNFS, SplitSizeStepOfFileList)) 
  #print(getSlicedList)
  #if args.verbose: print(len(getSlicedList))
  prefixName = 'TopDMJets_scalar_tWChan_Mchi_1_Mphi_'
  PathToGridpack = '/nfs/dust/cms/user/stefanon/DM_Sample_Production/DMsingleTop/DMScalar_top_tWChan_Mchi1_MphiXXX_slc6_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz'
  massNumber = path.replace('/pnfs/desy.de/cms/tier2/store/user/nstefano/TopDMJets_scalar_tWChan_Mchi_1_Mphi_', '').replace('_TuneCP5_13TeV_madgraphMLM_pythia8_RunIIFall17_GENSIM/', '')
  PathToGridpack = PathToGridpack.replace('XXX', massNumber)
  if args.verbose:
      print(path)
      print(PathToGridpack)
  #continue
  #sys.exit()
  # Set CMSSW BASE
  CMSSW_BASE_GET = subprocess.Popen(["echo $CMSSW_BASE"], shell=True,
                          stdout=subprocess.PIPE).communicate()[0]
  CMSSW_BASE= CMSSW_BASE_GET[:-1]

  pathsplit = path.split("/")
  DirectoryName = ""  
  DirectoryNameOld = ""
#GENSIM step adjustment
#  if pathsplit[-1]:
#    DirectoryName = pathsplit[-3]
#  else:
#    DirectoryName = pathsplit[-4]

  if pathsplit[-1]:
    DirectoryName = pathsplit[-1]  
  else:
    DirectoryName = pathsplit[-2]
  
  DirectoryNameOld = DirectoryName
  
  #DirectoryName = DirectoryName.replace(OldDirectoriesSuffix, NewDirectoriesSuffix)
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

#  if args.verbose: print(getListOfCondor)

  for subListIngetSlicedList in range(1358, 1434): #5000): #getSlicedList:
      if args.verbose: print(subListIngetSlicedList)
      countTemplateFiles +=1
      TemplateFileNameAdjusted = ''
  #    if SplitSizeStepOfFileList ==1:
      #subListIngetSlicedList = str(subListIngetSlicedList)
      if args.verbose:
              print("DirectoryNameOld ")
              print(DirectoryNameOld)

#          getNumberOfRootFileInDirectoryNameOld = subListIngetSlicedList.split(DirectoryNameOld+"_")                                                                                                                                       
         # getNumberOfRootFileInDirectoryNameOld = subListIngetSlicedList.split("/")
          #if args.verbose: print(getNumberOfRootFileInDirectoryNameOld)                                                                                                                                                                                     
          #getNumberOfRootFileInDirectoryNameOld = getNumberOfRootFileInDirectoryNameOld[-1].split("_")
          #if args.verbose: print(getNumberOfRootFileInDirectoryNameOld)                                                                                                                                                                                     
#          getNumberOfRootFileInDirectoryNameOld = getNumberOfRootFileInDirectoryNameOld[-1].split(".")
          #if args.verbose: print(getNumberOfRootFileInDirectoryNameOld)                                                                                                                                                                                     
          #getNumberOfRootFileInDirectoryNameOld = getNumberOfRootFileInDirectoryNameOld[-3]
          #if args.verbose: print(getNumberOfRootFileInDirectoryNameOld)                                                                                                                                                                                     
      TemplateFileNameAdjusted = templateFile.replace('template', str(subListIngetSlicedList)).replace('EXO', prefixName+massNumber)
#DirectoryName+"_"+str(getNumberOfRootFileInDirectoryNameOld)+"_"+templateFile
          #sys.exit("Stopping test")                                                                                         
          #sys.exit("Stopping test")          
#      else:
 #         TemplateFileNameAdjusted = DirectoryName+"_"+str(countTemplateFiles)+"_"+templateFile
      if not TemplateFileNameAdjusted: sys.exit("Error in  assinging a label in TemplateFileNameAdjusted.")
      exaktPathoutputRootfile = Pathtodirectory+"/"+DirectoryName+"/"+TemplateFileNameAdjusted[:-7]+".root"
      FileName = TemplateFileNameAdjusted[:-7]
      rootOutputFile = TemplateFileNameAdjusted[:-7]+".root"


      if not os.path.exists(DirectoryName+"/"+str(subListIngetSlicedList)) and not os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile) and not os.path.exists(NewDirectoryPath+"/"+rootOutputFile):
          if args.verbose: print(DirectoryName+"/"+str(subListIngetSlicedList)+" and "+"/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile+" not found ... let's create it new")
          
          os.makedirs(DirectoryName+"/"+str(subListIngetSlicedList))
          copy(PathToGridpack, DirectoryName+"/"+str(subListIngetSlicedList)+"/"+PathToGridpack.split('/')[-1])
      NewGridpackPath = NewDirectoryPath+"/"+str(subListIngetSlicedList)+"/"+PathToGridpack.split('/')[-1]
      NewGridpackPathDirectory = NewDirectoryPath+"/"+str(subListIngetSlicedList)


      if args.verbose: print(pycolors.red+FileName+pycolors.end)
      if not os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile):
       if not os.path.exists(NewDirectoryPath+"/"+rootOutputFile): # and not os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+outputRootfile):
        if not os.path.exists(NewDirectoryPath+"/"+TemplateFileNameAdjusted):
          copy(Pathtodirectory+"/"+templateFile, NewDirectoryPath+"/"+TemplateFileNameAdjusted)
          whatToReplace = "sed -i -e \"s?GRIDPACKPATH?"+NewGridpackPath+"?g\" "+NewDirectoryPath+"/"+TemplateFileNameAdjusted
          print(whatToReplace)
          subprocess.Popen([whatToReplace], shell=True,
                          stdout=subprocess.PIPE).communicate()[0]

          whatToReplace = "sed -i -e \"s?OUTPUTROOT?"+exaktPathoutputRootfile+"?g\" "+NewDirectoryPath+"/"+TemplateFileNameAdjusted
          subprocess.Popen([whatToReplace], shell=True,
                          stdout=subprocess.PIPE).communicate()[0]
      
        cmsRunCommand = "cmsRun "+NewDirectoryPath+"/"+TemplateFileNameAdjusted
        CreateSubmissionScript(Pathtodirectory, DirectoryName, CMSSW_BASE, cmsRunCommand, FileName, CreateEndOfSubmissionScript, NewGridpackPathDirectory)
        jobInBatch = False
        #for item_ask_condor in ask_condor:
        if FileName in ask_condor_getFileNames:
                jobInBatch = True
                
                if args.verbose: print("Job is already at HTCondor. No Job submission")
        if not jobInBatch:
           if args.submit:
            submitToHTCondor = "condor_submit "+DirectoryName+"/"+FileName+".submit"
            if args.verbose: print(pycolors.red+submitToHTCondor+pycolors.end)
            subprocess.Popen([submitToHTCondor], shell=True,
                              stdout=subprocess.PIPE).communicate()[0]
            getIdlingJobs += 1
            if getIdlingJobs > maxIdlingJobsAccepted:
                          sys.exit(pycolors.blue+"Stop running this script due to too many jobs idling on HTCondor; try later again"+pycolors.end)
      if args.check:
          
          if os.path.exists(NewDirectoryPath+"/"+rootOutputFile): # or os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile):
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
                           inputFile = ROOT.TFile.Open(NewDirectoryPath+"/"+rootOutputFile, "read")
                           getNEventsTier2Sample = inputFile.Get("Events")
                           getNEventsTier2 = getNEventsTier2Sample.GetEntries()
                           inputFile.Close()

                      except:
                           if args.verbose: print("File seems to be corrupted; let's remove it ...")
#                              checkremoveFile = "rm "+DirectoryName+"/"+rootOutputFile
 #                             if args.verbose: print(pycolors.red+checkremoveFile+pycolors.end)
  #                            subprocess.Popen([checkremoveFile], shell=True,
   #                                          stdout=subprocess.PIPE).communicate()[0]
    #                          with open(tobeRemovedtxt, 'a') as cobj:
     #                             cobj.write(checkremoveFile+"\n \n")
      #                        if args.verbose: print(pycolors.blue+"Corrupted file successfully removed."+pycolors.end)

                      
                      if args.verbose:
                          print("Number of Entries in "+FileName+": "+str(getNEventsTier2))
                      
                      ## Number of event check not enough; sometimes SimG4CoreApplication is missing and things break later on in other simulation steps 
                      #if getNEventsTier2 == 200:    
    #r.TFile.Open(h, "read")
                       #   getAllJobsSendForThatFile = []
                        #  for item_getListOfCondor in getLineByLineCondor:
                         #     print(item_getListOfCondor)
                          #    if FileName in item_getListOfCondor:
                           #       if args.verbose: print(item_getListOfCondor)
                            #      getAllJobsSendForThatFile.append(item_getListOfCondor)
                             #     SimG4CoreApplicationFound = False
#               BeginProcess = False
#               GotMessageLoggerSummary = False
#               GotLastCheck = False
#               FatalException = True
                          #if args.verbose: print(getAllJobsSendForThatFile)

# Let's check latest created HTCondor output file with suffix .err
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~               

# --- --- --- Finding the correct HTCondor output file --- --- ---

                   #       getExactJobFileName = ''
                   #       if ".err" in  getAllJobsSendForThatFile[-1]:
                    #                  getExactJobFileName = getAllJobsSendForThatFile[-1].split(' ')
                    #      elif ".err" in  getAllJobsSendForThatFile[-2]:
                     #                 if args.verbose: print("Passed  if not .err in getExactJobFileName:")
                      #                getExactJobFileName = getAllJobsSendForThatFile[-2].split(' ')
                       #   if not getExactJobFileName:
                        #              sys.exit("Error! Haven't found the correct HTCondor .err file for  "+FileName)
                         # whichJobFileToCheck = DirectoryName+"/HTCondorOutput/"+getExactJobFileName[-1]
                                  #print(getFileContent)

# --- --- --- Checking HTCondor output file if key words included/not included --- --- --- 
                         # checkSimG4CoreApplication = subprocess.Popen(["grep -r \"SimG4CoreApplication\" "+whichJobFileToCheck], shell=True,stdout=subprocess.PIPE).communicate()[0] 
                                  
                          #if checkSimG4CoreApplication: 
                           #           SimG4CoreApplicationFound = True
                            #          if args.verbose: print("Found SimG4CoreApplication")
#               checkBeginProcess = subprocess.Popen(["grep -r \"Begin processing the\" "+whichJobFileToCheck], shell=True,
#                                     stdout=subprocess.PIPE).communicate()[0]
#               if checkBeginProcess:
#                   BeginProcess = True
#                   if args.verbose: print("Found: Begin processing the")
#               checkFatalException  = subprocess.Popen(["grep -r \"Fatal Exception\" "+whichJobFileToCheck], shell=True,
#                                     stdout=subprocess.PIPE).communicate()[0]
#               if not checkFatalException:
#                   FatalException = False
#                   if args.verbose: print("Found: No Fatal Exception")
#
#               checkMessageLogger =  subprocess.Popen(["grep -r \"MessageLogger Summary\" "+whichJobFileToCheck], shell=True,
#                                     stdout=subprocess.PIPE).communicate()[0]
#               if args.verbose:
#                   print("checkMessageLogger")
#                   print(checkMessageLogger)
#               if checkMessageLogger:
#                   GotMessageLoggerSummary = True
 #                  if args.verbose: print("Found: MessageLogger Summary")
 #              checkGotLastCheck = subprocess.Popen(["grep -r \"dropped waiting message count 0\" "+whichJobFileToCheck+" | tail -1"], shell=True,
  #                                   stdout=subprocess.PIPE).communicate()[0]
  #             if args.verbose:
  #                 print("checkGotLastCheck")
  #                 print(checkGotLastCheck)
   #            if checkGotLastCheck: 
    #               GotLastCheck = True
     #              if args.verbose: print("Found: dropped waiting message count 0")
               #if GotLastCheck[-1].count("Aborted"):
      #          #   print "found aborted"
       #        if args.verbose:
        #           print("BeginProcess")
         #          print(BeginProcess)
          #         print("GotMessageLoggerSummary")
           #        print(GotMessageLoggerSummary)
            #       print("GotLastCheck")
             #      print(GotLastCheck)

# --- --- --- Decision about file's sanity according to  HTCondor output --- --- ---   
                      #BeginProcess and GotMessageLoggerSummary and GotLastCheck and not checkFatalException:
                      if getNEventsTier2 == 200: # and SimG4CoreApplicationFound: 
                       #if args.verbose: 
                           if args.verbose: print("File passed sanity check!")
                           if not os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile): # or  os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+DirectoryName+"/"+outputRootfile):
                               with open(FilesToBeCopiedToPNFStxt, 'a') as fobj1:
                                   fobj1.write("gfal-copy "+DirectoryName+"/"+rootOutputFile+" \'srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile+"\'"+"\n \n")
                               gfalCopyCommand = "gfal-copy "+DirectoryName+"/"+rootOutputFile+" \'srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile+"\'"
                               copyingIt =subprocess.Popen([gfalCopyCommand], shell=True, stdout=subprocess.PIPE).communicate()[0]
                               print(copyingIt)
                           subdirectoryToBeRemoved = False
                           if os.path.exists(DirectoryName+"/"+str(subListIngetSlicedList)):
                                   removeGridpackDirectory = "rm -rf "+DirectoryName+"/"+str(subListIngetSlicedList)
                                   if args.verbose: print(pycolors.red+removeGridpackDirectory+pycolors.end)
                                   subdirectoryToBeRemoved = True
                               #sys.exit()
                                   subprocess.Popen([removeGridpackDirectory], shell=True, stdout=subprocess.PIPE).communicate()[0]
                           if os.path.exists(DirectoryName+"/"+rootOutputFile):
                               print(pycolors.italic+"os.path.exists("+DirectoryName+"/"+rootOutputFile+") is "+str(os.path.exists(DirectoryName+"/"+rootOutputFile))+pycolors.end) 
#                               time.sleep(1.)
                               if os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile):
                                   print(pycolors.italic+" and os.path.exists(/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile+")  is "+str(os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile))+pycolors.end)
                                   print("Thus let's remove it")
                                   CleanupRootFile = "rm  "+DirectoryName+"/"+rootOutputFile
                                   if args.verbose: print(pycolors.green+CleanupRootFile+pycolors.end)
                               #subdirectoryToBeRemoved = True                                                                                                                                                                                                                                                                                               
                                   subprocess.Popen([CleanupRootFile], shell=True,
                                             stdout=subprocess.PIPE).communicate()[0]
                               else: print(pycolors.red+"/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile+" not found"+pycolors.end)
                           if subdirectoryToBeRemoved:
                                   if os.path.exists(DirectoryName+"/"+str(subListIngetSlicedList)):
                                                          sys.exit("Something went wrong when trying to remove directory: "+DirectoryName+"/"+str(subListIngetSlicedList))
                           if os.path.exists(DirectoryName+"/"+rootOutputFile) and os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile):
                               with open(CleanupAreatxt, 'a') as cobj1:
                                   cobj1.write("rm  "+DirectoryName+"/"+rootOutputFile+"\n \n")
                               CleanupRootFile = "rm  "+DirectoryName+"/"+rootOutputFile
                               if args.verbose: print(pycolors.green+CleanupRootFile+pycolors.end)
                               #subdirectoryToBeRemoved = True
                               subprocess.Popen([CleanupRootFile], shell=True,
                                             stdout=subprocess.PIPE).communicate()[0]

                           if os.path.exists("/pnfs/desy.de/cms/tier2/store/user/nstefano/"+ExtraDirectoryCreationOnPNFS+DirectoryName+"/"+rootOutputFile):
                               if os.path.exists(DirectoryName+"/"+TemplateFileNameAdjusted):
                                   with open(CleanupAreapy, 'a') as dobj1:
                                       dobj1.write("rm "+DirectoryName+"/"+TemplateFileNameAdjusted+"\n \n")
                                   CleanupRootupAreapy = "rm "+DirectoryName+"/"+TemplateFileNameAdjusted
                                   subprocess.Popen([CleanupRootupAreapy], shell=True,
                                             stdout=subprocess.PIPE).communicate()[0]
                                   
                      else:

# --- --- --- If HTCondor output's not okay, let's remove that file.  --- --- ---   
                              if args.verbose: print("File seems to be corrupted; let's remove it ...")
                              checkremoveFile = "rm "+DirectoryName+"/"+rootOutputFile
                              if args.verbose: print(pycolors.red+checkremoveFile+pycolors.end)
                              subprocess.Popen([checkremoveFile], shell=True,
                                             stdout=subprocess.PIPE).communicate()[0]
                              with open(tobeRemovedtxt, 'a') as cobj:
                                  cobj.write(checkremoveFile+"\n \n")
                              if args.verbose: print(pycolors.blue+"Corrupted file successfully removed."+pycolors.end)


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
