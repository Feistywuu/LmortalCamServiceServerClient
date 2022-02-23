# UI and main processing loop for server to receive packets and display them.

from queue import *
import threading
import logging
import Functions

' Plan of action'

# create client ui
#       show device in UI
#       dropdown box for device,quality,port,server ip
#       receive 'connection established etc' - might require a cookie sent back from server with a variable changed?

# create server ui
#       display video information
#       OR just go directly OBS

'Current'
# get ffmpegg to work on main implementation
# fix errors with larger packets being partitioned (haven't attempted yet)
#   /will throw error such as: struct.error: 'h' format requires -32768 <= number <= 32767
# fix delay to desired amount
# fix stability issues
# fps to 30


# need to change file name?
if __name__ == "__main__":

    # set variables
    queue = Queue()
    format1 = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format1, level=logging.INFO,
                        datefmt="%H:%M:%S")

    # create main socket recv thread
    thrd = threading.Thread(target=Functions.socketReceive())

    # spawn thread for tkinter gui
    #later

    # have button in the gui to stop listening - join() request_handler thread.
    #x.join()

# UI

#window = tk.Tk()

# add widgets here

#window.title('Hello Python')
#window.geometry("300x200+10+20")
#window.mainloop()

'later'
    #IIS on windows 10, app pools
    #iostream

