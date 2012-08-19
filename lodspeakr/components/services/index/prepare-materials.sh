#!/bin/bash

# git clone git://github.com/timrdf/pml.git github-pml
pushd github-pml &> /dev/null
   git pull
popd &> /dev/null

# hg clone http://dvcs.w3.org/hg/prov hg-prov-wg
pushd hg-prov-wg &> /dev/null
   hg pull
popd &> /dev/null
