#!/bin/sh
ffmpeg -r 15 -y -pix_fmt rgb8 -i rendering/crop_plot%05d.jpg sshd.mp4


