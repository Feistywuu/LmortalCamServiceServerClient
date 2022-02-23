# unused functions

def ProcessFrames(clientid, clientdictionary):
    '''
    Will pop the frame from the bottom of the stack.
    When given a the key from a dictionary, retrieves frames thread-safely and pops them from the dict,
    then performs decoding, timing to show frames as a video
    '''
    previoustime = threading.local()
    previoustime.t = 0.01
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)

    print('Start Processing')
    # iterate over frames in dictionary key
    for i in range(len(clientdictionary[clientid])):
        # iterating through frames

        frame = cv.putText(clientdictionary[clientid][i], 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        previoustime.t = fpsMaintainer(10, previoustime.t)
        cv.imshow("RECEIVING VIDEO", frame)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            #threadsocket.close()
            break


def fpsMaintainer(targetfps, previoustime):
    """
    Function to sleep thread according to desired fps.
    Starts recording time spent from first function call, when returning to function call again, sleep() thread
    if amount of time required to set a desired fps is needed.
    :return: time at specific point in function = int
    """
    print('FPS Check')

    # start recording time, with time()
    currentTime = time.time()

    # check value of 1/fps and compare value to time passed since last function call
    elapsedTime = currentTime - previoustime
    desiredSleep = 1 / targetfps
    print(elapsedTime)

    try:
        time.sleep(desiredSleep - elapsedTime)
        print(time.sleep(desiredSleep - elapsedTime))
    except ValueError:
        print('No sleep')

    return currentTime


command = ['ffmpeg',
               '-y',
               '-f', 'rawvideo',                            # global/input options
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24',
               '-s', "{}x{}".format(width, height),
               '-r', str(fps),                              # force fps to stated value
               '-i', '-',                                   # input url from pipe
               '-pix_fmt', 'yuv420p',                       # output file options
               '-preset', 'ultrafast',
               '-c:v', 'libx264',
               '-f', 'flv',
               '-listen', '1',
               rtmp_url]