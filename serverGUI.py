# UI and main processing loop for server to receive packets and display them.
# from queue import *
import sys
import threading
import logging
import functions

' Plan of action '

# fix delay to desired amount
# fix stability issues


# need to change file name?
def main():
    # set variables
    format1 = "%(asctime)s: %(message)s"

    logging.basicConfig(format=format1, level=logging.INFO, datefmt="%H:%M:%S")

    # create main socket recv thread
    thrd = threading.Thread(target=functions.socketReceive())

    return 0

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

' later '
 #IIS on windows 10, app pools
 #iostream


if __name__ == '__main__':
    sys.exit(main())
