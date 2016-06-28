#!/bin/bash 

#delete jobs older than 5 days except the Point Six job
find /srv/WindNinjaServer/Data/job/* -maxdepth 0 -type d -mtime +5 ! -name '23becdaadf7c4ec2993497261e63d813' -type d -exec rm -rf {} \;
