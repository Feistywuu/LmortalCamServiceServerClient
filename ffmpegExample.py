import os
import cv2 as cv
import subprocess
import imutils

print(os.getcwd())

rtmp_url = "rtmp://127.0.0.1:1935/live/app"

# opencv width,height, fps natively
# making sure whole frames
# ffmpeg locally

vid = cv.VideoCapture(0)

# gather video information for ffmpeg
G = lambda: ...

G.fps = int(vid.get(cv.CAP_PROP_FPS))
G.width = int(vid.get(cv.CAP_PROP_FRAME_WIDTH))
G.height = int(vid.get(cv.CAP_PROP_FRAME_HEIGHT))

print(str(G.width) + " " + str(G.height) + " " + str(G.fps))

command = ['ffmpeg',
            '-y',
            '-re',
            '-f', 'image2pipe',                            # global/input options
            '-c:v', 'mjpeg',
            '-pix_fmt', 'bgr24',
            '-s', "{}x{}".format(G.width, G.height),
            '-r', str(G.fps),                           # force fps to stated value
            '-i', '-',                              # input url from pipe
            '-pix_fmt', 'yuv420p',                  # output file options
            '-preset', 'ultrafast',
            '-c:v', 'libx264',
            '-f', 'flv',
            '-listen', '1',
             rtmp_url]


# create subprocess to run command and open pipe
p = subprocess.Popen(command, stdin=subprocess.PIPE) # , stdout=subprocess.PIPE)

while vid.isOpened():

    ret, frame = vid.read()
    if not ret:
        print("frame read failed")
        break

    frame = imutils.resize(frame, width=G.width, height=G.height)
    encoded, buffer = cv.imencode('.JPEG', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

    if encoded:
        p.stdin.write(buffer.tobytes())

    # XXX direct
    # p.stdin.write(frame.tobytes())

