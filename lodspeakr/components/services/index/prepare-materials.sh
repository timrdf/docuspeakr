#!/bin/bash

date +"%Y-%m-%d" | awk '{printf("%s",$1)}' > respec.publishDate

# git clone git://github.com/timrdf/pml.git github-pml
pushd github-pml &> /dev/null
   git pull
popd &> /dev/null

# hg clone http://dvcs.w3.org/hg/prov hg-prov-wg
pushd hg-prov-wg &> /dev/null
   hg pull
popd &> /dev/null

pushd includes &> /dev/null
   rm -f *.html; .././cross-reference.py pml http://provenanceweb.org/ns/pml# https://raw.github.com/timrdf/pml/master/ontology/pml-3.0.owl http://provenanceweb.org/ns/pml#
popd &> /dev/null
