#!/bin/bash

##############################################################################################
####
####    This script is meant for facilitating to check/create proxy, set crab3 environment 
####
###############################################################################################

#echo "Positional Parameters"
#echo '$0 = ' $0
#echo '$1 = ' $1



if [[ -n $1 ]]; then
    
    echo "Usage is: source crab3.sh in order to load proxy & crab3 and cmssw environment
          ";    
fi
if [[ -z $1 ]]; then
    cmsenv


    source /cvmfs/cms.cern.ch/crab3/crab.sh

    voms-proxy-info >& test_check_proxy.txt
#    cat test_check_proxy.txt
    gettime=$(grep "timeleft" test_check_proxy.txt);
    checktime=$(echo $gettime | grep -P -o "[0-9]+" | head -1)
#    echo $checktime
    if grep -q "Proxy not found" test_check_proxy.txt;  then
        echo "                                                                                                              
               No proxy has been found                                                                                      
               So let's one count ...                                                                                      
                                                                                                                            
               voms-proxy-init -voms cms 
             "
	voms-proxy-init -voms cms -hours 192    

################# If you gfal-copy on /pnfs make a new "voms-proxy-init -voms cms" 
################# since DESY_Tier2 does not allow uploading files with a proxy wiht a longer life time


    elif [[ $checktime -lt 8 ]]; then
	echo "
          Less than 8 hours left until proxy destruction; let's create a new proxy ... 
          
          voms-proxy-init -voms cms 
         "
	voms-proxy-init -voms cms -hours 192

    elif [[ $checktime -ge 8 ]]; then
	echo "
               Proxy has been checked
               its diel life's backed
               Thus enough time's left
               at work to be deft ...
               
               or in other words:



               Enough proxy life time available: "$checktime" hours;
               crab3 environment loaded

            "
    fi

    rm test_check_proxy.txt

fi



