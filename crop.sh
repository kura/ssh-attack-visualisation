#!/bin/sh
cd rendering
for file in `ls -lah plot* | awk '{print $8}'`;
do
  new_file=`echo $file | sed 's/\.png/\.jpg/'`
  convert -channel RGBA -depth 8 -crop 1136x720+53-0 $file crop_$new_file
done
