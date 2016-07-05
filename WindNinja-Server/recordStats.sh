#!/bin/sh

DIR=/srv/WindNinjaServer/Data/job
LOGFILE=/home/ubuntu/logs/stats.log

inotifywait -m "$DIR" --format '%w%f' -e create |
while read file; do
    (cat "$file/job.json"; echo "") >> "$LOGFILE"
done



