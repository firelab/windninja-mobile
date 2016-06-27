#!/bin/bash 

#delete jobs older than 5 days except the Point Six job
find /srv/WindNinjaServer/Data/job/* -maxdepth 0 -type d -ctime +5 -name '1a111111111111111111111111111111' -prune -o -exec rm -rf {} \;
