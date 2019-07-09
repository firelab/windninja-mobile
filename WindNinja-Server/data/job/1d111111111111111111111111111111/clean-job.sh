#!/bin/bash

# get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
echo $DIR
cd $DIR

# remove all files but the script and .clean files
shopt -s extglob
for f in !(*.clean|*.sh|*.pending); do
    rm -R -v $f
done

#rename any .clean files
for f in *.clean; do
    cp -a -v $f ${f%.*}
done
shopt -u extglob