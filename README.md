# LmortalCamService
 Client-Server pairs for UDP video streaming

# How to use / How it works
- Run server and client, client ui with 'send' button.
- socketReceive() has recvfrom() in it, then it will initialize 2 subprocesses with popen, then write() into first pipe .stdin

# Issue (more thoughts at top of Functions.py)
- In functions.py in sortpackets(), the p1.stdin.write() brings up these errors:
- BrokenPipeError: [Errno 32] Broken pipe
- OSError: [Errno 22] Invalid argument - this is very rare though.
- I think [Errno 32] is an I/O Error, something like the receiving pipe has an error which causes it to close;
I thought this might because I was putting in the wrong video data, but then I changed ffmpeg param. from 'rawvideo' to 'image2video' and
it removed the packet corrupt error and kept [Errno 32], so I'm thinking it might be something else more basic to do with pipes, like not using close() or something.


ffmpegExample is the isolated function which works with the rawdata from videocapture(), whereas in my function
I encode it into jpg > base64 and back, but upon checking packets they remain after decoding
; thus the issue is either:
- with the way the pipes are initialized and created
- the ffmpeg command parameters needing to be different for the jpg encoded frames.


# Other Errors if you come across them
- I was getting 'Packet corrupt (stream = 0, dts = 0)', when putting the .jpg imencode() data into the ffmpeg with 'rawvideo'
so that makes sense, as i'm not getting that anymore with correct params.
- /will throw error such as: struct.error: 'h' format requires -32768 <= number <= 32767, if you increae
packet size by changing data to png/bmp since I haven't finished properly splitting the packets before sending.

