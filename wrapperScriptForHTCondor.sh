#!/bin/sh

### not meant to be run directly; simply a wrapper executable
export LD_LIBRARY_PATH=${LD_LIB_PATH}
#export X509_USER_PROXY=${HOME}/.globus/usercert.pem
"$@"
