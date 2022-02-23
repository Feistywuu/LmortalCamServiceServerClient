import os
import subprocess
import ffmpeg
import cv2 as cv
import Functions
import subprocess
import numpy as np

print(os.getcwd())

rtmp_url = "rtmp://127.0.0.1:1935/live/app"

# opencv width,height, fps natively
# making sure whole frames
# ffmpeg locally

vid = cv.VideoCapture(0)

# gather video information for ffmpeg
fps = int(vid.get(cv.CAP_PROP_FPS))
width = int(vid.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(vid.get(cv.CAP_PROP_FRAME_HEIGHT))


command = ['ffmpeg',
            '-y',
            '-f', 'rawvideo',                       # global/input options
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', "{}x{}".format(width, height),
            '-r', str(fps),                           # force fps to stated value
            '-i', '-',                              # input url from pipe
            '-pix_fmt', 'yuv420p',                  # output file options
            '-preset', 'ultrafast',
            '-c:v', 'libx264',
            '-f', 'flv',
            '-listen', '1',
             rtmp_url]


# create subprocess to run command and open pipe
p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

while vid.isOpened():

    ret, frame = vid.read()
    if not ret:
        print("frame read failed")
        break
    # write to pipe
    p.stdin.write(frame.tobytes())
    print('hi1')
    p.stdout.readline()
    print('hi2')
    # p.stdin.close()
